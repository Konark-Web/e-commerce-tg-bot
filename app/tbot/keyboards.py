from telebot import types


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('🛍 Каталог'),
                 types.KeyboardButton('🛒 Корзина'))
    keyboard.add(types.KeyboardButton('ℹ️ Про магазин'),
                 types.KeyboardButton('👤 Мої замовлення'))
    keyboard.add(types.KeyboardButton('🔎 Пошук'))

    return keyboard


def registration_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Зареєструватися'))
    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def number_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Поділитися номером',
                                      request_contact=True))
    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def order_keyboard(info=False, number=False):
    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)

    if info:
        keyboard.add(types.KeyboardButton('✅ Підтвердити'))

    if number:
        keyboard.add(types.KeyboardButton('Відправити номер телефону',
                                          request_contact=True))

    keyboard.add(types.KeyboardButton('🔙 Назад'),
                 types.KeyboardButton('🚫 Відміна'))

    return keyboard


def search_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton('Пошук',
                                   switch_inline_query_current_chat=''))

    return keyboard


def skip_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def item_control_keyboard(item_cart_id, is_cart=False):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    cart_callback = ''
    if is_cart:
        cart_callback = 'cart|'

    keyboard.add(
        types.InlineKeyboardButton(
            text='-1',
            callback_data=f'remove_one_item|{cart_callback}{item_cart_id}'),
        types.InlineKeyboardButton(
            text='+1',
            callback_data=f'add_one_item|{cart_callback}{item_cart_id}'))

    keyboard.add(
        types.InlineKeyboardButton(
            text='❌ Видалити з корзини',
            callback_data=f'remove_cart_item|{cart_callback}{item_cart_id}'))

    return keyboard


def item_control_with_cart_keyboard(item_cart_id):
    keyboard = item_control_keyboard(item_cart_id)
    keyboard.add(types.InlineKeyboardButton('🛒 Перейти до корзини',
                                            callback_data=f'show_cart'))

    return keyboard


def back_to_cart_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('🛒 Повернутися до корзини'))

    return keyboard


def back_to_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1,
                                         resize_keyboard=True,
                                         one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('🔙 До головного меню'))

    return keyboard
