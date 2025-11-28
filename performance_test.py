#!/usr/bin/env python
"""
PERFORMANCE PROFILING TEST - Identifies exact bottlenecks in shipment_list view
"""
import os
import django
import time
import cProfile
import pstats
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from main.models import FoodSafetyAgencyInspection, InspectorMapping
from datetime import datetime, timedelta

User = get_user_model()

print("=" * 80)
print("PERFORMANCE PROFILING TEST - SHIPMENT LIST VIEW")
print("=" * 80)

# Clear cache for fresh test
cache.clear()
print("\n[OK] Cache cleared\n")

# Get an inspector user
inspector = User.objects.filter(role='inspector').first()
if not inspector:
    print("ERROR: No inspector user found!")
    exit(1)

print(f"Testing with user: {inspector.username} (Role: {inspector.role})")

# Create test client
client = Client()
client.force_login(inspector)

print("\n" + "=" * 80)
print("STEP-BY-STEP TIMING ANALYSIS")
print("=" * 80)

# Test 1: Database query time
print("\n[1] DATABASE QUERY TIME")
print("-" * 80)
start = time.time()
sixty_days_ago = (datetime.now() - timedelta(days=60)).date()
inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago
)
count = inspections.count()
db_time = time.time() - start
print(f"Time to count {count} inspections: {db_time:.3f}s")

# Test 2: Inspector filtering
print("\n[2] INSPECTOR FILTERING")
print("-" * 80)
start = time.time()
try:
    mapping = InspectorMapping.objects.get(
        inspector_name=inspector.get_full_name() or inspector.username
    )
    inspector_id = mapping.inspector_id
    inspector_name = mapping.inspector_name
    print(f"[OK] Found mapping: {inspector_name} (ID: {inspector_id})")
except InspectorMapping.DoesNotExist:
    print("[ERROR] No mapping found!")
    inspector_id = None
    inspector_name = None

if inspector_id and inspector_name:
    from django.db.models import Q
    filtered = inspections.filter(
        Q(inspector_id=inspector_id) | Q(inspector_name=inspector_name)
    )
    filtered_count = filtered.count()
    filter_time = time.time() - start
    print(f"Time to filter to {filtered_count} inspections: {filter_time:.3f}s")
else:
    print("Skipping filter test - no mapping")
    filtered_count = 0
    filter_time = 0

# Test 3: Grouping time
print("\n[3] GROUPING INSPECTIONS")
print("-" * 80)
start = time.time()
from django.db.models import Count, Max, Min
groups = filtered.values('client_name', 'date_of_inspection').annotate(
    inspection_count=Count('id'),
    latest_inspection_id=Max('id'),
    earliest_inspection_id=Min('id'),
).order_by('-date_of_inspection', 'client_name')[:25]
groups_list = list(groups)
group_time = time.time() - start
print(f"Time to group into {len(groups_list)} groups: {group_time:.3f}s")

# Test 4: Loading inspection details for groups
print("\n[4] LOADING INSPECTION DETAILS")
print("-" * 80)
start = time.time()
group_conditions = Q()
for group in groups_list:
    group_conditions |= Q(
        client_name=group['client_name'],
        date_of_inspection=group['date_of_inspection']
    )
all_inspections = filtered.filter(group_conditions)
all_count = all_inspections.count()
load_time = time.time() - start
print(f"Time to load {all_count} detailed inspections: {load_time:.3f}s")

# Test 5: Client cache loading
print("\n[5] CLIENT CACHE LOADING")
print("-" * 80)
start = time.time()
from main.models import Client
client_count = Client.objects.count()
clients = list(Client.objects.select_related().prefetch_related('additional_emails'))
client_time = time.time() - start
print(f"Time to load {client_count} clients with emails: {client_time:.3f}s")

# Test 6: Full page load via HTTP
print("\n[6] FULL PAGE LOAD (HTTP REQUEST)")
print("-" * 80)
start = time.time()
response = client.get('/shipment-list/')
http_time = time.time() - start
print(f"HTTP Status: {response.status_code}")
print(f"Total page load time: {http_time:.3f}s")

# Test 7: Cached page load
print("\n[7] CACHED PAGE LOAD")
print("-" * 80)
start = time.time()
response = client.get('/shipment-list/')
cached_time = time.time() - start
print(f"HTTP Status: {response.status_code}")
print(f"Cached page load time: {cached_time:.3f}s")

# Test 8: Page 2 load
print("\n[8] PAGE 2 LOAD (DIFFERENT CACHE KEY)")
print("-" * 80)
start = time.time()
response = client.get('/shipment-list/?page=2')
page2_time = time.time() - start
print(f"HTTP Status: {response.status_code}")
print(f"Page 2 load time: {page2_time:.3f}s")

# Summary
print("\n" + "=" * 80)
print("PERFORMANCE SUMMARY")
print("=" * 80)
print(f"Database query:        {db_time:.3f}s")
print(f"Inspector filtering:   {filter_time:.3f}s")
print(f"Grouping:              {group_time:.3f}s")
print(f"Loading details:       {load_time:.3f}s")
print(f"Client cache:          {client_time:.3f}s")
print(f"First HTTP load:       {http_time:.3f}s")
print(f"Cached HTTP load:      {cached_time:.3f}s")
print(f"Page 2 load:           {page2_time:.3f}s")
print("=" * 80)

# Identify bottleneck
print("\nBOTTLENECK ANALYSIS:")
steps = [
    ("Database query", db_time),
    ("Inspector filtering", filter_time),
    ("Grouping", group_time),
    ("Loading details", load_time),
    ("Client cache", client_time),
]
slowest = max(steps, key=lambda x: x[1])
print(f"SLOWEST STEP: {slowest[0]} ({slowest[1]:.3f}s)")

if http_time > 10:
    print(f"\n[WARNING] HTTP load time is {http_time:.3f}s (VERY SLOW)")
elif http_time > 5:
    print(f"\n[WARNING] HTTP load time is {http_time:.3f}s (SLOW)")
elif http_time > 2:
    print(f"\n[OK] HTTP load time is {http_time:.3f}s (ACCEPTABLE)")
else:
    print(f"\n[EXCELLENT] HTTP load time is {http_time:.3f}s (FAST)")

if cached_time > 2:
    print(f"[WARNING] Cached load is {cached_time:.3f}s (should be <2s)")
else:
    print(f"[OK] Cached load is {cached_time:.3f}s (GOOD)")

print("\n" + "=" * 80)

# Detailed profiling
print("\nRUNNING DETAILED PROFILER...")
print("=" * 80)
profiler = cProfile.Profile()
profiler.enable()
response = client.get('/shipment-list/')
profiler.disable()

s = StringIO()
ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
ps.print_stats(30)  # Top 30 functions
print("\nTOP 30 SLOWEST FUNCTIONS:")
print(s.getvalue())

print("\n" + "=" * 80)
print("PROFILING COMPLETE")
print("=" * 80)
