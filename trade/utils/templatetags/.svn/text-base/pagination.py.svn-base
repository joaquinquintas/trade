from django import template
from django.template import TemplateSyntaxError
from django.http import QueryDict 

register = template.Library()

def paginate(context, paginator=None, current_page=None):
    """
    Inclusion tag to display simple pagination with Next/Prev links.
    """
    data = {}

    try: 
        if paginator is None:
            paginator = context['paginator']
        if current_page is None:
            current_page = context['current_page']

    except KeyError:
        return {}

    data['paginator'] = paginator
    data['current_page'] = current_page

    if 'query' in context:
        data['query'] = context['query']

    return data
register.inclusion_tag('includes/paginate.html', takes_context=True)(paginate)


class QueryDictMergeNode(template.Node):
    def __init__(self, querydict, *args):
        self.querydict = template.Variable(querydict)
        if len(args) % 2 != 0:
            raise TemplateSyntaxError('You must have an event number of arguments after the QueryDict.')
        self.bits = zip(args[::2], args[1::2])

    def render(self, context):
        querydict = self.querydict.resolve(context)
        if not isinstance(querydict, QueryDict):
            raise TemplateSyntaxError('First argument must be of type QueryDict')
        querydict = querydict.copy()

        for key, value in self.bits:
            value = template.Variable(value).resolve(context)
            key = template.Variable(key).resolve(context)
            querydict[key] = value
        return querydict.urlencode()

def querydict_merge(parser, token):
    """
    Given a QueryDict object and a number of  key/value pairs, 
    will  merge the key/value into the QueryDict and return the 
    urlencoded string. 

    This is useful for pagination and queryset filtering 
    where you need to have links that take the current 
    queryset and merge their respective value into it.

    Example Usage::

        {% querydict_merge querydict "count" 1 "page" 2 %}

    This takes a django.http.QueryDict object and merges in "count" and "page"
    parameters with the given values, overwriting any existing values
    for "count" and "page".
    """

    chunks = token.split_contents()
    if len(chunks) < 4:
        raise template.TemplateSyntaxError('Usage: {% querydict_merge querydict "var1" val1 "var2" val2 ... %}')
    tag = chunks[0]
    querydict = chunks[1]

    args = chunks[2:]
    return QueryDictMergeNode(querydict, *args)

register.tag(querydict_merge) 


