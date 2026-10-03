from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import UserProfile
from business.models import BusinessProfile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Allow login by email or username
        user = authenticate(request, username=username_or_email, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials. Please verify your username/email and password.")

    return render(request, 'accounts/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        role = request.POST.get('role', 'entrepreneur').strip()
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        if not email or not password or not full_name:
            messages.error(request, "Please fill in all mandatory account fields.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email address already exists.")
            return render(request, 'accounts/register.html')

        # Create User
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else 'User'
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'officer' if role == 'officer' else 'entrepreneur'
        profile.full_name = full_name
        profile.phone = phone

        if role == 'officer':
            department = request.POST.get('department', 'Directorate of Industries, Maharashtra').strip()
            designation = request.POST.get('designation', 'Scrutiny Officer').strip()
            office_location = request.POST.get('office_location', 'District Industries Centre (DIC)').strip()
            officer_id = request.POST.get('officer_id', f"MAH-OFF-{user.id:04d}").strip()

            profile.department = department
            profile.designation = designation
            profile.office_location = office_location
            profile.officer_id = officer_id or f"MAH-OFF-{user.id:04d}"
            profile.save()

            login(request, user)
            messages.success(request, f"Welcome to AnumatiSetu Reviewing Authority Portal, {full_name}!")
            return redirect('officer_dashboard')
        else:
            profile.save()
            company_name = request.POST.get('company_name', '').strip() or f"{full_name} Enterprises"
            business_type = request.POST.get('business_type', 'Pvt Ltd')
            industry_sector = request.POST.get('industry_sector', 'Manufacturing')
            location = request.POST.get('location', '').strip() or 'Maharashtra Industrial Area'
            district = request.POST.get('district', 'Nashik').strip()
            investment = request.POST.get('investment_cr', '5.00')
            employees = request.POST.get('employees_count', '50')

            try:
                inv_val = float(investment)
            except ValueError:
                inv_val = 5.0
            try:
                emp_val = int(employees)
            except ValueError:
                emp_val = 50

            district_code = district[:3].upper() if len(district) >= 3 else 'MAH'
            BusinessProfile.objects.create(
                user=user,
                company_name=company_name,
                business_type=business_type,
                industry_sector=industry_sector,
                location=location,
                address=location,
                district=district,
                investment_cr=inv_val,
                employees_count=emp_val,
                project_stage='New Greenfield Unit',
                registration_no=f"MH-{district_code}-2026-{user.id:04d}",
                udyam_no=f"UDYAM-MH-26-{user.id:07d}",
            )

            login(request, user)
            messages.success(request, f"Welcome to AnumatiSetu, {full_name}! Your enterprise '{company_name}' has been registered.")
            return redirect('entrepreneur_dashboard')

    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out of AnumatiSetu.")
    return redirect('home')


def switch_demo_view(request, role):
    """Instant presentation demo persona switcher for SIH 2026 judges."""
    if role == 'entrepreneur':
        user = User.objects.filter(username='amol_patil').first()
        if user:
            login(request, user)
            messages.success(request, "Switched to Demo Persona: Entrepreneur (Amol Patil — Amol Foods Pvt. Ltd.)")
            return redirect('entrepreneur_dashboard')
    elif role == 'officer':
        user = User.objects.filter(username='rajesh_kulkarni').first()
        if user:
            login(request, user)
            messages.success(request, "Switched to Demo Persona: Government Officer (Dr. Rajesh Kulkarni — Joint Director DIC Nashik)")
            return redirect('officer_dashboard')
            
    messages.warning(request, "Specified demo user could not be found.")
    return redirect('home')
