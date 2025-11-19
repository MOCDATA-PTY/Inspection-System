import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Fix developer user
user = User.objects.get(username='developer')
user.role = 'developer'
user.is_superuser = True
user.is_staff = True
user.save()

print(f"Updated developer user: role={user.role}, superuser={user.is_superuser}, staff={user.is_staff}")
