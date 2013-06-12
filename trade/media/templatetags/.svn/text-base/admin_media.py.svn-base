from django.template import Library
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from trade.media.forms import AddRelatedImageForm, AddRelatedFileForm
from trade.media.models import ImageRelation, FileRelation

register = Library()

def image_sorter(context, model):
    """
    Adds a sortable list of images for models with a RelatedImagesField
    """
    form = AddRelatedImageForm(initial={
        'id': model.id,
        'model': "%s.%s" % (model._meta.app_label, model._meta.object_name),
    })

    context.update({
        'model' : model,
        'form' : form,
        'meta': model._meta
    })
    return context
register.inclusion_tag("admin/media/includes/image_sort.html", takes_context=True)(image_sorter)

def file_sorter(context, model):
    """
    Adds a sortable list of files for models with a RelatedFilesField
    """
    form = AddRelatedFileForm(initial={
        'id':model.id,
        'model': "%s.%s" % (model._meta.app_label, model._meta.object_name),
    })

    context.update({
        'model' : model,
        'form' : form,
        'meta': model._meta
    })
    return context
register.inclusion_tag("admin/media/includes/file_sort.html", takes_context=True)(file_sorter)

def image_list_filter(context):
    """
    Adds list filter for models related to an Image in the admin.
    """
    request = context['request']
    selected_model = None
    selected_id = None
    if 'relations__content_type__model' in request.GET:
        selected_model = request.GET['relations__content_type__model']
        if 'relations__object_id' in request.GET:
            selected_id = request.GET['relations__object_id']

    filters = []
    for model in ImageRelation.get_related_models():
        ctype = ContentType.objects.get_for_model(model)
        objs = model.objects.all()
        selected = None
        if selected_model == ctype.model:
            selected = selected_id
        filters.append({
            'name': model._meta.module_name,
            'verbose_name': model._meta.verbose_name,
            'ctype': ctype,
            'objects': objs,
            'selected': selected,
        })

    return {
        'filters': filters,
        'querydict': request.GET.copy()
    }
register.inclusion_tag("admin/media/includes/image_list_filter.html",
        takes_context=True)(image_list_filter)

def file_list_filter(context):
    """
    Adds list filter for models related to an File in the admin.
    """
    request = context['request']
    selected_model = None
    selected_id = None
    if 'relations__content_type__model' in request.GET:
        selected_model = request.GET['relations__content_type__model']
        if 'relations__object_id' in request.GET:
            selected_id = request.GET['relations__object_id']

    filters = []
    for model in FileRelation.get_related_models():
        ctype = ContentType.objects.get_for_model(model)
        objs = model.objects.all()
        selected = None
        if selected_model == ctype.model:
            selected = selected_id
        filters.append({
            'name': model._meta.module_name,
            'verbose_name': model._meta.verbose_name,
            'ctype': ctype,
            'objects': objs,
            'selected': selected,
        })

    return {
        'filters': filters,
        'querydict': request.GET.copy()
    }
register.inclusion_tag("admin/media/includes/file_list_filter.html",
        takes_context=True)(file_list_filter)
