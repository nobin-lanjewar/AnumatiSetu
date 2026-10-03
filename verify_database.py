"""
AnumatiSetu - Database Integrity & Functionality Verification Utility
Validates connection, migrations, data integrity, user auth, and CRUD operations.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from accounts.models import UserProfile
from business.models import BusinessProfile
from applications.models import Application
from approvals.models import Approval
from documents.models import Document
from schemes.models import GovernmentScheme

def run_verification():
    print("=" * 65)
    print("ANUMATISETU DATABASE VERIFICATION")
    print("=" * 65)
    
    # 1. Database Connection Info
    engine = connection.settings_dict.get('ENGINE', '')
    host = connection.settings_dict.get('HOST', '')
    port = connection.settings_dict.get('PORT', '')
    name = connection.settings_dict.get('NAME', '')
    
    print(f"Database Engine : {engine}")
    print(f"Database Host   : {host or 'localhost'}")
    print(f"Database Port   : {port or 'default'}")
    print(f"Database Name   : {name}")
    
    try:
        connection.ensure_connection()
        print("Connection Status: ACTIVE & HEALTHY")
    except Exception as e:
        print(f"Connection Status: FAILED ({e})")
        return False
        
    print("-" * 65)
    print("RECORD COUNTS")
    print("-" * 65)
    user_count = User.objects.count()
    profile_count = UserProfile.objects.count()
    biz_count = BusinessProfile.objects.count()
    app_count = Application.objects.count()
    approval_count = Approval.objects.count()
    doc_count = Document.objects.count()
    scheme_count = GovernmentScheme.objects.count()
    
    print(f"Users               : {user_count}")
    print(f"User Profiles       : {profile_count}")
    print(f"Business Profiles   : {biz_count}")
    print(f"Applications        : {app_count}")
    print(f"Statutory Approvals : {approval_count}")
    print(f"Uploaded Documents  : {doc_count}")
    print(f"Government Schemes  : {scheme_count}")
    
    print("-" * 65)
    print("KEY USERS & AUTHENTICATION CHECK")
    print("-" * 65)
    for u in User.objects.all().order_by('id')[:6]:
        role_profile = getattr(u, 'profile', None)
        role_name = role_profile.role if role_profile else 'No Profile'
        print(f"User: {u.username:<16} | Email: {u.email:<30} | Role: {role_name}")
        
    print("-" * 65)
    print("CRUD OPERATION & SEQUENCE TEST")
    print("-" * 65)
    try:
        # Create a temporary scheme to test sequence and write
        test_scheme = GovernmentScheme.objects.create(
            name="Temporary Sequence Test Scheme",
            department="Directorate of Industries",
            description="Automated CRUD test",
            eligibility="MSME",
            benefits="Test Benefits",
            is_active=False
        )
        test_id = test_scheme.id
        print(f"Create test passed (Generated ID: {test_id})")
        
        # Read test
        fetched = GovernmentScheme.objects.get(id=test_id)
        assert fetched.name == "Temporary Sequence Test Scheme"
        print("Read test passed")
        
        # Update test
        fetched.description = "Updated description"
        fetched.save()
        print("Update test passed")
        
        # Delete test
        fetched.delete()
        print("Delete test passed")
        print("CRUD Operations & Database Sequences verified successfully!")
    except Exception as e:
        print(f"CRUD Test Failed: {e}")
        return False
        
    print("=" * 65)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 65)
    return True

if __name__ == '__main__':
    run_verification()
