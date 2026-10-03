from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
import re
import os

from .models import ChatMessage
from approvals.models import Approval, ApprovalRequirement
from documents.models import Document
from applications.models import Application
from inspections.models import Inspection
from compliance.models import Compliance, Renewal
from schemes.models import GovernmentScheme
from business.models import BusinessProfile
from .ai_engine import (
    SYSTEM_TRAINING_PROMPT_TEMPLATE,
    get_enterprise_context,
    get_approvals_catalog,
    get_schemes_catalog,
    call_groq_llm,
)

def chat_view(request):
    """Anumati Assistant UI Page."""
    messages_history = []
    if request.user.is_authenticated:
        messages_history = list(ChatMessage.objects.filter(user=request.user).order_by('created_at')[:40])
    elif request.session.session_key:
        messages_history = list(ChatMessage.objects.filter(session_key=request.session.session_key).order_by('created_at')[:40])

    business = None
    if request.user.is_authenticated:
        business = request.user.business_profiles.first()

    has_groq = bool(os.getenv('GROQ_API_KEY', '').strip())
    groq_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    return render(request, 'assistant/chat.html', {
        'messages_history': messages_history,
        'business': business,
        'is_dashboard': request.user.is_authenticated,
        'has_groq': has_groq,
        'groq_model': groq_model,
    })


@csrf_exempt
def api_chat(request):
    """
    Hybrid Intelligent AI Query Engine:
    1. Primary: Groq Cloud Llama-3.3-70B trained on live Supabase records & statutory acts.
    2. Fallback: Fast deterministic RAG query engine grounded in local database records.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip()
    except Exception:
        user_message = request.POST.get('message', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    user_obj = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key or ''
    if not session_key and not user_obj:
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_key = request.session.session_key

    # Save user message to database
    ChatMessage.objects.create(
        user=user_obj,
        session_key=session_key,
        role='user',
        content=user_message
    )

    # 1. Retrieve Live Context from Supabase PostgreSQL
    approvals = list(Approval.objects.all())
    schemes = list(GovernmentScheme.objects.filter(is_active=True))

    business = None
    user_apps = Application.objects.none()
    user_docs = Document.objects.none()
    user_inspections = Inspection.objects.none()
    user_compliances = Compliance.objects.none()
    user_profile = getattr(user_obj, 'profile', None) if user_obj else None

    if user_obj:
        business = user_obj.business_profiles.first()
        user_apps = list(Application.objects.filter(user=user_obj))
        user_docs = list(Document.objects.filter(user=user_obj))
        user_inspections = list(Inspection.objects.filter(application__user=user_obj))
        if business:
            user_compliances = list(Compliance.objects.filter(business=business))

    biz_name = business.company_name if business else "Your Enterprise"
    biz_sector = business.industry_sector if business else "General Manufacturing"
    biz_district = business.district if business else "Maharashtra"

    # 2. Check if Groq Cloud LLM is available
    groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
    bot_response = ""
    intent = "general"
    sources = []

    if groq_api_key:
        try:
            # Build enterprise & catalog training context
            ent_context = get_enterprise_context(user_obj, business, user_apps, user_docs, user_inspections, user_compliances)
            apprv_catalog = get_approvals_catalog(approvals)
            schm_catalog = get_schemes_catalog(schemes)

            user_apps_summary = ", ".join([a.application_id for a in user_apps]) if user_apps else "None"

            system_prompt = SYSTEM_TRAINING_PROMPT_TEMPLATE.format(
                enterprise_context=ent_context,
                approvals_catalog=apprv_catalog,
                schemes_catalog=schm_catalog,
                user_apps_summary=user_apps_summary
            )

            # Retrieve prior conversation turns
            recent_chats = []
            if user_obj:
                recent_msgs = ChatMessage.objects.filter(user=user_obj).order_by('-created_at')[:6]
                recent_chats = [{'role': m.role, 'content': m.content} for m in reversed(list(recent_msgs))]

            llm_text, model_name = call_groq_llm(user_message, system_prompt, recent_chats)
            if llm_text:
                bot_response = llm_text
                intent = "groq_llm"
                sources.append(f"{model_name} (Grounded in AnumatiSetu Supabase DB)")
        except Exception as e:
            bot_response = ""

    # 3. Deterministic RAG Fallback (If Groq is unset or offline)
    if not bot_response:
        user_lower = user_message.lower()

        # Specific Approval Catalog Inquiry
        matched_approval = None
        for apprv in approvals:
            if (apprv.name.lower() in user_lower or 
                apprv.code.lower() in user_lower or 
                any(word in user_lower for word in apprv.name.lower().split() if len(word) > 4)):
                matched_approval = apprv
                break

        if not matched_approval:
            if any(k in user_lower for k in ['mpcb', 'consent to establish', 'cte', 'consent to operate', 'cto', 'pollution']):
                matched_approval = next((a for a in approvals if 'mpcb' in a.code.lower()), None)
            elif any(k in user_lower for k in ['dish', 'factory plan', 'factories act', 'factory licence', 'factory license']):
                matched_approval = next((a for a in approvals if 'dish' in a.code.lower()), None)
            elif any(k in user_lower for k in ['fire', 'fire noc', 'fire safety', 'midc fire']):
                matched_approval = next((a for a in approvals if 'fire' in a.code.lower()), None)
            elif any(k in user_lower for k in ['power', 'electricity', 'msedcl', 'load', 'feeder', 'ht connection']):
                matched_approval = next((a for a in approvals if 'msedcl' in a.code.lower()), None)
            elif any(k in user_lower for k in ['fssai', 'food safety', 'food license', 'food licence']):
                matched_approval = next((a for a in approvals if 'fssai' in a.code.lower()), None)
            elif any(k in user_lower for k in ['water', 'midc water', 'water supply', 'pipeline']):
                matched_approval = next((a for a in approvals if 'water' in a.code.lower()), None)
            elif any(k in user_lower for k in ['stamp duty', 'stamp waiver', 'registration fee exemption']):
                matched_approval = next((a for a in approvals if 'stamp' in a.code.lower()), None)
            elif any(k in user_lower for k in ['boiler', 'steam', 'boiler registration']):
                matched_approval = next((a for a in approvals if 'boiler' in a.code.lower()), None)

        if matched_approval:
            intent = "approval_detail"
            sources.append(f"{matched_approval.department}")
            reqs = ApprovalRequirement.objects.filter(approval=matched_approval).order_by('order')
            req_lines = [f"• {r.title} ({'Mandatory' if r.is_mandatory else 'Optional'})" for r in reqs]
            req_str = "\n".join(req_lines) if req_lines else "• Standard company registration and KYC documents."

            bot_response = (
                f"### 📋 {matched_approval.name}\n\n"
                f"• **Department:** {matched_approval.department}\n"
                f"• **Statutory SLA:** **{matched_approval.sla_max_days} Days** (RTS Act 2015 Mandate)\n"
                f"• **Fee Structure:** {matched_approval.fee_structure}\n"
                f"• **Validity / Renewal:** {matched_approval.renewal_period}\n"
                f"• **Legal Mandate:** {matched_approval.why_required[:180]}...\n\n"
                f"**Key Mandatory Requirements:**\n"
                f"{req_str}\n\n"
                f"👉 [Apply for this Approval in 1-Click](/applications/create/?approval={matched_approval.code})"
            )

        # Application Tracking / Status
        elif any(k in user_lower for k in ['status', 'application', 'track', 'progress', 'anm-', 'where is my file', 'kaha tak pahuncha', 'stithi']):
            intent = "application_status"
            sources.append("AnumatiSetu Real-Time Statutory Tracking Database")
            id_match = re.search(r'anm-[\w-]+', user_lower)
            if id_match:
                target_id = id_match.group(0).upper()
                target_app = Application.objects.filter(application_id__iexact=target_id).first()
                if target_app:
                    bot_response = (
                        f"### 🔍 Application Status: **{target_app.application_id}**\n\n"
                        f"• **Approval:** {target_app.approval.name}\n"
                        f"• **Current Stage:** **{target_app.current_stage}**\n"
                        f"• **Department:** {target_app.current_department}\n"
                        f"• **SLA Remaining:** **{target_app.sla_days_remaining} Days**\n"
                        f"• **Progress:** {target_app.progress_percent}%\n"
                        f"• **Officer Remarks:** {target_app.officer_remarks or 'Scrutiny in progress under RTS guidelines.'}\n\n"
                        f"👉 [View Full Audit Timeline & Queries](/applications/{target_app.id}/)"
                    )
                else:
                    bot_response = f"Application **{target_id}** could not be found. Please check your application ID or review your dashboard."
            elif user_apps:
                app_lines = [f"• **{a.application_id}** ({a.approval.name}): **{a.current_stage}** — SLA: {a.sla_days_remaining}d ({a.progress_percent}%)" for a in user_apps]
                bot_response = f"### 📂 Active Applications for **{biz_name}**:\n\n" + "\n".join(app_lines) + "\n\n👉 [Open Applications Workspace](/applications/)"
            else:
                bot_response = f"There are currently no active applications submitted for **{biz_name}**.\n\n👉 [Smart Approvals Discovery](/approvals/)"

        # Missing Documents & Pre-check Analysis
        elif any(k in user_lower for k in ['missing', 'document', 'documents', 'precheck', 'pre-check', 'upload', 'gap', 'kagadpatra', 'dastavej']):
            intent = "documents"
            sources.append("AnumatiSetu Automated AI Pre-check Engine")
            action_docs = [d for d in user_docs if d.status == 'Action Required']
            uploaded_docs = [d for d in user_docs if d.status == 'Uploaded']
            valid_docs = [d for d in user_docs if d.status == 'Pre-validated']

            if action_docs or uploaded_docs:
                lines = []
                if action_docs:
                    lines.append("**⚠️ Action Required / Missing:**")
                    for d in action_docs:
                        lines.append(f"• **{d.title}**: {d.validation_notes or 'Mandatory statutory document required for scrutiny.'}")
                if uploaded_docs:
                    lines.append("\n**⏳ Pending Verification:**")
                    for d in uploaded_docs:
                        lines.append(f"• {d.title} (Uploaded, awaiting review)")
                bot_response = f"### 📑 Document Verification Status for **{biz_name}**:\n\n" + "\n".join(lines) + "\n\n👉 [Go to Document Locker & Upload Missing Files](/documents/)"
            elif user_docs:
                bot_response = f"### 📑 Document Verification Status for **{biz_name}**:\n\n✅ **All {len(valid_docs)} corporate documents are pre-validated!**"
            else:
                bot_response = f"No documents have been uploaded to your enterprise vault yet.\n\n👉 [Upload Documents to Vault](/documents/)"

        # Inspections
        elif any(k in user_lower for k in ['inspection', 'visit', 'inspector', 'field visit', 'date', 'tapasani', 'officer visit']):
            intent = "inspection"
            sources.append("Joint Industrial Inspection Coordination System")
            if user_inspections:
                lines = []
                for insp in user_inspections:
                    icon = "🟢" if insp.status == 'Completed' else "🟡"
                    lines.append(f"{icon} **{insp.inspection_type}** ({insp.department}) by **{insp.inspector_name}** on **{insp.scheduled_date.strftime('%d %B %Y')}** at **{insp.time_slot}**")
                bot_response = f"### 🔍 Field Inspection Schedule for **{biz_name}**:\n\n" + "\n".join(lines) + "\n\n👉 [View Inspection Details](/inspections/)"
            else:
                bot_response = f"Based on live records, there are currently no scheduled site visits for **{biz_name}**."

        # Schemes & Subsidies
        elif any(k in user_lower for k in ['scheme', 'subsidy', 'incentive', 'grant', 'psi', 'cmegp', 'anudan', 'yojana', 'financial assistance', 'rebate']):
            intent = "schemes"
            sources.append("Directorate of Industries - Maharashtra Industrial Policy 2019 / PSI")
            inv_str = f"₹{business.investment_cr} Cr" if business else "MSME"
            bot_response = (
                f"### 💰 Government Subsidies & Incentives for **{biz_name}** ({biz_sector}, {biz_district}, Investment: {inv_str}):\n\n"
                f"1. **Maharashtra Package Scheme of Incentives (PSI 2019):**\n"
                f"   • **Capital Subsidy:** Up to 50% fixed capital investment subsidy in Zone C, D, and D+ areas.\n"
                f"   • **Stamp Duty Waiver:** 100% exemption on lease deed execution with MIDC.\n"
                f"   • **Power Tariff Rebate:** ₹1.50 per unit electricity rebate for 5 years.\n\n"
                f"2. **Chief Minister's Employment Generation Programme (CMEGP):**\n"
                f"   • Margin money grant up to ₹17.50 Lakhs with 10% entrepreneur equity contribution.\n\n"
                f"👉 [Calculate Live Enterprise Eligibility Score](/schemes/)"
            )

        # Approvals Roadmap
        elif any(k in user_lower for k in ['what approval', 'approvals needed', 'which approvals', 'clearance', 'require', 'permission', 'licence', 'license', 'parwangi', 'patra']):
            intent = "approvals_recommendation"
            sources.append("Maharashtra Single-Window Industrial Services Catalog (MAITRI / DIC)")
            bot_response = (
                f"### 🏭 Statutory Approvals Roadmap for **{biz_name}** ({biz_sector} in {biz_district}):\n\n"
                f"1. **Factory Plan Approval (DISH)** — Section 6, Factories Act 1948 (SLA: 45 Days)\n"
                f"2. **MPCB Consent to Establish (CTE)** — Orange/Red category pollution clearance (SLA: 60 Days)\n"
                f"3. **Industrial Fire Safety NOC** — MIDC Fire Services compliance (SLA: 30 Days)\n"
                f"4. **MSEDCL High/Low Tension Power Feeder** — Dedicated electrical energization (SLA: 30 Days)\n"
                f"5. **MIDC Water Connection NOC** — Industrial water supply sanction (SLA: 21 Days)\n\n"
                f"👉 [Explore All Approvals & Timelines](/approvals/)"
            )

        # Compliance
        elif any(k in user_lower for k in ['compliance', 'renewal', 'renew', 'expire', 'validity', 'annual return']):
            intent = "compliance"
            sources.append("AnumatiSetu Continuous Compliance Monitor")
            if user_compliances:
                lines = [f"🟢 **{c.title}**: Ref #{c.approval_ref} — Due by **{c.due_date.strftime('%d %b %Y')}** ({c.days_remaining}d left)" for c in user_compliances]
                bot_response = f"### 🛡️ Compliance & License Portfolio for **{biz_name}**:\n\n" + "\n".join(lines) + "\n\n👉 [Open Compliance & Renewal Hub](/compliance/)"
            else:
                bot_response = f"There are currently no active post-commissioning licenses registered for **{biz_name}**."

        # Officer Co-Pilot
        elif user_profile and user_profile.role == 'officer':
            intent = "officer_copilot"
            sources.append("Maharashtra Industrial Scrutiny & Reviewing Officer Portal")
            pending_apps = Application.objects.filter(current_stage__in=['Under Review', 'Submitted'])
            bot_response = (
                f"### 🏛️ Officer Command Co-Pilot — {user_profile.full_name or user_obj.username}\n\n"
                f"**Department:** {user_profile.department or 'Directorate of Industries'}\n"
                f"• **Pending Scrutiny:** **{pending_apps.count()} Applications** currently in queue awaiting evaluation.\n"
                f"• **RTS SLA Status:** 100% of active cases within mandated timeframe.\n\n"
                f"👉 [Open Officer Review Queue](/officer/dashboard/)"
            )

        # Fallback
        else:
            intent = "general"
            sources.append("AnumatiSetu Industrial Orchestration Knowledgebase")
            bot_response = (
                f"Namaskar! I am **Anumati Assistant**, your AI co-pilot for industrial setup, statutory approvals, and government schemes in Maharashtra.\n\n"
                f"Here are some specific queries I can assist **{biz_name}** with:\n"
                f"• *'What approvals are required for my enterprise?'*\n"
                f"• *'What documents are missing from my vault?'*\n"
                f"• *'Check the status of application ANM-2026-0042'*\n"
                f"• *'Tell me about MPCB Consent to Establish fees and timeline'*\n"
                f"• *'When is my factory site inspection scheduled?'*\n"
                f"• *'Which subsidies and grants apply under Maharashtra PSI 2019?'*"
            )

    # Append Statutory Disclaimer
    disclaimer = "\n\n---\n*ℹ️ Note: Guidance is generated by Anumati Assistant based on official statutory acts (Factories Act 1948, Water Act 1974, Maharashtra RTS Act 2015). Final decisions remain with the respective Government Department / Authority.*"
    full_response = bot_response + disclaimer

    # Save Assistant Response
    ChatMessage.objects.create(
        user=user_obj,
        session_key=session_key,
        role='assistant',
        content=full_response,
        intent=intent,
        context_sources=", ".join(sources)
    )

    return JsonResponse({
        'role': 'assistant',
        'content': full_response,
        'intent': intent,
        'sources': sources,
    })
