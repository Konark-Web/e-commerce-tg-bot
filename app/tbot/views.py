import telebot

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


@bot.message_handler(content_types=['contact'])
def contact_msg(message):
    user = get_user(message.chat.id)

    if user.state is not None:
        if message.contact.phone_number and 'reg_customer_phone' in user.state:
            dp.reg_customer_city(message, bot)