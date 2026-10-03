from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'Entrepreneur / Citizen'),
        ('assistant', 'Anumati Assistant AI'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_messages')
    session_key = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField()
    intent = models.CharField(max_length=100, blank=True)
    context_sources = models.TextField(blank=True, help_text="Cited official rules, acts, or user profile records")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."
