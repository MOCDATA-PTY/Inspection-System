#!/usr/bin/env python3
"""
Delete the 'Hellen' InspectorMapping (if present) and ensure Dimakatso mapping exists for id 202.

Usage:
    python apply_dimakatso_mapping.py
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db.models import Q
from main.models import InspectorMapping


def main():
    # Delete Hellen mapping(s)
    hellen_qs = InspectorMapping.objects.filter(Q(inspector_name__iexact='Hellen') | Q(inspector_id=9115))
    if hellen_qs.exists():
        print(f"Found {hellen_qs.count()} InspectorMapping(s) for 'Hellen' or id 9115. Deleting them...")
        for m in hellen_qs:
            print(f"  Deleting: id={m.id} inspector_id={m.inspector_id} name='{m.inspector_name}' active={m.is_active}")
        hellen_qs.delete()
    else:
        print("No InspectorMapping found for 'Hellen' or id 9115.")

    # Ensure Dimakatso mapping exists for id=202
    dim_qs = InspectorMapping.objects.filter(inspector_id=202)
    if dim_qs.exists():
        m = dim_qs.first()
        changed = False
        desired_name = 'Dimakatso Modiba'
        if m.inspector_name != desired_name:
            print(f"Updating inspector_name for id=202: '{m.inspector_name}' -> '{desired_name}'")
            m.inspector_name = desired_name
            changed = True
        if not m.is_active:
            print(f"Activating mapping id={m.id} (inspector_id=202)")
            m.is_active = True
            changed = True
        if changed:
            m.save()
            print("Updated existing Dimakatso mapping.")
        else:
            print("Dimakatso mapping for id=202 already exists and is correct.")
    else:
        print("Creating InspectorMapping for Dimakatso (inspector_id=202)")
        InspectorMapping.objects.create(inspector_id=202, inspector_name='Dimakatso Modiba', is_active=True)
        print("Created mapping.")


if __name__ == '__main__':
    main()
