from datetime import datetime, date, timedelta

from django.forms import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.template import Context, RequestContext, loader
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.utils import simplejson

from trade.utils.decorators import account_login_required

from trade.member.models import Member

from trade.product.models import Product, MemberProduct, ProductPhoto
from trade.product.forms import ProductForm, ProductPhotoForm

def detail(request, slug):
    product = Product.objects.get(slug=slug)

    data = {
        'product': product,

    }

    return render_to_response('product/detail.html', data,
        context_instance=RequestContext(request))

@account_login_required
def edit(request, slug):
    product = Product.objects.get(slug=slug)

    try:
        mp = MemberProduct.objects.get(product = product, member=Member.objects.get(user=request.user))
    except:
        return HttpResponseRedirect(reverse('account_login'))

    ProductPhotoFormSet = models.inlineformset_factory(Product, ProductPhoto, formset=models.BaseInlineFormSet, form=ProductPhotoForm,  extra=1, can_delete=True)

    if request.method == "POST":
        form = ProductForm(request.POST,request.FILES, instance=product)
        formset = ProductPhotoFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.active = True
            product.save()
            for form in formset.forms:
                #print form.cleaned_data
                form.save()


            request.session['product_message'] = "%s has been saved." %product.name
            return HttpResponseRedirect(reverse('member_home'))
        else:
            data = {'form': form,
            'formset': formset,
            'product': product
            }
            return render_to_response('product/edit.html',data, context_instance=RequestContext(request))
    else:

        form = ProductForm(instance=product)
        formset = ProductPhotoFormSet(instance=product)


    data = {'form': form,
            'formset': formset,
            'product': product
            }
    return render_to_response('product/edit.html',data, context_instance=RequestContext(request))

@account_login_required
def add(request):

    product = Product()
    ProductPhotoFormSet = models.inlineformset_factory(Product, ProductPhoto, formset=models.BaseInlineFormSet, form=ProductPhotoForm,  extra=1, can_delete=True)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductPhotoFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.active = True
            product.save()
            member = Member.objects.get(user = request.user)

            mp = MemberProduct(member= member, product=product).save()
            for form in formset.forms:
                #print form.cleaned_data
                image= form['image']
                print image
                photo = ProductPhoto(image= image, product = product).save()
                #photo.save()

            request.session['product_message'] = "%s has been saved." %product.name
            return HttpResponseRedirect(reverse('member_home'))
    else:

        form = ProductForm(instance=product)
        formset = ProductPhotoFormSet(instance=product)

    data = {'form': form,
            'formset': formset}
    return render_to_response('product/add.html',data, context_instance=RequestContext(request))


@account_login_required
def delete(request, slug):

    product = Product.objects.get(slug=slug)

    try:
        mp = MemberProduct.objects.get(product = product, member=Member.objects.get(user=request.user))
    except:
        return HttpResponseRedirect(reverse('account_login'))

    product.active = False
    product.save()

    data = {
        'product': product,

    }

    request.session['product_message'] = "%s has been removed." %product.name
    return HttpResponseRedirect(reverse('member_home'))

def search(request):
    q = request.POST['q']
    print q
    return HttpResponseRedirect(reverse('member_home'))