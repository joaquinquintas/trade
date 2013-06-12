from datetime import timedelta

from django import forms
from django.contrib.localflavor.ar import forms as flavorForms
from django.forms import ModelForm

#from trade.tagging_ext.widgets import TagAutoCompleteInput
from trade.media.forms.widgets import ImageInputWidget
from trade.media.forms.fields import RemovableImageFormField
from trade.product.models import Product, ProductPhoto

class ProductForm(ModelForm):
    image = forms.ImageField(widget=ImageInputWidget)
    #Includ tag autocomplete widget
    #tags = forms.CharField(widget=TagAutoCompleteInput)

    tags = forms.CharField()

    class Meta:
        model = Product
        exclude = ['slug', 'featured', 'file', 'category']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

class ProductPhotoForm(ModelForm):
    #Usar algo como hace el admin.
    iimage = forms.ImageField(widget=ImageInputWidget)

    class Meta:
        model = ProductPhoto
        exclude = ['product',]

    def __init__(self, *args, **kwargs):
        super(ProductPhotoForm, self).__init__(*args, **kwargs)