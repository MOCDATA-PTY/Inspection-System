#!/usr/bin/env python
"""
Pull ALL compliance documents from Google Drive for recent inspections.
Matches by account code only (ignores commodity mismatch).

Usage:
    python tests/pull_compliance_documents.py
    python tests/pull_compliance_documents.py --days 30
    python tests/pull_compliance_documents.py --client "Test1"
"""
import os
import sys
import argparse
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

from django.utils import timezone
from main.models import FoodSafetyAgencyInspection, Client
from main.services.daily_compliance_sync import DailyComplianceSyncService
from main.views.core_views import download_compliance_document, normalize_client_name


def pull_compliance_documents(days=7, client_filter=None, dry_run=False):
    """Pull compliance documents for recent inspections."""

    print("=" * 70)
    print("COMPLIANCE DOCUMENT PULL")
    print("=" * 70)

    # Load files from Google Drive
    sync = DailyComplianceSyncService()
    sync.is_running = True
    print("\nLoading Google Drive files...")
    file_lookup = sync.load_drive_files_standalone()

    if not file_lookup:
        print("ERROR: Could not load files from Google Drive")
        return

    print(f"Loaded {len(file_lookup)} files from Google Drive\n")

    # Build client mapping for account codes
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        key = normalize_client_name(client.client_id or '')
        if key:
            client_map[key] = client.internal_account_code

    print(f"Loaded {len(client_map)} clients with account codes\n")

    # Get recent inspections
    cutoff_date = timezone.now().date() - timedelta(days=days)

    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=cutoff_date
    ).order_by('-date_of_inspection')

    if client_filter:
        inspections = inspections.filter(client_name__icontains=client_filter)

    total = inspections.count()
    print(f"Found {total} inspections in last {days} days")
    if client_filter:
        print(f"  (filtered by client: '{client_filter}')")
    print("-" * 70)

    # Track stats
    processed = 0
    downloaded = 0
    skipped = 0
    errors = 0
    no_account = 0
    no_files = 0

    for insp in inspections:
        processed += 1

        # Get account code
        client_key = normalize_client_name(insp.client_name or '')
        account_code = insp.internal_account_code or client_map.get(client_key, '')

        if not account_code:
            no_account += 1
            continue

        # Find ALL matching files by account code (within 15 days of inspection)
        matching_files = []

        for file_key, file_info in file_lookup.items():
            if file_info.get('accountCode') == account_code:
                # Check date within 15 days
                file_date = file_info.get('zipDate')
                if file_date:
                    if hasattr(file_date, 'date'):
                        file_date = file_date.date()

                    insp_date = insp.date_of_inspection
                    if hasattr(insp_date, 'date'):
                        insp_date = insp_date.date()

                    try:
                        days_diff = abs((file_date - insp_date).days)
                        if days_diff <= 15:
                            matching_files.append({
                                'file_info': file_info,
                                'days_diff': days_diff
                            })
                    except:
                        pass

        if not matching_files:
            no_files += 1
            continue

        # Download each matching file
        print(f"\n[{processed}/{total}] {insp.client_name}")
        print(f"  Account: {account_code} | Date: {insp.date_of_inspection} | Commodity: {insp.commodity}")
        print(f"  Found {len(matching_files)} matching file(s)")

        for match in matching_files:
            file_info = match['file_info']
            file_name = file_info.get('name', 'unknown')
            file_commodity = file_info.get('commodity', 'UNKNOWN')

            if dry_run:
                print(f"    [DRY RUN] Would download: {file_name}")
                skipped += 1
                continue

            try:
                downloaded_path = download_compliance_document(
                    file_info['file_id'],
                    account_code,
                    file_commodity,  # Use file's commodity for folder organization
                    insp.date_of_inspection,
                    file_name,
                    insp.client_name,
                    None
                )

                if downloaded_path:
                    downloaded += 1
                    print(f"    [OK] {file_name} -> {downloaded_path}")
                else:
                    skipped += 1
                    print(f"    [SKIP] {file_name} (already exists or failed)")

            except Exception as e:
                errors += 1
                print(f"    [ERROR] {file_name}: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Inspections processed: {processed}")
    print(f"  Documents downloaded:  {downloaded}")
    print(f"  Skipped (exists):      {skipped}")
    print(f"  Errors:                {errors}")
    print(f"  No account code:       {no_account}")
    print(f"  No files in Drive:     {no_files}")
    print("=" * 70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull compliance documents from Google Drive')
    parser.add_argument('--days', type=int, default=7, help='Number of days back to look (default: 7)')
    parser.add_argument('--client', type=str, help='Filter by client name (partial match)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without downloading')

    args = parser.parse_args()

    pull_compliance_documents(
        days=args.days,
        client_filter=args.client,
        dry_run=args.dry_run
    )
