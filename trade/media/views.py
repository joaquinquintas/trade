import re

from django.utils.hashcompat import md5_constructor
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden, HttpResponseNotModified, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings

from trade.media.models import Image

def image_save(request, id):
    """
    Serve up an image as an attachment. This is useful for creating 'download' 
    links for images.
    """
    import os
    image = get_object_or_404(Image, pk=id)
    filename = image.filename.path
    file = open(filename, 'r')
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(image.filename.name)
    return response

def image_email(request, id):
    """
    Email an image.
    """
    from django.template.loader import render_to_string
    image = get_object_or_404(Image, pk=id)
    sent_mail = False

    if request.method == 'POST' and 'name' in request.POST and 'email' in request.POST:
        from django.core.mail import EmailMessage
        name = request.POST['name']
        to_email = request.POST['email']        
        from_email = 'China Art Objects <info@chinaartobjects.com>'
        subject = 'Image from China Art Objects'
        message = """
        %s thought you might be interested in seeing this image
        Visit us at http://chinaartobjects.com/
        """ % name

        email = EmailMessage(subject, message, from_email, (to_email,))
        file = open(image.filename.path, 'r')
        email.attach(image.title, file.read(), 'image/jpeg')
        email.send(fail_silently=False)
        sent_mail = True
        
    
    return render_to_response('media/image/email.html', RequestContext(request, {
        'image' : image,
        'sent_mail' : sent_mail
    }))

def thumbnail(request, path):
    """
    Generates a thumbnail using the sorl.thumbnail module and redirects to the 
    new image. This view is useful for generating thumbnail links with 
    javascript using the sorl.thumbnail module.
    """
    from sorl.thumbnail.main import DjangoThumbnail
    from sorl.thumbnail.base import ThumbnailException
    size = (100, 100)
    options = None
    if 'size' in request.GET:
        size = request.GET['size']
        size = tuple(size.split('x'))
    if 'options' in request.GET:
        options = request.GET['options']
        options = tuple(options.split(','))
    
    # make path relative to media root
    RE = r'^%s' % re.sub(r'^\/', '', settings.MEDIA_URL)
    path = re.sub(RE, '', path)
    
    try:
        thumb = DjangoThumbnail(path, size, options)
    except ThumbnailException:
        if settings.DEBUG:
            raise
        else:
            raise Http404()
    uri = "%s%s" % (settings.MEDIA_URL, thumb.relative_url)
    return HttpResponseRedirect(uri)

def color_bg(request, color, opacity=100):
    """
    Generates a 10x10 square image in the color requested.
    Useful for generating background colors based on user-provided 
    color settings.
    """
    import Image, ImageDraw, ImageColor
    
    alpha = int((int(opacity) / 100.0) * 255)

    if len(color) != 3 and len(color) != 6:
        raise Http404
    color = '#%s' % color
    color = ImageColor.getrgb(color) + (alpha,)
    

    size = (10,10)

    etag = md5_constructor("%s%s" % (color, size)).hexdigest()
    if request.META.get("HTTP_IF_NONE_MATCH") == etag:
        return HttpResponseNotModified()
    
    img = Image.new("RGBA", size=size, color=color)

    response = HttpResponse(mimetype="image/png")
    img.save(response, "PNG")
    response["Etag"] = etag
    return response
