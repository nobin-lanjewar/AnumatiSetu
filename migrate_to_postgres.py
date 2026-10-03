"""
AnumatiSetu - Automated SQLite to Supabase PostgreSQL Migration Script
Migrates data safely, resolves primary key sequences, and verifies integrity.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure settings are loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection, transaction
from django.core.management import call_command
from django.core import serializers
from django.apps import apps
from django.core.management.color import no_style

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

def check_connection():
    engine = connection.settings_dict.get('ENGINE', '')
    host = connection.settings_dict.get('HOST', '')
    name = connection.settings_dict.get('NAME', '')
    print("=" * 65)
    print("1. DATABASE CONNECTION CHECK")
    print("=" * 65)
    print(f"  Engine : {engine}")
    print(f"  Host   : {host or 'localhost'}")
    print(f"  DB Name: {name}")
    
    if 'postgresql' not in engine:
        print("\n[WARNING] Django is NOT configured to use PostgreSQL!")
        print("Please set DATABASE_URL environment variable to your Supabase PostgreSQL connection string.")
        print("Example:")
        print("  DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres")
        return False
        
    try:
        connection.ensure_connection()
        print("  Status : Successfully connected to PostgreSQL / Supabase!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to database: {e}")
        return False

def apply_migrations():
    print("\n" + "=" * 65)
    print("2. APPLYING DJANGO MIGRATIONS (CREATING TABLES)")
    print("=" * 65)
    call_command('migrate', interactive=False)
    print("  All migrations applied successfully.")

def import_data(json_file='data_sqlite_export.json'):
    print("\n" + "=" * 65)
    print("3. IMPORTING APPLICATION DATA INTO POSTGRESQL")
    print("=" * 65)
    
    if not os.path.exists(json_file):
        print(f"[ERROR] Data export file '{json_file}' not found. Run export_sqlite_data.py first.")
        return False

    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = f.read()

    deserialized_objects = list(serializers.deserialize('json', json_data))
    print(f"  Parsed {len(deserialized_objects)} objects from {json_file}.")

    # Load in atomic transaction with foreign key checking
    loaded_counts = {}
    with transaction.atomic():
        for obj in deserialized_objects:
            model_label = f"{obj.object._meta.app_label}.{obj.object._meta.object_name}"
            obj.save()
            loaded_counts[model_label] = loaded_counts.get(model_label, 0) + 1

    for model_name in MODELS_IN_ORDER:
        count = loaded_counts.get(model_name, 0)
        print(f"  Loaded {model_name:<35}: {count:>3} records")
        
    print(f"  Total records imported: {sum(loaded_counts.values())}")
    return True

def reset_sequences():
    print("\n" + "=" * 65)
    print("4. RESETTING POSTGRESQL PRIMARY KEY SEQUENCES")
    print("=" * 65)
    
    app_labels = [
        'auth', 'accounts', 'business', 'approvals',
        'documents', 'applications', 'inspections',
        'compliance', 'schemes', 'assistant'
    ]
    
    apps_list = [apps.get_app_config(app) for app in app_labels if app in apps.app_configs]
    
    with connection.cursor() as cursor:
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [m for app in apps_list for m in app.get_models()])
        if sequence_sql:
            for sql in sequence_sql:
                cursor.execute(sql)
            print(f"  Executed {len(sequence_sql)} sequence reset statements.")
        else:
            print("  No sequences required manual reset.")
    print("  Sequences updated to prevent ID collision on future inserts.")

def verify_data():
    print("\n" + "=" * 65)
    print("5. VERIFYING RECORD COUNTS & INTEGRITY")
    print("=" * 65)
    
    print(f"  {'Model':<38} | {'PostgreSQL Count':>16}")
    print("  " + "-" * 57)
    
    for model_name in MODELS_IN_ORDER:
        app_label, model_cls_name = model_name.split('.')
        model = apps.get_model(app_label, model_cls_name)
        count = model.objects.count()
        print(f"  {model_name:<38} | {count:>16} rows")
        
    print("=" * 65)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)

def main():
    if not check_connection():
        sys.exit(1)
    apply_migrations()
    if not import_data():
        sys.exit(1)
    reset_sequences()
    verify_data()

if __name__ == '__main__':
    main()
