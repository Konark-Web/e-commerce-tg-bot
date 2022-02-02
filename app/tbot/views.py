import telebot

from telebot import types
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render

from . import dispatcher as dp
from .bot import TBot
from .functions import get_user

tBot = TBot()
bot = tBot.get_bot()


@csrf_exempt
def get_hook(request):
    if request.META['CONTENT_TYPE'] == 'application/json':
        json_data = request.body.decode('utf-8')
        update = tBot.update(json_data)
        bot.process_new_updates([update])
        return HttpResponse(status=200)
    else:
        raise PermissionDenied


@bot.message_handler(commands=['start'])
def start_text(message):
    dp.start_message(message, bot)


@bot.message_handler(content_types=['text'])
def text_msg(message):
    user = get_user(message.chat.id)

    if message.text == 'Зареєструватися':
        dp.reg_customer_name(message, bot)
    elif message.text == '🛍 Каталог':
        dp.show_catalog(message, bot)
    elif message.text == '🛒 Корзина':
        dp.show_cart(message, bot)
    elif message.text == 'ℹ️ Про магазин':
        dp.show_about_shop(message, bot)
    elif message.text == '🔎 Пошук':
        dp.show_search_button(message, bot)
    elif message.text == '🔙 До головного меню':
        dp.start_message(message, bot)

    if user.state is not None:
        if message.text and 'reg_customer_name' in user.state:
            if message.text == 'Пропустити реєстрацію':
                dp.registration_skip(message, bot)
            else:
                dp.reg_customer_phone(message, bot)
        elif message.text and 'reg_customer_phone' in user.state:
            if message.text == 'Пропустити реєстрацію':
                dp.registration_skip(message, bot)
            else:
                dp.reg_customer_city(message, bot)
        elif message.text and 'reg_customer_city' in user.state:
            if message.text == 'Пропустити реєстрацію':
                dp.registration_skip(message, bot)
            else:
                dp.reg_customer_finish(message, bot)
        elif message.text and 'new_order_customer_name' in user.state:
            if message.text == '🔙 Назад' or message.text == '🚫 Відміна':
                dp.new_order_skip(message, bot)
            elif message.text == '✅ Підтвердити':
                dp.new_order_phone(message, bot, confirmed=True)
            else:
                dp.new_order_phone(message, bot)
        elif message.text and 'new_order_phone' in user.state:
            if message.text == '🚫 Відміна':
                dp.new_order_skip(message, bot)
            elif message.text == '🔙 Назад':
                dp.new_order_customer_name(message, bot)
            elif message.text == '✅ Підтвердити':
                dp.new_order_delivery(message, bot, confirmed=True)
            else:
                dp.new_order_delivery(message, bot)


@bot.message_handler(content_types=['contact'])
def contact_msg(message):
    user = get_user(message.chat.id)

    if user.state is not None:
        if message.contact.phone_number and 'reg_customer_phone' in user.state:
            dp.reg_customer_city(message, bot)
        elif message.contact.phone_number and 'new_order_phone' in user.state:
            dp.new_order_delivery(message, bot)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    if 'category_list' in call.data:
        dp.show_catalog(call, bot, page_num=call.data.split('|')[-1])
    elif 'product_list' in call.data:
        dp.show_products_list(call, bot, category_id=call.data.split('|')[-1])
    elif 'products_more' in call.data:
        dp.show_products_list(call,
                              bot,
                              category_id=call.data.split('|')[1],
                              page_num=call.data.split('|')[2])
    elif 'product_item' in call.data:
        dp.show_product(call, bot, product_id=call.data.split('|')[-1])
    elif 'image_product' in call.data:
        dp.show_product(call, bot, product_id=call.data.split('|')[1], img_num=call.data.split('|')[2])
    elif 'hide_product' in call.data:
        dp.hide_product(call, bot)
    elif 'add_to_cart' in call.data:
        dp.add_product_to_cart(call, bot, product_id=call.data.split('|')[-1])
    elif 'remove_cart_item' in call.data:
        is_cart = False
        if 'cart' in call.data:
            is_cart = True

        dp.remove_product_from_cart(call, bot, item_id=call.data.split('|')[-1], is_cart=is_cart)
    elif 'add_one_item' in call.data:
        is_cart = False
        if 'cart' in call.data:
            is_cart = True

        dp.add_one_more_item(call, bot, item_id=call.data.split('|')[-1], is_cart=is_cart)
    elif 'remove_one_item' in call.data:
        is_cart = False
        if 'cart' in call.data:
            is_cart = True

        dp.remove_one_item(call, bot, item_id=call.data.split('|')[-1], is_cart=is_cart)
    elif 'show_cart' in call.data:
        dp.show_cart(call, bot)
    elif 'new_order' in call.data:
        dp.new_order_customer_name(call, bot)


@bot.inline_handler(func=lambda query: True)
def query_text(query):
    user = get_user(query.from_user.id)

    if user.state is not None:
        if query.query and 'new_order_delivery' in user.state:
            pass
    else:
        dp.search_inline(query.query, query, bot)


@bot.chosen_inline_handler(func=lambda query: True)
def inline_chosen(query):
    dp.show_product(query, bot, product_id=query.result_id)

