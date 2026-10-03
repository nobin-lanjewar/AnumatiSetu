from django.db import models

class GovernmentScheme(models.Model):
    CATEGORY_CHOICES = (
        ('MSME', 'Micro, Small & Medium Enterprises (MSME)'),
        ('Large', 'Large & Mega Industrial Projects'),
        ('Agro-Food', 'Agro & Food Processing Special Incentives'),
        ('Women/SC/ST', 'Women / SC / ST Entrepreneurs'),
        ('Green Tech', 'Green Technology & Sustainability'),
    )

    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255, default='Directorate of Industries, Maharashtra')
    description = models.TextField()
    eligibility = models.TextField()
    benefits = models.TextField()
    max_subsidy = models.CharField(max_length=150, default="Up to 50% capital subsidy / ₹1 Crore")
    deadline = models.CharField(max_length=100, default="Open Round the Year / FY 2026-27")
    official_source = models.URLField(max_length=300, default="https://di.maharashtra.gov.in")
    
    category_tag = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='MSME')
    min_investment_cr = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_investment_cr = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    applicable_districts = models.TextField(default="All Districts of Maharashtra with enhanced rates for Zone C, D, D+")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category_tag})"
