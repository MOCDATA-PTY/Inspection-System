"""
Test script for password reset functionality
Tests sending password reset email to ethansevenster5@gmail.com
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime

def test_password_reset():
    """Test password reset email for developer account"""

    print("=" * 60)
    print("Testing Password Reset Functionality")
    print("=" * 60)

    # Target email (developer account only)
    target_email = 'ethansevenster5@gmail.com'
    print(f"\nTarget Email: {target_email}")

    # Find user with this email
    try:
        user = User.objects.filter(email__iexact=target_email).first()

        if not user:
            print(f"\n[ERROR] No user found with email: {target_email}")
            print("\nCreating test user...")
            # Create a test user if doesn't exist
            user = User.objects.create_user(
                username='ethan_dev',
                email=target_email,
                password='test123'
            )
            print(f"[SUCCESS] Created test user: {user.username}")

        print(f"\nUser Found: {user.username} ({user.email})")

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        print(f"\nGenerated Token: {token}")
        print(f"Generated UID: {uid}")

        # Build reset link (for local development)
        reset_link = f"http://localhost:8000/reset-password/{uid}/{token}/"
        print(f"\nReset Link: {reset_link}")

        # Prepare email context
        context = {
            'user': user,
            'reset_link': reset_link,
            'current_year': datetime.now().year,
        }

        # Render email template
        html_message = render_to_string('main/password_reset_email.html', context)

        print("\n" + "=" * 60)
        print("Sending Password Reset Email...")
        print("=" * 60)

        # Send email
        send_mail(
            subject='Password Reset Request - Food Safety Agency',
            message=f'Hello {user.username},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 1 hour.\n\nIf you did not request this, please ignore this email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            html_message=html_message,
            fail_silently=False,
        )

        print("\n[SUCCESS] Password reset email sent successfully!")
        print("=" * 60)
        print(f"Email sent to: {target_email}")
        print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"Reset Link: {reset_link}")
        print("\nPlease check your email at ethansevenster5@gmail.com")
        print("(Don't forget to check spam/junk folder)")
        print("=" * 60)

        print("\n[INFO] To test the password reset:")
        print("1. Check your email for the password reset link")
        print("2. Click the link (or copy and paste it into your browser)")
        print("3. Enter a new password")
        print("4. Try logging in with the new password")
        print("\n" + "=" * 60)

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("[ERROR] Failed to send password reset email")
        print("=" * 60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_password_reset()
