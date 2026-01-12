#!/usr/bin/env python3
"""Fix broken template tags in compare.html and home.html"""
import re

for filename in ['templates/compare.html', 'templates/home.html']:
    try:
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix template tags split across lines
        content = re.sub(r'{{\s*\n\s*', '{{ ', content)
        content = re.sub(r'\s*\n\s*}}', ' }}', content)
        content = re.sub(r'{%\s*\n\s*', '{% ', content)
        content = re.sub(r'\s*\n\s*%}', ' %}', content)
        
        # Write back
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {filename}")
    except Exception as e:
        print(f"Error fixing {filename}: {e}")
