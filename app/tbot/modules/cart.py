from django.core.exceptions import ObjectDoesNotExist

from shop.models import Cart, CartItem


def get_or_create_cart(user_id):
    cart, new_cart = Cart.objects.get_or_create(customer_id=user_id)

    return cart, new_cart


def get_or_create_cart_item(cart, product):
    cart_item, cart_item_new = CartItem.objects.get_or_create(
        cart=cart, product=product, is_active=True
    )

    return cart_item, cart_item_new


def get_cart_item_by_id(item_id):
    try:
        return CartItem.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return None


def get_cart_items(cart_id):
    return CartItem.objects.filter(cart=cart_id, is_active=True)


def cart_total_changed(user_id):
    cart = get_or_create_cart(user_id)[0]

    if cart.total_price != cart.get_subtotal[0]:
        return True

    return False


def cart_quantity_changed(user_id):
    cart = get_or_create_cart(user_id)[0]
    cart_items = get_cart_items(cart.pk)
    changed = False

    for item in cart_items:
        if item.quantity > item.product.quantity:
            equate_item_quantity_to_product(item)
            changed = True

    return changed


def equate_item_quantity_to_product(item):
    cart_item = get_cart_item_by_id(item.pk)
    cart_item.quantity = cart_item.product.quantity

    cart_item.save()


def is_product_empty_by_item(item):
    product = item.product

    if product.quantity <= 0 or not product.is_active:
        return True

    return False


def has_user_empty_products(user_id):
    cart = get_or_create_cart(user_id)
    cart_items = get_cart_items(cart[0].pk)
    has_empty = False

    for item in cart_items:
        has_empty = is_product_empty_by_item(item)

    return has_empty
