from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Approval, ApprovalRequirement

def discovery_view(request):
    """Smart Approval Discovery matching industrial sector, scale, and location."""
    business = None
    if request.user.is_authenticated and hasattr(request.user, 'business_profiles'):
        business = request.user.business_profiles.first()

    default_sector = business.industry_sector if business else 'All'
    default_stage = business.project_stage if business else 'New Greenfield Unit'
    default_investment = str(business.investment_cr) if business else '5'
    default_employees = str(business.employees_count) if business else '50'
    default_district = business.district if business else 'Nashik'

    sector = request.GET.get('sector', default_sector)
    stage = request.GET.get('stage', default_stage)
    investment = request.GET.get('investment', default_investment)
    employees = request.GET.get('employees', default_employees)
    district = request.GET.get('district', default_district)
    query = request.GET.get('q', '').strip()

    approvals = Approval.objects.all()

    if sector and sector != 'All':
        approvals = approvals.filter(applicable_sectors__icontains=sector)

    if query:
        approvals = approvals.filter(
            Q(name__icontains=query) |
            Q(department__icontains=query) |
            Q(why_required__icontains=query)
        )

    # Attach existing application status if entrepreneur is authenticated
    if request.user.is_authenticated:
        from applications.models import Application
        existing_apps = {app.approval_id: app for app in Application.objects.filter(user=request.user)}
        for a in approvals:
            a.user_application = existing_apps.get(a.id)

    return render(request, 'approvals/discovery.html', {
        'approvals': approvals,
        'business': business,
        'selected_sector': sector,
        'selected_stage': stage,
        'selected_investment': investment,
        'selected_employees': employees,
        'selected_district': district,
        'query': query,
        'is_dashboard': request.user.is_authenticated,
    })


def detail_view(request, code):
    """Detailed approval statutory breakdown with document checklist and SLAs."""
    approval = get_object_or_404(Approval, code=code)
    requirements = approval.requirements.all()
    
    user_application = None
    if request.user.is_authenticated:
        from applications.models import Application
        user_application = Application.objects.filter(user=request.user, approval=approval).first()

    return render(request, 'approvals/detail.html', {
        'approval': approval,
        'requirements': requirements,
        'user_application': user_application,
        'is_dashboard': request.user.is_authenticated,
    })


def api_filter_approvals(request):
    """AJAX endpoint for instant real-time filtering."""
    sector = request.GET.get('sector', '')
    query = request.GET.get('q', '')

    approvals = Approval.objects.all()
    if sector and sector != 'All':
        approvals = approvals.filter(applicable_sectors__icontains=sector)
    if query:
        approvals = approvals.filter(
            Q(name__icontains=query) |
            Q(department__icontains=query)
        )

    data = []
    for app in approvals:
        data.append({
            'code': app.code,
            'name': app.name,
            'name_mr': app.name_mr,
            'department': app.department,
            'category': app.category,
            'sla_max_days': app.sla_max_days,
            'expected_timeline_days': app.expected_timeline_days,
            'fee_structure': app.fee_structure,
            'inspection_required': app.inspection_required,
            'risk_category': app.risk_category,
        })
    return JsonResponse({'results': data})
