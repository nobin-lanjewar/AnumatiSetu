from django.db import models
from django.contrib.auth.models import User
import os

class Document(models.Model):
    DOC_TYPE_CHOICES = (
        ('pan', 'PAN Card / Tax Identity'),
        ('gst', 'GST Registration Certificate'),
        ('company_reg', 'Certificate of Incorporation / Partnership Deed'),
        ('land_deed', 'Land Ownership / MIDC Allotment Deed'),
        ('factory_plan', 'Architectural Factory Layout Plan'),
        ('environmental_noc', 'Environmental Management Plan / ETP Specs'),
        ('fire_layout', 'Fire Hydrant & Evacuation Layout Plan'),
        ('electricity_sld', 'Electrical Single Line Diagram (SLD)'),
        ('water_report', 'Water Potability & Effluent Analysis Report'),
        ('other', 'Supporting Statutory Annexure'),
    )

    STATUS_CHOICES = (
        ('Uploaded', 'Uploaded — Pending Analysis'),
        ('Pre-validated', 'Pre-validated by AnumatiSetu'),
        ('Action Required', 'Action Required — Review Flagged'),
        ('Verified', 'Department Verified'),
        ('Rejected', 'Incomplete / Invalid'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    business = models.ForeignKey('business.BusinessProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES, default='pan')
    file = models.FileField(upload_to='documents/%Y/%m/', blank=True, null=True)
    
    file_size_kb = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, default='application/pdf')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Uploaded')
    
    # OCR & Pre-validation Intelligent Layer
    is_ocr_processed = models.BooleanField(default=False)
    ocr_extracted_text = models.TextField(blank=True)
    ocr_confidence_score = models.FloatField(default=0.0)
    validation_notes = models.TextField(blank=True, help_text="AI and algorithmic pre-check notes")
    
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_doc_type_display()}) - {self.status}"

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        return "Not uploaded"
