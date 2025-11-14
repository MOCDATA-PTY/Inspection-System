import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print('ALL USERS AND ROLES:')
for user in User.objects.all().order_by('username'):
    print(f"{user.id}\t{user.username}\t{getattr(user, 'role', None)}")

print('\nCINGA:')
cinga = User.objects.filter(username__iexact='Cinga').first()
if cinga:
    print(f"id={cinga.id}, username={cinga.username}, role={getattr(cinga, 'role', None)}")
else:
    print('No user named Cinga')


