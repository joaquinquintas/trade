# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField

from trade.utils.fields import AutoSlugField

from trade.media.models import RelatedImagesField


class Category(models.Model):
    """
    Basic hierarchical category model for storing products.
    """

    name = models.CharField(_(u'name'), max_length=200)
    slug = AutoSlugField(max_length=200, unique=True, editable=False, prepopulate_from='name',
            help_text='Unique text identifier used in urls.')
    description = models.TextField(_(u'description'),
        blank=True)
    parent = models.ForeignKey('self', verbose_name=_(u'parent'),
        related_name='children', blank=True, null=True,
        help_text=_(u'All products in a category are also in its parent category.'))

    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")

    def __unicode__(self):
        if self.parent:
            return u'%s -- %s' % (self.parent, self.name)
        else:
            return self.name

    @models.permalink
    def get_absolute_url(self):
        pass

class Product(models.Model):

    def get_upload_to(self, filename):
        return 'img/%s/main/%s' %(self.slug, filename)

    name = models.CharField(_(u'name'), max_length=100)
    slug = AutoSlugField(max_length=200, unique=True, prepopulate_from='name',
            help_text='Unique text identifier used in urls.')

    description = models.TextField(_(u'description'),
        blank=True, null=True)
    featured = models.BooleanField(_(u'featured'), default=False)
    active = models.BooleanField(_('active'), default=False)
    image = models.ImageField(_(u'image'), upload_to=get_upload_to,
        blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    file = models.FileField(_(u'file'), upload_to='files',
        blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=_(u'category'),
        blank=True, null=True, related_name='products')

    tags = TagField(verbose_name=_('tags'), help_text=_(u'Write space or comma separated words that describe the product.'))

    published = models.BooleanField(default=False)

    images = RelatedImagesField()

    create_time = models.DateTimeField("created on", auto_now_add=True)
    update_time = models.DateTimeField("last updated on", auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _(u'product')
        verbose_name_plural = _(u'products')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('products.views.product_detail', [],
                {'product': self.slug})



class ProductPhoto(models.Model):
    def get_upload_to(self, filename):
        return 'img/%s/%s' %(self.product.slug, filename)

    product = models.ForeignKey(Product, related_name='photos',
        verbose_name=_(u'product'))
    image = models.ImageField(_(u'image'), upload_to=get_upload_to)

    class Meta:
        ordering = ('product__name',)
        verbose_name = _(u'product photo')
        verbose_name_plural = _(u'product photos')

    def __unicode__(self):
        return self.product.name

    def get_absolute_url(self):
        """Absolute URL for the object."""
        return self.product.get_absolute_url()

class MemberProduct(models.Model):
    member = models.ForeignKey("member.Member", related_name="my_products")
    product = models.ForeignKey("product.Product", related_name="members")
    create_time = models.DateTimeField("created on", auto_now_add=True)
    update_time = models.DateTimeField("last updated on", auto_now=True)
