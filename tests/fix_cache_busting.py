"""
Fix cache busting parameter placement - move it outside static tag
"""
import os
import re
from pathlib import Path

template_dir = Path('main/templates/main')
count = 0

for html_file in template_dir.glob('*.html'):
    content = html_file.read_text(encoding='utf-8')

    # Fix the cache busting - move ?v=2 outside the static tag
    # Pattern: {% static 'img/food_safety_background.jpg' %}
    # Replace with: {% static 'img/food_safety_background.jpg' %}?v=2

    new_content = re.sub(
        r"{% static ['\"]img/food_safety_background\.jpg['\"] %}",
        r"{% static 'img/food_safety_background.jpg' %}?v=2",
        content
    )

    if new_content != content:
        html_file.write_text(new_content, encoding='utf-8')
        count += 1
        print(f'Fixed: {html_file.name}')

print(f'\nTotal files fixed: {count}')
