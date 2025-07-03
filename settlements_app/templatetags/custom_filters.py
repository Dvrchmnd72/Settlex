from django import template

register = template.Library()

@register.filter(name='endswith')
def endswith(value, arg):
    try:
        return str(value).lower().endswith(str(arg).lower())
    except Exception:
        return False
