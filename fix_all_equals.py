#!/usr/bin/env python3
"""Comprehensively fix all template syntax errors in search.html"""
import re

# Read the file
with open('templates/search.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all instances of == without spaces using regex
# This will match things like filters.X==Y or filters.X=="Y" and add proper spacing
content = re.sub(r'(\w+)==(\w+|\".+?\")', r'\1 == \2', content)

# Write back
with open('templates/search.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed ALL == operators in search.html")
