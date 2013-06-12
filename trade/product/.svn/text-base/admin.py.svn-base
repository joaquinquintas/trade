from trade.product.models import *
from django.contrib import admin

class ProductPhotoInline(admin.StackedInline):
    model = ProductPhoto
    max_num = 5
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    model = Product
    save_on_top = True
    inlines = [ProductPhotoInline, ]

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(MemberProduct)

