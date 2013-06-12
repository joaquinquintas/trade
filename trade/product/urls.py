from django.conf.urls.defaults import *

from trade.member.views import *

urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/detail/$', 'trade.product.views.detail', name='product_detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', 'trade.product.views.edit', name='product_edit'),
    url(r'^add/$', 'trade.product.views.add', name='product_add'),
    url(r'^(?P<slug>[\w-]+)/delete/$', 'trade.product.views.delete', name='product_delete'),
    url(r'^search/$', 'trade.product.views.search', name='product_search'),


)
