from django.conf.urls.defaults import *

urlpatterns = patterns('trade.media.views',
    url(r'^image/(?P<id>\d+)/save/$', 'image_save', name="media-image-save"),
    url(r'^image/(?P<id>\d+)/email/$', 'image_email', name="media-image-email"),
    url(r'^thumbnails/(?P<path>.+)$', 'thumbnail', name="media-thumbnail"),
    (r'^bg/(?P<color>[a-zA-Z0-9]{3,6})\.png$', 'color_bg'),
    (r'^bg/(?P<color>[a-zA-Z0-9]{3,6})_(?P<opacity>[0-9]{1,3})\.png$', 'color_bg'),
)
