from django import template
from django.template.defaultfilters import stringfilter

from fanart.models import UnviewedPicture, Favorite

import logging
logger = logging.getLogger(__name__)

register = template.Library()


class ViewPictureNode(template.Node):

    def __init__(self, picture, user):
        self.picture = template.Variable(picture)
        self.user = template.Variable(user)

    def render(self, context):
        picture = self.picture.resolve(context)
        user = self.user.resolve(context)

        is_unviewed = False
        if user.is_authenticated:
            items_deleted, object_deletions = UnviewedPicture.objects.filter(picture=picture, user=user).delete()
            is_unviewed = items_deleted > 0

        return 'newpic' if is_unviewed else ''


class IsFavoritePictureNode(template.Node):

    def __init__(self, picture, user):
        self.picture = template.Variable(picture)
        self.user = template.Variable(user)

    def render(self, context):
        picture = self.picture.resolve(context)
        user = self.user.resolve(context)

        return 'isfave' if Favorite.objects.filter(picture=picture, user=user).exists() else ''


class IsFavoriteArtistNode(template.Node):

    def __init__(self, artist, user):
        self.artist = template.Variable(artist)
        self.user = template.Variable(user)

    def render(self, context):
        artist = self.artist.resolve(context)
        user = self.user.resolve(context)

        return 'isfave' if Favorite.objects.filter(artist=artist, user=user).exists() else ''


class IsVisibleNode(template.Node):

    def __init__(self, artist, user):
        self.artist = template.Variable(artist)
        self.user = template.Variable(user)

    def render(self, context):
        artist = self.artist.resolve(context)
        user = self.user.resolve(context)

        return 'isvisible' if Favorite.objects.filter(artist=artist, user=user, is_visible=True).exists() else ''


@register.tag(name='view_picture')
def do_view_picture(parser, token):
    try:
        tag_name, picture, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments, a picture and a user" % token.contents.split()[0]
        )
    return ViewPictureNode(picture, user)

@register.tag(name='is_favorite_picture')
def get_is_favorite_picture(parser, token):
    try:
        tag_name, picture, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments, a picture and a user" % token.contents.split()[0]
        )
    return IsFavoritePictureNode(picture, user)

@register.tag(name='is_favorite_artist')
def get_is_favorite_artist(parser, token):
    try:
        tag_name, artist, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments, an artist and a user" % token.contents.split()[0]
        )
    return IsFavoriteArtistNode(artist, user)

@register.tag(name='is_visible')
def get_is_visible(parser, token):
    try:
        tag_name, artist, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments, an artist and a user" % token.contents.split()[0]
        )
    return IsVisibleNode(artist, user)
