from itertools import chain
from django.core.exceptions import ObjectDoesNotExist

from shop.models import Category, Shop, Product, ProductImage


def get_categories():
    return Category.objects.filter(is_active=True).distinct()


def get_product_by_title(title):
    return Product.objects.filter(title__icontains=title, is_active=True)


def get_products_by_category(category_id=None):
    if not category_id:
        return None

    return Product.objects.filter(category=category_id, is_active=True).order_by('-created').distinct()


def get_product_by_id(product_id=None):
    if not product_id:
        return None

    try:
        return Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        return None


def get_product_images(product_id=None):
    if not product_id:
        return None

    product = Product.objects.filter(pk=product_id)
    images = ProductImage.objects.filter(product__pk=product_id)

    product_images = list(
        sorted(
            chain(product, images),
            key=lambda objects: objects.pk
        )
    )

    return product_images


def get_about_shop():
    about_shop = Shop.objects.filter(is_active=True).first()

    if not about_shop:
        return None

    return about_shop.about
