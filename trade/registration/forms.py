from django import forms
from django.contrib.auth.models import User

from trade.registration.models import RegistrationProfile

class RegistrationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':'20'}), label=u'Email')
    username = forms.CharField(widget=forms.TextInput(attrs={'size':'20'}), label=u'Usuario')
    password1 = forms.CharField(widget=forms.PasswordInput(), label=u'Clave')
    password2 = forms.CharField(widget=forms.PasswordInput(), label=u'Clave confirmacion')
    accept_terms = forms.BooleanField(required=False, label=u'Accept Terms')

    def clean_username(self):
        """
        Validates that the username is not already in use.
        """
        if self.cleaned_data.get('username', None):
            try:
                user = User.objects.get(username__exact=self.cleaned_data['username'])
            except User.DoesNotExist:
                return self.cleaned_data['username']
            raise forms.ValidationError(u'El nombre de usuario "%s" ya existe.' % self.cleaned_data['username'])


    def clean_password2(self):
        """
        Validates that the two password inputs match.
        """
        self.clean
        if self.cleaned_data.get('password1', None) and self.cleaned_data.get('password2', None) and \
           self.cleaned_data['password1'] == self.cleaned_data['password2']:
            return self.cleaned_data['password2']
        raise forms.ValidationError(u'Debes ingresar la misma clave')

    def clean_accept_terms(self):
        if self.cleaned_data.get('accept_terms', None) and self.cleaned_data['accept_terms']==True:
            return self.cleaned_data['accept_terms']
        raise forms.ValidationError(u'Debes aceptar los terminos y condiciones')


    def save(self):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.

        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.

        """
        new_user = RegistrationProfile.objects.create_inactive_member(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    accept_terms=self.cleaned_data['accept_terms'],
                )
        return new_user