#!/usr/bin/env python3
"""Fix template syntax errors in search.html"""

# Read the file
with open('templates/search.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spacing around == operators
content = content.replace('filters.make==make_id', 'filters.make == make_id')
content = content.replace('filters.model==model_id', 'filters.model == model_id')
content = content.replace('filters.governorate==code', 'filters.governorate == code')

# Write back
with open('templates/search.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all template syntax errors in search.html")
