from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
import os
import mimetypes

register = template.Library()
mimetype_image_dir = 'img/mime-icons'

mime_to_image = {
    'text/plain' : 'ascii.png',

    'video' : 'video.png',
    'application/x-shockwave-flash' : 'video.png', 
    'video/quicktime' : 'quicktime.png',

    'audio' : 'audio.png',

    'application/x-tar' : 'archive.png',
    'application/zip' : 'archive.png',
    'application/rar' : 'archive.png',
    'application/x-stuffit' : 'archive.png',
    
    'application/pdf' : 'pdf.png',
    'application/postscript' : 'postscript.png',

    'application/msword' : 'document.png',
    'application/vnd.oasis.opendocument.text' : 'document.png',
    'application/vnd.ms-excel' : 'spreadsheet.png',
    'application/vnd.oasis.opendocument.spreadsheet' : 'spreadsheet.png'
}

def get_mime_image(filename, size=64):
    """ Given a filename, will return the proper image icon for 
        the file type using the mimetypes module.

        size is the size of the icon to use.  This will only succeed
        if icons in that size are available. 64 is the default size.
    """
    filename = unicode(filename)
    mimetype = mimetypes.guess_type(filename)[0]
    if mimetype is None:
        mimetype = 'unknown'
    try:
        imagename = mime_to_image[mimetype]
    except KeyError:
        try:
            imagename = mime_to_image[mimetype.split('/')[0]]
        except KeyError:
            imagename = 'unknown.png'
    size_dir = "%sx%s" % (size, size)
    return os.path.join(settings.MEDIA_URL, mimetype_image_dir, size_dir, imagename)

class MimeImageNode(template.Node):
    def __init__(self, filename, context_var=None):
        self.filename = template.Variable(filename)
        self.context_var = context_var

    def render(self, context):
        relative_src = self.filename.resolve(context)
        if self.context_var is None:
            return get_mime_image(relative_src)
        context[self.context_var] = get_mime_image(relative_src)
        return ''


def mimetype_image(parser, token):
    """
        Given a filename, will output an image icon based
        on the mimetype determined by the mimetypes module.
    """
    args = token.split_contents()
    tag = args[0]

    context_var = None
    if len(args) > 2:
        if args[-2] == 'as':
            context_var = args[-1]
            args = args[:-2]
   
    if len(args) == 3:
        size = args.pop()
    if len(args) != 2:
        raise template.TemplateSyntaxError("Invalid syntax. Expected "
            "'{%% %s filename %%}' or "
            "'{%% %s filename as variable %%}'" % (tag, tag))
    filename = args[1]
    return MimeImageNode(filename, context_var=context_var)

register.tag(mimetype_image)

def video_embed(video, width=None, height=None):
    embed = video.get_embed(width=width, height=height)
    return mark_safe(embed)
register.simple_tag(video_embed)
