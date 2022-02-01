import re

from itertools import chain
from django.core.exceptions import ObjectDoesNotExist
from .models import BotConfig
from shop.models import Customer, Category, Shop, Product, ProductImage, Cart, CartItem


def get_bot_url():
    return BotConfig.objects.filter(is_active=True).first().server_url


def get_or_create_user(kwargs):
    customer, new_customer = Customer.objects.get_or_create(
        telegram_id=kwargs['telegram_id'],
        username=kwargs['username']
    )

    return customer, new_customer


def add_state_user(user_id, state=None):
    try:
        user = Customer.objects.get(telegram_id=user_id)
        user.state = state
        user.save()
        return user
    except Exception:
        return None


def change_customer_name(user_id, customer_name):
    try:
        user = Customer.objects.get(telegram_id=user_id)
        user.customer_name = customer_name
        user.save()
        return user
    except Exception:
        return None


def change_customer_phone(user_id, phone_number):
    try:
        user = Customer.objects.get(telegram_id=user_id)
        user.phone_number = phone_number
        user.save()
        return user
    except Exception:
        return None


def change_customer_city(user_id, city):
    try:
        user = Customer.objects.get(telegram_id=user_id)
        user.city = city
        user.save()
        return user
    except Exception:
        return None


def get_user(user_id):
    try:
        return Customer.objects.get(telegram_id=user_id)
    except ObjectDoesNotExist:
        return None


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


def get_or_create_cart(user_id):
    cart, new_cart = Cart.objects.get_or_create(customer_id=user_id, completed=False)

    return cart, new_cart


def get_or_create_cart_item(cart, product):
    cart_item, cart_item_new = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        is_active=True
    )

    return cart_item, cart_item_new


def get_cart_item_by_id(item_id):
    try:
        return CartItem.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return None


def get_cart_items(cart_id):
    return CartItem.objects.filter(cart=cart_id, is_active=True)


def get_about_shop():
    about_shop = Shop.objects.filter(is_active=True).first()

    if not about_shop:
        return None

    return about_shop.about


def validate_phone_number(message):
    string = message
    match1 = re.fullmatch(r'\+\d{12}', string)
    match2 = re.fullmatch(r'\+\d{3}\s\d{2}\s\d{3}\s\d{2}\s\d{2}', string)
    match3 = re.fullmatch(r'\d\s\d{2}\s\d{3}\s\d{2}\s\d{2}', string)
    match4 = re.fullmatch(r'\d{10}', string)
    match5 = re.fullmatch(r'\d{3}\s\d{2}\s\d{3}\s\d{2}\s\d{2}', string)
    match6 = re.fullmatch(r'\d{12}', string)
    match7 = re.fullmatch(r'\d{11}', string)

    return any([match1, match2, match3, match4, match5, match6, match7])

