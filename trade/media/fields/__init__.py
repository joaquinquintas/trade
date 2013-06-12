import types
import os, glob

from django.db.models import ImageField, FileField, signals
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from trade.media.forms import RemovableFileFormField, RemovableImageFormField, CustomImageFormField

class CustomFileField(FileField):
    """
    Adds customizations to django's built-in FileField
    """

    def contribute_to_class(self, cls, name):
        """Hook up events so we can access the instance."""
        super(CustomFileField, self).contribute_to_class(cls, name)

    def _maybe_delete_file(self, instance):
        """
        Deletes the file associated with this field,
        but only if no other model references the same file.
        returns True if the file was deleted
        """
        file = getattr(instance, self.attname)
        if file:
            # If the file exists and no other object of this type references it,
            # delete it from the filesystem.
            if os.path.exists(file.path):
                existing = instance.__class__._default_manager.filter(**{self.name: file.name}).exclude(pk=instance.pk)
                if not existing:
                    file.delete(save=False)
                    return True
        return False

    def save_form_data(self, instance, data):
        """
        Here we're handling two possibilities.  If the data is indexable, then
        we're dealing with a RemoveableFileFormField, which is a MultiValueField:
            data[0] : the normal file data
            data[1] : a delete flag to remove a file.
        Otherwise a regular FileField, and data is simply the uploaded file data.
        """
        # Separate out file data from delete flag if available
        if data:
            if type(data) == types.ListType:
                delete_flag = data[1]
                file_data = data = data[0]
            elif isinstance(data, UploadedFile):
                file_data = data
                delete_flag = False
            else:
                file_data = None
                delete_flag = False
        else:
            file_data = None
            delete_flag = False

        # Can't delete the file if field is not null/blank
        if not self.null and not self.blank:
            delete_flag = False

        if file_data: # Replace file
            self._maybe_delete_file(instance)
            super(CustomFileField, self).save_form_data(instance, file_data)
        elif delete_flag: # Delete file
            self._maybe_delete_file(instance)
            setattr(instance, self.name, None)
        else:
            super(CustomFileField, self).save_form_data(instance, data)

    def formfield(self, **kwargs):
        if self.blank or self.null:
            defaults = {'form_class': RemovableFileFormField}
        else:
            defaults = {}
        defaults.update(kwargs)
        return super(CustomFileField, self).formfield(**defaults)

    def get_internal_type(self):
        return 'FileField'


class CustomImageField(ImageField, CustomFileField):
    """
    Adds customizations to djangos built-in ImageField

    * Cleans thumbnails after a delete
    """
    thumbnail_glob = '*_[0-9]*x[0-9]*_q*'

    def contribute_to_class(self, cls, name):
        """Hook up events so we can access the instance."""
        super(CustomImageField, self).contribute_to_class(cls, name)
        signals.post_delete.connect(self._post_delete, sender=cls)
        signals.post_save.connect(self._post_save, sender=cls)

    def _post_save(self, instance=None, **kwargs):
        self.clean_thumbnails(instance)

    def _post_delete(self, instance=None, **kwargs):
        """Delete left-over files"""
        self.clean_thumbnails(instance)

    def clean_thumbnails(self, instance=None):
        file = getattr(instance, self.attname)
        if file:
            # Delete left-overs from thumbnail filters
            file_name = file.path
            basedir = os.path.dirname(file_name)
            base, ext = os.path.splitext(os.path.basename(file_name))
            thumb_file_glob = "%s%s%s%s" % (settings.THUMBNAIL_PREFIX, base, self.thumbnail_glob, ext)
            for file in glob.glob(os.path.join(basedir, settings.THUMBNAIL_SUBDIR, thumb_file_glob )):
                os.remove(os.path.join(basedir, file))

    def formfield(self, **kwargs):
        if self.blank or self.null:
            defaults = {'form_class': RemovableImageFormField}
        else:
            defaults = {'form_class': CustomImageFormField}
        defaults.update(kwargs)
        return super(CustomImageField, self).formfield(**defaults)

    def get_internal_type(self):
        return 'FileField'

# South Introspection Rules
try:
    from south.modelsinspector import add_introspection_rules
    rules = [
        (
            (CustomFileField, CustomImageField),
            [], {},
        ),
    ]

    add_introspection_rules(rules, ["^.+\.apps\.media\.fields"])

except ImportError:
    pass
