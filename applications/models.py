from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class Application(models.Model):
    STAGE_CHOICES = (
        ('Draft', 'Draft Application'),
        ('Submitted', 'Application Submitted'),
        ('Documents Verified', 'Documents Verified'),
        ('Under Review', 'Department Review / Technical Scrutiny'),
        ('Clarification Required', 'Clarification Required'),
        ('Inspection Scheduled', 'Field Inspection Scheduled'),
        ('Inspection Completed', 'Inspection Completed'),
        ('Approved', 'Approval Granted by Authority'),
        ('Rejected', 'Application Rejected'),
    )

    PRIORITY_CHOICES = (
        ('Normal', 'Standard Processing'),
        ('High', 'High Priority'),
        ('Urgent', 'Urgent / Escalated'),
    )

    application_id = models.CharField(max_length=50, unique=True, help_text="e.g. ANM-2026-01042")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    business = models.ForeignKey('business.BusinessProfile', on_delete=models.CASCADE, related_name='applications')
    approval = models.ForeignKey('approvals.Approval', on_delete=models.CASCADE, related_name='applications')
    
    current_stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='Submitted')
    current_department = models.CharField(max_length=255)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Normal')
    
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications')
    assigned_officer_name = models.CharField(max_length=150, blank=True, default="Dr. Rajesh Kulkarni")
    
    submission_date = models.DateTimeField(default=timezone.now)
    sla_days_total = models.PositiveIntegerField(default=30)
    sla_days_remaining = models.IntegerField(default=15)
    is_delayed = models.BooleanField(default=False)
    progress_percent = models.PositiveIntegerField(default=40)
    
    officer_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.application_id} - {self.approval.name} ({self.current_stage})"

    @classmethod
    def generate_application_id(cls):
        year = timezone.now().year
        count = cls.objects.filter(created_at__year=year).count() + 1
        candidate = f"APP-{year}-{count:05d}"
        while cls.objects.filter(application_id=candidate).exists():
            count += 1
            candidate = f"APP-{year}-{count:05d}"
        return candidate


class ApplicationDocument(models.Model):
    STATUS_CHOICES = (
        ('Verified', 'Verified ✓'),
        ('Pending', 'Pending Scrutiny ○'),
        ('Action Required', 'Action Required ⚠'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents_rel')
    document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True, related_name='application_links')
    doc_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, default='PDF')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    officer_feedback = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.application_id} - {self.doc_name} ({self.status})"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=100)
    new_status = models.CharField(max_length=100)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.application.application_id}: {self.previous_status} → {self.new_status}"


class DepartmentQuery(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open Query / Awaiting Entrepreneur Response'),
        ('Responded', 'Response Provided by Entrepreneur'),
        ('Resolved', 'Clarification Accepted & Resolved'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='queries')
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raised_queries')
    title = models.CharField(max_length=255)
    query_text = models.TextField()
    response_text = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Query [{self.status}] on {self.application.application_id}: {self.title}"
