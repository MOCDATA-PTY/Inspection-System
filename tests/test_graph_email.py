"""
Test script to send an email using Microsoft Graph API
Sends a test email to ethansevenster5@gmail.com
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_test_email():
    """Send a test email using Microsoft Graph API"""

    print("=" * 60)
    print("Testing Microsoft Graph API Email Configuration")
    print("=" * 60)
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Client ID: {settings.GRAPH_CLIENT_ID}")
    print(f"Tenant ID: {settings.GRAPH_TENANT_ID}")
    print("=" * 60)

    # Email details
    subject = "Test Email from Food Safety Agency System"
    message = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #007890;">🎉 Test Email Successful!</h2>

        <p>This is a test email from the <strong>Food Safety Agency Inspection System</strong>.</p>

        <p>The system is now configured to send emails using <strong>Microsoft Graph API</strong> with the following credentials:</p>

        <ul>
            <li><strong>From Email:</strong> info@eclick.co.za</li>
            <li><strong>API:</strong> Microsoft Graph API</li>
            <li><strong>Backend:</strong> GraphEmailBackend</li>
        </ul>

        <hr style="margin: 20px 0; border: 1px solid #ddd;">

        <p style="color: #666; font-size: 0.9em;">
            <strong>System Information:</strong><br>
            Sent from: Food Safety Agency Inspection System<br>
            Date: {date}<br>
            Purpose: Email configuration test
        </p>

        <p style="margin-top: 20px;">
            If you received this email, the email system is working correctly! ✅
        </p>
    </body>
    </html>
    """

    from datetime import datetime
    message = message.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    recipient = "ethansevenster5@gmail.com"

    print(f"\nSending test email to: {recipient}")
    print(f"Subject: {subject}")
    print("\nAttempting to send email...")

    try:
        # Send email
        num_sent = send_mail(
            subject=subject,
            message="This is a test email from Food Safety Agency System",  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=message,
            fail_silently=False,
        )

        if num_sent > 0:
            print("\n" + "=" * 60)
            print("[SUCCESS] Email sent successfully!")
            print("=" * 60)
            print(f"Test email sent to: {recipient}")
            print(f"From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"Subject: {subject}")
            print("\nPlease check the inbox at ethansevenster5@gmail.com")
            print("(Don't forget to check spam/junk folder if not in inbox)")
            print("=" * 60)
            return True
        else:
            print("\n[ERROR] No emails were sent")
            return False

    except Exception as e:
        print("\n" + "=" * 60)
        print("[ERROR] Failed to send email")
        print("=" * 60)
        print(f"Error message: {str(e)}")
        print("\nPossible issues:")
        print("1. Check that the Microsoft Graph API credentials are correct")
        print("2. Verify that the app has 'Mail.Send' permissions in Azure")
        print("3. Ensure the service principal has access to send emails")
        print("4. Check your internet connection")
        print("=" * 60)
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    send_test_email()
