#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client

def test_compliance_column():
    client = Client()
    success = client.login(username='developer', password='XHnj1C#QkFs9')
    
    if not success:
        print("Login failed")
        return False
    
    response = client.get('/inspections/')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for the new column header
        if 'Compliant/Non-Compliant' in content:
            print("SUCCESS: New compliance column header found!")
        else:
            print("FAILED: Compliance column header not found")
            return False
        
        # Check for compliance status text
        compliant_count = content.count('Compliant')
        non_compliant_count = content.count('Non-Compliant')
        
        print(f"Compliance status found:")
        print(f"  Compliant: {compliant_count}")
        print(f"  Non-Compliant: {non_compliant_count}")
        
        if compliant_count > 0 or non_compliant_count > 0:
            print("SUCCESS: Compliance status indicators found!")
            return True
        else:
            print("No compliance status indicators found")
            return False
    else:
        print("Failed to load page")
        return False

if __name__ == "__main__":
    test_compliance_column()
