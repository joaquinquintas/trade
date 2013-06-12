# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField

from trade.utils.fields import AutoSlugField


class Offer(models.Model):

    from_member = models.ForeignKey("member.Member", related_name="my_sent_offers")
    to_member = models.ForeignKey("member.Member", related_name="my_reviced_offers")
    message = models.TextField(blank=True)
    from_products = models.ManyToManyField("product.MemberProduct", related_name="from_products")
    to_products = models.ManyToManyField("product.MemberProduct", related_name="to_products")
    status = models.CharField(max_length=50)

    parent = models.ForeignKey('self', verbose_name=_(u'parent'),
        related_name='children', blank=True, null=True,)

    diff_amount = models.DecimalField(default="0.00", decimal_places=2, max_digits=10, blank=True, null=True,)

    create_time = models.DateTimeField("created on", auto_now_add=True)
    update_time = models.DateTimeField("last updated on", auto_now=True)

    class Meta:
        verbose_name = _("Oferta")
        verbose_name_plural = _("Ofertas")

    def __unicode__(self):
        if self.parent:
            return u'%s -- %s' % (self.from_member.user.username, self.to_member.user.username)
        else:
            return self.name

