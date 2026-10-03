from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Compliance, Renewal

def calendar_view(request):
    """Compliance & Renewal Calendar view with countdown meters and statutory alerts."""
    business = None
    if request.user.is_authenticated and hasattr(request.user, 'business_profiles'):
        business = request.user.business_profiles.first()

    if business:
        compliances = Compliance.objects.filter(business=business)
    else:
        compliances = Compliance.objects.all()

    # Calculate statistics
    urgent_count = compliances.filter(status='Urgent').count()
    approaching_count = compliances.filter(status='Approaching').count()
    compliant_count = compliances.filter(status='Compliant').count()

    return render(request, 'compliance/calendar.html', {
        'compliances': compliances,
        'urgent_count': urgent_count,
        'approaching_count': approaching_count,
        'compliant_count': compliant_count,
        'is_dashboard': request.user.is_authenticated,
    })


@login_required
def submit_renewal(request, compliance_id):
    """Submits renewal application and updates compliance record in MySQL."""
    compliance = get_object_or_404(Compliance, id=compliance_id)

    if request.method == 'POST':
        remarks = request.POST.get('remarks', 'Renewal fee paid and renewal dossier submitted.')
        
        # Create renewal record
        Renewal.objects.create(
            compliance=compliance,
            renewal_due_date=compliance.due_date,
            renewal_submitted_date=timezone.now().date(),
            renewal_fee_paid=True,
            status='Submitted',
            remarks=remarks
        )

        compliance.status = 'Compliant'
        compliance.save()

        messages.success(request, f"Renewal submitted for '{compliance.title}'. Status updated to Compliant.")
        return redirect('compliance:calendar')

    return redirect('compliance:calendar')
