"""
Assign all tickets to user Ethan and send email notifications
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.mail import send_mail
from main.models import Ticket

print("="*80)
print("ASSIGNING ALL TICKETS TO ETHAN")
print("="*80)

try:
    # Find user Ethan
    try:
        ethan = User.objects.get(username='Ethan')
        print(f"\n[OK] Found user: {ethan.username}")
        print(f"     Email: ethansevenster5@gmail.com")
    except User.DoesNotExist:
        print("\n[ERROR] User 'Ethan' not found. Creating user...")
        ethan = User.objects.create_user(
            username='Ethan',
            email='ethansevenster5@gmail.com',
            first_name='Ethan',
            last_name='Sevenster'
        )
        print(f"[OK] Created user: {ethan.username}")

    # Get all tickets
    all_tickets = Ticket.objects.all()
    total_tickets = all_tickets.count()

    print(f"\n[INFO] Found {total_tickets} total tickets")

    if total_tickets == 0:
        print("\n[INFO] No tickets to assign. Exiting.")
        exit()

    # Count tickets not assigned to Ethan
    unassigned_tickets = all_tickets.exclude(assigned_to=ethan)
    unassigned_count = unassigned_tickets.count()

    print(f"[INFO] {unassigned_count} tickets need to be assigned to Ethan")

    # Assign all tickets to Ethan
    updated_count = unassigned_tickets.update(assigned_to=ethan)

    print(f"\n[OK] Assigned {updated_count} tickets to {ethan.username}")

    # Prepare email content
    print(f"\n" + "="*80)
    print("SENDING EMAIL NOTIFICATION")
    print("="*80)

    # Get ticket summary by status
    open_tickets = Ticket.objects.filter(assigned_to=ethan, status='open').count()
    in_progress_tickets = Ticket.objects.filter(assigned_to=ethan, status='in-progress').count()
    resolved_tickets = Ticket.objects.filter(assigned_to=ethan, status='resolved').count()
    closed_tickets = Ticket.objects.filter(assigned_to=ethan, status='closed').count()

    # Get high priority tickets
    high_priority_tickets = Ticket.objects.filter(
        assigned_to=ethan,
        priority__in=['high', 'urgent']
    ).order_by('-priority', '-created_at')

    # Build email content
    email_subject = "Food Safety Agency - Ticket Assignment Update"

    email_body = f"""Good day Ethan,

This is an automated notification regarding your assigned tickets in the Food Safety Agency Inspection System.

TICKET SUMMARY
{"="*60}

Total Tickets Assigned to You: {total_tickets}

Status Breakdown:
  - Open:        {open_tickets}
  - In Progress: {in_progress_tickets}
  - Resolved:    {resolved_tickets}
  - Closed:      {closed_tickets}

"""

    if high_priority_tickets.exists():
        email_body += f"""HIGH PRIORITY TICKETS ({high_priority_tickets.count()})
{"="*60}

"""
        for i, ticket in enumerate(high_priority_tickets[:10], 1):
            email_body += f"""{i}. #{ticket.id} - {ticket.title}
   Priority: {ticket.get_priority_display()}
   Status: {ticket.get_status_display()}
   Issue Type: {ticket.issue_type or 'N/A'}
   Affected Area: {ticket.affected_area or 'N/A'}
   Description: {ticket.description[:100]}{'...' if len(ticket.description) > 100 else ''}

"""

    email_body += f"""
{"="*60}

Please review your assigned tickets in the FSA Operations Board.

Best regards,
Food Safety Agency System
"""

    print(f"\nEmail Details:")
    print(f"  To: ethansevenster5@gmail.com")
    print(f"  Subject: {email_subject}")
    print(f"  Body length: {len(email_body)} characters")

    # Send email
    try:
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email='info@eclick.co.za',
            recipient_list=['ethansevenster5@gmail.com'],
            fail_silently=False,
        )
        print(f"\n[OK] Email sent successfully to ethansevenster5@gmail.com")
    except Exception as email_error:
        print(f"\n[WARNING] Failed to send email: {email_error}")
        print(f"[INFO] Tickets were still assigned successfully")

    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n  Total tickets: {total_tickets}")
    print(f"  Assigned to Ethan: {total_tickets}")
    print(f"  Updated in this run: {updated_count}")
    print(f"  Email sent to: ethansevenster5@gmail.com")

    print(f"\n" + "="*80)
    print("[SUCCESS] All tickets assigned to Ethan!")
    print("="*80)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
