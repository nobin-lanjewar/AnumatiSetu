from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from approvals.models import Approval
from applications.models import Application
from documents.models import Document
from inspections.models import Inspection
from compliance.models import Compliance
from schemes.models import GovernmentScheme
from business.models import BusinessProfile

def home_view(request):
    """Public Landing Page matching Section 13-17 & 29."""
    approvals_preview = Approval.objects.all()[:4]
    schemes_preview = GovernmentScheme.objects.all()[:3]
    return render(request, 'home.html', {
        'approvals_preview': approvals_preview,
        'schemes_preview': schemes_preview,
        'is_dashboard': False,
    })


def how_it_works_view(request):
    """Dedicated How It Works page with Image 2 (Section 17)."""
    return render(request, 'how_it_works.html', {
        'is_dashboard': False,
    })


def about_view(request):
    """About & Technical Architecture page (Section 34 & 35)."""
    return render(request, 'about.html', {
        'is_dashboard': False,
    })


def location_intelligence_view(request):
    """Maharashtra Location Intelligence & DIC network (Section 29 & Image 5)."""
    return render(request, 'location_intelligence.html', {
        'is_dashboard': False,
    })


@login_required
def dashboard_redirect(request):
    """Role-based automatic redirection."""
    if hasattr(request.user, 'profile') and request.user.profile.role == 'officer':
        return redirect('officer_dashboard')
    return redirect('entrepreneur_dashboard')


@login_required
def entrepreneur_dashboard_view(request):
    """Entrepreneur Dashboard matching Section 31 (Amol Patil, Amol Foods Pvt. Ltd.)."""
    if hasattr(request.user, 'profile') and request.user.profile.role == 'officer':
        return redirect('officer_dashboard')

    business = request.user.business_profiles.first()
    if not business:
        name = request.user.first_name or request.user.username
        business = BusinessProfile.objects.create(
            user=request.user,
            company_name=f"{name} Enterprises",
            industry_sector='Manufacturing',
            location='Maharashtra Industrial Area',
            district='Nashik',
            investment_cr=5.0,
            employees_count=50,
        )
    applications = Application.objects.filter(user=request.user)
    documents = Document.objects.filter(user=request.user)
    inspections = Inspection.objects.filter(application__user=request.user)
    compliances = Compliance.objects.filter(business=business) if business else Compliance.objects.none()
    schemes = GovernmentScheme.objects.filter(is_active=True)[:3]

    # Metrics
    apps_count = applications.count()
    docs_valid_count = documents.filter(status='Pre-validated').count()
    inspections_count = inspections.filter(status='Scheduled').count()
    pending_compliances = compliances.filter(status__in=['Approaching', 'Urgent']).count()

    # Pre-check alert check (Missing environmental document)
    missing_docs = documents.filter(status='Action Required')

    return render(request, 'dashboard/entrepreneur.html', {
        'business': business,
        'applications': applications,
        'documents': documents,
        'inspections': inspections,
        'compliances': compliances,
        'schemes': schemes,
        'apps_count': apps_count,
        'docs_valid_count': docs_valid_count,
        'inspections_count': inspections_count,
        'pending_compliances': pending_compliances,
        'missing_docs': missing_docs,
        'is_dashboard': True,
    })


@login_required
def officer_dashboard_view(request):
    """Government Officer Dashboard matching Section 24 & Image 4 (Dr. Rajesh Kulkarni)."""
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'officer'):
        messages.error(request, "Access restricted to authorized reviewing authorities.")
        return redirect('entrepreneur_dashboard')

    applications = Application.objects.all()
    inspections = Inspection.objects.all()

    # Stats
    total_apps = applications.count()
    under_review_count = applications.filter(current_stage='Under Review').count()
    clarification_count = applications.filter(current_stage='Clarification Required').count()
    inspection_count = applications.filter(current_stage='Inspection Scheduled').count()
    approved_count = applications.filter(current_stage='Approved').count()
    delayed_count = sum(1 for app in applications if app.sla_days_remaining <= 0 and app.current_stage not in ['Approved', 'Rejected'])

    return render(request, 'dashboard/officer.html', {
        'applications': applications,
        'inspections': inspections,
        'total_apps': total_apps,
        'under_review_count': under_review_count,
        'clarification_count': clarification_count,
        'inspection_count': inspection_count,
        'approved_count': approved_count,
        'delayed_count': delayed_count,
        'is_dashboard': True,
    })


def health_check_view(request):
    """Institutional readiness and liveness probe for cloud load balancers and container orchestrators."""
    from django.http import JsonResponse
    from django.db import connection
    from django.conf import settings

    db_ok = True
    db_err = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_ok = False
        db_err = str(e)

    status_code = 200 if db_ok else 503
    return JsonResponse({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else f'error: {db_err}',
        'environment': 'development' if settings.DEBUG else 'production',
        'system': 'AnumatiSetu Single-Window Industrial Orchestration Platform',
        'version': '1.0.0'
    }, status=status_code)

