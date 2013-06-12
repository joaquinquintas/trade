from django.conf.urls.defaults import *

urlpatterns = patterns('trade.media.admin.views',
    url(r'link_browser/$', 'link_browser', name="admin-media-link_browse"),
    url(r'image/file_browser/$', 'image_browser', name="admin-media-image_browser"),

    # ImageRelations
    url(r'image/attach/$', 'attach_images', name="admin-media-image-attach"),
    url(r'image/sort/$', 'image_sort', name='admin-media-image-sort'),
    url(r'image/(?P<id>\d+)/delete_relation/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<obj_id>\d+)/$',
        'delete_image_relation', name='admin-media-image-delete_relation'),

    # FileRelations
    url(r'file/attach/$', 'attach_files', name="admin-media-file-attach"),
    url(r'file/sort/$', 'file_sort', name='admin-media-file-sort'),
    url(r'file/(?P<id>\d+)/delete_relation/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<obj_id>\d+)/$',
        'delete_file_relation', name='admin-media-file-delete_relation'),

    # VideoRelation
    url(r'video/sort/$', 'video_sort', name='admin-media-video-sort'),
    url(r'video/(?P<id>\d+)/delete_relation/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<obj_id>\d+)/$',
        'delete_video_relation', name='admin-media-video-delete_relation'),
)
