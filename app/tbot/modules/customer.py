from django.core.exceptions import ObjectDoesNotExist

from shop.models import Customer


def get_or_create_user(kwargs):
    customer, new_customer = Customer.objects.get_or_create(
        telegram_id=kwargs['telegram_id'],
        username=kwargs['username']
    )

    return customer, new_customer


def get_user_by_id(user_id):
    try:
        return Customer.objects.get(telegram_id=user_id)
    except ObjectDoesNotExist:
        return None


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


def change_customer_address(user_id, address, post_number=None):
    try:
        user = Customer.objects.get(telegram_id=user_id)
        user.address = address

        if post_number:
            user.post_number = post_number

        user.save()
        return user
    except Exception:
        return None
