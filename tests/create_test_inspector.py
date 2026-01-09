import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

# Create test inspector account
username = 'test_inspector'
password = 'inspector123'
email = 'inspector@test.com'

# Check if user already exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"User '{username}' already exists. Updating password and role...")
    user.set_password(password)
    user.role = 'inspector'
    user.email = email
    user.is_staff = False
    user.is_superuser = False
    user.save()
    print(f"[SUCCESS] Updated existing user: {username}")
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.role = 'inspector'
    user.is_staff = False
    user.is_superuser = False
    user.first_name = 'Test'
    user.last_name = 'Inspector'
    user.save()
    print(f"[SUCCESS] Created new test inspector account")

print("\n" + "="*50)
print("TEST INSPECTOR ACCOUNT CREATED")
print("="*50)
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Email:    {email}")
print(f"Role:     inspector")
print("="*50)
print("You can now login with these credentials.")
print("="*50)
