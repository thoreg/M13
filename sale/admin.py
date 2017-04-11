from django.contrib import admin

from .models import Category, Product, ProductMarker, SubCategory, Transaction


class TransactionAdmin(admin.ModelAdmin):
    pass


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ['asin', 'sku', 'name']


class ProductMarkerAdmin(admin.ModelAdmin):
    list_display = ('product_short_description', 'category', 'description', 'modified')
    list_filter = ('modified', 'category')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.order_by('sku')
        return super(ProductMarkerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name',)


class SubCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductMarker, ProductMarkerAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
