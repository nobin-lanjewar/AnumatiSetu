from django.db import models
from django.utils import timezone

class Compliance(models.Model):
    STATUS_CHOICES = (
        ('Compliant', 'Compliant ✓'),
        ('Approaching', 'Renewal Approaching ⏰'),
        ('Urgent', 'Urgent Action Required ⚠'),
        ('Overdue', 'Overdue / Non-Compliant ✕'),
    )

    business = models.ForeignKey('business.BusinessProfile', on_delete=models.CASCADE, related_name='compliances')
    approval = models.ForeignKey('approvals.Approval', on_delete=models.SET_NULL, null=True, blank=True, related_name='compliances')
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    approval_ref = models.CharField(max_length=100, help_text="e.g. DISH-LIC-2025-8841")
    
    due_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Approaching')
    annual_fee = models.CharField(max_length=100, default="₹15,000")
    penalties = models.CharField(max_length=255, default="Statutory late fee of ₹500/week after due date")
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.approval_ref} ({self.status})"

    @property
    def days_remaining(self):
        delta = self.due_date - timezone.now().date()
        return delta.days


class Renewal(models.Model):
    STATUS_CHOICES = (
        ('Upcoming', 'Upcoming Renewal Notice'),
        ('Submitted', 'Renewal Application Submitted'),
        ('Approved', 'Renewal Approved & Extended'),
        ('Delayed', 'Action Delayed'),
    )

    compliance = models.ForeignKey(Compliance, on_delete=models.CASCADE, related_name='renewals')
    renewal_due_date = models.DateField()
    renewal_submitted_date = models.DateField(null=True, blank=True)
    renewal_fee_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Upcoming')
    valid_until = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-renewal_due_date']

    def __str__(self):
        return f"Renewal for {self.compliance.title} - {self.status}"
