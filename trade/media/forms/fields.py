from django import forms
from trade.media.forms.widgets import *

__all__ = ["CustomImageFormField", "RemovableFileFormField", "RemovableImageFormField",]

class CustomImageFormField(forms.ImageField):
    widget = ImageInputWidget


class RemovableFileFormField(forms.MultiValueField):
    """ A multi-value form field for removable files."""
    field = forms.FileField
    widget = RemovableFileWidget

    def __init__(self, *args, **kwargs):
        fields = [self.field(*args, **kwargs), forms.BooleanField(required=False)]
        if 'max_length' in kwargs:
            del kwargs['max_length']
        kwargs['required'] = False
        super(RemovableFileFormField, self).__init__(fields, **kwargs)

    def clean(self, value):
        if not isinstance(value, (list, tuple)):
            value = [value, False]
        return super(RemovableFileFormField, self).clean(value)

    def compress(self, data_list):
        return data_list


class RemovableImageFormField(RemovableFileFormField):
    """ A multi-value form field for removable image files."""
    field = forms.ImageField
    widget = RemovableImageWidget
