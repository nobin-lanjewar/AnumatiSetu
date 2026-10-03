def user_profile_context(request):
    """Provides user role and business profile to all templates."""
    context = {
        'user_profile': None,
        'is_entrepreneur': False,
        'is_officer': False,
        'active_business': None,
        'unread_notifications_count': 0,
    }
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            context['user_profile'] = profile
            context['is_entrepreneur'] = (profile.role == 'entrepreneur')
            context['is_officer'] = (profile.role == 'officer')
            
            # Unread notifications
            context['unread_notifications_count'] = request.user.notifications.filter(is_read=False).count()
            
            # Primary business profile if entrepreneur
            if profile.role == 'entrepreneur' and hasattr(request.user, 'business_profiles'):
                context['active_business'] = request.user.business_profiles.first()
    
    return context
