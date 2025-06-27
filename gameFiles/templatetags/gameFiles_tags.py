from django import template

register = template.Library()

@register.filter
def to_class_name(value):
    return value.__class__.__name__

@register.filter
def getattribute(obj, attr):
    return getattr(obj, attr)

@register.filter
def get_label(field):
    return field.label

@register.filter
def get_errors(field):
    """Returns errors of a form field"""
    if hasattr(field, 'errors'):
        return field.errors
    return None

@register.filter
def get_field(form, field_name):
    """
    Returns a form field by its name using dictionary-style access
    """
    try:
        return form[field_name]
    except (KeyError, TypeError):
        return None
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)