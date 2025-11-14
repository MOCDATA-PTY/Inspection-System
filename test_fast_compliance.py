"""
Fast test for compliance documents with caching enabled
Tests the caching optimization for Google Drive file retrieval
"""

import os
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.http import HttpRequest
from main.views.core_views import load_drive_files_real

def test_caching_speedup():
    """Test how caching speeds up compliance document retrieval"""
    
    print("=" * 100)
    print(" " * 25 + "COMPLIANCE DOCUMENTS CACHING SPEED TEST")
    print("=" * 100)
    print()
    
    request = HttpRequest()
    
    # =============================
    # TEST 1: First call (no cache)
    # =============================
    print("TEST 1: First call (with cache enabled, but no cached data)")
    print("-" * 100)
    
    start_time = time.time()
    
    # First call - will load from Google Drive and cache
    file_lookup_1 = load_drive_files_real(request, use_cache=True)
    
    first_call_time = time.time() - start_time
    
    print(f"\nTime taken: {first_call_time:.2f} seconds")
    print(f"Files loaded: {len(file_lookup_1)}")
    print()
    
    # =============================
    # TEST 2: Second call (with cache)
    # =============================
    print("TEST 2: Second call (with cache)")
    print("-" * 100)
    
    start_time = time.time()
    
    # Second call - should use cache
    file_lookup_2 = load_drive_files_real(request, use_cache=True)
    
    second_call_time = time.time() - start_time
    
    print(f"\nTime taken: {second_call_time:.2f} seconds")
    print(f"Files loaded: {len(file_lookup_2)}")
    print(f"Speedup: {first_call_time / second_call_time:.2f}x faster!")
    print()
    
    # =============================
    # TEST 3: Third call (with cache)
    # =============================
    print("TEST 3: Third call (with cache)")
    print("-" * 100)
    
    start_time = time.time()
    
    # Third call - should use cache
    file_lookup_3 = load_drive_files_real(request, use_cache=True)
    
    third_call_time = time.time() - start_time
    
    print(f"\nTime taken: {third_call_time:.2f} seconds")
    print(f"Files loaded: {len(file_lookup_3)}")
    print()
    
    # =============================
    # TEST 4: Call without cache
    # =============================
    print("TEST 4: Call without cache (force reload)")
    print("-" * 100)
    
    start_time = time.time()
    
    # Call without cache
    file_lookup_4 = load_drive_files_real(request, use_cache=False)
    
    no_cache_time = time.time() - start_time
    
    print(f"\nTime taken: {no_cache_time:.2f} seconds")
    print(f"Files loaded: {len(file_lookup_4)}")
    print()
    
    # =============================
    # SUMMARY
    # =============================
    print("=" * 100)
    print(" " * 40 + "RESULTS SUMMARY")
    print("=" * 100)
    print()
    print("First call (no cache):          {:.2f} seconds".format(first_call_time))
    print("Second call (with cache):        {:.2f} seconds".format(second_call_time))
    print("Third call (with cache):         {:.2f} seconds".format(third_call_time))
    print("Fourth call (no cache, forced):  {:.2f} seconds".format(no_cache_time))
    print()
    print("=" * 100)
    print()
    print("OPTIMIZATION SUMMARY:")
    print("-" * 100)
    print("Caching is ENABLED by default!")
    print()
    print("Benefits:")
    print("  1. First call loads all files from Google Drive and caches them")
    print("  2. Subsequent calls use cached data (instant retrieval)")
    print("  3. Cache lasts for 60 minutes (3600 seconds)")
    print("  4. Can be cleared by calling with use_cache=False")
    print()
    print(f"Performance improvement: {first_call_time / second_call_time:.1f}x faster with cache")
    print()
    print("=" * 100)

if __name__ == "__main__":
    try:
        test_caching_speedup()
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        import traceback
        traceback.print_exc()

