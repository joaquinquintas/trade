import re
from django import template

register = template.Library()

class OrderedQuerysetNode(template.Node):
    def __init__(self, queryset, format_string, var_name):
        self.queryset = template.Variable(queryset)
        self.format_string = format_string
        self.var_name = var_name
    
    def render(self, context):
        qs = self.queryset.resolve(context)
        fields = tuple((f.strip() for f in self.format_string.split(',')))
        qs = qs.order_by(*fields)
        context[self.var_name] = qs
        return ''

def order_queryset_by(parser, token):
    """
    Takes a queryset and orders it by the fields specified in its argument.
    Example:
    {% ordered_queryset "title, pk" as ordered_queryset %}
    """
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r'(.*?) (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "Invalid arguments \nexample: {%% %r \"field1, field2\" as var_name %%}" % tag_name
    
    queryset, format_string, var_name = m.groups()
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name

    return OrderedQuerysetNode(queryset, format_string[1:-1], var_name)

register.tag('order_queryset_by', order_queryset_by)
