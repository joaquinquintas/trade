from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.template import Context, RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

from trade.member.models import Member
from trade.member.forms import ProfileForm

@login_required
def dashboard(request):

    try:
        member = Member.objects.get(user=request.user)
    except:
        return HttpResponseRedirect(reverse('account_login'))

    data = {
        'member': member,

    }

    return render_to_response('member/dashboard.html', data,
        context_instance=RequestContext(request))

@login_required
def perfil_edit(request):
    member = get_object_or_404(Member, user=request.user)


    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=member.profile)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('member_home'))
    else:
        form = ProfileForm(instance = member.profile)

    data = {
        'form': form,

    }
    return render_to_response('member/perfil_edit.html', data,
        context_instance=RequestContext(request))