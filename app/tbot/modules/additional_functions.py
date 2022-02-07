import re

from telebot import types

from tbot import keyboards as kb
from tbot.models import BotConfig
from tbot.modules.cart import (is_product_empty_by_item,
                               has_user_empty_products)


def get_nova_poshta_api():
    return BotConfig.objects.filter(is_active=True).first().nova_poshta_api


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


def get_cart_item_text(product_title,
                       quantity=None,
                       price=None,
                       subtotal=None,
                       is_cart=False,
                       only_added=False,
                       item=None):
    if is_cart:
        message_text = f'<b>{product_title}</b>\n\n' \
                       f'Кількість: {quantity}\n' \
                       f'Ціна за ед.: {price}\n' \
                       f'Сума: {subtotal}\n'

        if item and is_product_empty_by_item(item):
            message_text += '\n<b>Нажаль, товару немає у наявності. ' \
                            'Перед оформленням замовлення, ' \
                            'будь-ласка видаліть цей товар з корзини.</b>'

    else:
        message_text = f'<b>Товар {product_title} доданий у корзину.</b>'

        if not only_added and quantity:
            message_text += f'\n\nЗараз цього товару у корзині: {quantity}'

    return message_text


def get_item_text_and_keyboard(obj, bot, cart_item, is_cart):
    if is_cart:
        item_quantity = cart_item.quantity
        item_price = cart_item.product.price
        item_subtotal = item_quantity * item_price

        text_message = get_cart_item_text(
            product_title=cart_item.product.title,
            quantity=item_quantity,
            price=item_price,
            subtotal=item_subtotal,
            is_cart=True)
        keyboard = kb.item_control_keyboard(cart_item.pk, is_cart=True)

        subtotal_message, subtotal_keyboard = \
            get_subtotal_text_and_keyboard(cart_item.cart)

        bot.edit_message_text(text=subtotal_message,
                              chat_id=obj.from_user.id,
                              message_id=cart_item.cart.total_message_id,
                              reply_markup=subtotal_keyboard)
    else:
        text_message = get_cart_item_text(
            product_title=cart_item.product.title,
            quantity=cart_item.quantity)
        keyboard = kb.item_control_with_cart_keyboard(cart_item.pk)

    if obj.message.content_type == 'photo':
        bot.edit_message_caption(caption=text_message,
                                 chat_id=obj.from_user.id,
                                 message_id=obj.message.message_id,
                                 reply_markup=keyboard)
    else:
        bot.edit_message_text(text=text_message,
                              chat_id=obj.from_user.id,
                              message_id=obj.message.message_id,
                              reply_markup=keyboard)


def get_subtotal_text_and_keyboard(cart):
    subtotal, quantity = cart.get_subtotal
    product_empty = has_user_empty_products(cart.customer.pk)

    if subtotal:
        subtotal_message = f'Загальная сума замовлення: {subtotal} грн.\n\n' \
                           f'Кількість товарів: {quantity}'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        if not product_empty:
            cart.total_price = subtotal
            cart.save()

            keyboard.add(types.InlineKeyboardButton('Зробити замовлення',
                                                    callback_data='new_order'))
        else:
            keyboard.add(types.InlineKeyboardButton(
                'Видалити неактуальні товари',
                callback_data='remove_empty_products'))
            subtotal_message += '\n\n<b>Для того щоб почати оформлювати ' \
                                'замовлення, видаліть з корзини ' \
                                'товари яких немає у наявності.</b>'
    else:
        subtotal_message = 'Вже немає чого купувати. ' \
                           'Додайте щось і ми продовжимо.'
        keyboard = None

    return subtotal_message, keyboard


def get_phone_number(obj, bot):
    customer_phone = None
    if obj.content_type == 'contact':
        customer_phone = obj.contact.phone_number
    else:
        if not validate_phone_number(obj.text):
            bot.send_message(obj.from_user.id, 'Введіть коректний номер.')
        else:
            customer_phone = obj.text

    return customer_phone
