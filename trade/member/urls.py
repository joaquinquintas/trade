from django.conf.urls.defaults import *

from trade.member.views import *

urlpatterns = patterns('',
    url(r'^$', 'trade.member.views.dashboard', name='member_home'),
    url(r'^perfil/editar/$', 'trade.member.views.perfil_edit', name='perfil_edit'),


)
