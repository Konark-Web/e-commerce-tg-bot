from django.db import transaction

from tbot.modules.customer import get_user_by_id
from tbot.modules.cart import get_or_create_cart, get_cart_items
from shop.models import Order, OrderItem


def create_order(user_id):
    user = get_user_by_id(user_id)
    cart = get_or_create_cart(user_id)[0]

    with transaction.atomic():
        order = Order.objects.create(customer=user,
                                     customer_name=user.customer_name,
                                     phone_number=user.phone_number,
                                     city=user.city,
                                     address=user.address,
                                     post_number=user.post_number,
                                     total=cart.get_subtotal[0],
                                     status='processing')

        cart_items = get_cart_items(cart.pk)
        order_items = []
        for item in cart_items:
            product = item.product
            order_items.append(OrderItem(order=order,
                                         product=product,
                                         price=item.product.price,
                                         quantity=item.quantity,
                                         total=item.product.price * item.quantity))

            product.quantity = product.quantity - item.quantity
            product.save()

        OrderItem.objects.bulk_create(order_items)
        cart_items.update(is_active=False)
        cart.update(total_price=0)

    return order


def get_orders_by_user_id(user_id):
    return Order.objects.filter(customer=user_id)


def get_item_orders_by_order_id(order_id):
    return OrderItem.objects.filter(order=order_id)