from django import template
from django.template.defaultfilters import stringfilter

import logging
logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='times')
def times(number):
    return range(number)
