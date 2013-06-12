from datetime import timedelta

from django import forms
from django.contrib.localflavor.ar import forms as flavorForms
from django.forms import ModelForm

from trade.member.models import UserProfile

class ProfileForm(ModelForm):

    province = forms.CharField(max_length=100, widget=flavorForms.ARProvinceSelect, required=False)
    postal_code = flavorForms.ARPostalCodeField(required=False)

    class Meta:
        model = UserProfile