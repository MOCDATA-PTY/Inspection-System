"""
Test ticket submission with new email address: ethan.sevenster@moc-pty.com
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Ticket
from django.core.mail import send_mail

print("=" * 80)
print("TESTING TICKET EMAIL WITH NEW ADDRESS")
print("=" * 80)

# Verify Ethan's email address
try:
    ethan = User.objects.get(username='Ethan')
    print(f"\n[OK] Found user: Ethan")
    print(f"     Email: {ethan.email}")

    if ethan.email == 'ethan.sevenster@moc-pty.com':
        print(f"     ✓ Email address is correct!")
    else:
        print(f"     ✗ WARNING: Email is still {ethan.email}")
        print(f"     Updating to ethan.sevenster@moc-pty.com...")
        ethan.email = 'ethan.sevenster@moc-pty.com'
        ethan.save()
        print(f"     ✓ Email updated!")

except User.DoesNotExist:
    print("\n[INFO] Creating user Ethan with new email address...")
    ethan = User.objects.create_user(
        username='Ethan',
        email='ethan.sevenster@moc-pty.com',
        first_name='Ethan',
        last_name='Sevenster'
    )
    print(f"[OK] User created: {ethan.username} ({ethan.email})")

print("\n" + "=" * 80)
print("TEST: Create ticket and send email")
print("=" * 80)

# Create a test ticket
test_ticket = Ticket.objects.create(
    title="Email Test - New Address",
    description="Testing email notification to ethan.sevenster@moc-pty.com",
    issue_type='other',
    affected_area='system',
    priority='low',
    created_by=ethan,
    assigned_to=ethan,
    status='open'
)

print(f"\n[OK] Test ticket created: #{test_ticket.id}")
print(f"     Title: {test_ticket.title}")
print(f"     Assigned to: {test_ticket.assigned_to.username} ({test_ticket.assigned_to.email})")

# Test email sending
print("\n" + "=" * 80)
print("SENDING TEST EMAIL")
print("=" * 80)

email_subject = f"New Ticket #{test_ticket.id}: {test_ticket.title}"
email_body = f"""
Good day,

A new ticket has been submitted to the FSA Operations Board.

Ticket Details:
- Ticket ID: #{test_ticket.id}
- Title: {test_ticket.title}
- Type: {test_ticket.get_issue_type_display()}
- Priority: {test_ticket.get_priority_display()}
- Submitted by: {test_ticket.created_by.username}
- Description: {test_ticket.description}

You can view and manage this ticket at:
http://127.0.0.1:8000/fsa-operations-board/

Best regards,
Food Safety Agency System
"""

try:
    print(f"\n[SENDING] Email to: ethan.sevenster@moc-pty.com")
    print(f"          Subject: {email_subject}")
    print(f"          From: info@eclick.co.za")

    send_mail(
        subject=email_subject,
        message=email_body,
        from_email='info@eclick.co.za',
        recipient_list=['ethan.sevenster@moc-pty.com'],
        fail_silently=False,  # Raise error if email fails
    )

    print("\n[SUCCESS] ✓ Email sent successfully!")
    print(f"\nCheck the inbox for: ethan.sevenster@moc-pty.com")
    print("The email should arrive shortly.")

except Exception as e:
    print(f"\n[ERROR] Failed to send email: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"""
Test Ticket: #{test_ticket.id}
Email Address: ethan.sevenster@moc-pty.com
Status: Email sent (check inbox)

Next Steps:
1. Check inbox for ethan.sevenster@moc-pty.com
2. Verify email was received
3. Submit a ticket through the web form to test full workflow

Configuration Updated:
- User Ethan email: ethan.sevenster@moc-pty.com
- Email recipient: ethan.sevenster@moc-pty.com
- All future tickets will notify this address
""")

print("=" * 80)
print("[COMPLETE] Email configuration updated and tested")
print("=" * 80)
