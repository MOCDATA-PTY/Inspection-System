#!/usr/bin/env python3
"""
Clean up the incorrectly created inspector users
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def clean_inspector_users():
    """Delete the incorrectly created inspector users"""
    print("🧹 Cleaning up incorrectly created inspector users")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # List of usernames to delete
    usernames_to_delete = [
        'benvisagie', 'gladysmanganye', 'thatosekhotho', 'percymaleka',
        'cingangongo', 'sandisiwedlisani', 'xolampeluza', 'kutlwanokuntwane',
        'nelisantoyaphi', 'jofredsteyn', 'neonoe', 'lwandilemaqina', 'mokgadiselone'
    ]
    
    deleted_count = 0
    not_found_count = 0
    
    for username in usernames_to_delete:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ Deleted user: {username}")
            deleted_count += 1
        except User.DoesNotExist:
            print(f"⚠️  User not found: {username}")
            not_found_count += 1
    
    print("\n" + "=" * 60)
    print("📈 CLEANUP SUMMARY")
    print("=" * 60)
    print(f"✅ Deleted: {deleted_count} users")
    print(f"⚠️  Not found: {not_found_count} users")
    print(f"📊 Total processed: {len(usernames_to_delete)}")
    
    # Show remaining users
    print(f"\n👥 REMAINING USERS:")
    print("-" * 30)
    remaining_users = User.objects.all().order_by('username')
    for user in remaining_users:
        print(f"• {user.username} ({user.role})")

if __name__ == "__main__":
    try:
        clean_inspector_users()
        print("\n🎉 Cleanup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
