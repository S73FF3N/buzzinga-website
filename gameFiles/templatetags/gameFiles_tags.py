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