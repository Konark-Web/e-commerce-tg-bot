import telebot

from telebot import types
from django.core.paginator import Paginator

from .functions import get_or_create_user, add_state_user, change_customer_name, change_customer_phone,\
    validate_phone_number, change_customer_city, get_user, get_categories, get_about_shop,\
    get_products_by_category, get_product_by_id, get_product_images, get_or_create_cart, get_or_create_cart_item,\
    get_cart_item_by_id, get_cart_items, get_product_by_title, get_bot_url


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
        bot.send_message(message.chat.id,
                         '<b>Ви перейшли до головного меню.</b>\n\n'
                         '🛍 Каталог - пошук та купівля товару\n'
                         '🛒 Корзина - оформлення замовлень\n'
                         'ℹ️ Про магазин - більше інформації про нас\n'
                         '👤 Мої замовлення - перегляд попередніх замовлень\n'
                         '🔎 Пошук - пошук по каталогу товарів магазину',
                         reply_markup=main_keyboard())


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
            return bot.send_message(message.from_user.id, 'Введіть корректний номер.')

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


def show_products_list(obj, bot, category_id, page_num=1):
    products = get_products_by_category(category_id)
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

        keyboard.add(types.InlineKeyboardButton('ℹ️ Подробиці', callback_data=f'product_item|{product.pk}'))

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


def show_product(obj, bot, product_id, img_num=1):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    product = get_product_by_id(product_id)

    product_images = get_product_images(product_id)
    paginator = Paginator(product_images, 1)
    product_image = paginator.get_page(img_num)

    product_text = f'<b>{product.title}</b>\n\n' \
                   f'{product.description}\n\n' \
                   f'<b>Ціна:</b> {product.price}'

    if product.quantity:
        product_text += f'\n<b>У наявності:</b> {product.quantity}'
        keyboard.add(types.InlineKeyboardButton('🛒 Додати до корзини', callback_data=f'add_to_cart|{product_id}'))
    else:
        product_text += f'\n\n<i>Нажаль, товару поки немає в наявності.</i>'

    if paginator.num_pages > 1:
        if product_image.has_previous():
            prev_image = product_image.previous_page_number()
        else:
            prev_image = paginator.num_pages

        if product_image.has_next():
            next_image = product_image.next_page_number()
        else:
            next_image = 1

        keyboard.add(
            types.InlineKeyboardButton('⬅️ Попереднє фото', callback_data=f'image_product|{product_id}|{prev_image}'),
            types.InlineKeyboardButton('Наступне фото ➡️', callback_data=f'image_product|{product_id}|{next_image}')
        )

    keyboard.add(types.InlineKeyboardButton('🔙 Назад', callback_data='hide_product'))
    if product.image:
        if img_num == 1:
            bot.send_photo(obj.from_user.id, product.image, product_text, reply_markup=keyboard)
        else:
            bot.edit_message_media(types.InputMedia(type='photo',media=product_image[0].image),
                                   obj.from_user.id,
                                   obj.message.message_id,
                                   reply_markup=keyboard)
            bot.edit_message_caption(product_text,
                                     obj.from_user.id,
                                     obj.message.message_id,
                                     reply_markup=keyboard)
    else:
        bot.send_message(obj.from_user.id, product_text, reply_markup=keyboard)


def hide_product(obj, bot):
    bot.delete_message(obj.message.chat.id, obj.message.message_id)


def add_product_to_cart(obj, bot, product_id):
    cart, new_cart = get_or_create_cart(obj.from_user.id)
    product = get_product_by_id(product_id)
    cart_item, cart_item_new = get_or_create_cart_item(cart, product)

    if not cart_item_new:
        if cart_item.quantity >= product.quantity:
            bot.answer_callback_query(obj.id, 'Нажаль, поки це все що є в наявності.', False)
        else:
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()

            bot.answer_callback_query(obj.id,
                                      f'Додано ще 1 одиницю товару до корзини. Зараз у корзині: {cart_item.quantity}',
                                      show_alert=False)
    else:
        bot.send_message(obj.message.chat.id,
                         get_cart_item_text(product_title=product.title),
                         reply_markup=item_control_with_cart_keyboard(cart_item.pk))


def remove_product_from_cart(obj, bot, item_id, is_cart=False):
    cart_item = get_cart_item_by_id(item_id)
    cart_item.is_active = False
    cart_item.save()

    bot.delete_message(obj.message.chat.id, obj.message.message_id)
    bot.answer_callback_query(obj.id,
                              f'Товар успішно видалений с корзини.',
                              show_alert=False)

    if is_cart:
        subtotal_message, subtotal_keyboard = get_subtotal_text_and_keyboard(cart_item.cart)
        bot.edit_message_text(text=subtotal_message,
                              chat_id=obj.message.chat.id,
                              message_id=cart_item.cart.total_message_id,
                              reply_markup=subtotal_keyboard)


def add_one_more_item(obj, bot, item_id, is_cart=False):
    cart_item = get_cart_item_by_id(item_id)

    if not cart_item.is_active:
        add_product_to_cart(obj, bot, cart_item.product.pk)

    if cart_item.quantity >= cart_item.product.quantity:
        bot.answer_callback_query(obj.id, 'Нажаль, поки це все що є в наявності.', False)
    else:
        cart_item.quantity = cart_item.quantity + 1
        cart_item.save()

        get_item_text_and_keyboard(obj, bot, cart_item, is_cart)
        bot.answer_callback_query(obj.id, f'Додано 1 одиницю товару до корзини.', show_alert=False)


def remove_one_item(obj, bot, item_id, is_cart=False):
    cart_item = get_cart_item_by_id(item_id)

    if cart_item.quantity <= 1:
        bot.answer_callback_query(obj.id,
                                  'Меньше вже немає куди. Можете тільки видалити товар з корзини.',
                                  show_alert=False)
    else:
        cart_item.quantity = cart_item.quantity - 1
        cart_item.save()

        get_item_text_and_keyboard(obj, bot, cart_item, is_cart)
        bot.answer_callback_query(obj.id, f'Видалено 1 одиницю товару з корзини.', show_alert=False)


def show_cart(obj, bot):
    cart, new_cart = get_or_create_cart(obj.from_user.id)
    cart_items = get_cart_items(cart)

    # TODO: Make pagination for cart
    # paginator = Paginator(cart_items, 5)
    # items_per_page = paginator.get_page(page_num)

    if not cart_items:
        bot.send_message(obj.from_user.id, 'Нажаль, корзина поки що порожня.')
        return

    for item in cart_items:
        item_quantity = item.quantity
        item_price = item.product.price
        item_subtotal = item_quantity * item_price

        item_keyboard = item_control_keyboard(item.pk, is_cart=True)
        text_message = get_cart_item_text(product_title=item.product.title,
                                          quantity=item_quantity,
                                          price=item_price,
                                          subtotal=item_subtotal,
                                          is_cart=True)

        if item.product.image:
            bot.send_photo(chat_id=obj.from_user.id,
                           photo=item.product.image,
                           caption=text_message,
                           reply_markup=item_keyboard)
        else:
            bot.send_message(chat_id=obj.from_user.id,
                             text=text_message,
                             reply_markup=item_keyboard)

    subtotal_message, keyboard = get_subtotal_text_and_keyboard(cart)
    cart_total_obj = bot.send_message(chat_id=obj.from_user.id, text=subtotal_message, reply_markup=keyboard)

    cart.total_message_id = cart_total_obj.message_id
    cart.save()


def new_order_customer_name(obj, bot):
    user_id = obj.from_user.id
    user = get_user(user_id)

    bot.send_message(obj.from_user.id, 'Давайте почнемо оформлювати замовлення.')
    add_state_user(user_id, 'new_order_customer_name')

    if user.customer_name:
        bot.send_message(chat_id=user_id,
                         text=f'У Вас вже встановленне ім\'я. Введіть нове чи підтвердіть поточне.\n'
                         f'Зараз: {user.customer_name}',
                         reply_markup=order_keyboard(True))
    else:
        bot.send_message(chat_id=user_id,
                         text=f'Введіть ім\'я людини яка буде забирати замовлення.',
                         reply_markup=order_keyboard())


def new_order_phone(obj, bot, confirmed=False):
    user_id = obj.from_user.id
    user = get_user(user_id)

    if not confirmed:
        user = change_customer_name(user_id, obj.text)
        bot.send_message(user_id, f'✅ Ім\'я успішно змінено на {user.customer_name}.')

    add_state_user(user_id, 'new_order_phone')

    if user.phone_number:
        bot.send_message(chat_id=user_id,
                         text=f'У Вас вже встановленний номер телефону. '
                              f'Введіть новий (або поширте задопомогою кнопки нижче) чи підтвердіть поточний.\n'
                              f'Зараз: {user.phone_number}',
                         reply_markup=order_keyboard(info=True, number=True))
    else:
        bot.send_message(chat_id=user_id,
                         text=f'Введіть номер телефону або поширте його задопомогою кнопки нижче.',
                         reply_markup=order_keyboard(number=True))


def new_order_delivery(obj, bot, confirmed=False):
    user_id = obj.from_user.id
    user = get_user(user_id)

    if not confirmed:
        # TODO: Refactor this part of code, duplicate (registration)
        if obj.content_type == 'contact':
            customer_phone = obj.contact.phone_number
        else:
            customer_phone = obj.text
            if not validate_phone_number(customer_phone):
                return bot.send_message(obj.from_user.id, 'Введіть корректний номер.')

        user = change_customer_phone(user_id, customer_phone)
        bot.send_message(user_id, f'✅ Номер телефону успішно змінено на {user.phone_number}.')

    add_state_user(user_id, 'new_order_delivery')

    if user.city and user.address and user.post_number:
        bot.send_message(chat_id=user_id,
                         text=f'У Вас вже встановлена адреса доставки. '
                              f'Виберіть нову у формі пошуку нижче чи підтвердіть поточну.\n'
                              f'Зараз: {user.city} {user.address} {user.post_number}',
                         reply_markup=order_keyboard(info=True))
    else:
        bot.send_message(chat_id=user_id,
                         text=f'Виберіть відділення Нової Пошти у формі пошуку нижче.',
                         reply_markup=order_keyboard())

    bot.send_message(obj.from_user.id,
                     f'Для пошука відділення Нової Пошти натисніть "Пошук" та введіть назву населенного пункту.',
                     reply_markup=search_keyboard())


def new_order_skip(obj, bot):
    add_state_user(user_id=obj.from_user.id)
    show_cart(obj, bot)


def show_about_shop(message, bot):
    about = get_about_shop()

    if about:
        bot.send_message(message.chat.id, about, reply_markup=back_to_main_keyboard())
    else:
        bot.send_message(message.chat.id, 'Нажаль, поки немає інформації про магазин.',
                         reply_markup=back_to_main_keyboard())


def show_search_button(message, bot):
    bot.send_message(message.from_user.id,
                     f'Для пошука товару в нашому магазині натисніть "Пошук" та введіть назву товару.',
                     reply_markup=search_keyboard())


def search_inline(search, query, bot):
    inlines = []
    results = get_product_by_title(search)
    offset = int(query.offset) if query.offset else 0

    for result in results:
        inlines.append(types.InlineQueryResultArticle(
            id=result.pk,
            title=result.title,
            description=result.excerpt,
            thumb_url=get_bot_url() + result.image.url,
            input_message_content=types.InputTextMessageContent(
                message_text=f'Товар: {result.title}'
            )
        ))

    next_offset = f"{offset + 10}"
    bot.answer_inline_query(
        inline_query_id=query.id,
        results=inlines[offset: offset + 10],
        cache_time=0,
        next_offset=next_offset
    )


# Keyboards
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
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Поділитися номером', request_contact=True))
    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def order_keyboard(info=False, number=False):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    if info:
        keyboard.add(types.KeyboardButton('✅ Підтвердити'))

    if number:
        keyboard.add(types.KeyboardButton('Відправити номер телефону', request_contact=True))

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
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('Пропустити реєстрацію'))

    return keyboard


def item_control_keyboard(item_cart_id, is_cart=False):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    cart_callback = ''
    if is_cart:
        cart_callback = 'cart|'

    keyboard.add(types.InlineKeyboardButton(text='-1',
                                            callback_data=f'remove_one_item|{cart_callback}{item_cart_id}'),
                 types.InlineKeyboardButton(text='+1',
                                            callback_data=f'add_one_item|{cart_callback}{item_cart_id}'))

    keyboard.add(types.InlineKeyboardButton(text='❌ Видалити з корзини',
                                            callback_data=f'remove_cart_item|{cart_callback}{item_cart_id}'))

    return keyboard


def item_control_with_cart_keyboard(item_cart_id):
    keyboard = item_control_keyboard(item_cart_id)
    keyboard.add(types.InlineKeyboardButton('🛒 Перейти до корзини', callback_data=f'show_cart'))

    return keyboard


def back_to_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    keyboard.add(types.KeyboardButton('🔙 До головного меню'))

    return keyboard


# Temp function
def get_cart_item_text(product_title, quantity=None, price=None, subtotal=None, is_cart=False, only_added=False):
    if is_cart:
        message_text = f'<b>{product_title}</b>\n\n' \
                       f'Кількість: {quantity}\n' \
                       f'Ціна за ед.: {price}\n' \
                       f'Загальная ціна: {subtotal}\n'
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

        text_message = get_cart_item_text(product_title=cart_item.product.title,
                                          quantity=item_quantity,
                                          price=item_price,
                                          subtotal=item_subtotal,
                                          is_cart=True)
        keyboard = item_control_keyboard(cart_item.pk, is_cart=True)

        subtotal_message, subtotal_keyboard = get_subtotal_text_and_keyboard(cart_item.cart)
        bot.edit_message_text(text=subtotal_message,
                              chat_id=obj.message.chat.id,
                              message_id=cart_item.cart.total_message_id,
                              reply_markup=subtotal_keyboard)
    else:
        text_message = get_cart_item_text(product_title=cart_item.product.title,
                                          quantity=cart_item.quantity)
        keyboard = item_control_with_cart_keyboard(cart_item.pk)

    if obj.message.content_type == 'photo':
        bot.edit_message_caption(caption=text_message,
                                 chat_id=obj.message.chat.id,
                                 message_id=obj.message.message_id,
                                 reply_markup=keyboard)
    else:
        bot.edit_message_text(text=text_message,
                              chat_id=obj.message.chat.id,
                              message_id=obj.message.message_id,
                              reply_markup=keyboard)


def get_subtotal_text_and_keyboard(cart):
    subtotal, quantity = cart.get_subtotal
    if subtotal:
        subtotal_message = f'Загальная сума замовлення: {subtotal} грн.\n\n' \
                           f'Кількість товарів: {quantity}'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton('Зробити замовлення', callback_data='new_order'))
    else:
        subtotal_message = 'Вже немає чого купувати. Додайте щось і ми продовжимо.'
        keyboard = None

    return subtotal_message, keyboard
