import telebot
from telebot import types

from .functions import get_or_create_user, add_state_user, change_customer_name, change_customer_phone,\
    validate_phone_number, change_customer_city, get_user


def start_message(message, bot):
    user_info = {
        'telegram_id': message.chat.id,
        'username': message.from_user.username,
    }

    customer, new_customer = get_or_create_user(user_info)

    if new_customer:
        bot.send_message(message.chat.id,
                         'Вітаємо!\n\n'
                         'Вас вітає магазин кальянних аксесуарів. '
                         'В нас ви зможете купити все для комфортного проведення часу.\n\n'
                         'Давайте пройдемо коротку реєстрацію, але Ви можете її пропустити.',
                         reply_markup=registration_keyboard())
    else:
        bot.send_message(message.chat.id, '<b>Ви перейшли до головного меню.</b>\n\n'
                         '🛍 Каталог - пошук та купівля товару\n'
                         '🛒 Корзина - оформлення замовлень\n'
                         'ℹ️ Про магазин - більше інформації про нас\n'
                         '👤 Мої замовлення - перегляд попередніх замовлень\n', reply_markup=main_keyboard())


def reg_customer_name(message, bot):
    add_state_user(message.chat.id, 'reg_customer_name')
    bot.send_message(message.chat.id, 'Введіть ваш ПІБ', reply_markup=skip_keyboard())


def reg_customer_phone(message, bot):
    change_customer_name(message.chat.id, message.text)
    add_state_user(message.chat.id, 'reg_customer_phone')
    bot.send_message(message.chat.id, 'Введіть або розшарте ваш номер телефону.', reply_markup=number_keyboard())


def reg_customer_city(message, bot):
    if message.content_type == 'contact':
        customer_phone = message.contact.phone_number
    else:
        customer_phone = message.text
        if not validate_phone_number(customer_phone):
            return bot.send_message(message.chat.id, 'Введіть корректний номер.')

    change_customer_phone(message.chat.id, customer_phone)
    add_state_user(message.chat.id, 'reg_customer_city')
    bot.send_message(message.chat.id, 'Введіть Ваше місто.', reply_markup=skip_keyboard())


def reg_customer_finish(message, bot):
    user = get_user(message.chat.id)
    change_customer_city(message.chat.id, message.text)
    add_state_user(message.chat.id)

    bot.send_message(message.chat.id, f'Дякую за реєстрацію, {user.customer_name}!\n\n'
                                      f'Тепер Ви можете перейти до покупок.')
    start_message(message, bot)


def registration_skip(message, bot):
    add_state_user(message.chat.id)
    start_message(message, bot)


# Keyboards
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('🛍 Каталог'),
                 types.KeyboardButton('🛒 Корзина'))
    keyboard.add(types.KeyboardButton('ℹ️ Про магазин'),
                 types.KeyboardButton('👤 Мої замовлення'))

    return keyboard


def registration_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Зареєструватися'))
    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def number_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Поділитися номером', request_contact=True))
    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def skip_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard
