"""
Views which allow users to create and activate accounts.

"""

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.core.urlresolvers import reverse

from trade.registration.models import RegistrationProfile
from trade.registration.forms import RegistrationForm

def activate(request, activation_key):
    """
    Activates a user's account, if their key is valid and hasn't
    expired.

    Context::
        account
            The ``User`` object corresponding to the account,
            if the activation was successful.

        expiration_days
            The number of days for which activation keys stay valid.

    Template::
        accounts/activate.html

    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    registration_profile = RegistrationProfile.objects.activate_user(activation_key)
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    return render_to_response('registration/activate.html',
        {
        'registration_profile': registration_profile,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        'site':current_site,
        }, context_instance=RequestContext(request))


def register(request, success_url=None,
             form_class=RegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html',
             extra_context=None):
    """
    Allows a new user to register an account.

    On successful registration, an email will be sent to the new user
    with an activation link to click to make the account active. This
    view will then redirect to ``success_url``, which defaults to
    '/accounts/register/complete/'. This application has a URL pattern
    for that URL and routes it to the ``direct_to_template`` generic
    view to display a short message telling the user to check their
    email for the account activation link.

    Context::
        form
            The registration form

    Template::
        registration/registration_form.html

    """

    if request.method == 'POST':
        response_dict = {}
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save()
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            from django.contrib.auth import login
            from django.contrib.auth import authenticate
            print new_user.password
            print new_user.username
            user_auth = authenticate(username=new_user.username, password=form.cleaned_data['password1'])
            print user_auth
            login(request, user_auth)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            response_dict.update({'success': True, 'url': reverse('member_home')})
            return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

        else:
            response_dict.update({'success': False, 'message': 'Oops! Ocurrieron errores, porfavor revise el formulario.'})
            response_dict.update({'errors': {}})
            response_dict['errors'] = dict()
            for field in form.errors:
                response_dict['errors'][field] = [unicode(error) for error in form.errors[field]]
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)

