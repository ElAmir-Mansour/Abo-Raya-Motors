from django import template

register = template.Library()

@register.filter(name='has_file')
def has_file(field):
    """Check if a file field has a file"""
    try:
        return bool(field and field.name)
    except:
        return False

@register.filter(name='to_str')
def to_str(value):
    """Convert value to string"""
    return str(value)

@register.filter(name='noloc')
def noloc(value):
    """Return value as string without localization (for years, etc.)"""
    try:
        return str(int(value))
    except (ValueError, TypeError):
        return str(value)
