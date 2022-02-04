from django.core.exceptions import ObjectDoesNotExist

from shop.models import Product


def get_product_by_id(product_id=None):
    try:
        return Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        return None
