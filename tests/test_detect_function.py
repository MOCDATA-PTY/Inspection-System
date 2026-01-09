import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import detect_corporate_group

test_names = [
    "Pick 'n Pay - Kroonstad",
    "Boxer Superstore Protea Glen",
    "Shoprite Kenako Mall",
    "Checkers Northmead Square",
    "Food Lover's Market Comaro Crossing",
    "Spar Newtown"
]

print("Testing detect_corporate_group function:")
print("=" * 60)

for name in test_names:
    result = detect_corporate_group(name)
    print(f"{name[:40]:<40} -> {result}")

print("=" * 60)
