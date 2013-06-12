import urllib2

from django.contrib import admin
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import resolve
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context, RequestContext
from django.utils.dateformat import format as date_format
from django.utils.encoding import force_unicode
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.admin.widgets import AdminFileWidget
from django.conf import settings

from tagging.models import TaggedItem, Tag
from trade.media.models import Image, File, Video, ImageRelation, FileRelation, VideoRelation
from trade.media.admin.widgets import ImageForeignKeyWidget, FileForeignKeyWidget
from trade.media.templatetags.media import get_mime_image
from trade.utils.forms.widgets import VisualEditor
from trade.utils.fields import TagSelectField

class MediaItemAdmin(admin.ModelAdmin):
    ordering = ('-modified',)
    list_display = ('image_column', 'title', 'tags', 'created_column', 'modified_column', 'published')
    list_filter = ('published', )
    search_fields = ('title', 'filename', 'caption', 'related_tags__tag__name')
    list_per_page = 50
    actions = ['delete_selected',]
    #list_editable = ('title', 'caption', 'published', 'tags',)

    fieldsets = [
        (None, {'fields': ('filename', 'title', 'published', 'caption',)}),
        ('Tags', {'fields': ('tags',)}),
    ]
    add_fieldsets = [
        (None, {'fields': ('filename', 'published',)}),
    ]

    # Columns
    def image_column(self, obj):
        from sorl.thumbnail.main import DjangoThumbnail
        from sorl.thumbnail.base import ThumbnailException
        try:
            thumb_url = DjangoThumbnail(obj.filename.name, (80, 80)).absolute_url
        except ThumbnailException:
            thumb_url = get_mime_image(unicode(obj.filename), size=32)
        t = '<img src="%s" alt="%s"/>' % (thumb_url,obj.title)
        return t
    image_column.allow_tags = True
    image_column.short_description = 'Image'
    image_column.admin_order_field = 'filename'

    def date_column(self, date):
        return '<span style="white-space:nowrap">%s</span><br/>%s' % (
            date_format(date, "M j, Y"),
            date_format(date, settings.TIME_FORMAT))

    def created_column(self, obj):
        return self.date_column(obj.created)
    created_column.short_description = 'Created'
    created_column.admin_order_field = 'created'
    created_column.allow_tags = True

    def modified_column(self, obj):
        return self.date_column(obj.modified)
    modified_column.short_description = 'Created'
    modified_column.admin_order_field = 'modified'
    modified_column.allow_tags = True

    # Actions
    def make_published(self, request, queryset):
        """
        An action to publish selected items.
        """
        queryset.update(published=True)
        self.message_user(request, "Published %s %ss." % (queryset.count(), self.model._meta.module_name))
    make_published.short_description = "Publish selected %(verbose_name_plural)s"

    def make_unpublished(self, request, queryset):
        """
        An action to unpublish selected items.
        """
        queryset.update(published=False)
        self.message_user(request, "Unpublished %s %ss." % (queryset.count(), self.model._meta.module_name))
    make_unpublished.short_description = "Unpublish selected %(verbose_name_plural)s"



    # Forms & Fieldsets
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(MediaItemAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None):
        """
        Returns a form with related models added.
        """
        formclass = super(MediaItemAdmin, self).get_form(request, obj)

        for model in self.relation_model.get_related_models():
            # Proxy models are not handled well so ignore them for now.
            # Proxy models have the same contenttype as their parent, and
            # so cannot be distinguished when saving the media item.
            if model._meta.proxy:
                continue
            model_name = model._meta.module_name
            ctype = ContentType.objects.get_for_model(model)

            if model_name not in flatten_fieldsets(self.fieldsets):
                self.fieldsets.append((
                    model._meta.verbose_name_plural.title(),
                    {'fields': [model_name], 'classes': ('collapse-closed',)}
                ))

            if obj:
                initial_objs = [r.object_id for r in obj.relations.filter(content_type=ctype)]
            else:
                initial_objs = None

            formclass.base_fields[model_name] = forms.ModelMultipleChoiceField(
                model.objects.all(), required=False, initial=initial_objs,
                widget=admin.widgets.FilteredSelectMultiple(model._meta.verbose_name_plural, False)
            )
        return formclass

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Make content field an mceEditor instance
        if db_field.name == 'caption':
            request = kwargs.pop('request')
            if resolve(request.META.get('PATH_INFO'))[0].func_name == 'changelist_view':
                kwargs['widget'] = forms.Textarea(attrs={'rows': '8', 'cols': '20'})
                return db_field.formfield(**kwargs)
            else:
                kwargs['widget'] = VisualEditor(attrs={'config':'acEditorSimple', 'rows': '10'})
                return db_field.formfield(**kwargs)

        if db_field.name == 'filename':
            kwargs.pop('request')
            kwargs['widget'] = AdminFileWidget
            return db_field.formfield(**kwargs)

        if isinstance(db_field, TagSelectField):
            formfield = super(MediaItemAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            rel = lambda: 0
            rel.to = Tag
            return formfield

        return super(MediaItemAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    # Views
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(MediaItemAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name

        myurls = patterns('',
            url(r'^(?P<view>organize|detail)/$',self.changelist_view),
            url(r'^add_tag/$', self.admin_site.admin_view(self.add_tag_view),
                name="%s_%s_add_tag" % info),
            url(r'^remove_tag/$', self.admin_site.admin_view(self.remove_tag_view),
                name="%s_%s_remove_tag" % info),
            url(r'^remove_all_tags/$', self.admin_site.admin_view(self.remove_all_tags_view),
                name="%s_%s_remove_all_tags" % info),
            url(r'^recently_added/$', self.admin_site.admin_view(self.recently_added_view),
                name="%s_%s_recently_added" % info),
        )
        return myurls + urls

    def recently_added_view(self, request):
        recent = request.session.get('recently_uploaded_%ss' % self.model._meta.module_name)
        if recent:
            return HttpResponseRedirect('../detail/?id__in=%s' % ",".join([str(id) for id in recent]))
        return HttpResponseRedirect('../detail/')

    def queryset(self, request):
        # Check for untagged query search based on tag_id == 0
        tag_filter = request.GET.get('related_tags__tag')
        if tag_filter and tag_filter == '0':
            request.GET = request.GET.copy()
            request.GET.pop('related_tags__tag')
            qs = super(MediaItemAdmin, self).queryset(request)
            return qs.exclude(related_tags__isnull=False)
        return super(MediaItemAdmin, self).queryset(request)

    def add_tag_view(self, request):
        item_ids = request.POST.getlist('items')
        tag = request.POST.get('tag')
        if item_ids and tag:
            for item_id in item_ids:
                item = self.model.objects.get(id=item_id)
                try:
                    Tag.objects.add_tag(item, '"%s"' % tag)
                    tag = Tag.objects.get(name=tag)
                except (AttributeError, Tag.DoesNotExist):
                    return HttpResponse('error')
            return HttpResponse(str(tag.id))
        else:
            return HttpResponseBadRequest('Invalid post parameters.')

        return HttpResponse('ok')

    def remove_tag_view(self, request):
        item_ids = request.POST.getlist('items')
        ctype = ContentType.objects.get_for_model(self.model)
        tag = request.POST.get('tag')
        if item_ids and tag:
            for item_id in item_ids:
                tagged = TaggedItem.objects.get(tag__name=tag, content_type=ctype, object_id=item_id)
                tagged.delete()
        else:
            return HttpResponseBadRequest('Invalid post parameters.')

        return HttpResponse('0')

    def remove_all_tags_view(self, request):
        item_ids = request.POST.getlist('items')
        ctype = ContentType.objects.get_for_model(self.model)
        if item_ids:
            for item_id in item_ids:
                TaggedItem.objects.filter(content_type=ctype, object_id=item_id).delete()
        else:
            return HttpResponseBadRequest('Invalid post parameters.')

        return HttpResponse('0')

    def changelist_view(self, request, extra_context={}, view=None):
        module = self.model._meta.module_name
        if view == 'detail':
            request.session['%s_view' % module] =  'detail'
            return HttpResponseRedirect('../?%s' % request.GET.urlencode())
        elif view == 'organize':
            request.session['%s_view' % module] = 'organize'
            return HttpResponseRedirect('../?%s' % request.GET.urlencode())

        view = request.session.get('%s_view' % module)
        if request.GET.has_key('pop'):
            request.GET = request.GET.copy()
            try:
                multiple = bool(request.GET.get('multiple'))
                request.GET.pop('multiple')
            except KeyError:
                multiple = False
            extra_context.update({
                'multiple': multiple
            })
            self.change_list_template = 'admin/media/%s/selection_change_list.html' % module
        else:
            if view == 'organize':
                self.change_list_template = 'admin/media/%s/collection_change_list.html' % module
                selected_tag_id = request.GET.get('related_tags__tag')
                if selected_tag_id:
                    if selected_tag_id != '0':
                        selected_tag = get_object_or_404(Tag, id=selected_tag_id)
                    else:
                        selected_tag = '0'
                else:
                    selected_tag = None
                extra_context.update({
                    'selected_tag': selected_tag
                    })
            else:
                self.change_list_template = None
                view = 'detail'

            extra_context.update({
                'view': view
            })
        return super(MediaItemAdmin, self).changelist_view(request, extra_context)


    def save_model(self, request, item, form, change):
        """
        Saves media item and then saves selected related objects
        """
        item.save()

        # save item to selected related objects
        for model in self.relation_model.get_related_models():
            model_name = model._meta.module_name
            if model_name not in form.cleaned_data:
                continue
            objects = form.cleaned_data[model_name]
            ctype = ContentType.objects.get_for_model(model)
            obj_ids = [obj.pk for obj in objects]
            item.relations.filter(content_type=ctype).exclude(object_id__in=obj_ids).delete()
            for obj in objects:
                field = getattr(obj, self.model._meta.module_name + 's')
                field.add(item)


class ImageAdmin(MediaItemAdmin):
    model = Image
    relation_model = ImageRelation
    add_form_template = 'admin/media/image/add_images.html'

    def image_column(self, obj):
        t = Template("""
            {% load thumbnail %}<img src="{% thumbnail obj.filename 80x80 detail %}" alt="{{obj.filename}}"/><br/>
        """)
        return t.render(Context({'obj': obj}))
    image_column.allow_tags = True
    image_column.short_description = 'Image'
    image_column.admin_order_field = 'filename'


class FileAdmin(MediaItemAdmin):
    model = File
    relation_model = FileRelation
    add_form_template = 'admin/media/file/add_files.html'


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video

    def clean_url(self):
        url = self.cleaned_data['url']
        try:
            r = Video.vimeo_oembed_request('url=%s' % url)
        except urllib2.HTTPError:
            raise forms.ValidationError('Vimeo.com did not recognize this URL. Please enter the full URL for the video.')

        return url

class VideoAdmin(admin.ModelAdmin):
    fields = ('url', 'title',  'caption', )
    list_display = ('image_column', 'title', 'url', )
    form = VideoAdminForm

    def image_column(self, obj):
        t = Template('{% load thumbnail %}<img src="{{obj.thumbnail_url}}" width="100" alt="{{obj.title}}"/>')
        return t.render(Context({'obj': obj}))
    image_column.allow_tags = True
    image_column.short_description = 'Image'
    image_column.admin_order_field = 'filename'

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Make content field an mceEditor instance
        if db_field.name == 'caption':
            kwargs.pop('request')
            kwargs['widget'] = VisualEditor(attrs={'config':'acEditorSimple', 'rows': '10'})
            return db_field.formfield(**kwargs)
        return super(VideoAdmin, self).formfield_for_dbfield(db_field, **kwargs)

#admin.site.register(Image, ImageAdmin)
#admin.site.register(File, FileAdmin)
#admin.site.register(Video, VideoAdmin)


from django.contrib.contenttypes import generic
class RelatedMediaInlineForm(forms.ModelForm):
    """
    Adds an upload field for media inlines.
    """
    upload = forms.FileField(required=False, label='Upload a file')

    def clean(self):
        cleaned_data = self.cleaned_data
        model = self._meta.model
        media_model = model.item.field.rel.to
        if cleaned_data.get('upload'):
            item_upload = self.cleaned_data['upload']
            upload = media_model()
            upload.filename.save(name=item_upload.name, content=item_upload)
            cleaned_data['item'] = upload
        elif not cleaned_data.get('item'):
            raise forms.ValidationError('Please add or select an %s.' % media_model._meta.verbose_name)
        return cleaned_data

class RelatedMediaInline(generic.GenericStackedInline):
    extra = 0
    raw_id_fields = ('item',)
    form = RelatedMediaInlineForm

    fieldsets = (
        ('', {
            'fields': ('upload', 'item', 'sort',),
            'classes': ('wide',)
        }),
    )

    class Media:
        js = (settings.MEDIA_URL + "js/jquery/ui/ui.core.js",
              settings.MEDIA_URL + "js/jquery/ui/ui.sortable.js",
            )
        css = {"screen" : (settings.ADMIN_MEDIA_PREFIX + "css/artcode/sortables.css",)}


    def __init__(self, *args, **kwargs):
        self.media_model = self.model.item.field.rel.to
        if not self.verbose_name:
            self.verbose_name = self.media_model._meta.verbose_name
        if not self.verbose_name_plural:
            self.verbose_name_plural = self.media_model._meta.verbose_name_plural
        super(RelatedMediaInline, self).__init__(*args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'item':
            kwargs['required'] = False
            kwargs['label'] = 'Add from media library'
            kwargs['widget'] = FileForeignKeyWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(RelatedMediaInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class RelatedImagesInlineForm(RelatedMediaInlineForm):
    upload = forms.ImageField(required=False, label='Upload an image')
    class Meta:
        model = ImageRelation

class RelatedImagesInline(RelatedMediaInline):
    model = ImageRelation
    form = RelatedImagesInlineForm
    template = 'admin/edit_inline/image_sort.html'

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'item':
            kwargs['required'] = False
            kwargs['label'] = 'Add from media library'
            kwargs['widget'] = ImageForeignKeyWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(RelatedImagesInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class RelatedFilesInlineForm(RelatedMediaInlineForm):
    class Meta:
        model = FileRelation

class RelatedFilesInline(RelatedMediaInline):
    model = FileRelation
    form = RelatedFilesInlineForm
    template = 'admin/edit_inline/file_sort.html'

class RelatedVideosInlineForm(forms.ModelForm):
    url = forms.URLField(label="Add a new Video", required=False,
        help_text="Enter a Vimeo video URL (e.g. http://vimeo.com/VIDEO_ID/).")

    class Meta:
        model = VideoRelation

    def _post_clean(self):
        # Only do the post clean from ModelForm if there is an item.
        if self.cleaned_data.get('item'):
            super(RelatedVideosInlineForm, self)._post_clean()

    def clean_url(self):
        # Make sure we've got a valid vimeo video.
        video_url = self.cleaned_data.get('url')
        if video_url:
            try:
                r = Video.vimeo_oembed_request('url=%s' % video_url)
            except urllib2.HTTPError:
                raise forms.ValidationError('Vimeo.com did not recognize this URL. Please enter the full URL for the video.')
        return video_url

    def clean(self):
        cleaned_data = self.cleaned_data
        model = self._meta.model
        media_model = model.item.field.rel.to
        if cleaned_data.get('url'):
            video_url = self.cleaned_data['url']
            video = Video.objects.create(url=video_url)
            cleaned_data['item'] = video
        elif not cleaned_data.get('item'):
            raise forms.ValidationError('Please add or select an %s.' % media_model._meta.verbose_name)
        return cleaned_data


class RelatedVideosInline(generic.GenericStackedInline):
    model = VideoRelation
    form = RelatedVideosInlineForm
    verbose_name = 'Video'
    verbose_name_plural = 'Videos'
    extra = 0
    raw_id_fields = ('item',)
    template = 'admin/edit_inline/video_sort.html'
    fieldsets = (
        ('', {
            'fields': ('url', 'item', 'sort',),
            'classes': ('wide',)
        }),
    )

    def formfield_for_dbfield(self, db_field, *args, **kwargs):
        return super(RelatedVideosInline, self).formfield_for_dbfield(db_field, *args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        from django.contrib.admin.widgets import ForeignKeyRawIdWidget
        if db_field.name == 'item':
            kwargs['required'] = False
            kwargs['label'] = 'Add from media library'
            kwargs['widget'] = ForeignKeyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(RelatedVideosInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
