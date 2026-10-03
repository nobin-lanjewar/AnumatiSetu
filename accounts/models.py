from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('entrepreneur', 'Entrepreneur / Business Owner'),
        ('officer', 'Government Officer / Reviewing Authority'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='entrepreneur')
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Government Officer specific attributes
    designation = models.CharField(max_length=150, blank=True, help_text="e.g. Joint Director of Industries (Nashik Region)")
    department = models.CharField(max_length=200, blank=True, help_text="e.g. Directorate of Industries, Government of Maharashtra")
    office_location = models.CharField(max_length=200, blank=True, help_text="e.g. DIC Trimbak Road, Nashik")
    officer_id = models.CharField(max_length=50, blank=True, help_text="e.g. MAH-IND-OFF-0442")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name or self.user.username} ({self.get_role_display()})"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('info', 'Information'),
        ('warning', 'Action Required'),
        ('success', 'Approval / Clearance'),
        ('urgent', 'Urgent Deadline'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    link_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type.upper()}] {self.title} for {self.user.username}"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, full_name=instance.get_full_name() or instance.username)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
