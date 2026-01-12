#!/usr/bin/env python3
"""Fix broken template tags split across lines in search.html"""
import re

# Read the file
with open('templates/search.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix template tags split across lines by joining them
# Pattern: {{ something \n more_stuff }}
content = re.sub(r'{{\s*\n\s*', '{{ ', content)
content = re.sub(r'\s*\n\s*}}', ' }}', content)

# Fix template tags like: {% if something \n %}stuff{% endif %}
content = re.sub(r'{%\s*\n\s*', '{% ', content)
content = re.sub(r'\s*\n\s*%}', ' %}', content)

# Write back
with open('templates/search.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all split template tags in search.html")
