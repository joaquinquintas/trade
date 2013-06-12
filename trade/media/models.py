import os
import mimetypes
import urllib2

from django.db import models
from django.template.defaultfilters import title
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils import simplejson as json

import tagging
from tagging.fields import TagField
from trade.media.fields import CustomImageField, CustomFileField
from trade.media.fields.related import RelatedMediaField
from trade.utils.fields import AutoSlugField, TagSelectField

###############
# Media Types #
###############

class MediaItemManager(models.Manager):
    def published(self):
        """
        Returns all public items.
        """
        return self.get_query_set().filter(published=True)

class MediaItem(models.Model):
    """
    A Generic Media item (images, files, videos, etc. should subclass)
    New media types should subclass MediaItem.
    """
    title = models.CharField(max_length=200, blank=True)
    published = models.BooleanField(default=True, help_text='Deselect to keep file private.')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    caption = models.TextField(blank=True)

    objects = MediaItemManager()

    class Meta:
        abstract = False

    def get_mimetype(self):
        if hasattr(self, 'filename'):
            type = mimetypes.guess_type(self.filename.name)[0]
            if type is None:
                return 'unkown'
            else:
                return type
        else:
            return 'unknown'
    mimetype = property(get_mimetype)

    def get_type(self):
        return self._meta.module_name
    type = property(get_type)

    def __unicode__(self):
        return u'Media Item: %s' %  self.title


class File(MediaItem):
    """ A generic file model. """
    filename = CustomFileField(upload_to='files', help_text='Select a file to upload.')

    tags = TagSelectField(help_text='Enter keywords separated by space or comma.  Keywords help you search for this file in your media library.')
    related_tags = generic.GenericRelation(tagging.models.TaggedItem)

    objects = MediaItemManager()

    def save(self, *args, **kwargs):
        # If title isn't set, create one based on filename
        if not self.title:
            self.title = title(os.path.splitext(os.path.basename(self.filename.name))[0].replace('_', ' '))
        super(File, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"File: %s (%s)" % (self.title, os.path.basename(self.filename.name))

    def get_absolute_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.filename.name)

#tagging.register(File, tag_descriptor_attr='tag_set')

class Image(MediaItem):
    """ An image model. """
    filename = CustomImageField(upload_to='images', width_field='width', height_field='height',
                help_text='Select an image file to upload.')
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    tags = TagSelectField(help_text='Enter keywords separated by space or comma.  Keywords help you search for this file in your media library.')
    related_tags = generic.GenericRelation(tagging.models.TaggedItem)

    objects = MediaItemManager()

    def save(self, *args, **kwargs):
        # If title isn't set, create one based on filename
        if not self.title:
            self.title = title(os.path.splitext(os.path.basename(self.filename.name))[0].replace('_', ' '))
        super(Image, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Image: %s (%s)" % (self.title, os.path.basename(self.filename.name))

    def get_absolute_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.filename.name)

#tagging.register(Image, tag_descriptor_attr='tag_set')

VIMEO_OEMBED_URL = 'http://vimeo.com/api/oembed.json'

class Video(MediaItem):
    """ A video which is hosted at vimeo.com """
    url = models.URLField(max_length=255, help_text="Enter the URL for a vimeo video (e.g. http://vimeo.com/VIDEO_ID/).")
    thumbnail_url = models.URLField(max_length=255, editable=False)

    objects = MediaItemManager()

    def __unicode__(self):
        return u"Video: %s" % self.url

    def get_absolute_url(self):
        return self.url

    def save(self, *args, **kwargs):
        info = self.info
        self.thumbnail_url = info['thumbnail_url']
        if not self.title:
            self.title = info['title']
        super(Video, self).save(*args, **kwargs)

    @staticmethod
    def vimeo_oembed_request(query):
        """
        Makes a request to vimeo.com oEmbed api.
        query: is the query string (e.g. url=http://vimeo.com/203499)
        returns the response object returned from sending the request.
        """
        url = "%s?%s" % (VIMEO_OEMBED_URL, query)
        headers = {'User-Agent': 'Django'}
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        return response

    def get_info(self, **kwargs):
        """
        Uses Vimeo's oEmbed api to fetch information about the video using the
        saved url.  Keyword arguments are used as parameters for the request to
        override defaults.
        """
        params = {
            'url': self.url,
            'portrait': 'false',
            'byline': 'false',
        }
        params.update(kwargs)
        query = "&".join(["%s=%s" % (k, v) for k, v in params.items()])
        cache_key = 'vimeo_oembed_%s' %  md5_constructor(query).hexdigest()

        info = cache.get(cache_key)
        if info:
            return info

        response = self.vimeo_oembed_request(query)
        data = json.loads(response.read())
        cache.set(cache_key, data, 15* 60)
        return data
    info = property(get_info)

    def get_embed(self, **kwargs):
        """
        Returns the embed code from Vimeo for this video.
        """
        return self.get_info(**kwargs)['html']
    embed = property(get_embed)

#################
# Related Media #
#################

class MediaRelation(models.Model):
    """
    Abstract class to form generic m2m relations between a MediaItem
    and another model.  MediaItem types should each provide a corresponding
    subclass of MediaRelation so the media type can be easily attached to
    other model types.
    """
    content_type = models.ForeignKey(ContentType)
    object_id    = models.PositiveIntegerField('object id', db_index=True)
    object       = generic.GenericForeignKey('content_type', 'object_id')
    sort = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name="sort order")

    class Meta:
        abstract = True
        ordering = ('content_type', 'sort')
        unique_together = ('item', 'object_id', 'content_type')

    def save(self, *args, **kwargs):
        # new items should be added to the end of the list of
        # existing items as ordered by the `sort` field.
        if not self.pk and not self.sort:
            model = type(self)
            max_sort = model.objects.filter(
                    content_type=self.content_type,
                    object_id=self.object_id
                ).aggregate(max_sort=models.Max('sort'))['max_sort']
            if max_sort is not None:
                self.sort = max_sort + 1
        super(MediaRelation, self).save(*args, **kwargs)

    @classmethod
    def get_related_models(cls):
        registered_models = getattr(cls._meta, '_media_registry', [])
        child_models = [x for y in registered_models for x in y.__subclasses__()]
        return registered_models + child_models

    @classmethod
    def relates_to(cls, model):
        return model in cls.get_related_models()


class ImageRelation(MediaRelation):
    item = models.ForeignKey(Image, related_name='relations')


class RelatedImagesField(RelatedMediaField):
    """Attach images to objects with images = RelatedImagesField()"""
    to = ImageRelation
    mediatype = Image


class FileRelation(MediaRelation):
    item = models.ForeignKey(File, related_name='relations')


class RelatedFilesField(RelatedMediaField):
    """Attach files to objects with images = RelatedFilesField()"""
    to = FileRelation
    mediatype = File

class VideoRelation(MediaRelation):
    item = models.ForeignKey(Video, related_name='relations')

class RelatedVideosField(RelatedMediaField):
    to = VideoRelation
    mediatype = Video


#####################
# Media Collections #
#####################

class MediaCollection(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(max_length=200, unique=True, editable=False, prepopulate_from='name',
            help_text='Unique text identifier used in urls.')
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        abstract = True

    def __unicode__(self):
        return self.name

# South Introspection Rules
try:
    from south.modelsinspector import add_ignored_fields
    add_ignored_fields(["^.+\.apps\.media\.models"])
except ImportError:
    pass
