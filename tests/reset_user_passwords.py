import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def reset_user_password(old_username, new_username, new_password):
    """Reset a user's password, capitalize username, and make them superadmin"""
    try:
        user = User.objects.get(username=old_username)
        user.username = new_username
        user.set_password(new_password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'super_admin'  # Set application role to super_admin
        user.save()
        return True, user
    except User.DoesNotExist:
        return False, None

# Define new complex passwords
armand_password = "Arm@nd#2024$SuperP@ss!"
louis_password = "L0u!s#V1s@g1e$2024&Admin"

print("=" * 60)
print("USER PASSWORD RESET UTILITY")
print("=" * 60)

# Reset Armand's password (username already Armand from previous run)
success, user = reset_user_password('Armand', 'Armand', armand_password)
if success:
    print(f"\n[SUCCESS] ARMAND - Username Capitalized, Password Reset & Promoted to Superadmin")
    print(f"  Old Username: armand -> New Username: Armand")
    print(f"  Password: {armand_password}")
    print(f"  Email: {user.email if user.email else '(not set)'}")
    print(f"  Staff: {user.is_staff}")
    print(f"  Superuser: {user.is_superuser}")
    print(f"  Application Role: {user.role}")
    print(f"  Active: {user.is_active}")
else:
    print("\n[FAILED] ARMAND - User not found")

# Reset Louis's password (username already capitalized)
success, user = reset_user_password('Louis', 'Louis', louis_password)
if success:
    print(f"\n[SUCCESS] LOUIS - Password Reset & Promoted to Superadmin")
    print(f"  Username: Louis")
    print(f"  Password: {louis_password}")
    print(f"  Email: {user.email if user.email else '(not set)'}")
    print(f"  Staff: {user.is_staff}")
    print(f"  Superuser: {user.is_superuser}")
    print(f"  Application Role: {user.role}")
    print(f"  Active: {user.is_active}")
else:
    print("\n[FAILED] LOUIS - User not found")

print("\n" + "=" * 60)
print("CREDENTIALS SUMMARY")
print("=" * 60)
print("\nArmand:")
print(f"  Username: Armand")
print(f"  Password: {armand_password}")
print("\nLouis:")
print(f"  Username: Louis")
print(f"  Password: {louis_password}")
print("\n" + "=" * 60)
