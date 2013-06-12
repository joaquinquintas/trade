import datetime
from haystack.indexes import *
from haystack import site

from trade.product.models import Product, Category

class ProductIndex(SearchIndex):
    description = CharField(document=True, use_template=True)
    name = CharField(model_attr='name')
    update_time = DateTimeField(model_attr='update_time')
    published = BooleanField(model_attr='published')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Event.objects.filter(published=True, type='event')

class CategoryIndex(SearchIndex):
    description = CharField(document=True, use_template=True)
    name = CharField(model_attr='name')
    published = BooleanField(model_attr='published')

    def get_queryset(self):
        return Category.objects.filter(published=True)

site.register(Product, ProductIndex)
site.register(Category, CategoryIndex)
