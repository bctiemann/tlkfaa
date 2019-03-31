from django import template
from django.template.defaultfilters import stringfilter

import logging
logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='times')
def times(number):
    return list(range(number))

@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]
upto.is_safe = True
