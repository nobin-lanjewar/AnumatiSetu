from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import GovernmentScheme
from business.models import BusinessProfile

def list_view(request):
    category = request.GET.get('category', 'all')
    
    schemes = GovernmentScheme.objects.filter(is_active=True)
    if category != 'all':
        schemes = schemes.filter(category_tag=category)

    business = None
    if request.user.is_authenticated and hasattr(request.user, 'business_profiles'):
        business = request.user.business_profiles.first()

    return render(request, 'schemes/list.html', {
        'schemes': schemes,
        'selected_category': category,
        'business': business,
        'is_dashboard': request.user.is_authenticated,
    })


def check_eligibility_api(request, scheme_id):
    """Calculates eligibility compatibility score against user's business profile."""
    scheme = get_object_or_404(GovernmentScheme, id=scheme_id)
    
    company_name = "Enterprise"
    sector = "Manufacturing"
    investment = 5.0
    district = "Nashik"

    if request.user.is_authenticated and hasattr(request.user, 'business_profiles'):
        b = request.user.business_profiles.first()
        if b:
            company_name = b.company_name
            sector = b.industry_sector
            investment = float(b.investment_cr)
            district = b.district

    # Eligibility evaluation
    is_eligible = True
    match_reasons = []

    if investment >= float(scheme.min_investment_cr) and investment <= float(scheme.max_investment_cr):
        match_reasons.append(f"Investment of ₹{investment} Cr falls within the eligible range (₹{scheme.min_investment_cr} Cr – ₹{scheme.max_investment_cr} Cr).")
    else:
        is_eligible = False

    if scheme.category_tag == 'Agro-Food' and 'Food' in sector:
        match_reasons.append("Sector matches dedicated Agro & Food Processing criteria.")
    elif scheme.category_tag == 'MSME' and investment <= 50.0:
        match_reasons.append("Entity qualifies under Maharashtra MSME definition.")
    elif scheme.category_tag == 'Green Tech':
        match_reasons.append("Eligible for captive renewable energy & green transition subsidy.")
    else:
        match_reasons.append(f"General industrial applicability across {district} district.")

    return JsonResponse({
        'scheme_name': scheme.name,
        'company_name': company_name,
        'is_eligible': is_eligible,
        'score': 95 if is_eligible else 60,
        'reasons': match_reasons,
        'benefits_summary': scheme.benefits,
        'max_subsidy': scheme.max_subsidy,
        'official_source': scheme.official_source,
    })
