from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseServerError, Http404

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

def fetch_url(request):
    from django.utils.datastructures import MultiValueDictKeyError
    from django.db.models.loading import get_model
    try:
        model_string = request.GET['model']
        pk = request.GET['pk']
    except MultiValueDictKeyError:
        raise Http404
    
    try:
        (app_label, model_name) = model_string.split('.')
    except ValueError:
        raise Http404

    model = get_model(app_label, model_name)
    if model is None:
        raise Http404

    obj = get_object_or_404(model, pk=pk)

    try:
        url = obj.get_absolute_url()
    except AttributeError:
        raise Http404

    return HttpResponse(url)
