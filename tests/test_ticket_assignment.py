"""
Test script to verify all tickets are assigned to Ethan
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Ticket

print("="*80)
print("TESTING: Ticket Assignment to Ethan")
print("="*80)

try:
    # Find user Ethan
    try:
        ethan = User.objects.get(username='Ethan')
        print(f"\n[OK] Found user: {ethan.username}")
        print(f"     Email: {ethan.email}")
        print(f"     Full name: {ethan.first_name} {ethan.last_name}")
    except User.DoesNotExist:
        print("\n[ERROR] User 'Ethan' not found!")
        print("[FAIL] Test failed - user doesn't exist")
        exit(1)

    # Test 1: Check total tickets
    print(f"\n" + "="*80)
    print("TEST 1: Total Tickets Count")
    print("="*80)

    total_tickets = Ticket.objects.count()
    print(f"\n  Total tickets in system: {total_tickets}")

    if total_tickets == 0:
        print("\n[INFO] No tickets found in the system")
        print("[PASS] Test completed (no tickets to verify)")
        exit(0)

    # Test 2: Check tickets assigned to Ethan
    print(f"\n" + "="*80)
    print("TEST 2: Tickets Assigned to Ethan")
    print("="*80)

    ethan_tickets = Ticket.objects.filter(assigned_to=ethan).count()
    print(f"\n  Tickets assigned to Ethan: {ethan_tickets}")
    print(f"  Total tickets: {total_tickets}")

    if ethan_tickets == total_tickets:
        print(f"\n  [PASS] All {total_tickets} tickets are assigned to Ethan!")
    else:
        unassigned = total_tickets - ethan_tickets
        print(f"\n  [FAIL] {unassigned} tickets are NOT assigned to Ethan")

        # Show tickets not assigned to Ethan
        other_tickets = Ticket.objects.exclude(assigned_to=ethan)[:5]
        if other_tickets:
            print(f"\n  Sample of unassigned tickets:")
            for ticket in other_tickets:
                assigned_to = ticket.assigned_to.username if ticket.assigned_to else "Unassigned"
                print(f"    - #{ticket.id}: {ticket.title} (assigned to: {assigned_to})")

    # Test 3: Breakdown by status
    print(f"\n" + "="*80)
    print("TEST 3: Ethan's Tickets by Status")
    print("="*80)

    open_count = Ticket.objects.filter(assigned_to=ethan, status='open').count()
    in_progress_count = Ticket.objects.filter(assigned_to=ethan, status='in-progress').count()
    resolved_count = Ticket.objects.filter(assigned_to=ethan, status='resolved').count()
    closed_count = Ticket.objects.filter(assigned_to=ethan, status='closed').count()

    print(f"\n  Open:        {open_count}")
    print(f"  In Progress: {in_progress_count}")
    print(f"  Resolved:    {resolved_count}")
    print(f"  Closed:      {closed_count}")
    print(f"  -----------")
    print(f"  Total:       {open_count + in_progress_count + resolved_count + closed_count}")

    # Test 4: Breakdown by priority
    print(f"\n" + "="*80)
    print("TEST 4: Ethan's Tickets by Priority")
    print("="*80)

    low_count = Ticket.objects.filter(assigned_to=ethan, priority='low').count()
    medium_count = Ticket.objects.filter(assigned_to=ethan, priority='medium').count()
    high_count = Ticket.objects.filter(assigned_to=ethan, priority='high').count()
    urgent_count = Ticket.objects.filter(assigned_to=ethan, priority='urgent').count()

    print(f"\n  Low:    {low_count}")
    print(f"  Medium: {medium_count}")
    print(f"  High:   {high_count}")
    print(f"  Urgent: {urgent_count}")
    print(f"  -----------")
    print(f"  Total:  {low_count + medium_count + high_count + urgent_count}")

    # Test 5: Show sample of Ethan's tickets
    print(f"\n" + "="*80)
    print("TEST 5: Sample of Ethan's Tickets")
    print("="*80)

    sample_tickets = Ticket.objects.filter(assigned_to=ethan).order_by('-priority', '-created_at')[:5]

    if sample_tickets:
        print(f"\n  Showing first 5 tickets (ordered by priority):\n")
        for i, ticket in enumerate(sample_tickets, 1):
            print(f"  {i}. #{ticket.id} - {ticket.title}")
            print(f"     Status: {ticket.get_status_display()}")
            print(f"     Priority: {ticket.get_priority_display()}")
            print(f"     Issue Type: {ticket.issue_type or 'N/A'}")
            print(f"     Affected Area: {ticket.affected_area or 'N/A'}")
            print(f"     Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()
    else:
        print("\n  No tickets found for Ethan")

    # Final verdict
    print("="*80)
    print("TEST RESULTS")
    print("="*80)

    all_assigned = (ethan_tickets == total_tickets)

    if all_assigned:
        print(f"\n  [SUCCESS] All tests passed!")
        print(f"  All {total_tickets} tickets are correctly assigned to Ethan")
        print(f"  Email: ethansevenster5@gmail.com")
    else:
        print(f"\n  [FAILURE] Some tests failed!")
        print(f"  {ethan_tickets}/{total_tickets} tickets are assigned to Ethan")
        print(f"  {total_tickets - ethan_tickets} tickets need to be reassigned")

    print("\n" + "="*80)

except Exception as e:
    print(f"\n[ERROR] Test failed with exception: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
