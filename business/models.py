from django.db import models
from django.contrib.auth.models import User

class BusinessProfile(models.Model):
    BUSINESS_TYPE_CHOICES = (
        ('Pvt Ltd', 'Private Limited Company'),
        ('LLP', 'Limited Liability Partnership (LLP)'),
        ('Partnership', 'Registered Partnership Firm'),
        ('Proprietorship', 'Sole Proprietorship'),
        ('Public Ltd', 'Public Limited Company'),
    )

    SECTOR_CHOICES = (
        ('Food Processing', 'Agro & Food Processing'),
        ('Manufacturing', 'Heavy Engineering & Manufacturing'),
        ('Automobile', 'Automobile & Auto-components'),
        ('Pharmaceuticals', 'Pharmaceuticals & Life Sciences'),
        ('Chemical', 'Chemicals & Petrochemicals'),
        ('Textile', 'Textile, Apparel & Technical Textiles'),
        ('IT & Electronics', 'Information Technology & Electronics'),
        ('Renewable Energy', 'Renewable Energy & Green Tech'),
        ('Warehousing', 'Logistics, Warehousing & Cold Chain'),
    )

    STAGE_CHOICES = (
        ('New Greenfield Unit', 'Setting Up New Greenfield Unit'),
        ('Expansion Unit', 'Substantial Expansion of Existing Unit'),
        ('Land Acquired', 'Pre-Construction / Land Acquired'),
        ('Operational Modernization', 'Operational Modernization & Technology Upgradation'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_profiles')
    company_name = models.CharField(max_length=200, help_text="e.g. Amol Foods Pvt. Ltd.")
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE_CHOICES, default='Pvt Ltd')
    industry_sector = models.CharField(max_length=100, choices=SECTOR_CHOICES, default='Food Processing')
    location = models.CharField(max_length=150, default='Nashik, Maharashtra')
    address = models.TextField(blank=True, default='Plot B-42, Satpur MIDC Industrial Area, Nashik - 422007')
    district = models.CharField(max_length=100, default='Nashik')
    
    investment_cr = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, help_text="Proposed investment in Crores INR (e.g. 5.00)")
    employees_count = models.PositiveIntegerField(default=120, help_text="Total projected workforce/employees")
    project_stage = models.CharField(max_length=100, choices=STAGE_CHOICES, default='New Greenfield Unit')
    
    registration_no = models.CharField(max_length=100, blank=True, default='MH-NSK-2026-8942')
    udyam_no = models.CharField(max_length=100, blank=True, default='UDYAM-MH-26-0045891')
    pan_number = models.CharField(max_length=20, blank=True, default='AABCA1234F')
    gst_number = models.CharField(max_length=30, blank=True, default='27AABCA1234F1Z5')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} ({self.district}, {self.industry_sector})"
