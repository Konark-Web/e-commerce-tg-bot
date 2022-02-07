from django.contrib import admin

from .models import (Category, Customer, Order, OrderItem, Product,
                     ProductImage, Shop)

admin.site.register(Shop)


class OrderAdminInline(admin.StackedInline):
    model = Order
    extra = 0
    show_change_link = True


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'customer_name', 'phone_number', 'city',
                    'is_active')
    list_filter = ('city', 'is_active')
    inlines = [OrderAdminInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage
    max_num = 9
    verbose_name = 'Зображення'
    verbose_name_plural = 'Зображення'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
    list_display = ('title', 'category', 'price', 'quantity', 'is_active')
    list_filter = ('category', 'is_active',)

    class Meta:
        model = Product


class OrderItemAdmin(admin.StackedInline):
    model = OrderItem
    extra = 0
    verbose_name = 'Товар'
    verbose_name_plural = 'Товар'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemAdmin]
    readonly_fields = ('total', )
    list_display = ('pk', 'customer_name', 'phone_number', 'address', 'total',
                    'status')
    list_filter = ('status',)

    class Meta:
        model = Order
