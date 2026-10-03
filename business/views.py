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
        location = request.POST.get('location', '').strip() or (business.location if business else '') or district or 'Maharashtra'
        address = request.POST.get('address', '').strip()
        district = request.POST.get('district', '').strip()
        investment = request.POST.get('investment_cr', '5.0')
        employees = request.POST.get('employees_count', '120')
        project_stage = request.POST.get('project_stage')
        pan_number = request.POST.get('pan_number', '').strip()
        gst_number = request.POST.get('gst_number', '').strip()

        if not business:
            business = BusinessProfile(user=request.user)

        business.company_name = company_name
        business.industry_sector = industry_sector
        business.business_type = business_type
        business.location = location
        business.address = address
        business.district = district
        business.project_stage = project_stage
        business.pan_number = pan_number
        business.gst_number = gst_number
        
        try:
            business.investment_cr = float(investment)
        except ValueError:
            pass
        try:
            business.employees_count = int(employees)
        except ValueError:
            pass

        business.save()
        messages.success(request, "Enterprise Profile updated successfully!")
        return redirect('business:profile')

    return render(request, 'dashboard/business_profile.html', {
        'business': business,
        'is_dashboard': True,
    })
