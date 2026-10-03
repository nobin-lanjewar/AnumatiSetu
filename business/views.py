from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile

@login_required
def profile_view(request):
    business = request.user.business_profiles.first()
    
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        industry_sector = request.POST.get('industry_sector')
        business_type = request.POST.get('business_type')
        district = request.POST.get('district', '').strip() or (business.district if business else 'Nashik')
        location = request.POST.get('location', '').strip() or (business.location if business else '') or district or 'Maharashtra Industrial Area'
        address = request.POST.get('address', '').strip()
        investment = request.POST.get('investment_cr', '5.0')
        employees = request.POST.get('employees_count', '120')
        project_stage = request.POST.get('project_stage')
        pan_number = request.POST.get('pan_number', '').strip()
        gst_number = request.POST.get('gst_number', '').strip()

        if not business:
            business = BusinessProfile(user=request.user)

        if company_name:
            business.company_name = company_name
        elif not business.company_name:
            business.company_name = f"{request.user.first_name or request.user.username} Enterprise"

        if industry_sector:
            business.industry_sector = industry_sector
        elif not business.industry_sector:
            business.industry_sector = 'Manufacturing'

        if business_type:
            business.business_type = business_type
        elif not business.business_type:
            business.business_type = 'Pvt Ltd'

        if project_stage:
            business.project_stage = project_stage
        elif not business.project_stage:
            business.project_stage = 'New Greenfield Unit'

        business.location = location
        business.address = address
        business.district = district
        business.pan_number = pan_number
        business.gst_number = gst_number
        
        try:
            business.investment_cr = float(investment)
        except (ValueError, TypeError):
            pass
        try:
            business.employees_count = int(employees)
        except (ValueError, TypeError):
            pass

        business.save()
        messages.success(request, "Enterprise Profile updated successfully!")
        return redirect('business:profile')

    return render(request, 'dashboard/business_profile.html', {
        'business': business,
        'is_dashboard': True,
    })
