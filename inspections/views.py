from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Inspection
from applications.models import Application, ApplicationStatusHistory

@login_required
def list_view(request):
    is_officer = hasattr(request.user, 'profile') and request.user.profile.role == 'officer'
    
    if is_officer:
        inspections = Inspection.objects.all()
        applications_for_schedule = Application.objects.exclude(current_stage__in=['Approved', 'Rejected'])
    else:
        inspections = Inspection.objects.filter(application__user=request.user)
        applications_for_schedule = []

    return render(request, 'inspections/list.html', {
        'inspections': inspections,
        'applications_for_schedule': applications_for_schedule,
        'is_dashboard': True,
    })


@login_required
def schedule_inspection_view(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'officer'):
        messages.error(request, "Only authorized officers can schedule inspections.")
        return redirect('inspections:list')

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        inspector_name = request.POST.get('inspector_name', '').strip()
        inspector_designation = request.POST.get('inspector_designation', '').strip()
        location = request.POST.get('location', '').strip()
        scheduled_date = request.POST.get('scheduled_date')
        time_slot = request.POST.get('time_slot', '11:00 AM - 01:00 PM')
        inspection_type = request.POST.get('inspection_type', 'Pre-Establishment Site Visit')
        remarks = request.POST.get('remarks', '').strip()

        application = get_object_or_404(Application, application_id=app_id)

        inspection = Inspection.objects.create(
            application=application,
            department=application.approval.department,
            inspector_name=inspector_name or "Er. Sachin Deshmukh",
            inspector_designation=inspector_designation or "Divisional Safety & Environmental Inspector",
            location=location or application.business.address,
            scheduled_date=scheduled_date,
            time_slot=time_slot,
            inspection_type=inspection_type,
            status='Scheduled',
            remarks=remarks
        )

        # Transition application status to Inspection Scheduled
        prev_status = application.current_stage
        application.current_stage = 'Inspection Scheduled'
        application.progress_percent = 75
        application.save()

        ApplicationStatusHistory.objects.create(
            application=application,
            previous_status=prev_status,
            new_status='Inspection Scheduled',
            changed_by=request.user,
            remarks=f"Field inspection scheduled on {scheduled_date} with {inspector_name}."
        )

        messages.success(request, f"Inspection scheduled successfully for {application.application_id} on {scheduled_date}.")
        return redirect('inspections:list')

    return redirect('inspections:list')


@login_required
def update_inspection_status(request, inspection_id):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'officer'):
        messages.error(request, "Unauthorized action.")
        return redirect('inspections:list')

    inspection = get_object_or_404(Inspection, id=inspection_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        remarks = request.POST.get('remarks', '').strip()
        if new_status:
            inspection.status = new_status
            if remarks:
                inspection.remarks = f"{inspection.remarks}\n[Update]: {remarks}".strip()
            inspection.save()

            if new_status == 'Completed':
                inspection.application.current_stage = 'Inspection Completed'
                inspection.application.progress_percent = 85
                inspection.application.save()

                ApplicationStatusHistory.objects.create(
                    application=inspection.application,
                    previous_status='Inspection Scheduled',
                    new_status='Inspection Completed',
                    changed_by=request.user,
                    remarks=f"Inspection completed with remarks: {remarks}"
                )

            messages.success(request, f"Inspection status updated to '{new_status}'.")

    return redirect('inspections:list')
