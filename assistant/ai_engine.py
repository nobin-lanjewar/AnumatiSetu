"""
Anumati Assistant AI Engine — Trained on Maharashtra Industrial Regulations,
Statutory Clearance Protocols, and Real-Time Supabase Enterprise Data.
Powered by Groq Cloud (Llama-3.3-70B-Versatile) with Intelligent Local Fallback.
"""

import os
import json
import logging
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)

SYSTEM_TRAINING_PROMPT_TEMPLATE = """
You are **Anumati Assistant**, the official intelligent regulatory AI co-pilot for Maharashtra's Single-Window Industrial Ecosystem (AnumatiSetu - Smart India Hackathon 2026, Problem Statement SIH26130).

### 🎯 YOUR MISSION & ROLE
You guide entrepreneurs, factory owners, and reviewing officers through the complete lifecycle of setting up and operating manufacturing enterprises in Maharashtra, including:
1. Identifying applicable pre-establishment, pre-operation, and post-operation statutory approvals.
2. Explaining legal mandates, Right to Services (RTS) SLA timelines, and fee structures.
3. Conducting document gap analysis and pre-checking submitted files.
4. Tracking real-time application stages, officer queries, and SLA burn-downs.
5. Recommending tailored financial incentives and subsidies under Maharashtra Package Scheme of Incentives (PSI 2019) and CMEGP.
6. Assisting reviewing officers with technical scrutiny and compliance audits.

---

### 🏛️ YOUR STATUTORY TRAINING & GOVERNING ACTS
You have rigorous domain knowledge of:
- **Factories Act, 1948 & Maharashtra Factories Rules, 1963**: Directorate of Industrial Safety & Health (DISH) - Section 6 Factory Plan Approval and Section 7 Factory License.
- **Water (Prevention & Control of Pollution) Act, 1974 & Air Act, 1981**: Maharashtra Pollution Control Board (MPCB) - Consent to Establish (CTE) and Consent to Operate (CTO) based on Red, Orange, Green, and White industrial categorizations.
- **Maharashtra Fire Prevention and Life Safety Measures Act, 2006**: MIDC / Municipal Fire Services Industrial Fire NOC for hazardous and standard industrial premises.
- **Electricity Act, 2003 & MSEDCL Supply Code**: Dedicated HT/LT industrial feeder energization and load sanction.
- **Food Safety and Standards Act, 2006**: FSSAI State and Central manufacturing licenses for food & agro-processing.
- **Maharashtra Right to Services (RTS) Act, 2015**: Legally binding statutory disposal timeframes (15 to 60 days depending on service) with deemed approval mechanisms.
- **Maharashtra Package Scheme of Incentives (PSI 2019)**:
  - Fixed Capital Investment Subsidy: Up to 50% in Zone C, D, and D+ areas (e.g., Nashik, Chhatrapati Sambhajinagar, Amravati, Nagpur, Nanded).
  - 100% Stamp Duty Exemption on MIDC land lease/purchase.
  - Electricity Duty Exemption for 7 years and Power Tariff Rebate of ₹1.50/unit for 5 years.
  - Interest Subvention up to 5% p.a. on term loans for MSMEs.
- **Chief Minister's Employment Generation Programme (CMEGP)**: Margin money assistance up to ₹17.50 Lakhs for project costs up to ₹50 Lakhs.

---

### 📊 CURRENT ENTERPRISE CONTEXT (LIVE DATABASE RECORDS)
{enterprise_context}

---

### 📚 STATUTORY APPROVALS CATALOG IN DATABASE
{approvals_catalog}

---

### 💰 ACTIVE GOVERNMENT SCHEMES IN DATABASE
{schemes_catalog}

---

### 💬 BEHAVIOR & RESPONSE GUIDELINES
1. **Always Ground in Real Data**: If the user has active applications or documents, reference their exact IDs ({user_apps_summary}) and status.
2. **Actionable Platform Links**: Use Markdown links to guide users to the platform's features:
   - [Documents Locker](/documents/)
   - [Smart Approvals Discovery](/approvals/)
   - [Applications Tracking](/applications/)
   - [Government Schemes](/schemes/)
   - [Compliance Hub](/compliance/)
   - [Inspections Portal](/inspections/)
3. **Multilingual Proficiency**: Fluently answer in English, Marathi (मराठी), and Hindi (हिंदी) depending on the user's language. If asked in Hindi or Marathi, respond warmly in the same language.
4. **Tone**: Institutional, highly knowledgeable, polite, encouraging, structured, and concise. Use clean markdown headings (`###`), bullet points, and emoji indicators.
5. **Regulatory Disclaimer**: Do not add extra repetitive disclaimers as the system automatically appends the official statutory disclaimer footer.
"""

def get_enterprise_context(user_obj, business, user_apps, user_docs, user_inspections, user_compliances) -> str:
    """Builds dynamic enterprise context for the user."""
    if not user_obj:
        return "User is browsing publicly as a Guest Citizen. Provide general industrial guidance for Maharashtra."

    user_profile = getattr(user_obj, 'profile', None)
    role = user_profile.role if user_profile else 'entrepreneur'

    if role == 'officer':
        dept = user_profile.department if user_profile else 'Directorate of Industries'
        return (
            f"Logged-in User: Government Reviewing Officer ({user_profile.full_name or user_obj.username})\n"
            f"Department: {dept}\n"
            f"Role: Technical Review & Statutory Scrutiny Officer.\n"
            f"Act as a high-efficiency Officer Co-Pilot, summarizing pending review queues and RTS compliance."
        )

    if not business:
        return f"Logged-in User: {user_obj.username} (Entrepreneur). No enterprise profile has been registered yet."

    # Active applications summary
    app_lines = []
    for a in user_apps:
        app_lines.append(f"  - App ID: {a.application_id} | Approval: {a.approval.name} | Stage: {a.current_stage} | SLA Remaining: {a.sla_days_remaining}d | Progress: {a.progress_percent}%")
    app_str = "\n".join(app_lines) if app_lines else "  No active applications currently."

    # Documents summary
    doc_lines = []
    for d in user_docs:
        doc_lines.append(f"  - {d.title} ({d.get_doc_type_display()}): {d.status} (Notes: {d.validation_notes or 'OK'})")
    doc_str = "\n".join(doc_lines) if doc_lines else "  No documents uploaded to vault yet."

    # Inspections summary
    insp_lines = []
    for i in user_inspections:
        insp_lines.append(f"  - {i.inspection_type} by {i.inspector_name} ({i.department}) on {i.scheduled_date} at {i.time_slot} [Status: {i.status}]")
    insp_str = "\n".join(insp_lines) if insp_lines else "  No field inspections currently scheduled."

    # Compliance summary
    comp_lines = []
    for c in user_compliances:
        comp_lines.append(f"  - {c.title} (Ref: {c.approval_ref}): Status {c.status}, Due: {c.due_date} ({c.days_remaining}d remaining)")
    comp_str = "\n".join(comp_lines) if comp_lines else "  No post-commissioning licenses registered yet."

    return (
        f"Registered Enterprise: **{business.company_name}**\n"
        f"Entity Type: {business.entity_type}\n"
        f"Sector: {business.industry_sector}\n"
        f"Location: {business.district}, Maharashtra (MIDC: {business.midc_industrial_area or 'Industrial Zone'})\n"
        f"Capital Investment: ₹{business.investment_cr} Crores\n"
        f"Employment Count: {business.employment_count} personnel\n\n"
        f"Active Applications:\n{app_str}\n\n"
        f"Vault Documents:\n{doc_str}\n\n"
        f"Inspections:\n{insp_str}\n\n"
        f"Compliances:\n{comp_str}"
    )


def get_approvals_catalog(approvals) -> str:
    """Serializes approvals database records."""
    lines = []
    for a in approvals:
        lines.append(
            f"• **{a.name}** (Code: `{a.code}`)\n"
            f"  Department: {a.department}\n"
            f"  RTS SLA: {a.sla_max_days} Days | Fee: {a.fee_structure} | Validity: {a.renewal_period}\n"
            f"  Why Required: {a.why_required[:120]}...\n"
            f"  Sectors: {a.applicable_sectors}"
        )
    return "\n\n".join(lines)


def get_schemes_catalog(schemes) -> str:
    """Serializes schemes database records."""
    lines = []
    for s in schemes:
        lines.append(
            f"• **{s.name}** ({s.category_tag})\n"
            f"  Department: {s.department}\n"
            f"  Benefit: {s.max_subsidy}\n"
            f"  Eligibility: {s.eligibility[:140]}..."
        )
    return "\n\n".join(lines)


def call_groq_llm(user_message: str, system_prompt: str, chat_history: List[Dict]) -> Tuple[str, str]:
    """Invokes Groq Cloud LLM using Llama-3.3-70b-versatile."""
    groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_api_key:
        return "", ""

    groq_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile').strip()

    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)

        messages = [{"role": "system", "content": system_prompt}]

        # Append last 6 conversation turns for continuity
        for msg in chat_history[-6:]:
            role = 'assistant' if msg.get('role') == 'assistant' else 'user'
            content = msg.get('content', '')
            if content:
                # Strip disclaimer if previously appended
                cleaned_content = content.split('\n\n---\n*ℹ️ Note: Guidance is generated')[0]
                messages.append({"role": role, "content": cleaned_content})

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=groq_model,
            messages=messages,
            temperature=0.25,
            max_tokens=900,
            top_p=0.9,
        )

        reply = response.choices[0].message.content.strip()
        model_used = f"Groq {groq_model}"
        return reply, model_used

    except Exception as e:
        logger.warning(f"Groq API call error: {e}. Falling back to deterministic RAG engine.")
        return "", ""
