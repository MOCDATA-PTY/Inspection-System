#!/usr/bin/env python3
"""
Pull inspections for an inspector by name (with fuzzy matching) and optionally export to CSV.

Usage:
  python pull_inspections_for_inspector.py --name Dimakatso --export dimakatso.csv

The script will:
 - Query `FoodSafetyAgencyInspection` for exact / icontains matches on the provided name
 - Build a list of close inspector_name values using difflib and include those
 - Print counts per inspector_id and sample rows
 - Optionally export all matching rows to a CSV file
"""

import os
import sys
import django
import argparse
import csv
import difflib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db.models import Q
from main.models import FoodSafetyAgencyInspection


def find_similar_names(target, choices, cutoff=0.6, max_matches=20):
    # Use difflib to find close matches (case-insensitive)
    lowercase_map = {c: c for c in choices}
    cand_list = list(lowercase_map.keys())
    matches = difflib.get_close_matches(target, cand_list, n=max_matches, cutoff=cutoff)
    return matches


def export_to_csv(rows, path):
    if not rows:
        print(f"No rows to export to {path}")
        return
    keys = ['id', 'remote_id', 'inspector_id', 'inspector_name', 'date_of_inspection', 'client_name', 'commodity', 'product_name']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(keys)
        for r in rows:
            writer.writerow([getattr(r, k) for k in keys])
    print(f"Exported {len(rows)} rows to {path}")


def main():
    parser = argparse.ArgumentParser(description='Pull inspections for an inspector (fuzzy)')
    parser.add_argument('--name', '-n', required=True, help='Inspector name to search for')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Sample rows to print per match')
    parser.add_argument('--export', '-e', help='Optional CSV file path to export full results')
    parser.add_argument('--cutoff', type=float, default=0.6, help='Similarity cutoff for fuzzy matching (0-1)')
    args = parser.parse_args()

    name = args.name.strip()
    limit = args.limit
    cutoff = args.cutoff

    print('=' * 80)
    print(f"Searching inspections for: '{name}' (cutoff={cutoff})")
    print('=' * 80)

    # 1) exact and icontains
    exact_qs = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_name__iexact=name) | Q(inspector_name__icontains=name)
    )
    exact_count = exact_qs.count()
    print(f"Direct matches (iexact / icontains) count: {exact_count}")
    if exact_count:
        print("Sample direct matches:")
        for insp in exact_qs.order_by('-date_of_inspection')[:limit]:
            print(f"  id={insp.id} remote_id={insp.remote_id} inspector_id={insp.inspector_id} inspector_name='{insp.inspector_name}' date={insp.date_of_inspection} client='{insp.client_name}'")
    print()

    # 2) gather distinct inspector_name values to fuzzy match against
    names_qs = FoodSafetyAgencyInspection.objects.values_list('inspector_name', flat=True).distinct()
    all_names = [n for n in names_qs if n]
    # Use case-insensitive matching via mapping to lowercase
    lowered = {n.lower(): n for n in all_names}
    target = name.lower()
    candidates = list(lowered.keys())

    similar_low = difflib.get_close_matches(target, candidates, n=30, cutoff=cutoff)
    similar = [lowered[s] for s in similar_low]

    if similar:
        print(f"Fuzzy-matched inspector_name values (approx): {len(similar)}")
        for s in similar[:30]:
            # show counts per matched name
            cnt = FoodSafetyAgencyInspection.objects.filter(inspector_name__iexact=s).count()
            print(f"  '{s}' -> {cnt} rows")
    else:
        print("No fuzzy name matches found in existing inspector_name values.")
    print()

    # 3) Also check last-name only matches if name contains spaces
    last_name_matches = []
    if ' ' in name:
        last = name.split()[-1]
        last_qs = FoodSafetyAgencyInspection.objects.filter(inspector_name__icontains=last)
        if last_qs.exists():
            print(f"Matches by last name '{last}': {last_qs.count()}")
            last_name_matches = list(last_qs[:limit])
            for insp in last_name_matches[:limit]:
                print(f"  id={insp.id} inspector_id={insp.inspector_id} inspector_name='{insp.inspector_name}' date={insp.date_of_inspection}")
        print()

    # 4) Gather matches by inspector_id if mapping exists locally
    # Get inspector_ids for exact matches and fuzzy matched names
    matched_ids = set()
    for insp in exact_qs.values('inspector_id').distinct():
        if insp['inspector_id'] is not None:
            matched_ids.add(insp['inspector_id'])
    for s in similar:
        for insp in FoodSafetyAgencyInspection.objects.filter(inspector_name__iexact=s).values('inspector_id').distinct():
            if insp['inspector_id'] is not None:
                matched_ids.add(insp['inspector_id'])

    if matched_ids:
        print(f"Inspections for inspector_id(s): {sorted(matched_ids)}")
        for iid in sorted(matched_ids):
            cnt = FoodSafetyAgencyInspection.objects.filter(inspector_id=iid).count()
            print(f"  id={iid} -> {cnt} rows")
    else:
        print("No inspector_id matches discovered for this name in local inspections.")
    print()

    # 5) Combine queries to fetch all matching rows (by name variants and last name)
    combined_q = Q()
    combined_q |= Q(inspector_name__iexact=name) | Q(inspector_name__icontains=name)
    for s in similar:
        combined_q |= Q(inspector_name__iexact=s)
    if ' ' in name:
        last = name.split()[-1]
        combined_q |= Q(inspector_name__icontains=last)

    all_matches = FoodSafetyAgencyInspection.objects.filter(combined_q).order_by('-date_of_inspection')
    total = all_matches.count()
    print(f"Total matching inspections found: {total}")
    if total:
        print(f"Showing up to {limit} recent matches:")
        for insp in all_matches[:limit]:
            print(f"  id={insp.id} remote_id={insp.remote_id} inspector_id={insp.inspector_id} inspector_name='{insp.inspector_name}' date={insp.date_of_inspection} client='{insp.client_name}' commodity='{insp.commodity}' product='{insp.product_name}'")

    # Export if requested
    if args.export:
        export_to_csv(list(all_matches), args.export)


if __name__ == '__main__':
    main()
