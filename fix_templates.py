#!/usr/bin/env python3
"""
Comprehensive Django Template Syntax Fixer - v2
Fixes ALL common syntax issues that break Django templates.
"""

import os
import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

def fix_all_issues(content: str) -> str:
    """Apply all fixes to template content"""
    
    # 1. Fix comparison operators without spaces in {% if %} blocks
    # Match patterns like: filters.something=="value" or var==var2
    # Be careful not to break HTML attributes or JavaScript
    
    # Pattern to find inside {% ... %} blocks and fix == operators
    def fix_if_blocks(match):
        block = match.group(0)
        # Add spaces around == if not already there
        block = re.sub(r'(\w+)==(\w+)', r'\1 == \2', block)
        block = re.sub(r'(\w+)=="([^"]*)"', r'\1 == "\2"', block)
        block = re.sub(r"(\w+)=='([^']*)'", r"\1 == '\2'", block)
        # Also fix other operators
        block = re.sub(r'(\w+)!=(\w+)', r'\1 != \2', block)
        block = re.sub(r'(\w+)!="([^"]*)"', r'\1 != "\2"', block)
        return block
    
    # Process {% if ... %} blocks
    content = re.sub(r'\{%\s*if\s+[^%]+%\}', fix_if_blocks, content)
    
    # 2. Fix split template tags (both {% %} and {{ }})
    # Tags that span multiple lines
    content = re.sub(r'\{%\s*endif\s*\n\s*%\}', '{% endif %}', content)
    content = re.sub(r'\{%\s*endfor\s*\n\s*%\}', '{% endfor %}', content)
    content = re.sub(r'\{%\s*endblock\s*\n\s*%\}', '{% endblock %}', content)
    content = re.sub(r'\{%\s*endwith\s*\n\s*%\}', '{% endwith %}', content)
    content = re.sub(r'\{%\s*else\s*\n\s*%\}', '{% else %}', content)
    
    # Fix {{ variable }} tags that are split across lines
    # e.g., {{ listing.trim.year|noloc 
    #       }}
    content = re.sub(r'\{\{\s*([^}]+)\n\s*\}\}', r'{{ \1 }}', content)
    content = re.sub(r'\{\{\n\s*([^}]+)\}\}', r'{{ \1 }}', content)
    
    return content

def fix_template(filepath: Path) -> tuple[bool, list[str]]:
    """Fix a single template file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = fix_all_issues(original)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, ["Applied syntax fixes"]
    
    return False, []

def main():
    print("=" * 60)
    print("Django Template Syntax Fixer v2")
    print("=" * 60)
    
    if not TEMPLATES_DIR.exists():
        print(f"Error: Templates directory not found at {TEMPLATES_DIR}")
        return
    
    total_fixed = 0
    
    for html_file in sorted(TEMPLATES_DIR.glob("**/*.html")):
        was_modified, fixes = fix_template(html_file)
        if was_modified:
            total_fixed += 1
            print(f"✅ Fixed: {html_file.name}")
        else:
            print(f"   OK: {html_file.name}")
    
    print()
    print(f"✅ Fixed {total_fixed} template(s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
