"""
Update Ethan's email address and test ticket notification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Ticket
from django.core.mail import send_mail

print("=" * 80)
print("UPDATING ETHAN'S EMAIL ADDRESS")
print("=" * 80)

# Get Ethan user
try:
    ethan = User.objects.get(username='Ethan')
    print(f"\n[FOUND] User: Ethan")
    print(f"  Current email: {ethan.email}")

    # Update email
    ethan.email = 'ethan.sevenster@moc-pty.com'
    ethan.save()

    print(f"  Updated email: {ethan.email}")
    print("[OK] Email address updated successfully!")

except User.DoesNotExist:
    print("\n[CREATING] User Ethan doesn't exist, creating...")
    ethan = User.objects.create_user(
        username='Ethan',
        email='ethan.sevenster@moc-pty.com',
        first_name='Ethan',
        last_name='Sevenster'
    )
    print(f"[OK] User created: {ethan.username} ({ethan.email})")

print("\n" + "=" * 80)
print("CREATING TEST TICKET")
print("=" * 80)

# Create test ticket
test_ticket = Ticket.objects.create(
    title="Test Email to New Address",
    description="Testing email notification to ethan.sevenster@moc-pty.com",
    issue_type='other',
    affected_area='system',
    priority='low',
    created_by=ethan,
    assigned_to=ethan,
    status='open'
)

print(f"\n[OK] Test ticket created:")
print(f"  Ticket ID: #{test_ticket.id}")
print(f"  Title: {test_ticket.title}")
print(f"  Assigned to: {test_ticket.assigned_to.email}")

print("\n" + "=" * 80)
print("SENDING EMAIL NOTIFICATION")
print("=" * 80)

email_subject = f"New Ticket #{test_ticket.id}: {test_ticket.title}"
email_body = f"""Good day,

A new ticket has been submitted to the FSA Operations Board.

Ticket Details:
- Ticket ID: #{test_ticket.id}
- Title: {test_ticket.title}
- Type: {test_ticket.issue_type}
- Priority: {test_ticket.priority}
- Description: {test_ticket.description}

View ticket at: http://127.0.0.1:8000/fsa-operations-board/

Best regards,
Food Safety Agency System
"""

try:
    print(f"\nSending email...")
    print(f"  To: ethan.sevenster@moc-pty.com")
    print(f"  From: info@eclick.co.za")
    print(f"  Subject: {email_subject}")

    send_mail(
        subject=email_subject,
        message=email_body,
        from_email='info@eclick.co.za',
        recipient_list=['ethan.sevenster@moc-pty.com'],
        fail_silently=False,
    )

    print("\n[SUCCESS] Email sent successfully!")
    print("\nCheck inbox: ethan.sevenster@moc-pty.com")

except Exception as e:
    print(f"\n[ERROR] Email failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("CONFIGURATION SUMMARY")
print("=" * 80)

print(f"""
User Email Updated:
  Username: Ethan
  Email: ethan.sevenster@moc-pty.com

Email Recipients:
  Ticket notifications: ethan.sevenster@moc-pty.com

Test Ticket: #{test_ticket.id}

Next Steps:
1. Check inbox for ethan.sevenster@moc-pty.com
2. Submit a ticket via web form to test live
3. Verify email arrives at new address

All future ticket submissions will notify: ethan.sevenster@moc-pty.com
""")

print("=" * 80)
print("[COMPLETE]")
print("=" * 80)
