from django.contrib import admin
from .models import Category, Customer, Shop, Product, ProductImage, Order

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Shop)
admin.site.register(Order)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage
    max_num = 9


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]

    class Meta:
        model = Product


# @admin.register(ProductImageAdmin)
# class ProductImageAdmin(admin.ModelAdmin):
#     pass
