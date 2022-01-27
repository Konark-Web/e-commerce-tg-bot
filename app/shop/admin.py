from django.contrib import admin
from .models import Category, Customer, Shop

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Shop)
