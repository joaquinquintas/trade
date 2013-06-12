import re

from django import forms
from django.db.models import SlugField
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify as dj_slugify
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe

from tagging.models import Tag
from tagging.fields import TagField
from tagging.utils import parse_tag_input

def slugify(s):
    s = s.replace(':', '-')
    return dj_slugify(s)

class AutoSlugField(SlugField):
    """
    Allows a SlugField to pre-populate from a model field automatically when model is saved.

    Call like this:
    AutoSlugField(prepopulate_from='name', separator='_')
    """

    separator = '-'

    def __init__(self, prepopulate_from, *args, **kwargs):
        """
        prepopulate_from is the field you want to use to create the slug
        """
        super(AutoSlugField, self).__init__(*args, **kwargs)
        self.prepopulate_from = prepopulate_from

    def pre_save(self, instance, add):
        """
        Populates the field from the field given in prepopulate_from attribute
        """
        # slugify and check for existing conflict
        cls = instance._meta.get_field_by_name(self.attname)[1]
        if not cls:
            cls = instance.__class__
        proposal = getattr(instance, self.attname)
        if not self.editable or not proposal:
            proposal = slugify(getattr(instance, self.prepopulate_from))
            if not proposal: # field only contained non-numeric chars
                proposal = 'zzz'
        if instance.pk:
            similar_ones = cls.objects.filter(**{self.attname + "__startswith": proposal}).exclude(pk=instance.pk).values(self.attname)
        else:
            similar_ones = cls.objects.filter(**{self.attname + "__startswith": proposal}).values(self.attname)
        similar_ones = [elem[self.attname] for elem in similar_ones]
        if proposal not in similar_ones:
            slug = proposal
        else:
            numbers = []
            for value in similar_ones:
                match = re.match(r'^%s%s(\d+)$' % (proposal, self.separator), value)
                if match:
                    numbers.append(int(match.group(1)))
            if len(numbers)==0:
                slug = "%s%s2" % (proposal, self.separator)
            else:
                largest = sorted(numbers)[-1]
                slug = "%s%s%d" % (proposal, self.separator, largest + 1)

        assert( slug not in similar_ones)
        setattr(instance, self.attname, slug)
        return slug

    def formfield(self, **kwargs):
        # max_length and error_message can be overridden 
        kwargs['max_length'] = kwargs.get('max_length', self.max_length) 
        kwargs['error_message'] = kwargs.get( 
 	        'error_message', 
 	        _(u'Please enter a value containing only letters, numbers, ' 
              u'dashes, and underscores.') 
            )
        defaults = {'regex': r'^[-\w]+$', # from django.core.validators.slug_re
                    'form_class': forms.RegexField,
                   } 
        # other defaults cannot be overridden 
        kwargs.update(defaults) 
        return super(AutoSlugField, self).formfield(**kwargs) 
    
    def get_internal_type(self):
        return 'SlugField'

    def db_type(self, connection):
        return 'varchar(%s)' % self.max_length


class TagSelectFormField(forms.MultipleChoiceField):
    def clean(self, value):
        return ', '.join(['"%s"' % tag for tag in value ])

class TagSelectMultiple(forms.SelectMultiple):
    def render(self, name, value, attrs={}, *args, **kwargs):
        output = []
        output.append(super(TagSelectMultiple, self).render(name, value, attrs))
        output.append("""
        <script type="text/javascript" charset="utf-8">
        $(function() {
            var $input = $('#%(id)s');
            var $link = $('<a class="add-another" href="#"></a>').insertAfter($input)
                .click(function() {
                    var tag = prompt('New Tag:');
                    if (tag) {
                        $input.append('<option selected="selected" value="'+tag+'">'+tag+'</option>')
                        $input.trigger('change').trigger('focus');
                    }
                    return false;
                });
        });
        </script>
        """ % {'id': attrs['id']})
        return mark_safe(u''.join(output))
    
    def _has_changed(self, initial, data):
        initial = parse_tag_input(initial)
        return super(TagSelectMultiple, self)._has_changed(initial, data)
        
class TagSelectField(TagField):
    """
    TagSelectField

    A variation of the django-tagging TagField which uses a 
    SelectMultiple widget instead of free text field.

    class MyModel(models.Model):
        ...
        tags = TagSelectField(filter_horizontal=True, blank=False)

    """
    def __init__(self, filter_horizontal=False, *args, **kwargs):
        super(TagSelectField, self).__init__(*args, **kwargs)
        self.filter_horizontal = filter_horizontal

    def contribute_to_class(self, cls, name):
        self.model = cls        
        super(TagSelectField, self).contribute_to_class(cls, name)       
        
    def formfield(self, **defaults):
        if self.filter_horizontal:
            widget = FilteredSelectMultiple(self.verbose_name, is_stacked=False)
        else:
            widget = TagSelectMultiple()
        
        def _render(name, value, attrs=None, *args, **kwargs):
            value = parse_tag_input(value)            
            return type(widget).render(widget, name, value, attrs, *args, **kwargs)
        widget.render = _render
        defaults['widget'] = widget

        choices = [ (str(t), str(t)) for t in Tag.objects.usage_for_model(self.model) ]
        return TagSelectFormField(choices=choices, required=not self.blank, **defaults)



class UserChoiceField(forms.ModelChoiceField):
    """
    A ModelChoiceField for User models which shows
    the full name if available
    """
    def label_from_instance(self, obj):
        label = obj.get_full_name()
        if label.strip():
            return label
        return super(UserChoiceField, self).label_from_instance(obj)


# South Introspection Rules
try:
    from south.modelsinspector import add_introspection_rules
    rules = [
        (
            (AutoSlugField,),
            [],
            {
                "prepopulate_from": ["prepopulate_from", {}],
            },
        ),
        (
            (UserChoiceField,),
            [], {},
        ),
    ]

    add_introspection_rules(rules, ["^.+\.apps\.utils\.fields"])

except ImportError:
    pass
