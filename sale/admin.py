from django.contrib import admin

from .models import Category, Product, ProductMarker, SubCategory, Transaction


class TransactionAdmin(admin.ModelAdmin):
    pass


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)


class ProductMarkerAdmin(admin.ModelAdmin):
    list_display = ('product_short_description', 'description', 'modified')
    list_filter = ('modified',)


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name',)


class SubCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductMarker, ProductMarkerAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
