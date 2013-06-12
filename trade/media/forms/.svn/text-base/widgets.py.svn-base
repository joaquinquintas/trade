from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminFileWidget
from django.conf import settings

__all__ = ("DeleteCheckboxWidget", "ImageInputWidget", "RemovableFileWidget", "RemovableImageWidget")

class DeleteCheckboxWidget(forms.CheckboxInput):
    """ 
    Checkbox widget used to delete items.  This widget is meant to be used in a MultiWidget with FileInput
    show_delete: The parent widget is responsible for setting the show_delete flag.
    """
    def __init__(self, *args, **kwargs):
        self.show_delete = False
        self.show_delete_once = False
        if 'show_delete' in kwargs:
            self.show_delete = kwargs.pop('show_delete')
        super(DeleteCheckboxWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if self.show_delete or self.show_delete_once:
            self.show_delete_once = False
            return u'<br/><label>&nbsp;</label><label for="%s" class="small delete-checkbox">%s %s</label><br class="clear" />' % (attrs['id'], super(DeleteCheckboxWidget, self).render(name, value, attrs), _('Delete'))
        else:
            return u''

class ImageInputWidget(forms.FileInput):
    """
    A file input for images showing thumbnail of current image.
    This widget uses filters based on http://code.google.com/p/sorl-thumbnail/
    """
    def __init__(self, *args, **kwargs):
        self.display_size = kwargs.pop('display_size', (150,150))
        super(ImageInputWidget, self).__init__(*args, **kwargs)
        
    def render(self, name, value, attrs=None):
        """ Render parent fileinput widget along with a thumbnail. """
        from django.template import Template, Context
        if type(value) == list:
            value = value[0]
        output = []
        output.append(super(ImageInputWidget, self).render(name, value, attrs))
        if value:
            t = Template( '{% load thumbnail %}<br/><br/> <label>&nbsp;</label><a target="_blank" href="{{media_url}}{{value}}"><img src="{% thumbnail value size %}" /></a><br/> ')
            o = t.render(Context({
                'media_url': settings.MEDIA_URL, 
                'value': value,
                'size': 'x'.join(str(s) for s in self.display_size)
                }))
            output.append(o)
        return mark_safe(u''.join(output))

class RemovableFileWidget(forms.MultiWidget):
    """ 
    Combines a FileInput with DeleteCheckboxWidget.
    """
    needs_multipart_form = True

    def __init__(self):
        widgets = (AdminFileWidget, DeleteCheckboxWidget())
        super(RemovableFileWidget, self).__init__(widgets)
    
    def decompress(self, value):
        if value:
            return [value, None]
        else :
            return [None, None]
    
    def render(self, name, value, attrs=None):
        file_value = self.decompress(value)[0]
        if file_value: self.widgets[1].show_delete_once = True
        return super(RemovableFileWidget, self).render(name, value, attrs)

class RemovableImageWidget(forms.MultiWidget):
    """ 
    Combines a ImageInputWidget with DeleteCheckboxWidget.
    """
    needs_multipart_form = True

    def __init__(self):
        widgets = (ImageInputWidget(), DeleteCheckboxWidget())
        super(RemovableImageWidget, self).__init__(widgets)
    
    def decompress(self, value):
        if value:
            return [value, None]
        else :
            return [None, None]
    
    def render(self, name, value, attrs=None):
        file_value = self.decompress(value)[0]
        if file_value: self.widgets[1].show_delete_once = True
        return super(RemovableImageWidget, self).render(name, value, attrs)
