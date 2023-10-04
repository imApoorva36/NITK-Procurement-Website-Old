# Inside your_project/your_app/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='percentage')
def calculate_percentage(value):
    return value*0.02
