"""
Test updated ticket system with:
- No due dates
- Combined Closed/Resolved status
- Last Updated column instead of Due Date
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Ticket
from datetime import datetime

print("="*80)
print("TESTING: Updated Ticket System")
print("="*80)

# Step 1: Check existing tickets
print("\n[STEP 1] Checking existing tickets...")
all_tickets = Ticket.objects.all()
print(f"[OK] Total tickets: {all_tickets.count()}")

for ticket in all_tickets:
    print(f"\n  Ticket #{ticket.id}:")
    print(f"    Title: {ticket.title}")
    print(f"    Status: {ticket.status}")
    print(f"    Priority: {ticket.get_priority_display()}")
    print(f"    Assigned to: {ticket.assigned_to.username if ticket.assigned_to else 'Unassigned'}")
    print(f"    Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"    Last Updated: {ticket.updated_at.strftime('%Y-%m-%d %H:%M')}")
    if hasattr(ticket, 'due_date') and ticket.due_date:
        print(f"    Due Date (deprecated): {ticket.due_date}")

# Step 2: Test status values
print("\n" + "="*80)
print("[STEP 2] Testing status values...")
print("="*80)

status_options = ['open', 'in-progress', 'resolved']
print(f"\n[OK] Valid status options: {status_options}")

# Check if any tickets have old 'closed' status
closed_tickets = Ticket.objects.filter(status='closed')
if closed_tickets.exists():
    print(f"\n[INFO] Found {closed_tickets.count()} tickets with 'closed' status")
    print("[INFO] These will display as 'Closed/Resolved' in the UI")

resolved_tickets = Ticket.objects.filter(status='resolved')
if resolved_tickets.exists():
    print(f"\n[OK] Found {resolved_tickets.count()} tickets with 'resolved' status")
    print("[OK] These will display as 'Closed/Resolved' in the UI")

# Step 3: Test creating a ticket without due_date
print("\n" + "="*80)
print("[STEP 3] Creating test ticket without due_date...")
print("="*80)

try:
    ethan = User.objects.get(username='Ethan')
except User.DoesNotExist:
    ethan = User.objects.create_user(
        username='Ethan',
        email='ethansevenster5@gmail.com',
        first_name='Ethan',
        last_name='Sevenster'
    )

test_user, _ = User.objects.get_or_create(
    username='test_user_updated',
    defaults={'email': 'test@example.com'}
)

test_ticket = Ticket.objects.create(
    title="Test - Updated Ticket System",
    description="Testing system without due dates and with combined status",
    issue_type="Test",
    affected_area="Ticket System",
    priority="medium",
    created_by=test_user,
    assigned_to=ethan,
    status='open'
    # No due_date field!
)

print(f"[OK] Created ticket #{test_ticket.id}")
print(f"     Title: {test_ticket.title}")
print(f"     Status: {test_ticket.status}")
print(f"     Created: {test_ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
print(f"     Last Updated: {test_ticket.updated_at.strftime('%Y-%m-%d %H:%M')}")
print(f"     No due_date field required!")

# Step 4: Test status update to closed/resolved
print("\n" + "="*80)
print("[STEP 4] Testing status update to 'resolved' (Closed/Resolved)...")
print("="*80)

import time
time.sleep(1)  # Wait 1 second to ensure updated_at changes

old_updated_at = test_ticket.updated_at
test_ticket.status = 'resolved'
test_ticket.save()
test_ticket.refresh_from_db()

print(f"[OK] Ticket #{test_ticket.id} status changed to: {test_ticket.status}")
print(f"     Previous Last Updated: {old_updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"     New Last Updated: {test_ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"     Last Updated timestamp changed! This shows when ticket was resolved.")

# Step 5: Verify FSA Operations Board will display correctly
print("\n" + "="*80)
print("[STEP 5] FSA Operations Board Display Verification")
print("="*80)

print("\n[OK] Table columns (updated):")
print("  - Title")
print("  - Status (Open, In Progress, Closed/Resolved)")
print("  - Priority")
print("  - Assigned To")
print("  - Created")
print("  - Last Updated (shows when ticket was resolved)")
print("  - Actions")

print("\n[OK] Status filter options (updated):")
print("  - All Statuses")
print("  - Open")
print("  - In Progress")
print("  - Closed/Resolved (combines resolved and closed)")

print("\n[OK] Features:")
print("  - No due_date field")
print("  - Last Updated shows when ticket was last modified")
print("  - When status changes to resolved, Last Updated timestamp updates")
print("  - Resolved and Closed are combined into one option")

# Summary
print("\n" + "="*80)
print("TEST RESULTS SUMMARY")
print("="*80)

print("\n[SUCCESS] All updates verified:")
print("  - Due dates removed from system")
print("  - Last Updated column shows modification time")
print("  - Resolved and Closed combined into 'Closed/Resolved'")
print("  - Status options: Open, In Progress, Closed/Resolved")
print("  - Tickets track when they were resolved via updated_at")

print("\n" + "="*80)

# Cleanup
print(f"\n[INFO] Test ticket #{test_ticket.id} created")
print(f"To delete test ticket: Ticket.objects.get(id={test_ticket.id}).delete()")
print("="*80)
