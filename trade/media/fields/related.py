from django.db.models.fields.related import RelatedField, Field, ManyToManyRel
from django.contrib.contenttypes.models import ContentType

class RelatedMediaField(RelatedField, Field):
    """
    A Field that provides access to RelatedMediaManager, which allows any
    model class to manage a set of MediaItem instances (can change/add/remove).
    """
    to = None           # Subclasses should define this, i.e. to = ImageRelation
    mediatype = None    # Subclasses should define this, i.e. mediatype = Image

    def __init__(self, **kwargs):
        if self.__class__ == RelatedMediaField:
            raise ValueError, 'RelatedMediaField cannot be used directly.  You must subclass it.'

        kwargs['rel'] = RelatedMediaRel(self.to,
                            related_name=kwargs.pop('related_name', None),
                            limit_choices_to=kwargs.pop('limit_choices_to', None),
                            symmetrical=kwargs.pop('symmetrical', True))

        # We don't create any tables, but use generic relations through MediaRelation
        self.creates_table = False

        self.object_id_field_name = 'object_id'

        kwargs['blank'] = True
        kwargs['editable'] = False
        kwargs['serialize'] = False
        Field.__init__(self, **kwargs)

    def contribute_to_class(self, cls, name):
        super(RelatedMediaField, self).contribute_to_class(cls, name)

        # Save a reference to which model this class is on for future use
        self.model = cls

        setattr(cls, 'has_related_media', True)
        setattr(cls, 'has_related_%ss' % self.mediatype._meta.module_name, True)

        # Add the descriptor for the m2m relation
        setattr(cls, self.name, RelatedMediaDescriptor(self))

    def contribute_to_related_class(self, cls, related):
        rel = related.model

        # Save the related model to the relation's registry
        if not rel._meta.abstract:
            opts = cls._meta
            if not hasattr(opts, '_media_registry'):
                opts._media_registry = []
            if rel not in opts._media_registry:
                opts._media_registry.append(rel)

    def m2m_db_table(self):
        return self.rel.to._meta.db_table

    def m2m_column_name(self):
        return self.object_id_field_name

    def m2m_reverse_name(self):
        return self.model._meta.pk.column

    def set_attributes_from_rel(self):
        pass

    def get_internal_type(self):
        return "ManyToManyField"

    def db_type(self, connection):
        # Since we're simulating a ManyToManyField, in effect, best return the
        # same db_type as well.
        return None

class RelatedMediaDescriptor(object):
    """
    A descriptor object used by RelatedMediaField
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, instance_type=None):
        if instance is None:
            raise AttributeError, "Manager must be accessed via instance"

        superclass = self.field.mediatype._default_manager.__class__
        RelatedManager = create_related_media_manager(superclass, self.field.to, self.field.mediatype)
        return RelatedManager(instance=instance, model=instance_type)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError, "Manager must be accessed via instance"

        manager = self.__get__(instance, instance.__class__)
        manager.update(*value)


class RelatedMediaRel(ManyToManyRel):
    def __init__(self, to, related_name=None, limit_choices_to=None, symmetrical=True):
        self.to = to
        self.related_name = related_name
        self.limit_choices_to = limit_choices_to or {}
        self.symmetrical = symmetrical
        self.multiple = True
        self.through = None

    def get_accessor_name(self):
        return None

def create_related_media_manager(superclass, relation_class, media_class):
    """
    Factory function to create a manager for RelatedMediaField instances. The
    manager subclasses 'superclass'.

    relation_class:  a subclass of MediaRelation model
    media_class:  a subclass of MediaItem model
    """
    from trade.media.models import MediaItem, MediaRelation

    if not issubclass(media_class, MediaItem):
        raise ValueError, '%s must be a subclass of MediaItem' % media_class
    if not issubclass(relation_class, MediaRelation):
        raise ValueError, '%s must be a subclass of MediaRelation' % relation_class

    class RelatedMediaManager(superclass):
        """
        Manager for media items related to a specific model
        """
        def __init__(self, instance, model):
            self.instance = instance
            self.model = model
            self.ctype = ContentType.objects.get_for_model(self.model)

            if instance.pk is None:
                raise ValueError("%r instance needs to have a primary key value before this relation can be used." %
                        model)

        def get_query_set(self):
            return media_class.objects.filter(
                    relations__content_type__pk=self.ctype.pk,
                    relations__object_id=self.instance.pk
                ).order_by('relations__sort')
        def update(self, *items):
            """
            Update the items related to this object to match the specified set.
            """
            current_items = list(self.filter(relations__content_type=self.ctype, relations__object_id=self.instance.pk))

            # Determine items to be removed
            items_for_removal = [item for item in current_items if item not in items]
            if items_for_removal:
                relation_class._default_manager.filter(
                        content_type=self.ctype,
                        object_id=self.instance.pk,
                        item__in=items_for_removal
                ).delete()

            # Add new items
            for count, item in enumerate(items):
                if item not in current_items and \
                        item not in items_for_removal:
                    rel = relation_class(item=item, object=self.instance)
                    rel.save()
        update.alters_data = True

        def add(self, *items):
            """
            Add each of the items to this object.
            """
            current_items = list(self.filter(relations__content_type=self.ctype, relations__object_id=self.instance.pk))

            count = self.get_query_set().count()
            for item in items:
                if item not in current_items:
                    count += 1
                    rel = relation_class(item=item, object=self.instance)
                    rel.sort = count
                    rel.save()
        add.alters_data = True

        def set_order(self, item_id, order):
            """
            Sets the order of a media item.
            """
            rel = relation_class.objects.get(item=item_id, object_id=self.instance.pk, content_type=self.ctype)
            rel.sort = order
            rel.save()

        def remove(self, *items):
            """
            Remove the relations between the items and the object
            """
            relation_class._default_manager.filter(
                content_type=self.ctype,
                object_id=self.instance.pk,
                item__in=items
            ).delete()
        remove.alters_data = True

        def clear(self):
            """
            Remove all item relations for this object.
            """
            relation_class._default_manager.filter(
                content_type=self.ctype,
                object_id=self.instance.pk
            ).delete()
        clear.alters_data = True

    return RelatedMediaManager
