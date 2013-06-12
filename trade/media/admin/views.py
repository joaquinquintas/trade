from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from trade.media.models import Image, File, Video

@staff_member_required
@csrf_protect
def attach_images(request):
    """
    Attach a new image to some object.
    """
    from trade.media.forms import AddRelatedImageForm

    # check permissions first
    if not request.user.has_perm('media.add_image'):
        raise PermissionDenied

    # Add the image
    if request.method == 'POST':
        form = AddRelatedImageForm(request.POST, request.FILES)
        if form.is_valid():
            obj, image = form.save(request.user)
            messages.info(request, 'The new image has been added successfully.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        redirect = referer
    else:
        redirect = '../'

    return HttpResponseRedirect(redirect)

@staff_member_required
def image_sort(request):
    """
    Ajax post view to set sort order for images associated with some object.
    Note: The object's model must have: images = RelatedImagesField()
    """
    # check permissions first
    if not request.user.has_perm('media.change_image_relation'):
        raise PermissionDenied

    if request.method == 'POST':
        # get the model for the object we're sorting for
        model = request.POST.get('model')
        id = request.POST.get('id')
        (app_label, model_name) = model.split('.')
        model_obj = get_model(app_label, model_name)
        object = model_obj.objects.get(pk=id)

        # Set ordering
        image_ids = request.POST.getlist('image')
        for index, image_id in enumerate(image_ids):
            object.images.set_order(item_id=image_id, order=index)

        return HttpResponse('ok')
    return HttpResponseBadRequest('no data provided');

@staff_member_required
@csrf_protect
def delete_image_relation(request, id, app_label, model_name, obj_id):
    """
    Remove an image relation to some object, or optionally delete the image completely.
    Note: The object's model must have: images = RelatedImagesField()
    """

    # get the model for the object we're sorting for
    model_obj = get_model(app_label, model_name)

    # check permissions first
    perm = "%s.%s" % (app_label, model_obj._meta.get_change_permission())
    if not request.user.has_perm('media.delete_image') or not request.user.has_perm(perm):
        raise PermissionDenied

    obj = get_object_or_404(model_obj, pk=obj_id)
    image = get_object_or_404(Image, pk=id)

    if request.POST:
        if 'delete' in request.POST and request.POST['delete'] == '1':
            image.delete()
            messages.info(request, 'The image was deleted sucessfully.')
        else:
            obj.images.remove(image)
            messages.info(request, 'The image was removed successfully.')

        return_url = request.session.get('return_url', reverse('admin:media_image_changelist'))
        del request.session['return_url']
        return HttpResponseRedirect('%s%s' % (return_url, '#images'))
    else:
        # save return page for after confirmation
        referer = request.META.get('HTTP_REFERER')
        if referer:
            request.session['return_url'] = referer
        else:
            request.session['return_url'] = '../../../'

    opts = {
        'app_label': app_label,
        'module_name': obj._meta.module_name,
        'verbose_name' : obj._meta.verbose_name,
        'verbose_name_plural' : obj._meta.verbose_name_plural
    }
    context = {
        'object' : obj,
        'image' : image,
        'opts' : opts
    }
    return render_to_response('admin/media/image/delete_image_relation.html', context,
            context_instance=RequestContext(request))



@staff_member_required
@csrf_protect
def attach_files(request):
    """
    Attach a new file to some object.
    """
    from trade.media.forms import AddRelatedFileForm

    # check permissions first
    if not request.user.has_perm('media.add_image'):
        raise PermissionDenied

    # Add the file
    if request.method == 'POST':
        form = AddRelatedFileForm(request.POST, request.FILES)
        if form.is_valid():
            obj, file = form.save(request.user)
            messages.info(request, 'The new file has been added successfully.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        redirect = referer
    else:
        redirect = '../'

    return HttpResponseRedirect(referer)

@staff_member_required
def file_sort(request):
    """
    Ajax post view to set sort order for files associated with some object.
    Note: The object's model must have: files = RelatedFilesField()
    """
    # check permissions first
    if not request.user.has_perm('media.change_file_relation'):
        raise PermissionDenied

    if 'file' in request.POST:
        # get the model for the object we're sorting for
        model = request.POST.get('model')
        id = request.POST.get('id')
        (app_label, model_name) = model.split('.')
        model_obj = get_model(app_label, model_name)
        object = model_obj.objects.get(pk=id)

        file_ids = request.POST.getlist('file')
        for index, file_id in enumerate(file_ids):
            object.files.set_order(item_id=file_id, order=index)

        return HttpResponse('ok')
    return HttpResponseBadRequest('no data provided');

@staff_member_required
@csrf_protect
def delete_file_relation(request, id, app_label, model_name, obj_id):
    """
    Remove an file relation to some object, or optionally delete the file completely.

    Note: The object's model must have: files = RelatedFilesField()
    """
    # get the model for the object we're sorting for
    model_obj = get_model(app_label, model_name)

    # check permissions first
    perm = "%s.%s" % (app_label, model_obj._meta.get_change_permission())
    if not request.user.has_perm('media.delete_file') or not request.user.has_perm(perm):
        raise PermissionDenied

    obj = get_object_or_404(model_obj, pk=obj_id)
    file = get_object_or_404(File, pk=id)

    if request.POST:
        if 'delete' in request.POST and request.POST['delete'] == '1':
            file.delete()
            messages.info(request, 'The file was deleted sucessfully.')
        else:
            obj.files.remove(file)
            messages.info(request, 'The file was removed successfully.')

        return_url = request.session.get('return_url', reverse('admin:media_file_changelist'))
        del request.session['return_url']
        return HttpResponseRedirect('%s%s' % (return_url, '#files'))
    else:
        # save return page for after confirmation
        referer = request.META.get('HTTP_REFERER')
        if referer:
            request.session['return_url'] = referer
        else:
            request.session['return_url'] = '../../../'

    opts = {
        'app_label': app_label,
        'module_name': obj._meta.module_name,
        'verbose_name' : obj._meta.verbose_name,
        'verbose_name_plural' : obj._meta.verbose_name_plural
    }
    context = {
        'object' : obj,
        'file' : file,
        'opts' : opts
    }
    return render_to_response('admin/media/file/delete_file_relation.html', context,
            context_instance=RequestContext(request))


@staff_member_required
def video_sort(request):
    """
    Ajax post view to set sort order for videos associated with some object.
    Note: The object's model must have: videos = RelatedVideosField()
    """
    # check permissions first
    if not request.user.has_perm('media.change_video_relation'):
        raise PermissionDenied

    if 'video' in request.POST:
        # get the model for the object we're sorting for
        model = request.POST.get('model')
        id = request.POST.get('id')
        (app_label, model_name) = model.split('.')
        model_obj = get_model(app_label, model_name)
        object = model_obj.objects.get(pk=id)

        video_ids = request.POST.getlist('video')
        for index, video_id in enumerate(video_ids):
            object.videos.set_order(item_id=video_id, order=index)

        return HttpResponse('ok')
    return HttpResponseBadRequest('no data provided');

@staff_member_required
@csrf_protect
def delete_video_relation(request, id, app_label, model_name, obj_id):
    """
    Remove an video relation to some object, or optionally delete the video completely.

    Note: The object's model must have: videos = RelatedVideosField()
    """
    # get the model for the object we're sorting for
    model_obj = get_model(app_label, model_name)

    # check permissions first
    perm = "%s.%s" % (app_label, model_obj._meta.get_change_permission())
    if not request.user.has_perm('media.delete_video') or not request.user.has_perm(perm):
        raise PermissionDenied

    obj = get_object_or_404(model_obj, pk=obj_id)
    video = get_object_or_404(Video, pk=id)

    if request.POST:
        if 'delete' in request.POST and request.POST['delete'] == '1':
            video.delete()
            messages.info(request, 'The video was deleted sucessfully.')
        else:
            obj.videos.remove(video)
            messages.info(request, 'The video was removed successfully.')

        return_url = request.session.get('return_url', reverse('admin:media_video_changelist'))
        del request.session['return_url']
        return HttpResponseRedirect('%s%s' % (return_url, '#videos'))
    else:
        # save return page for after confirmation
        referer = request.META.get('HTTP_REFERER')
        if referer:
            request.session['return_url'] = referer
        else:
            request.session['return_url'] = '../../../'

    opts = {
        'app_label': app_label,
        'module_name': obj._meta.module_name,
        'verbose_name' : obj._meta.verbose_name,
        'verbose_name_plural' : obj._meta.verbose_name_plural
    }
    context = {
        'object' : obj,
        'video' : video,
        'opts' : opts
    }
    return render_to_response('admin/media/video/delete_video_relation.html', context,
            context_instance=RequestContext(request))


# Files browsers used by popup dialogs
@staff_member_required
def link_browser(request):
    return render_to_response('admin/media/link_browser.html', {},
            context_instance=RequestContext(request))

@staff_member_required
def image_browser(request):
    return render_to_response('admin/media/image_browser.html', {},
            context_instance=RequestContext(request))

