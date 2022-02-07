from django.db import transaction

from shop.models import Order, OrderItem
from tbot.modules.cart import get_cart_items, get_or_create_cart
from tbot.modules.customer import get_user_by_id


def create_order(user_id):
    user = get_user_by_id(user_id)
    cart = get_or_create_cart(user_id)[0]

    if not cart.get_subtotal[-1]:
        return None

    with transaction.atomic():
        order = Order.objects.create(
            customer=user,
            customer_name=user.customer_name,
            phone_number=user.phone_number,
            city=user.city,
            address=user.address,
            post_number=user.post_number,
            total=cart.get_subtotal[0],
        )

        cart_items = get_cart_items(cart.pk)
        order_items = []
        for item in cart_items:
            product = item.product
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    price=item.product.price,
                    quantity=item.quantity,
                    total=item.product.price * item.quantity,
                )
            )

            product.quantity = product.quantity - item.quantity
            product.save()

        OrderItem.objects.bulk_create(order_items)
        cart_items.update(is_active=False)
        cart.total_price = 0
        cart.save()

    return order
