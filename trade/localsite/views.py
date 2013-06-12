from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, resolve

from trade.registration.forms import RegistrationForm

def home(request):

    # Render homepage template
    return render_to_response('index.html', {'form':RegistrationForm()
    }, context_instance=RequestContext(request))


