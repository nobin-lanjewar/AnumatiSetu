from django.db import models

class Inspection(models.Model):
    STATUS_CHOICES = (
        ('Scheduled', 'Inspection Scheduled'),
        ('Completed', 'Inspection Completed ✓'),
        ('Pending Report', 'Pending Field Report ⌛'),
        ('Rescheduled', 'Rescheduled ↻'),
    )

    TYPE_CHOICES = (
        ('Pre-Establishment Site Visit', 'Pre-Establishment Site Inspection'),
        ('Pollution Compliance Audit', 'Pollution Control & ETP Audit'),
        ('Fire Safety Verification', 'Fire Safety & Hydrant Simulation'),
        ('Factory Layout Inspection', 'Factory Layout & Safety Clearances'),
        ('Joint Departmental Inspection', 'Joint Departmental Single-Window Inspection'),
    )

    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='inspections')
    department = models.CharField(max_length=255)
    inspector_name = models.CharField(max_length=150, default='Er. Sachin Deshmukh')
    inspector_designation = models.CharField(max_length=150, default='Divisional Safety & Environmental Inspector')
    location = models.CharField(max_length=255, default='Plot B-42, Satpur MIDC Industrial Area, Nashik')
    
    scheduled_date = models.DateField()
    time_slot = models.CharField(max_length=100, default='11:00 AM – 01:30 PM')
    inspection_type = models.CharField(max_length=100, choices=TYPE_CHOICES, default='Pre-Establishment Site Visit')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Scheduled')
    
    remarks = models.TextField(blank=True)
    report_file = models.FileField(upload_to='inspection_reports/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.inspection_type} - {self.application.application_id} ({self.status})"
