from django import forms
from django.utils.safestring import mark_safe
from django.utils.importlib import import_module
from django.conf import settings

__all__ = ("VisualEditor", "MDTextarea", "MCETextEditor", "CKTextEditor", "ColorInput", "SliderInput")


class MDTextarea(forms.widgets.Textarea):
    """
    A textarea widget that has a toolbar and preview area if you're using 
    Markdown as a formatting language.
    """
    def __init__(self, attrs={}):
        self.markup_set = attrs.pop('markdownSet', 'markdown')
        if attrs:
            if 'cols' not in attrs:
                attrs['cols'] = '60'
            if 'markup_set' in attrs:
                self.markup_set = attrs['markup_set']
        super(MDTextarea, self).__init__(attrs)

    def render(self, name, value, attrs={}):
        attrs['class'] = self.markup_set
        output = []
        output.append('<span>This field supports <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank">markdown</a> formatting.</span><br/>')
        output.append(super(MDTextarea, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


    class Media:
        js = (settings.MEDIA_URL + "js/showdown/showdown.js",
              settings.MEDIA_URL + "js/jquery/jquery.markitup.js", 
              settings.MEDIA_URL + "js/markdown_set.js",
              settings.MEDIA_URL + "js/jquery/ui/ui.core.js",
              settings.MEDIA_URL + "js/jquery/ui/ui.draggable.js",
              settings.MEDIA_URL + "js/jquery/ui/ui.dialog.js",
              )

        css = {"screen" : (settings.MEDIA_URL + "css/mdeditor/mdeditor.css",)}

class MCETextEditor(forms.widgets.Textarea):
    """
    A textarea widget that uses TinyMCE editor for WYSIWYG html editing.
    """
    def __init__(self, attrs=None):
        super(MCETextEditor, self).__init__(attrs)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'mceEditor'

    def render(self, name, value, attrs=None):
        output = []
        output.append(super(MCETextEditor, self).render(name, value, attrs))
        #output.append('<script type="text/javascript">tinyMCE.EditorManager.init(mceEditor);</script>')
        return mark_safe(u''.join(output))

    class Media:
        js = (settings.MEDIA_URL + "js/tiny_mce/tiny_mce.js",
              settings.ADMIN_MEDIA_PREFIX + "js/artcode/mce_config.js",
             )


class CKTextEditor(forms.widgets.Textarea):
    def __init__(self, attrs={}):
        self.config = attrs.pop('config', 'acEditor')
        super(CKTextEditor, self).__init__(attrs)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'ckEditor'

    def render(self, name, value, attrs=None):
        output = []
        attrs['ckconfig'] = self.config
        output.append(super(CKTextEditor, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

    class Media:
        js = (settings.MEDIA_URL + "js/ckeditor/ckeditor.js",
              settings.ADMIN_MEDIA_PREFIX + "js/artcode/ck_config.js",
              settings.ADMIN_MEDIA_PREFIX + "js/artcode/ck_editor.js",
             )

# The Visual Editor Type
def get_visual_editor():
    """
    Imports and returns the widget by the path defined in settings.VISUAL_EDITOR
    """
    editor_path = getattr(settings, 'VISUAL_EDITOR', 'cms.apps.utils.forms.widgets.MDTextarea')    
    module_path = '.'.join(editor_path.split('.')[:-1])
    cls = editor_path.split('.')[-1]
    module = import_module(module_path)
    return getattr(module, cls)

VisualEditor = get_visual_editor()


class ColorInput(forms.TextInput):
    """
    Widget that shows a javascript color chooser.
    """
    def render(self, name, value, attrs={}):
        attrs['class'] = 'color-input'
        attrs['size'] = 6
        output = []
        output.append(super(ColorInput, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
    
    class Media:
        js = (
            settings.MEDIA_URL + "js/jquery/farbtastic/farbtastic.js",
            settings.MEDIA_URL + "admin/js/artcode/facade_widgets.js",
        )
        css = {"screen" : (settings.MEDIA_URL + "js/jquery/farbtastic/farbtastic.css",)}

class SliderInput(forms.TextInput):
    """
    A widget that shows a javascript slider.
    """
    def render(self, name, value, attrs={}):
        output = []
        output.append('<div class="ui-slider"></div>')
        output.append(super(SliderInput, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

    class Media:
        js = (
            settings.MEDIA_URL + "js/jquery/ui/ui.core.js",
            settings.MEDIA_URL + "js/jquery/ui/ui.slider.js",
            settings.ADMIN_MEDIA_PREFIX + "js/artcode/facade_widgets.js",
        )
        css = {"screen" : (settings.ADMIN_MEDIA_PREFIX + "css/ui-theme/ui.theme.css",
                           settings.ADMIN_MEDIA_PREFIX + "css/ui-theme/ui.core.css",
                           settings.ADMIN_MEDIA_PREFIX + "css/ui-theme/ui.slider.css",)}
