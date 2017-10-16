from django import template
from django.template.defaultfilters import stringfilter

from fanart.models import UnviewedPicture, Favorite

import logging
logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='depth_indent')
#@stringfilter
def get_indent_px(depth):
    return depth * 20

@register.tag(name='is_blockd')
def do_is_blocked(parser, token):
    try:
        tag_name, commenter, artist = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments, a user and an artist (blocker)" % token.contents.split()[0]
        )
    return ViewPictureNode(picture, user)


