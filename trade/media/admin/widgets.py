from django import forms
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.template import Template, Context
from django.conf import settings

class ImageForeignKeyWidget(ForeignKeyRawIdWidget):
    """
    Raw ForeignKey Widget for Image model.
    Displays a link and a thumbnail image.
    """
    def render(self, name, value, attrs):
        output = []
        output.append(super(ImageForeignKeyWidget, self).render(name,value,attrs))
        output.append("""
        <script type="text/javascript">
            $(function() { new ImageForeignKeyWidget('id_%s')});
        </script>
        """ % (name))
        return mark_safe(u''.join(output))

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to.objects.get(**{key: value})
        except self.rel.to.DoesNotExist:
            return super(ImageForeignKeyWidget, self).label_for_value(value)

        t = Template('{% load thumbnail%}<br/><span class="foreignKeyImage"><label>&nbsp;</label><a target="_blank" href="{% url admin:media_image_change obj.pk %}"><img src="{% thumbnail obj.filename 120x120 %}" /></a></span>')
        return t.render(Context({'obj': obj}))

    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + 'js/artcode/custom_widgets.js', )

class FileForeignKeyWidget(ForeignKeyRawIdWidget):
    """
    Raw ForeignKey Widget for File model.
    Displays link to file along with widget.
    """
    def label_for_value(self, value):
        output = []
        output.append(super(FileForeignKeyWidget, self).label_for_value(value))
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to.objects.get(**{key: value})
            info = obj._meta.app_label, obj._meta.module_name
            t = Template(' (<a href="{%% url admin:%s_%s_change obj.pk %%}" target="_blank">edit file</a>)' % info )
            output.append(t.render(Context({'obj': obj})))
        except:
            pass
        return mark_safe(u''.join(output))
