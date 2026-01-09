"""
Test script to send an email using Django's email configuration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("="*80)
print("TESTING EMAIL SENDING")
print("="*80)
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
print(f"Email Host User: {settings.EMAIL_HOST_USER}")
print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
print("="*80)

# Check if password is set
if not settings.EMAIL_HOST_PASSWORD:
    print("\n⚠️  ERROR: EMAIL_HOST_PASSWORD is not set!")
    print("Please set the EMAIL_HOST_PASSWORD environment variable or update settings.py")
    print("\nExample:")
    print("  export EMAIL_HOST_PASSWORD='your_password_here'")
    print("  OR")
    print("  set EMAIL_HOST_PASSWORD=your_password_here  (Windows)")
    exit(1)

# Test email details
to_email = 'ethansevenster5@gmail.com'
subject = 'Test Email from Food Safety Agency System'
message = '''Hello,

This is a test email from the Food Safety Agency Inspection System.

If you receive this email, it means the email configuration is working correctly!

Best regards,
Food Safety Agency Team
'''

html_message = '''
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #007890;">Test Email</h2>
            <p>Hello,</p>
            <p>This is a test email from the <strong>Food Safety Agency Inspection System</strong>.</p>
            <p>If you receive this email, it means the email configuration is working correctly! ✅</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 0.85em; color: #999;">Best regards,<br>Food Safety Agency Team</p>
        </div>
    </body>
</html>
'''

print(f"\nSending test email to: {to_email}")
print("Please wait...")

try:
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
        html_message=html_message
    )
    print("\n✅ SUCCESS! Email sent successfully!")
    print(f"Email sent from: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Email sent to: {to_email}")
except Exception as e:
    print(f"\n❌ ERROR: Failed to send email")
    print(f"Error details: {str(e)}")
    print("\nCommon issues:")
    print("  1. Email password is incorrect")
    print("  2. 'Less secure app access' needs to be enabled (for Gmail)")
    print("  3. Two-factor authentication requires an app-specific password")
    print("  4. SMTP server/port is incorrect")
    print("  5. Firewall is blocking the connection")

print("\n" + "="*80)
print("Done!")
