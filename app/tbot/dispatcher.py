import telebot
from telebot import types

from django.core.paginator import Paginator

from .functions import get_or_create_user, add_state_user, change_customer_name, change_customer_phone,\
    validate_phone_number, change_customer_city, get_user, get_categories, get_about_shop,\
    get_product_by_category


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


def show_catalog(obj, bot, page_num=1):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard_page_btn = []
    categories = get_categories()
    paginator = Paginator(categories, 10)
    items_per_page = paginator.get_page(page_num)

    for item in items_per_page:
        keyboard.add(types.InlineKeyboardButton(item.name, callback_data=f'product_list|{item.pk}'))

    if items_per_page.has_previous():
        next_page = items_per_page.previous_page_number()
        keyboard_page_btn.append(types.InlineKeyboardButton('⬅️', callback_data=f'category_list|{next_page}'))

    if items_per_page.has_next():
        next_page = items_per_page.next_page_number()
        keyboard_page_btn.append(types.InlineKeyboardButton('➡️', callback_data=f'category_list|{next_page}'))

    keyboard.add(*keyboard_page_btn)

    if page_num == 1:
        bot.send_message(obj.chat.id, 'Оберіть категорію яка Вас цікавить:', reply_markup=keyboard)
    else:
        bot.edit_message_reply_markup(obj.message.chat.id, obj.message.message_id, reply_markup=keyboard)


def show_products(obj, bot, category_id, page_num=1):
    products = get_product_by_category(category_id)
    paginator = Paginator(products, 5)
    products_per_page = paginator.get_page(page_num)

    if not products:
        bot.send_message(obj.message.chat.id, 'Нажаль, активних товарів в цій категорії немає.')
        show_catalog(obj.message, bot)

    for index, product in enumerate(products_per_page, start=1):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        product_text = f'<b>{product.title}</b>\n\n' \
                       f'{product.excerpt}\n\n' \
                       f'<b>Ціна:</b> {product.price}'

        if not product.quantity:
            product_text += '\n\n<i>Нажаль, товару поки немає в наявності.</i>'

        keyboard.add(types.InlineKeyboardButton('ℹ️ Подробиці', callback_data=f'product|{product.pk}'))

        if page_num != 1:
            bot.edit_message_reply_markup(obj.message.chat.id, obj.message.message_id, reply_markup=keyboard)

        if index == len(products_per_page) and products_per_page.has_next():
            next_page = products_per_page.next_page_number()
            keyboard.add(types.InlineKeyboardButton('Загрузити більше товарів',
                                                    callback_data=f'products_more|{product.category.pk}|{next_page}'))

        if product.image:
            bot.send_photo(obj.message.chat.id, product.image, product_text, reply_markup=keyboard)
        else:
            bot.send_message(obj.message.chat.id, product_text, reply_markup=keyboard)


def show_about_shop(message, bot):
    about = get_about_shop()

    if about:
        bot.send_message(message.chat.id, about, reply_markup=back_to_main_keyboard())
    else:
        bot.send_message(message.chat.id, 'Нажаль, поки немає інформації про магазин.',
                         reply_markup=back_to_main_keyboard())


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


def back_to_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('🔙 До головного меню'))

    return keyboard
