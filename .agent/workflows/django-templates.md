---
description: How to safely edit Django templates without causing syntax errors
---

# Django Template Editing Workflow

## CRITICAL RULES

When editing Django template files (`.html` files in `/templates/`), **ALWAYS** follow these rules:

### 1. Spaces Around Comparison Operators

Django template tags **require spaces** around comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`).

**CORRECT:**
```html
{% if filters.make == make_id %}selected{% endif %}
{% if listing.mileage < 60000 %}Low Mileage{% endif %}
{% if LANGUAGE_CODE == 'ar' %}عربي{% else %}English{% endif %}
```

**INCORRECT (WILL CAUSE ERRORS):**
```html
{% if filters.make==make_id %}selected{% endif %}
{% if listing.mileage<60000 %}Low Mileage{% endif %}
```

### 2. Use `{% with %}` Blocks for Complex Comparisons

When comparing to computed values or filters, use a `{% with %}` block to create a simple variable first:

```html
{% with make_id=make.id|stringformat:"s" %}
    <option value="{{ make.id }}" 
        {% if filters.make == make_id %}selected{% endif %}>
        {{ make.name_en }}
    </option>
{% endwith %}
```

### 3. Never Let Formatters Touch Templates

The project has `.prettierignore` and `.editorconfig` configured to prevent formatters from modifying templates. Do NOT:
- Run Prettier on `.html` files
- Enable "Format on Save" for HTML in VS Code
- Use any HTML beautifier on Django templates

### 4. Multi-line Template Tags

If a template tag must span multiple lines, ensure the `{% %}` delimiters are on the same line:

**CORRECT:**
```html
<option value="{{ make.id }}" 
    {% if filters.make == make_id %}selected{% endif %}>
```

**INCORRECT:**
```html
<option value="{{ make.id }}" {% if filters.make == make_id %}
    selected{% endif %}>
```

## Common Error Messages

If you see these errors, the template has been corrupted by a formatter:

1. `Could not parse the remainder: '==make_id' from 'filters.make==make_id'`
   - **Fix:** Add spaces around `==`

2. `Invalid block tag on line X: 'endif', expected 'empty' or 'endfor'`
   - **Fix:** Check for unclosed `{% if %}` blocks or split template tags

3. `Could not parse some characters: filters.make|==make.id||stringformat:"s"`
   - **Fix:** The `|` filter syntax is being misinterpreted. Use `{% with %}` blocks.

## Quick Fix Script

If templates get corrupted, run:
```bash
# From project root
python fix_all_templates.py
```

// turbo-all
