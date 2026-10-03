from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import UserProfile, Notification
from business.models import BusinessProfile
from approvals.models import Approval, ApprovalRequirement
from documents.models import Document
from applications.models import Application, ApplicationDocument, ApplicationStatusHistory, DepartmentQuery
from inspections.models import Inspection
from compliance.models import Compliance, Renewal
from schemes.models import GovernmentScheme

class Command(BaseCommand):
    help = 'Seeds database with realistic demonstration data for AnumatiSetu SIH26130'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting AnumatiSetu Database Seeding...'))

        # 1. Superuser
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@anumatisetu.gov.in',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('password123')
        admin_user.save()
        if hasattr(admin_user, 'profile'):
            admin_user.profile.role = 'officer'
            admin_user.profile.full_name = 'AnumatiSetu Administrator'
            admin_user.profile.designation = 'Chief Technology Officer'
            admin_user.profile.department = 'Maharashtra State Innovation Society'
            admin_user.profile.save()

        # 2. Entrepreneur: Amol Patil
        ent_user, _ = User.objects.get_or_create(
            username='amol_patil',
            defaults={
                'email': 'amol.patil@amolfoods.in',
                'first_name': 'Amol',
                'last_name': 'Patil',
            }
        )
        ent_user.set_password('password123')
        ent_user.save()
        ent_profile, _ = UserProfile.objects.get_or_create(user=ent_user)
        ent_profile.role = 'entrepreneur'
        ent_profile.full_name = 'Amol Patil'
        ent_profile.phone = '+91 98220 54321'
        ent_profile.save()

        # 3. Government Officer: Dr. Rajesh Kulkarni
        off_user, _ = User.objects.get_or_create(
            username='rajesh_kulkarni',
            defaults={
                'email': 'jd.nashik@maharashtra.gov.in',
                'first_name': 'Rajesh',
                'last_name': 'Kulkarni',
                'is_staff': True,
            }
        )
        off_user.set_password('password123')
        off_user.save()
        off_profile, _ = UserProfile.objects.get_or_create(user=off_user)
        off_profile.role = 'officer'
        off_profile.full_name = 'Dr. Rajesh Kulkarni'
        off_profile.phone = '+91 253 2571234'
        off_profile.designation = 'Joint Director of Industries (Nashik Region)'
        off_profile.department = 'Directorate of Industries, Government of Maharashtra'
        off_profile.office_location = 'District Industries Centre (DIC), Trimbak Road, Nashik'
        off_profile.officer_id = 'MAH-IND-OFF-0442'
        off_profile.save()

        self.stdout.write(self.style.SUCCESS('Created Users: Entrepreneur (amol_patil) and Officer (rajesh_kulkarni)'))

        # 4. Business Profile: Amol Foods Pvt. Ltd.
        business, _ = BusinessProfile.objects.get_or_create(
            company_name='Amol Foods Pvt. Ltd.',
            defaults={
                'user': ent_user,
                'business_type': 'Pvt Ltd',
                'industry_sector': 'Food Processing',
                'location': 'Nashik, Maharashtra',
                'address': 'Plot B-42, Satpur MIDC Industrial Area, Nashik - 422007',
                'district': 'Nashik',
                'investment_cr': 5.00,
                'employees_count': 120,
                'project_stage': 'New Greenfield Unit',
                'registration_no': 'MH-NSK-2026-8942',
                'udyam_no': 'UDYAM-MH-26-0045891',
                'pan_number': 'AABCA1234F',
                'gst_number': '27AABCA1234F1Z5',
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Created Business Profile: {business.company_name}'))

        # 5. Approvals Catalog (Maharashtra Regulatory Clearances)
        approvals_data = [
            {
                'code': 'dish-factory-plan',
                'name': 'Factory Plan Approval',
                'name_mr': 'कारखाना नकाशा मंजुरी',
                'department': 'Directorate of Industrial Safety & Health (DISH)',
                'category': 'Pre-Establishment',
                'why_required': 'Mandatory under Section 6 of the Factories Act 1948 to ensure occupational safety, ventilation, emergency exits, and worker health standards prior to civil construction.',
                'eligibility': 'Any manufacturing unit employing 10 or more workers with power, or 20 or more without power.',
                'expected_timeline_days': 15,
                'sla_max_days': 30,
                'fee_structure': '₹5,000 to ₹25,000 based on installed horsepower and worker strength',
                'inspection_required': True,
                'renewal_period': 'One-time approval unless substantial expansion occurs',
                'official_source': 'https://dish.maharashtra.gov.in',
                'applicable_sectors': 'Food Processing, Manufacturing, Automobile, Chemical, Textile, Pharmaceuticals',
                'risk_category': 'High',
                'reqs': [
                    ('Process Flow Chart & Technical Description', 'Step-by-step manufacturing process and material safety balance sheet.', 'process_flow', True),
                    ('Architectural Factory Building Plan', 'Detailed layout blueprint certified by a registered chartered architect.', 'factory_plan', True),
                    ('Land Ownership / MIDC Allotment Deed', 'Title deed, registered lease agreement or MIDC formal land allotment order.', 'land_deed', True),
                    ('Safety Equipment Layout Diagram', 'Positions of fire exits, ventilation blowers, and first aid stations.', 'safety_plan', True),
                    ('Machinery & Power Load Schedule', 'List of heavy processing machinery with connected electrical kW.', 'machinery_list', True),
                ]
            },
            {
                'code': 'mpcb-cte',
                'name': 'MPCB Consent to Establish (CTE)',
                'name_mr': 'प्रदूषण नियंत्रण संमती (CTE)',
                'department': 'Maharashtra Pollution Control Board (MPCB)',
                'category': 'Pre-Establishment',
                'why_required': 'Statutory consent under Water (Prevention & Control of Pollution) Act 1974 and Air Act 1981 before starting civil construction or equipment installation.',
                'eligibility': 'All industrial units categorized under Red, Orange or Green industrial classifications by CPCB/MPCB.',
                'expected_timeline_days': 30,
                'sla_max_days': 45,
                'fee_structure': '₹15,000 to ₹1,00,000 based on Capital Investment (₹5 Cr bracket = ₹25,000)',
                'inspection_required': True,
                'renewal_period': 'Valid for 5 years or until commercial commissioning',
                'official_source': 'https://mpcb.gov.in',
                'applicable_sectors': 'Food Processing, Chemical, Pharmaceuticals, Textile, Manufacturing',
                'risk_category': 'High',
                'reqs': [
                    ('Effluent Treatment Plant (ETP) / STP Layout', 'Technical drawing and flow scheme for industrial effluent neutralizer.', 'environmental_noc', True),
                    ('Air Pollution Control System Specs', 'Chimney stack height calculation, wet scrubbers and emission filters.', 'air_specs', True),
                    ('MIDC Water Allotment Letter / Ground Water NOC', 'Approved water connection sanction or CGWA NOC.', 'water_noc', True),
                    ('Raw Material Balance Sheet & Hazardous Waste Estimate', 'Detailed annual consumption and solid waste disposal plan.', 'waste_plan', True),
                ]
            },
            {
                'code': 'fire-noc',
                'name': 'Industrial Fire Safety NOC',
                'name_mr': 'अग्निशमन ना-हरकत प्रमाणपत्र (NOC)',
                'department': 'MIDC Fire Services / Maharashtra Fire Services',
                'category': 'Pre-Establishment',
                'why_required': 'Mandatory compliance with Maharashtra Fire Prevention and Life Safety Measures Act 2006 to ensure fire hydrant networks, smoke detectors, and emergency evacuation.',
                'eligibility': 'All commercial and industrial factory buildings exceeding 500 sq. meters built-up area.',
                'expected_timeline_days': 14,
                'sla_max_days': 21,
                'fee_structure': '₹10 per sq. meter built-up area fire infrastructure cess',
                'inspection_required': True,
                'renewal_period': 'Annual renewal via Form B inspection certificate',
                'official_source': 'https://midcindia.org',
                'applicable_sectors': 'Food Processing, Manufacturing, Automobile, Chemical, Warehousing',
                'risk_category': 'High',
                'reqs': [
                    ('Architectural Fire Tender Driveway Layout', 'Site plan demonstrating clear 6-meter driveway for fire tenders.', 'fire_layout', True),
                    ('Hydrant and Sprinkler Pipeline Scheme', 'Water storage reservoir capacity calculation for firefighting.', 'hydrant_spec', True),
                    ('Licensed Fire Agency Form A Certificate', 'Certified execution audit by Maharashtra licensed fire agency.', 'form_a', True),
                ]
            },
            {
                'code': 'msedcl-power',
                'name': 'HT/LT Industrial Electricity Connection',
                'name_mr': 'औद्योगिक वीज जोडणी (MSEDCL)',
                'department': 'Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL)',
                'category': 'Pre-Operation',
                'why_required': 'Sanction of dedicated HT/LT commercial power load for industrial processing machines and continuous factory operations.',
                'eligibility': 'Any registered enterprise holding valid land title or lease agreement in Maharashtra.',
                'expected_timeline_days': 10,
                'sla_max_days': 20,
                'fee_structure': 'Estimate quotation based on load demand (₹50,000 to ₹3,00,000)',
                'inspection_required': True,
                'renewal_period': 'Permanent connection with monthly billing',
                'official_source': 'https://www.mahadiscom.in',
                'applicable_sectors': 'Food Processing, Manufacturing, Automobile, Chemical, Textile, IT & Electronics',
                'risk_category': 'Medium',
                'reqs': [
                    ('Electrical Single Line Diagram (SLD)', 'Approved by Electrical Inspector, Industries Department.', 'electricity_sld', True),
                    ('Connected Load Schedule & Test Report', 'Certified by licensed electrical contractor.', 'contractor_cert', True),
                    ('Ownership / MIDC Allotment Deed', 'Proof of possession of premises.', 'land_deed', True),
                ]
            },
            {
                'code': 'fssai-license',
                'name': 'FSSAI State Manufacturing License',
                'name_mr': 'अन्न सुरक्षा व मानके परवाना (FSSAI)',
                'department': 'Food & Drugs Administration (FDA Maharashtra)',
                'category': 'Pre-Operation',
                'why_required': 'Mandatory licensing under Food Safety and Standards Act 2006 for manufacturing, packing, or storing food items.',
                'eligibility': 'Agro & Food Processing units with turnover up to ₹20 Crore (State License) or higher (Central License).',
                'expected_timeline_days': 20,
                'sla_max_days': 30,
                'fee_structure': '₹3,000/year to ₹5,000/year based on production capacity',
                'inspection_required': True,
                'renewal_period': '1 to 5 years tenure (Annual Renewal)',
                'official_source': 'https://foscos.fssai.gov.in',
                'applicable_sectors': 'Food Processing',
                'risk_category': 'High',
                'reqs': [
                    ('Water Potability & Chemical Analysis Report', 'Testing report from NABL-accredited laboratory.', 'water_report', True),
                    ('Food Safety Management System (FSMS) Plan', 'HACCP or standard food hygiene SOP document.', 'fsms_plan', True),
                    ('List of Food Categories & Machinery', 'Detailed specification of packaged food variants.', 'food_spec', True),
                ]
            },
            {
                'code': 'dish-factory-licence',
                'name': 'Factory Operating Licence (Form 4)',
                'name_mr': 'कारखाना चालू करण्याचा परवाना (नमुना ४)',
                'department': 'Directorate of Industrial Safety & Health (DISH)',
                'category': 'Pre-Operation',
                'why_required': 'Statutory permit under Section 6 of Factories Act 1948 to commence active manufacturing operations with workforce.',
                'eligibility': 'Units that have completed civil construction in accordance with approved Factory Plan.',
                'expected_timeline_days': 15,
                'sla_max_days': 25,
                'fee_structure': '₹10,000 to ₹40,000 based on worker headcount',
                'inspection_required': True,
                'renewal_period': 'Annual or 5-year renewal cycle',
                'official_source': 'https://dish.maharashtra.gov.in',
                'applicable_sectors': 'Food Processing, Manufacturing, Automobile, Chemical, Textile',
                'risk_category': 'Medium',
                'reqs': [
                    ('Factory Plan Approval Certificate', 'Copy of approved plan reference number.', 'factory_plan', True),
                    ('Stability Certificate by Chartered Structural Engineer', 'Civil load stability certification.', 'stability_cert', True),
                    ('List of Safety Officers / First Aid Personnel', 'Qualified staff list with certified training.', 'safety_staff', True),
                ]
            },
            {
                'code': 'boiler-registration',
                'name': 'Steam Boiler & Pipeline Erection Registration',
                'name_mr': 'स्टीम बॉयलर नोंदणी प्रमाणपत्र',
                'department': 'Directorate of Steam Boilers, Maharashtra',
                'category': 'Pre-Operation',
                'why_required': 'Registration under Indian Boilers Act 1923 for high-pressure steam vessels used in food sterilization and steam boiling.',
                'eligibility': 'Manufacturing units operating boilers with capacity exceeding 25 litres.',
                'expected_timeline_days': 14,
                'sla_max_days': 21,
                'fee_structure': '₹8,000 to ₹35,000 based on heating surface area',
                'inspection_required': True,
                'renewal_period': 'Annual hydraulic test renewal',
                'official_source': 'https://boiler.maharashtra.gov.in',
                'applicable_sectors': 'Food Processing, Chemical, Textile, Pharmaceuticals',
                'risk_category': 'High',
                'reqs': [
                    ('Boiler Manufacturer Test Certificate (Form II, III, IV)', 'Certified metallurgical safety report.', 'boiler_cert', True),
                    ('Erection Drawing & Steam Pipeline Layout', 'Detailed pressure diagram.', 'pipeline_layout', True),
                ]
            },
            {
                'code': 'di-stamp-duty-waiver',
                'name': 'Stamp Duty Exemption Certificate (PSI 2019)',
                'name_mr': 'मुद्रांक शुल्क माफी प्रमाणपत्र',
                'department': 'Directorate of Industries, Maharashtra',
                'category': 'Incentive',
                'why_required': 'Incentive under Maharashtra Industrial Policy 2019 granting 100% stamp duty waiver on land purchase/lease in MIDC industrial areas (Zone C, D, D+).',
                'eligibility': 'Eligible MSME and Large units establishing in designated developing talukas of Maharashtra.',
                'expected_timeline_days': 20,
                'sla_max_days': 30,
                'fee_structure': 'Nil (Government Promotional Scheme)',
                'inspection_required': False,
                'renewal_period': 'One-time fiscal incentive waiver',
                'official_source': 'https://di.maharashtra.gov.in',
                'applicable_sectors': 'Food Processing, Manufacturing, Automobile, Textile, Chemical, IT & Electronics',
                'risk_category': 'Low',
                'reqs': [
                    ('Udyam Registration / EM-II', 'Valid MSME recognition certificate.', 'udyam_cert', True),
                    ('Detailed Project Report (DPR)', 'Financial projection and employment commitment.', 'dpr', True),
                    ('MIDC Land Allotment Letter', 'Letter specifying zone classification.', 'land_deed', True),
                ]
            }
        ]

        created_approvals = {}
        for app_item in approvals_data:
            reqs = app_item.pop('reqs')
            approval, _ = Approval.objects.update_or_create(
                code=app_item['code'],
                defaults=app_item
            )
            created_approvals[approval.code] = approval
            
            # Create requirements
            for idx, (title, desc, doc_code, is_mand) in enumerate(reqs, start=1):
                ApprovalRequirement.objects.update_or_create(
                    approval=approval,
                    order=idx,
                    defaults={
                        'title': title,
                        'description': desc,
                        'doc_type_code': doc_code,
                        'is_mandatory': is_mand,
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_approvals)} Approvals in regulatory catalog'))

        # 6. Documents for Amol Foods (Matching Image 3 & Pre-check Specifications)
        docs_data = [
            {
                'title': 'PAN Card / Tax Identity Document',
                'doc_type': 'pan',
                'file_size_kb': 420,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'GOVERNMENT OF INDIA INCOME TAX DEPARTMENT\nPermanent Account Number: AABCA1234F\nName: AMOL FOODS PRIVATE LIMITED\nIncorporation Date: 14/02/2022',
                'ocr_confidence_score': 98.4,
                'validation_notes': 'Verified against NSDL/CBDT Tax Master. Identity matches Business Profile.',
            },
            {
                'title': 'GST Registration Certificate (Form REG-06)',
                'doc_type': 'gst',
                'file_size_kb': 612,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'GOVERNMENT OF MAHARASHTRA STATE TAX DEPARTMENT\nGSTIN: 27AABCA1234F1Z5\nLegal Name: AMOL FOODS PRIVATE LIMITED\nTrade Name: AMOL FOODS\nPrincipal Place: Plot B-42, Satpur MIDC, Nashik - 422007',
                'ocr_confidence_score': 99.1,
                'validation_notes': 'Active GSTIN. Nashik jurisdiction confirmed. Zero pending compliance defaults.',
            },
            {
                'title': 'Certificate of Incorporation (MCA)',
                'doc_type': 'company_reg',
                'file_size_kb': 840,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'MINISTRY OF CORPORATE AFFAIRS - ROC MUMBAI\nCIN: U15100MH2022PTC384910\nAmol Foods Private Limited\nPaid-up Capital: INR 5,00,00,000',
                'ocr_confidence_score': 97.8,
                'validation_notes': 'Verified with Registrar of Companies (ROC Mumbai). Directors verified.',
            },
            {
                'title': 'MIDC Land Possession & Lease Agreement',
                'doc_type': 'land_deed',
                'file_size_kb': 1450,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'MAHARASHTRA INDUSTRIAL DEVELOPMENT CORPORATION (MIDC)\nPlot No. B-42, Satpur Industrial Area, Nashik\nAllotment Order Ref: MIDC/RO/NSK/2025/1109\nArea: 4,500 sq. meters',
                'ocr_confidence_score': 96.2,
                'validation_notes': 'Possession confirmed. 95-year industrial lease deed valid and stamped.',
            },
            {
                'title': 'Certified Factory Architectural Blueprint Layout',
                'doc_type': 'factory_plan',
                'file_size_kb': 3240,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'DIRECTORATE OF INDUSTRIAL SAFETY & HEALTH - FACTORY PLAN\nAmol Foods Pvt Ltd - Food Processing Plant\nArchitect: Ar. Vilas Shinde (CA/2012/55481)\nBuilt-up Area: 2,400 sq.m, Height: 9.5m, Emergency Exits: 4',
                'ocr_confidence_score': 95.0,
                'validation_notes': 'Meets Section 6 Factories Act specifications. Ventilation and exit ratios compliant.',
            },
            {
                'title': 'Environmental Management Plan / ETP Specification',
                'doc_type': 'environmental_noc',
                'file_size_kb': 0,
                'status': 'Action Required',
                'is_ocr_processed': False,
                'ocr_extracted_text': '',
                'ocr_confidence_score': 0.0,
                'validation_notes': 'Document Missing! Required for MPCB Consent to Establish and DISH scrutiny. Upload detailed Effluent Treatment Plant flowchart to complete pre-validation.',
            },
            {
                'title': 'Fire Hydrant & Emergency Evacuation Drawing',
                'doc_type': 'fire_layout',
                'file_size_kb': 1920,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'MIDC FIRE SAFETY DIVISION - EVACUATION PLAN\nStatic water tank capacity: 1,00,000 Litres\nHydrant ring main with 6 bar pump pressure',
                'ocr_confidence_score': 94.7,
                'validation_notes': 'Fire tender road width (6.2m) exceeds 6.0m requirement. Compliant.',
            },
            {
                'title': 'MSEDCL Approved Single Line Diagram (SLD)',
                'doc_type': 'electricity_sld',
                'file_size_kb': 980,
                'status': 'Pre-validated',
                'is_ocr_processed': True,
                'ocr_extracted_text': 'MSEDCL NASHIK URBAN CIRCLE - ELECTRICAL SLD\nContract Demand: 350 kVA / 11 kV HT Dedicated Feeder\nSubstation: Satpur 33/11 kV Substation',
                'ocr_confidence_score': 98.0,
                'validation_notes': 'Feeder capacity approved by Executive Engineer MSEDCL Nashik.',
            }
        ]

        created_docs = {}
        for d in docs_data:
            doc, _ = Document.objects.update_or_create(
                user=ent_user,
                title=d['title'],
                defaults={
                    'business': business,
                    'doc_type': d['doc_type'],
                    'file_size_kb': d['file_size_kb'],
                    'status': d['status'],
                    'is_ocr_processed': d['is_ocr_processed'],
                    'ocr_extracted_text': d['ocr_extracted_text'],
                    'ocr_confidence_score': d['ocr_confidence_score'],
                    'validation_notes': d['validation_notes'],
                }
            )
            created_docs[d['doc_type']] = doc

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_docs)} Documents for {business.company_name}'))

        # 7. Applications (Directly matching Image 4 & Image 2)
        # App 1: ANM-2026-01042 -> Factory Plan Approval (Image 4 & 5 showcase: Under Review, 72% progress, 3 Days SLA)
        app1, _ = Application.objects.update_or_create(
            application_id='ANM-2026-01042',
            defaults={
                'user': ent_user,
                'business': business,
                'approval': created_approvals['dish-factory-plan'],
                'current_stage': 'Under Review',
                'current_department': 'Directorate of Industrial Safety & Health (DISH)',
                'priority': 'High',
                'assigned_officer': off_user,
                'assigned_officer_name': 'Dr. Rajesh Kulkarni',
                'submission_date': timezone.now() - timedelta(days=12),
                'sla_days_total': 15,
                'sla_days_remaining': 3,
                'is_delayed': False,
                'progress_percent': 72,
                'officer_remarks': 'Technical scrutiny of structural blueprints in progress. Site layout verified. Single-window inspection coordinated.',
            }
        )

        # App 2: ANM-2026-00124 -> MPCB Consent to Establish (Clarification Required - Missing ETP spec)
        app2, _ = Application.objects.update_or_create(
            application_id='ANM-2026-00124',
            defaults={
                'user': ent_user,
                'business': business,
                'approval': created_approvals['mpcb-cte'],
                'current_stage': 'Clarification Required',
                'current_department': 'Maharashtra Pollution Control Board (MPCB)',
                'priority': 'Urgent',
                'assigned_officer': off_user,
                'assigned_officer_name': 'Dr. Rajesh Kulkarni',
                'submission_date': timezone.now() - timedelta(days=22),
                'sla_days_total': 30,
                'sla_days_remaining': 8,
                'is_delayed': False,
                'progress_percent': 55,
                'officer_remarks': 'Clarification requested regarding daily wastewater discharge volume and proposed Zero Liquid Discharge (ZLD) system.',
            }
        )

        # App 3: ANM-2026-00388 -> Fire Safety NOC (Inspection Scheduled - Image 2 match!)
        app3, _ = Application.objects.update_or_create(
            application_id='ANM-2026-00388',
            defaults={
                'user': ent_user,
                'business': business,
                'approval': created_approvals['fire-noc'],
                'current_stage': 'Inspection Scheduled',
                'current_department': 'MIDC Fire Services',
                'priority': 'Normal',
                'assigned_officer': off_user,
                'assigned_officer_name': 'Dr. Rajesh Kulkarni',
                'submission_date': timezone.now() - timedelta(days=8),
                'sla_days_total': 21,
                'sla_days_remaining': 13,
                'is_delayed': False,
                'progress_percent': 65,
                'officer_remarks': 'Provisional Fire NOC verified. Field hydrant simulation scheduled with Divisional Fire Officer.',
            }
        )

        # App 4: ANM-2026-00055 -> MSEDCL Power Connection (Approved)
        app4, _ = Application.objects.update_or_create(
            application_id='ANM-2026-00055',
            defaults={
                'user': ent_user,
                'business': business,
                'approval': created_approvals['msedcl-power'],
                'current_stage': 'Approved',
                'current_department': 'Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL)',
                'priority': 'Normal',
                'assigned_officer': off_user,
                'assigned_officer_name': 'Dr. Rajesh Kulkarni',
                'submission_date': timezone.now() - timedelta(days=28),
                'sla_days_total': 20,
                'sla_days_remaining': 0,
                'is_delayed': False,
                'progress_percent': 100,
                'officer_remarks': 'Demand note cleared. Meter installation and 350 kVA HT energization completed successfully.',
            }
        )

        # Connect Application Documents
        app_docs_mapping = [
            (app1, 'Architectural Factory Plan', 'factory_plan', 'Verified', 'Architect certified. Dimensions conform to building regulations.'),
            (app1, 'Land Ownership / MIDC Deed', 'land_deed', 'Verified', 'Satpur MIDC plot allotment verified.'),
            (app1, 'PAN / Tax Identity', 'pan', 'Verified', 'Corporate PAN verified.'),
            (app2, 'Environmental Management Plan', 'environmental_noc', 'Action Required', 'Missing ETP design schematics. Please upload.'),
            (app2, 'Certificate of Incorporation', 'company_reg', 'Verified', 'MCA verification complete.'),
            (app3, 'Fire Tender Driveway Layout', 'fire_layout', 'Verified', 'Clearance verified.'),
            (app4, 'Electrical Single Line Diagram (SLD)', 'electricity_sld', 'Verified', 'Substation sanction received.'),
        ]

        for app, doc_name, doc_code, status, feedback in app_docs_mapping:
            doc_obj = created_docs.get(doc_code)
            ApplicationDocument.objects.update_or_create(
                application=app,
                doc_name=doc_name,
                defaults={
                    'document': doc_obj,
                    'file_type': 'PDF',
                    'status': status,
                    'officer_feedback': feedback,
                }
            )

        # 8. Application Status History (Complete audit trail)
        history_events = [
            (app1, 'Draft', 'Submitted', ent_user, 'Online submission via AnumatiSetu single window orchestration.', timezone.now() - timedelta(days=12)),
            (app1, 'Submitted', 'Documents Verified', off_user, 'Automated checklist pre-validation passed. Mandatory annexures verified.', timezone.now() - timedelta(days=10)),
            (app1, 'Documents Verified', 'Under Review', off_user, 'Forwarded to Senior Safety Engineer DISH Nashik for technical blueprint scrutiny.', timezone.now() - timedelta(days=6)),

            (app2, 'Draft', 'Submitted', ent_user, 'MPCB Consent to Establish Form submitted.', timezone.now() - timedelta(days=22)),
            (app2, 'Submitted', 'Documents Verified', off_user, 'Basic statutory documents accepted.', timezone.now() - timedelta(days=18)),
            (app2, 'Documents Verified', 'Clarification Required', off_user, 'ETP effluent specs and chemical oxygen demand calculation missing.', timezone.now() - timedelta(days=5)),

            (app3, 'Submitted', 'Inspection Scheduled', off_user, 'Field verification and hydrant water pressure test scheduled.', timezone.now() - timedelta(days=4)),
            (app4, 'Submitted', 'Approved', off_user, 'Transformer installation verified. Power clearance letter issued.', timezone.now() - timedelta(days=2)),
        ]

        for app, prev, new_s, user, rem, ts in history_events:
            ApplicationStatusHistory.objects.get_or_create(
                application=app,
                previous_status=prev,
                new_status=new_s,
                defaults={
                    'changed_by': user,
                    'remarks': rem,
                    'timestamp': ts,
                }
            )

        # 9. Department Queries
        DepartmentQuery.objects.get_or_create(
            application=app2,
            title='Clarification on Effluent Treatment Plant (ETP) Capacity',
            defaults={
                'raised_by': off_user,
                'query_text': 'Kindly furnish detailed design calculations for the proposed 50 KLD Effluent Treatment Plant and clarify whether Zero Liquid Discharge (ZLD) with RO recycling will be implemented as per Red/Orange category guidelines.',
                'response_text': 'We are finalizing the detailed engineering drawings with our environmental consultant (EnviroChem Nashik) and will upload the revised ETP specifications within 48 hours.',
                'status': 'Responded',
            }
        )

        # 10. Inspections (Matching Image 2 & Section 25)
        Inspection.objects.update_or_create(
            application=app3,
            department='MIDC Fire Services, Nashik Division',
            defaults={
                'inspector_name': 'Chief Fire Officer S. V. Gaikwad',
                'inspector_designation': 'Divisional Fire Officer (Nashik & Ahmednagar)',
                'location': 'Plot B-42, Satpur MIDC Industrial Area, Nashik - 422007',
                'scheduled_date': timezone.now().date() + timedelta(days=4),
                'time_slot': '11:00 AM – 01:00 PM',
                'inspection_type': 'Fire Safety Verification',
                'status': 'Scheduled',
                'remarks': 'Field simulation of static water reservoir pump and 6.0m fire tender driveway clearance. Entrepreneur requested to keep licensed fire agency representative present.',
            }
        )

        Inspection.objects.update_or_create(
            application=app1,
            department='Directorate of Industrial Safety & Health (DISH)',
            defaults={
                'inspector_name': 'Er. Sachin Deshmukh',
                'inspector_designation': 'Deputy Director of Industrial Safety & Health',
                'location': 'Plot B-42, Satpur MIDC Industrial Area, Nashik - 422007',
                'scheduled_date': timezone.now().date() + timedelta(days=9),
                'time_slot': '02:30 PM – 04:30 PM',
                'inspection_type': 'Pre-Establishment Site Visit',
                'status': 'Scheduled',
                'remarks': 'Joint site inspection to verify proposed emergency evacuation exits and machinery layout setbacks.',
            }
        )

        # 11. Compliance & Renewals (Section 27)
        c1, _ = Compliance.objects.update_or_create(
            business=business,
            title='Factory Operating Licence Renewal (Form 4)',
            defaults={
                'approval': created_approvals['dish-factory-licence'],
                'department': 'Directorate of Industrial Safety & Health (DISH)',
                'approval_ref': 'DISH-NSK-LIC-2025-4418',
                'due_date': timezone.now().date() + timedelta(days=42),
                'status': 'Approaching',
                'annual_fee': '₹15,000',
                'penalties': '₹500 per month late fee after statutory due date',
                'remarks': 'Annual renewal requires submitting Form 4 with updated worker register and safety audit report.',
            }
        )
        Renewal.objects.update_or_create(
            compliance=c1,
            renewal_due_date=c1.due_date,
            defaults={
                'status': 'Upcoming',
                'remarks': 'Notice generated by AnumatiSetu compliance shield.',
            }
        )

        c2, _ = Compliance.objects.update_or_create(
            business=business,
            title='MPCB Consent to Operate (CTO) Renewal',
            defaults={
                'approval': created_approvals['mpcb-cte'],
                'department': 'Maharashtra Pollution Control Board (MPCB)',
                'approval_ref': 'MPCB-RO-NSK-CTO-2024-912',
                'due_date': timezone.now().date() + timedelta(days=18),
                'status': 'Urgent',
                'annual_fee': '₹25,000',
                'penalties': 'Statutory notice under Section 33A Water Act and penalty up to ₹5,000/day',
                'remarks': 'Urgent: Environmental monitoring report from recognized laboratory must be submitted alongside application.',
            }
        )
        Renewal.objects.update_or_create(
            compliance=c2,
            renewal_due_date=c2.due_date,
            defaults={
                'status': 'Upcoming',
                'remarks': 'Automated reminder alert sent to entrepreneur.',
            }
        )

        c3, _ = Compliance.objects.update_or_create(
            business=business,
            title='Annual Fire Safety Inspection Certificate (Form B)',
            defaults={
                'approval': created_approvals['fire-noc'],
                'department': 'MIDC Fire Services',
                'approval_ref': 'MIDC-FIRE-NSK-2025-781',
                'due_date': timezone.now().date() + timedelta(days=75),
                'status': 'Compliant',
                'annual_fee': '₹8,500',
                'penalties': 'Cancellation of provisional fire safety clearance',
                'remarks': 'Annual fire drill and maintenance certificate from licensed fire contractor.',
            }
        )

        # 12. Government Schemes (Section 28)
        schemes_data = [
            {
                'name': 'Maharashtra Package Scheme of Incentives (PSI 2019 / 2024 Policy)',
                'department': 'Directorate of Industries, Government of Maharashtra',
                'description': 'Comprehensive fiscal incentives including Capital Investment Subsidy (up to 50% for Nashik Zone C/D), 100% Stamp Duty Exemption, Electricity Duty Exemption for 7 years, and ₹1.50/unit Power Tariff Subsidy.',
                'eligibility': 'New Greenfield Units and Substantial Expansion in MSME & Large sectors set up in developing areas (Zones B, C, D, D+). Investment minimum ₹25 Lakhs.',
                'benefits': '• Up to 50% Capital Subsidy on Gross Fixed Capital Investment\n• 100% Stamp Duty Exemption during land acquisition\n• 7-year Electricity Duty Exemption\n• Interest Subsidy @ 5% p.a. on term loan',
                'max_subsidy': 'Up to ₹1.50 Crore for MSME; higher for Mega units',
                'deadline': 'Valid under 2019-2024 Industrial Policy Extension',
                'official_source': 'https://di.maharashtra.gov.in',
                'category_tag': 'MSME',
                'min_investment_cr': 0.25,
                'max_investment_cr': 50.00,
            },
            {
                'name': 'Maharashtra Food Processing Policy Capital Subsidy Scheme',
                'department': 'Department of Agriculture & Industries, Maharashtra',
                'description': 'Dedicated financial assistance for setting up fruit & vegetable processing, dairy processing, and cold chain preservation facilities near farm clusters like Nashik, Pune, and Nagpur.',
                'eligibility': 'Enterprises establishing commercial food processing facilities with minimum 50 direct rural employments.',
                'benefits': '• 35% to 50% Capital Subsidy for agro-processing machinery\n• Cold chain logistics subsidy up to ₹50 Lakhs\n• Quality certification reimbursement (ISO 22000, HACCP)',
                'max_subsidy': 'Up to ₹1.00 Crore Capital Grant',
                'deadline': 'Open Round the Year / FY 2026-27',
                'official_source': 'https://krishi.maharashtra.gov.in',
                'category_tag': 'Agro-Food',
                'min_investment_cr': 1.00,
                'max_investment_cr': 25.00,
            },
            {
                'name': 'Chief Minister’s Employment Generation Programme (CMEGP)',
                'department': 'Maharashtra State Khadi & Village Industries Board / Directorate of Industries',
                'description': 'Flagship government initiative to foster grassroots entrepreneurship and employment generation across semi-urban and rural Maharashtra.',
                'eligibility': 'Any Indian citizen above 18 years establishing manufacturing (up to ₹50 Lakhs) or service unit (up to ₹20 Lakhs).',
                'benefits': '• 15% to 35% margin money government grant\n• Soft loans through nationalized and scheduled banks\n• Priority single-window licensing via DICs',
                'max_subsidy': 'Up to ₹17.50 Lakhs margin money grant',
                'deadline': 'Open Round the Year',
                'official_source': 'https://maha-cmegp.gov.in',
                'category_tag': 'MSME',
                'min_investment_cr': 0.10,
                'max_investment_cr': 0.50,
            },
            {
                'name': 'Dr. Babasaheb Ambedkar Special Incentive Scheme for SC/ST Entrepreneurs',
                'department': 'Social Justice & Special Assistance Department, Maharashtra',
                'description': 'Special empowerment package providing preferential land allotment in MIDC, 100% stamp duty waiver, and up to 30% capital grant for affirmative business growth.',
                'eligibility': 'Enterprises with more than 51% equity held by entrepreneurs from Scheduled Castes or Scheduled Tribes.',
                'benefits': '• 30% Capital Investment Subsidy\n• Power tariff subsidy of ₹2.00 per unit for 5 years\n• 20% land rebate on MIDC industrial plots',
                'max_subsidy': 'Up to ₹2.00 Crore',
                'deadline': 'Open Round the Year',
                'official_source': 'https://sjsa.maharashtra.gov.in',
                'category_tag': 'Women/SC/ST',
                'min_investment_cr': 0.10,
                'max_investment_cr': 100.00,
            },
            {
                'name': 'Green Industrial Transition & Rooftop Solar Adoption Subsidy',
                'department': 'Maharashtra Energy Development Agency (MEDA)',
                'description': 'Promoting industrial carbon footprint reduction through subsidized rooftop solar installations and energy audit reimbursements.',
                'eligibility': 'Operational and new manufacturing units establishing captive renewable energy generation above 50 kWp.',
                'benefits': '• Net-metering accelerated grid synchronization\n• 20% capital grant on solar installation cost\n• 50% reimbursement for BEE-certified energy audit',
                'max_subsidy': 'Up to ₹25 Lakhs per manufacturing premise',
                'deadline': 'FY 2026-27 Solar Transition Mission',
                'official_source': 'https://meda.mahaurja.com',
                'category_tag': 'Green Tech',
                'min_investment_cr': 0.50,
                'max_investment_cr': 200.00,
            }
        ]

        for s in schemes_data:
            GovernmentScheme.objects.update_or_create(
                name=s['name'],
                defaults=s
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(schemes_data)} Government Schemes'))

        # 13. Notifications for Users
        Notification.objects.get_or_create(
            user=ent_user,
            title='Clarification Required on MPCB Consent (ANM-2026-00124)',
            defaults={
                'message': 'MPCB Sub-Regional Officer has requested clarification on ETP capacity. Please review and respond to avoid SLA delay.',
                'notif_type': 'warning',
                'link_url': '/applications/ANM-2026-00124/',
            }
        )

        Notification.objects.get_or_create(
            user=ent_user,
            title='Field Inspection Scheduled for Fire NOC (ANM-2026-00388)',
            defaults={
                'message': 'Divisional Fire Officer will inspect your Satpur factory site on the scheduled date. Please ensure site readiness.',
                'notif_type': 'info',
                'link_url': '/inspections/',
            }
        )

        Notification.objects.get_or_create(
            user=off_user,
            title='New Application Pending Review (ANM-2026-01042)',
            defaults={
                'message': 'Amol Foods Pvt. Ltd. has submitted Factory Plan Approval. 3 days remaining before statutory SLA deadline.',
                'notif_type': 'urgent',
                'link_url': '/officer/applications/ANM-2026-01042/',
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully completed AnumatiSetu demo data seeding!'))
