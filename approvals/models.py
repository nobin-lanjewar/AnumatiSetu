from django.db import models

class Approval(models.Model):
    CATEGORY_CHOICES = (
        ('Pre-Establishment', 'Pre-Establishment (Before Construction)'),
        ('Pre-Operation', 'Pre-Operation (Before Production)'),
        ('Post-Operation', 'Post-Operation (During Operations)'),
        ('Incentive', 'Incentive & Subsidy Claims'),
    )

    RISK_CHOICES = (
        ('High', 'High Risk / Stringent Regulatory Audit'),
        ('Medium', 'Medium Risk / Standard Compliance'),
        ('Low', 'Low Risk / Fast-track Clearances'),
    )

    code = models.SlugField(max_length=100, unique=True, help_text="e.g. dish-factory-plan, mpcb-cte")
    name = models.CharField(max_length=255)
    name_mr = models.CharField(max_length=255, blank=True, help_text="Marathi Official Name")
    department = models.CharField(max_length=255, help_text="e.g. Directorate of Industrial Safety & Health (DISH)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Pre-Establishment')
    
    why_required = models.TextField(help_text="Statutory justification and legal mandate")
    eligibility = models.TextField(help_text="Units or criteria that must secure this approval")
    expected_timeline_days = models.PositiveIntegerField(default=15)
    sla_max_days = models.PositiveIntegerField(default=30, help_text="RTS Act statutory maximum disposal timeframe")
    
    fee_structure = models.CharField(max_length=255, default="Statutory slab-based fee")
    inspection_required = models.BooleanField(default=True)
    renewal_period = models.CharField(max_length=100, default="One-time approval")
    official_source = models.URLField(max_length=300, blank=True, default="https://maitri.mahaonline.gov.in")
    
    applicable_sectors = models.TextField(default="Food Processing, Manufacturing, Automobile, Chemical, Textile", help_text="Comma-separated applicable sectors")
    risk_category = models.CharField(max_length=20, choices=RISK_CHOICES, default='High')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} — {self.department}"

    def get_sectors_list(self):
        return [s.strip() for s in self.applicable_sectors.split(',') if s.strip()]


class ApprovalRequirement(models.Model):
    approval = models.ForeignKey(Approval, on_delete=models.CASCADE, related_name='requirements')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    doc_type_code = models.CharField(max_length=50, blank=True, help_text="e.g. factory_plan, environmental_noc, fire_layout")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.approval.name}: {self.title}"
