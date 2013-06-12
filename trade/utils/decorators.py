from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def account_login_required(f):
        def wrap(request, *args, **kwargs):
            print request.user.is_authenticated()
            if request.user.is_authenticated():
                return f(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse('account_login'))
        wrap.__doc__=f.__doc__
        wrap.__name__=f.__name__
        return wrap