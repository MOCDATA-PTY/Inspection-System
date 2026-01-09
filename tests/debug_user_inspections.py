#!/usr/bin/env python3
"""
Diagnostic script to help find why a user's inspections (e.g. 'Dimakatso') aren't showing.

Usage:
    python debug_user_inspections.py --user Dimakatso

The script will:
 - Look up the Django `User` for the provided username/email
 - Show any `InspectorMapping` entries that might map that user to an inspector_id
 - Search `FoodSafetyAgencyInspection` for matches by `inspector_name` and `inspector_id`
 - Suggest likely causes and next steps
"""

import os
import sys
import django
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Q
from main.models import InspectorMapping, FoodSafetyAgencyInspection


def find_user(identifier):
    # Try username, then email, then full name
    user = None
    try:
        user = User.objects.filter(username__iexact=identifier).first()
        if user:
            return user
        user = User.objects.filter(email__iexact=identifier).first()
        if user:
            return user
        # Try splitting into names
        parts = identifier.split()
        if len(parts) >= 2:
            user = User.objects.filter(first_name__iexact=parts[0], last_name__iexact=parts[-1]).first()
            if user:
                return user
    except Exception as e:
        print(f"Error while looking up user: {e}")
    return None


def show_inspections_for_name(name, limit=10):
    qs = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_name__icontains=name) | Q(inspector_name__iexact=name)
    )
    count = qs.count()
    print(f"Inspections where inspector_name matches '{name}': {count}")
    if count:
        print("Sample rows:")
        for insp in qs.order_by('-date_of_inspection')[:limit]:
            print(f"  id={insp.id} remote_id={insp.remote_id} inspector_id={insp.inspector_id} inspector_name='{insp.inspector_name}' date={insp.date_of_inspection} client='{insp.client_name}'")
    print()


def show_inspections_for_ids(ids, limit=10):
    qs = FoodSafetyAgencyInspection.objects.filter(inspector_id__in=ids)
    count = qs.count()
    print(f"Inspections for inspector_id in {ids}: {count}")
    if count:
        print("Sample rows:")
        for insp in qs.order_by('-date_of_inspection')[:limit]:
            print(f"  id={insp.id} remote_id={insp.remote_id} inspector_id={insp.inspector_id} inspector_name='{insp.inspector_name}' date={insp.date_of_inspection} client='{insp.client_name}'")
    print()


def main():
    parser = argparse.ArgumentParser(description='Debug missing inspections for a user')
    parser.add_argument('--user', '-u', help='Username, email, or full name to check', required=True)
    parser.add_argument('--limit', '-n', help='Number of sample rows to show per query', type=int, default=10)
    args = parser.parse_args()

    identifier = args.user.strip()
    limit = args.limit

    print('=' * 80)
    print(f"Diagnostic for identifier: '{identifier}'")
    print('=' * 80)

    user = find_user(identifier)
    if user:
        print(f"Found Django user: username='{user.username}' full_name='{user.first_name} {user.last_name}' email='{user.email}' role='{getattr(user, 'role', None)}' employee_id='{getattr(user, 'employee_id', None)}'")
    else:
        print("Django user not found by username/email/fullname lookup.")
    print()

    # Find inspector mappings that may reference this username/full name/email
    possible_names = set()
    possible_names.add(identifier)
    if user:
        full = f"{user.first_name} {user.last_name}".strip()
        if full:
            possible_names.add(full)
        possible_names.add(user.username)
        if user.email:
            possible_names.add(user.email)

    print('Searching InspectorMapping for possible matches...')
    mappings = InspectorMapping.objects.filter(
        Q(inspector_name__in=list(possible_names)) |
        Q(inspector_name__icontains=identifier) |
        Q(inspector_name__icontains=(user.first_name if user else ''))
    )
    if mappings.exists():
        print(f"Found {mappings.count()} InspectorMapping entries:")
        ids = []
        for m in mappings:
            print(f"  - id={m.id} inspector_id={m.inspector_id} name='{m.inspector_name}' active={m.is_active}")
            ids.append(m.inspector_id)
    else:
        print("No InspectorMapping entries found that match this identifier.")
        ids = []
    print()

    # Check INSPECTOR_NAME_MAP if available (helps when remote SQL rows rely on static map)
    try:
        from main.views.data_views import INSPECTOR_NAME_MAP
        mapped_ids = [k for k, v in INSPECTOR_NAME_MAP.items() if any(x.lower() in v.lower() for x in possible_names)]
        if mapped_ids:
            print(f"INSPECTOR_NAME_MAP contains these ids mapping to similar names: {mapped_ids}")
        else:
            print("INSPECTOR_NAME_MAP has no similar names for this identifier.")
    except Exception:
        print("Could not import INSPECTOR_NAME_MAP (skipping).")
    print()

    # Search inspections by name
    for name in list(possible_names):
        show_inspections_for_name(name, limit=limit)

    # Search inspections by mapping ids
    if ids:
        show_inspections_for_ids(ids, limit=limit)

    # Helpful suggestions
    print('=' * 80)
    print('Suggestions:')
    print("- If inspections exist with a different inspector_name but the user's mapping is missing, add an InspectorMapping record or add the inspector_id to INSPECTOR_NAME_MAP in `main/views/data_views.py`.")
    print("- If no inspections exist at all for this person, verify the remote SQL Server data and that sync jobs ran successfully.")
    print("- If inspections exist but use an unexpected inspector_id, update InspectorMapping and re-run any sync/association logic.")
    print('=' * 80)


if __name__ == '__main__':
    main()
