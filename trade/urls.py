from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # STATIC MEDIA For Development Server
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    # Home Page
    url(r'^$', 'trade.localsite.views.home', name='home'),
    #Privacy
    url(r'^privacidad/$',  TemplateView.as_view(template_name="privacy.html"), name='privacy'),
    #Term of service
    url(r'^terminos-y-condiciones/$', TemplateView.as_view(template_name="tos.html"), name='tos'),
    #contacto
    (r'^contacto/$', include('contact.urls')),

    (r'^busqueda/', include('haystack.urls')),

    (r'^registro/', include('registration.urls')),
    (r'^articulos/', include('product.urls')),
    (r'^cuenta/', include('member.urls')),
    (r'^admin/', include(admin.site.urls)),
)

from django.conf import settings
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^translate/', include('rosetta.urls')),
    )


from tagging.models import TaggedItem
from trade.product.models import Product

tagged_models = (

  dict(title="Products",
    query=lambda tag : TaggedItem.objects.get_by_model(Product, tag),
  ),
)

tagging_ext_kwargs = {
  'tagged_models':tagged_models,
  # You can add your own special template to be the default
  #'default_template':'custom_templates/special.html'
}

urlpatterns += patterns('',
  url(r'^tags/(?P<tag>.+)/(?P<model>.+)$', 'tagging_ext.views.tag_by_model',
        kwargs=tagging_ext_kwargs, name='tagging_ext_tag_by_model'),
  url(r'^tags/(?P<tag>.+)/$', 'tagging_ext.views.tag',
        kwargs=tagging_ext_kwargs, name='tagging_ext_tag'),
  url(r'^tags/$', 'tagging_ext.views.index', name='tagging_ext_index'),
  url(r'^tags/', include('tagging_ext.urls')),
)

urlpatterns += staticfiles_urlpatterns()