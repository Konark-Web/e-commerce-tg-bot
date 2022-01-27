import re

from shop.models import Customer, Category, Shop


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
    return Customer.objects.get(telegram_id=user_id)


def get_categories():
    return Category.objects.filter(is_active=True).order_by('-priority').distinct()


def get_about_shop():
    about_shop = Shop.objects.filter(is_active=True).first()
    if about_shop:
        return about_shop.about

    return None


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

