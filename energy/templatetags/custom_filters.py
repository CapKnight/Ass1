from django import template

register = template.Library()

@register.filter
def display_percent(value):
    if value is None:
        return "-%"
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return "-%"

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
