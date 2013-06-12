from django import forms
from django.db.models.loading import get_model
from django.core.exceptions import PermissionDenied

from fields import *
from widgets import *

class AddImageForm(forms.Form):
    imagefile = forms.ImageField(label='New Image')

class AddFileForm(forms.Form):
    file = forms.FileField(label='New File')


class AddRelatedImageForm(forms.Form):
    """
    Given the pk of a related model, this form will add a newly uploaded image
    and associate it with the related model.
    This assumes that the related model has a m2m relationship with Image.
    """
    id = forms.IntegerField(required=True, widget=forms.HiddenInput)
    imagefile = forms.ImageField(label='New Image')
    model = forms.CharField(widget=forms.HiddenInput)

    def save(self, user):
        from cms.apps.media.models import Image

        # Get the related class
        (app_label, model_name) = self.cleaned_data['model'].split('.')
        related_class = get_model(app_label, model_name)
        
        # Check permissions
        change_perm = "%s.%s" % (app_label, related_class._meta.get_change_permission())
        if not user.has_perm(change_perm):
            raise PermissionDenied

        # Create a new image.
        image = Image()
        image.filename.save(self.cleaned_data['imagefile'].name, self.cleaned_data['imagefile'], save=False)
        image.save()

        # Attach image to the related object.
        related_obj = related_class.objects.get(pk=self.cleaned_data['id'])
        related_obj.images.add(image)
        return (related_obj, image)

class AddRelatedFileForm(forms.Form):
    """
    Given the pk of a related model, this form will add a newly uploaded file
    and associate it with the related model.
    This assumes that the related model has a m2m relationship with File.
    """
    id = forms.IntegerField(required=True, widget=forms.HiddenInput)
    filefile = forms.FileField(label='New File')
    model = forms.CharField(widget=forms.HiddenInput)

    def save(self, user):
        from cms.apps.media.models import File

        # Get the related class
        (app_label, model_name) = self.cleaned_data['model'].split('.')
        related_class = get_model(app_label, model_name)
        
        # Check permissions
        change_perm = "%s.%s" % (app_label, related_class._meta.get_change_permission())
        if not user.has_perm(change_perm):
            raise PermissionDenied
        # Create a new file
        file = File()
        file.filename.save(self.cleaned_data['filefile'].name, self.cleaned_data['filefile'], save=False)
        file.save()

        # Attach file to the related object
        related_obj = related_class.objects.get(pk=self.cleaned_data['id'])
        related_obj.files.add(file)
        return (related_obj, file)
