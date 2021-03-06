from django.conf.urls.defaults import *
from django.views.generic import TemplateView

from django.contrib.auth import views as auth_views

from views import activate, register

urlpatterns = patterns('',
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]+ because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.

    url(r'^activar/(?P<activation_key>\w+)/$', activate, name='account_activate'),
    url(r'^ingresar/$', auth_views.login, {'template_name': 'registration/login.html'}, name='account_login'),
    url(r'^adios/$', auth_views.logout, {'template_name': 'registration/logout.html', 'next_page': '/'}, name='account_logout'),
    url(r'^nuevo/$', register, name='account_register'),
    url(r'^nuevo/completo/$', TemplateView.as_view(template_name="registration/registration_complete.html"), name='account_register-complete'),

    url(r'^clave/cambiar/$', auth_views.password_change, name='auth_password_change'),
    url(r'^clave/cambiar/fin/$', auth_views.password_change_done, name='auth_password_change_done'),
    url(r'^clave/restaurar/$', auth_views.password_reset,{'template_name': 'registration/password_reset.html'}, name='auth_password_reset'),
    url(r'^clave/restaurar/confirmacion/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm,
       {'template_name': 'registration/password_confirm.html'},
       name='auth_password_reset_confirm'),
    url(r'^clave/restarurar/completo/$', auth_views.password_reset_complete,
       {'template_name': 'registration/password_reset_complete.html'},
       name='auth_password_reset_complete'),
    url(r'^clave/restaurar/fin/$', auth_views.password_reset_done,{'template_name': 'registration/password_reset_done.html'}, name='auth_password_reset_done'),

)
