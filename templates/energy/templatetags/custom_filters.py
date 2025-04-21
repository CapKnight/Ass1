from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    value = dictionary.get(str(key))
    return f"{value:.2f}" if isinstance(value, float) else value