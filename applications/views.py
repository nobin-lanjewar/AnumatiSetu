from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Application, ApplicationDocument, ApplicationStatusHistory, DepartmentQuery
from approvals.models import Approval
from business.models import BusinessProfile
from documents.models import Document
from inspections.models import Inspection

@login_required
def list_view(request):
    """List of applications for the current entrepreneur or officer."""
    is_officer = hasattr(request.user, 'profile') and request.user.profile.role == 'officer'
    
    stage_filter = request.GET.get('stage', 'all')
    
    if is_officer:
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(user=request.user)

    total_count = applications.count()

    if stage_filter != 'all':
        applications = applications.filter(current_stage=stage_filter)

    return render(request, 'applications/list.html', {
        'applications': applications,
        'total_count': total_count,
        'selected_stage': stage_filter,
        'is_dashboard': True,
    })


@login_required
def create_redirect_view(request):
    """Gracefully handles /applications/create/ and /applications/create/?approval=..."""
    approval_code = request.GET.get('approval') or request.GET.get('code')
    if approval_code and Approval.objects.filter(code=approval_code).exists():
        return redirect('applications:create', approval_code=approval_code)
    first_app = Approval.objects.first()
    if first_app:
        return redirect('applications:create', approval_code=first_app.code)
    return redirect('approvals:discovery')


@login_required
def create_view(request, approval_code):
    """Creates a new application in MySQL with auto-generated ANM Application ID."""
    approval = get_object_or_404(Approval, code=approval_code)
    business = request.user.business_profiles.first()
    
    if not business:
        messages.error(request, "Please create a Business Profile first before applying.")
        return redirect('business:profile')

    if request.method == 'POST':
        priority = request.POST.get('priority', 'Normal')
        remarks = request.POST.get('remarks', '')

        # Generate unique Application ID
        app_id = Application.generate_application_id()

        app = Application.objects.create(
            application_id=app_id,
            user=request.user,
            business=business,
            approval=approval,
            current_stage='Submitted',
            current_department=approval.department,
            priority=priority,
            sla_days_total=approval.sla_max_days,
            sla_days_remaining=approval.sla_max_days,
            progress_percent=20,
            officer_remarks='Application formally submitted through AnumatiSetu single-window orchestration.',
        )

        # Create audit history record
        ApplicationStatusHistory.objects.create(
            application=app,
            previous_status='Draft',
            new_status='Submitted',
            changed_by=request.user,
            remarks=remarks or f"Submitted online application for {approval.name}."
        )

        # Attach available pre-validated user documents
        for req in approval.requirements.all():
            matching_doc = Document.objects.filter(user=request.user, doc_type=req.doc_type_code).first()
            ApplicationDocument.objects.create(
                application=app,
                document=matching_doc,
                doc_name=req.title,
                file_type='PDF',
                status='Verified' if (matching_doc and matching_doc.status == 'Pre-validated') else 'Pending',
                officer_feedback='Pre-validated by AnumatiSetu system' if (matching_doc and matching_doc.status == 'Pre-validated') else 'Pending technical scrutiny'
            )

        messages.success(request, f"Application {app.application_id} for '{approval.name}' created and submitted to {approval.department}!")
        return redirect('applications:track', app_id=app.application_id)

    # Required docs
    requirements = approval.requirements.all()
    user_docs = Document.objects.filter(user=request.user)
    valid_doc_types = set(user_docs.filter(status='Pre-validated').values_list('doc_type', flat=True))

    return render(request, 'applications/create.html', {
        'approval': approval,
        'business': business,
        'requirements': requirements,
        'user_docs': user_docs,
        'valid_doc_types': valid_doc_types,
        'is_dashboard': True,
    })


@login_required
def track_view(request, app_id):
    """Unified application tracking timeline, SLA monitor, and audit history (Section 22)."""
    application = get_object_or_404(Application, application_id=app_id)
    
    # Ownership and role enforcement
    is_officer = hasattr(request.user, 'profile') and request.user.profile.role == 'officer'
    if not is_officer and application.user != request.user:
        messages.error(request, "Access denied. You do not have permission to view this application dossier.")
        return redirect('applications:list')
    history = application.history.all()
    documents = application.documents_rel.all()
    queries = application.queries.all()
    inspections = application.inspections.all()

    # Timeline stage states
    stages_order = [
        'Submitted',
        'Documents Verified',
        'Under Review',
        'Clarification Required',
        'Inspection Scheduled',
        'Approved'
    ]

    current_stage = application.current_stage
    stage_index = -1
    for idx, s in enumerate(stages_order):
        if s.lower() in current_stage.lower() or current_stage.lower() in s.lower():
            stage_index = idx
            break

    # Calculate SLA delay
    is_delayed = application.sla_days_remaining <= 0 and current_stage not in ['Approved', 'Rejected']

    return render(request, 'applications/track.html', {
        'application': application,
        'history': history,
        'documents': documents,
        'queries': queries,
        'inspections': inspections,
        'stage_index': stage_index,
        'stages_order': stages_order,
        'is_delayed': is_delayed,
        'is_dashboard': True,
    })


@login_required
def officer_review_view(request, app_id):
    """Officer Application Review portal (Section 24 & Image 4)."""
    # Enforce officer role
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'officer'):
        messages.error(request, "Access restricted to authorized Government Officers.")
        return redirect('dashboard_redirect')

    application = get_object_or_404(Application, application_id=app_id)
    history = application.history.all()
    documents = application.documents_rel.all()
    queries = application.queries.all()
    inspections = application.inspections.all()

    return render(request, 'officer/review.html', {
        'application': application,
        'history': history,
        'documents': documents,
        'queries': queries,
        'inspections': inspections,
        'is_dashboard': True,
    })


@login_required
def officer_update_status(request, app_id):
    """Officer action: Update application status with audit trail logging in MySQL (Section 23)."""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'officer'):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard_redirect')

    application = get_object_or_404(Application, application_id=app_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        remarks = request.POST.get('remarks', '').strip()

        if new_status and new_status != application.current_stage:
            prev_status = application.current_stage
            application.current_stage = new_status
            application.officer_remarks = remarks
            
            # Update progress percent according to stage
            progress_map = {
                'Submitted': 20,
                'Documents Verified': 40,
                'Under Review': 60,
                'Clarification Required': 50,
                'Inspection Scheduled': 75,
                'Inspection Completed': 85,
                'Approved': 100,
                'Rejected': 100,
            }
            application.progress_percent = progress_map.get(new_status, application.progress_percent)
            application.save()

            # Create immutable history record
            ApplicationStatusHistory.objects.create(
                application=application,
                previous_status=prev_status,
                new_status=new_status,
                changed_by=request.user,
                remarks=remarks or f"Status transitioned to {new_status} by reviewing officer."
            )

            messages.success(request, f"Application {application.application_id} updated to '{new_status}'. Audit entry recorded in database.")

    return redirect('applications:officer_review', app_id=app_id)


@login_required
def officer_raise_query(request, app_id):
    """Officer action: Request clarification from entrepreneur."""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'officer'):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard_redirect')

    application = get_object_or_404(Application, application_id=app_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        query_text = request.POST.get('query_text', '').strip()

        if title and query_text:
            DepartmentQuery.objects.create(
                application=application,
                raised_by=request.user,
                title=title,
                query_text=query_text,
                status='Open'
            )

            # Move status to Clarification Required
            prev_status = application.current_stage
            application.current_stage = 'Clarification Required'
            application.save()

            ApplicationStatusHistory.objects.create(
                application=application,
                previous_status=prev_status,
                new_status='Clarification Required',
                changed_by=request.user,
                remarks=f"Department query raised: {title}"
            )

            messages.success(request, f"Clarification request sent to {application.business.company_name}.")

    return redirect('applications:officer_review', app_id=app_id)


@login_required
def respond_query(request, query_id):
    """Entrepreneur response to departmental query."""
    query = get_object_or_404(DepartmentQuery, id=query_id)
    if query.application.user != request.user:
        messages.error(request, "Unauthorized action. Only the registered applicant can respond to queries.")
        return redirect('applications:list')
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text', '').strip()
        if response_text:
            query.response_text = response_text
            query.status = 'Responded'
            query.save()

            # Add to history
            ApplicationStatusHistory.objects.create(
                application=query.application,
                previous_status='Clarification Required',
                new_status='Under Review',
                changed_by=request.user,
                remarks=f"Entrepreneur responded to query: '{query.title}'. Resubmitted for officer scrutiny."
            )
            query.application.current_stage = 'Under Review'
            query.application.save()

            messages.success(request, "Clarification response submitted to reviewing department.")

    return redirect('applications:track', app_id=query.application.application_id)
