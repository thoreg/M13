from django.contrib import admin

from .models import Category, Product, SubCategory, Transaction


class TransactionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Transaction, TransactionAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)

admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(Category, CategoryAdmin)


class SubCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(SubCategory, SubCategoryAdmin)
