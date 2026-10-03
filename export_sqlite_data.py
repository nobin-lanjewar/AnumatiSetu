"""
Export SQLite data for AnumatiSetu safely with UTF-8 encoding.
Excludes contenttypes and auth.permission to prevent collision on PostgreSQL.
"""
import os
import sys
import json
from pathlib import Path

# Ensure Django environment is configured
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = ''  # Guarantee reading from local SQLite db.sqlite3

import django
django.setup()

from django.core import serializers
from django.apps import apps

MODELS_IN_ORDER = [
    'auth.User',
    'accounts.UserProfile',
    'business.BusinessProfile',
    'approvals.Approval',
    'approvals.ApprovalRequirement',
    'documents.Document',
    'applications.Application',
    'applications.ApplicationDocument',
    'applications.ApplicationStatusHistory',
    'applications.DepartmentQuery',
    'inspections.Inspection',
    'compliance.Compliance',
    'compliance.Renewal',
    'schemes.GovernmentScheme',
    'assistant.ChatMessage',
    'accounts.Notification',
]

def export_data(output_path='data_sqlite_export.json'):
    all_objects = []
    summary = {}
    
    for model_name in MODELS_IN_ORDER:
        app_label, model_cls_name = model_name.split('.')
        model = apps.get_model(app_label, model_cls_name)
        objects = list(model.objects.all().order_by('pk'))
        summary[model_name] = len(objects)
        all_objects.extend(objects)
        
    serialized = serializers.serialize('json', all_objects, indent=2, ensure_ascii=False)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(serialized)
        
    print("=" * 60)
    print("ANUMATISETU SQLITE DATA EXPORT SUMMARY")
    print("=" * 60)
    total = 0
    for model_name, count in summary.items():
        print(f"  - {model_name:<38}: {count:>3} records")
        total += count
    print("-" * 60)
    print(f"  TOTAL EXPORTED RECORDS: {total}")
    print(f"  Export file: {output_path} ({len(serialized.encode('utf-8')):,} bytes)")
    print("=" * 60)
    return total

if __name__ == '__main__':
    export_data()
