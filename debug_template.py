#!/usr/bin/env python
"""
Debug script to test the template logic directly
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.template import Template, Context

def test_template_logic():
    """Test the template logic directly"""
    print("=" * 60)
    print("TESTING TEMPLATE LOGIC DIRECTLY")
    print("=" * 60)
    
    # Get a few test inspections
    test_ids = [8905, 8904, 8896, 8897]
    
    for inspection_id in test_ids:
        try:
            inspection = FoodSafetyAgencyInspection.objects.get(remote_id=inspection_id)
            
            print(f"\nInspection ID: {inspection_id}")
            print(f"Client: {inspection.client_name}")
            print(f"is_direction_present_for_this_inspection: {inspection.is_direction_present_for_this_inspection}")
            
            # Test the exact template logic
            template_code = """
            {% if product.is_direction_present_for_this_inspection %}
                <span class="compliance-status non-compliant" title="Non-Compliant (Direction Present)">Non-Compliant</span>
            {% else %}
                <span class="compliance-status compliant" title="Compliant (No Direction)">Compliant</span>
            {% endif %}
            """
            
            template = Template(template_code)
            context = Context({'product': inspection})
            result = template.render(context)
            
            print(f"Template result: {result.strip()}")
            
            # Check if the field exists and what type it is
            if hasattr(inspection, 'is_direction_present_for_this_inspection'):
                field_value = getattr(inspection, 'is_direction_present_for_this_inspection')
                print(f"Field exists: Yes, Value: {field_value}, Type: {type(field_value)}")
            else:
                print("Field does not exist!")
                
        except FoodSafetyAgencyInspection.DoesNotExist:
            print(f"Inspection {inspection_id} not found")
        except Exception as e:
            print(f"Error with inspection {inspection_id}: {e}")

if __name__ == "__main__":
    test_template_logic()
