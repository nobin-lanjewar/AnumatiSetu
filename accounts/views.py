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
        
    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Allow login by email or username
        user = authenticate(request, username=username_or_email, password=password)
        if not user:
            # Check by email safely without MultipleObjectsReturned exception
            matching_users = User.objects.filter(email__iexact=username_or_email)
            for candidate in matching_users:
                user = authenticate(request, username=candidate.username, password=password)
                if user:
                    break

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials. Please verify your username/email and password.")

    return render(request, 'accounts/login.html', {'next': next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        role = request.POST.get('role', 'entrepreneur').strip()
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        # Basic mandatory check
        if not email or not password or not full_name:
            messages.error(request, "Please fill in all mandatory account fields (Name, Email, and Password).")
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        # Email format validation
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please provide a valid email address.")
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        # Duplicate email prevention (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email address already exists. Please log in.")
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        # Phone number validation (at least 10 digits)
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not clean_phone or len(clean_phone.replace('+91', '')) < 10 or not clean_phone.replace('+', '').isdigit():
            messages.error(request, "Please enter a valid 10-digit mobile number.")
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        # Password length validation
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        # Entrepreneur specific field validations
        if role == 'entrepreneur':
            company_name = request.POST.get('company_name', '').strip()
            if not company_name:
                messages.error(request, "Please specify your Company / Enterprise Name.")
                return render(request, 'accounts/register.html', {'form_data': request.POST})

            location = request.POST.get('location', '').strip()
            if not location:
                messages.error(request, "Please provide your Factory Location / MIDC Plot address.")
                return render(request, 'accounts/register.html', {'form_data': request.POST})

            investment = request.POST.get('investment_cr', '').strip()
            try:
                inv_val = float(investment)
                if inv_val <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Projected investment must be a valid positive number in ₹ Crores.")
                return render(request, 'accounts/register.html', {'form_data': request.POST})

            employees = request.POST.get('employees_count', '').strip()
            try:
                emp_val = int(employees)
                if emp_val < 1:
                    raise ValueError
            except ValueError:
                messages.error(request, "Projected workforce must be at least 1 employee.")
                return render(request, 'accounts/register.html', {'form_data': request.POST})

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
        profile.phone = clean_phone

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
            business_type = request.POST.get('business_type', 'Pvt Ltd')
            industry_sector = request.POST.get('industry_sector', 'Manufacturing')
            district = request.POST.get('district', 'Nashik').strip()

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
