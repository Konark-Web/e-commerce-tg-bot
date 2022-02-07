import requests

from telebot import types
from itertools import chain
from django.core.paginator import Paginator

from . import keyboards as kb
from tbot.models import BotConfig
from shop.models import Category, Product, ProductImage, Shop, Order, OrderItem

from tbot.modules.customer import (get_or_create_user, add_state_user, change_customer_name,
                                   change_customer_phone, change_customer_city, change_customer_address,
                                   get_user_by_id)
from tbot.modules.catalog import get_product_by_id
from tbot.modules.cart import (get_or_create_cart, get_or_create_cart_item, get_cart_item_by_id,
                               get_cart_items, is_product_empty_by_item, has_user_empty_products,
                               cart_total_changed, cart_quantity_changed)
from tbot.modules.order import create_order
from tbot.modules.additional_functions import validate_phone_number, get_nova_poshta_api


def start_message(message, bot):
    user_info = {
        'telegram_id': message.from_user.id,
        'username': message.from_user.username,
    }

    customer, new_customer = get_or_create_user(user_info)
    add_state_user(message.from_user.id)

    if new_customer:
        bot.send_message(message.from_user.id,
                         'Вітаємо!\n\n'
                         'Вас вітає магазин кальянних аксесуарів. '
                         'У нас Ви зможете купити все для комфортного проведення часу.\n\n'
                         'Давайте пройдемо коротку реєстрацію, але Ви можете її пропустити.',
                         reply_markup=kb.registration_keyboard())
    else:
        bot.send_message(message.from_user.id,
                         '<b>Ви перейшли до головного меню.</b>\n\n'
                         '🛍 Каталог - пошук та купівля товару\n'
                         '🛒 Корзина - оформлення замовлень\n'
                         'ℹ️ Про магазин - більше інформації про нас\n'
                         '👤 Мої замовлення - перегляд попередніх замовлень\n'
                         '🔎 Пошук - пошук по каталогу товарів магазину',
                         reply_markup=kb.main_keyboard())


def reg_customer_name(message, bot):
    add_state_user(message.from_user.id, 'reg_customer_name')
    bot.send_message(message.from_user.id, 'Введіть ваш ПІБ', reply_markup=kb.skip_keyboard())


def reg_customer_phone(message, bot):
    change_customer_name(message.from_user.id, message.text)
    add_state_user(message.from_user.id, 'reg_customer_phone')
    bot.send_message(message.from_user.id,
                     'Введіть або розшарте ваш номер телефону.',
                     reply_markup=kb.number_keyboard())


def reg_customer_city(message, bot):
    customer_phone = get_phone_number(message, bot)
    if not customer_phone:
        return

    change_customer_phone(message.from_user.id, customer_phone)
    add_state_user(message.from_user.id, 'reg_customer_city')
    bot.send_message(message.from_user.id, 'Введіть або виберіть з списку своє місто.', reply_markup=kb.skip_keyboard())
    bot.send_message(message.from_user.id,
                     f'Для пошуку міста натисніть "Пошук" та введіть назву населенного пункту.',
                     reply_markup=kb.search_keyboard())


def reg_customer_finish(message, bot):
    user_id = message.from_user.id
    if message.result_id:
        customer_city = message.result_id.split('|')[-1]
    else:
        customer_city = message.text

    user = get_user_by_id(user_id)
    change_customer_city(user_id, customer_city)
    add_state_user(user_id)

    bot.send_message(user_id, f'Дякую за реєстрацію, {user.customer_name}!\n\n'
                              f'Тепер Ви можете перейти до покупок.')
    start_message(message, bot)


def registration_skip(message, bot):
    add_state_user(message.from_user.id)
    start_message(message, bot)


def show_catalog(obj, bot, page_num=1):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard_page_btn = []
    categories = Category.objects.filter(is_active=True).distinct()
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
        bot.edit_message_reply_markup(obj.from_user.id, obj.message.message_id, reply_markup=keyboard)


def show_products_list(obj, bot, category_id, page_num=1):
    products_stock = Product.objects.filter(category=category_id, quantity__gt=0, is_active=True).distinct()
    products_out_of_stock = Product.objects.filter(category=category_id, quantity__lte=0, is_active=True).distinct()
    products = list(
        sorted(
            chain(products_stock, products_out_of_stock),
            key=lambda objects: objects.is_active
        )
    )
    paginator = Paginator(products, 5)
    products_per_page = paginator.get_page(page_num)

    category = Category.objects.filter(pk=category_id).first()
    bot.send_message(obj.from_user.id,
                     f'🛍 Каталог товарів з категорії <b>{category.name}</b>\n'
                     f'Сторінка {products_per_page.number}/{products_per_page.paginator.num_pages}')

    if not products:
        bot.send_message(obj.from_user.id, 'Нажаль, активних товарів в цій категорії немає.')
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
            bot.edit_message_reply_markup(obj.from_user.id, obj.message.message_id, reply_markup=keyboard)

        if index == len(products_per_page) and products_per_page.has_next():
            next_page = products_per_page.next_page_number()
            keyboard.add(types.InlineKeyboardButton('Загрузити більше товарів',
                                                    callback_data=f'products_more|{product.category.pk}|{next_page}'))

        if product.image:
            bot.send_photo(obj.from_user.id, product.image, product_text, reply_markup=keyboard)
        else:
            bot.send_message(obj.from_user.id, product_text, reply_markup=keyboard)


def show_product(obj, bot, product_id, img_num=1):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    product = Product.objects.filter(pk=product_id)
    images = ProductImage.objects.filter(product__pk=product_id)

    product_images = list(
        sorted(
            chain(product, images),
            key=lambda objects: objects.pk
        )
    )

    product = product[0]
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
            bot.edit_message_media(types.InputMedia(type='photo', media=product_image[0].image),
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
    bot.delete_message(obj.from_user.id, obj.message.message_id)


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
        bot.send_message(obj.from_user.id,
                         get_cart_item_text(product_title=product.title),
                         reply_markup=kb.item_control_with_cart_keyboard(cart_item.pk))


def remove_product_from_cart(obj, bot, item_id, is_cart=False):
    cart_item = get_cart_item_by_id(item_id)
    cart_item.is_active = False
    cart_item.save()

    bot.delete_message(obj.from_user.id, obj.message.message_id)
    bot.answer_callback_query(obj.id,
                              f'Товар успішно видалений с корзини.',
                              show_alert=False)

    if is_cart:
        subtotal_message, subtotal_keyboard = get_subtotal_text_and_keyboard(cart_item.cart)
        bot.edit_message_text(text=subtotal_message,
                              chat_id=obj.from_user.id,
                              message_id=cart_item.cart.total_message_id,
                              reply_markup=subtotal_keyboard)


def remove_empty_products(obj, bot):
    cart = get_or_create_cart(obj.from_user.id)
    cart_items = get_cart_items(cart[0].pk)
    count = 0

    for item in cart_items:
        if is_product_empty_by_item(item):
            item.is_active = False
            item.save()

            count += 1

    bot.send_message(obj.from_user.id, f'Неактивні товари успішно видалені з корзини у кількості: {count}')
    show_cart(obj, bot)


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

    if isinstance(obj, types.CallbackQuery):
        bot.send_message(obj.from_user.id, '🛒 Корзина', reply_markup=kb.main_keyboard())

    if not cart_items:
        bot.send_message(obj.from_user.id, 'Нажаль, корзина поки що порожня.', reply_markup=kb.main_keyboard())
        return

    for item in cart_items:
        item_quantity = item.quantity
        item_price = item.product.price
        item_subtotal = item_quantity * item_price

        item_keyboard = kb.item_control_keyboard(item.pk, is_cart=True)
        text_message = get_cart_item_text(product_title=item.product.title,
                                          quantity=item_quantity,
                                          price=item_price,
                                          subtotal=item_subtotal,
                                          is_cart=True,
                                          item=item)

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


def new_order_customer_name(obj, bot, need_change=False):
    user_id = obj.from_user.id
    user = get_user_by_id(user_id)

    if cart_changed(obj, bot):
        return

    if (user.customer_name and user.phone_number and user.address) and not need_change:
        new_order_finish(obj, bot, True, True)
        return

    bot.send_message(obj.from_user.id, 'Давайте почнемо оформлювати замовлення.')
    add_state_user(user_id, 'new_order_customer_name')

    if user.customer_name:
        bot.send_message(chat_id=user_id,
                         text=f'У Вас вже встановленне ім\'я. Введіть нове чи підтвердіть поточне.\n'
                              f'Зараз: {user.customer_name}',
                         reply_markup=kb.order_keyboard(True))
    else:
        bot.send_message(chat_id=user_id,
                         text=f'Введіть ім\'я людини яка буде забирати замовлення.',
                         reply_markup=kb.order_keyboard())


def new_order_phone(obj, bot, confirmed=False):
    user_id = obj.from_user.id
    user = get_user_by_id(user_id)

    if not confirmed:
        user = change_customer_name(user_id, obj.text)
        bot.send_message(user_id, f'✅ Ім\'я успішно змінено на {user.customer_name}.')

    add_state_user(user_id, 'new_order_phone')

    if user.phone_number:
        bot.send_message(chat_id=user_id,
                         text=f'У Вас вже встановленний номер телефону. '
                              f'Введіть новий (або поширте за допомогою кнопки нижче) чи підтвердіть поточний.\n'
                              f'Зараз: {user.phone_number}',
                         reply_markup=kb.order_keyboard(info=True, number=True))
    else:
        bot.send_message(chat_id=user_id,
                         text=f'Введіть номер телефону або поширте його за допомогою кнопки нижче.',
                         reply_markup=kb.order_keyboard(number=True))


def new_order_delivery(obj, bot, confirmed=False):
    user_id = obj.from_user.id
    user = get_user_by_id(user_id)
    keyboard = kb.search_keyboard()

    if not confirmed:
        customer_phone = get_phone_number(obj, bot)
        if not customer_phone:
            return

        user = change_customer_phone(user_id, customer_phone)
        bot.send_message(user_id, f'✅ Номер телефону успішно змінено на {user.phone_number}.')

    add_state_user(user_id, 'new_order_delivery')

    if user.city and user.address:
        bot.send_message(chat_id=user_id,
                         text=f'У Вас вже встановлена адреса доставки. '
                              f'Виберіть нову у формі пошуку нижче чи підтвердіть поточну.\n'
                              f'Зараз: {user.address}, {user.city} ',
                         reply_markup=kb.order_keyboard(info=True))
    else:
        if user.city:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton('Пошук', switch_inline_query_current_chat=user.city))

        bot.send_message(chat_id=user_id,
                         text=f'Виберіть відділення Нової Пошти у формі пошуку нижче.',
                         reply_markup=kb.order_keyboard())

    bot.send_message(obj.from_user.id,
                     f'Для пошуку відділення Нової Пошти натисніть "Пошук" та введіть назву населенного пункту.',
                     reply_markup=keyboard)


def new_order_finish(obj, bot, confirmed=False, from_cart=False):
    user_id = obj.from_user.id
    user = get_user_by_id(user_id)
    add_state_user(user_id, 'new_order_finish')

    if not confirmed:
        response = requests.post('https://api.novaposhta.ua/v2.0/json/', json={
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "Ref": obj.result_id
            },
            "apiKey": get_nova_poshta_api()
        })

        nova_poshta_post = response.json()['data']
        change_customer_city(user_id, city=nova_poshta_post[0]['CityDescription'])

        user = change_customer_address(user_id,
                                       address=nova_poshta_post[0]['Description'],
                                       post_number=nova_poshta_post[0]['Number'])

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton('Підтвердити', callback_data='confirm_order'),
                 types.InlineKeyboardButton('Змінити', callback_data='change_order_info'))

    if from_cart:
        bot.send_message(user_id, 'Останній крок.', reply_markup=kb.back_to_cart_keyboard())
    else:
        bot.send_message(user_id, 'Ми вже на фініші.', reply_markup=kb.order_keyboard())

    bot.send_message(user_id,
                     f'Перевірте коректність данних для замовлення:\n'
                     f'Ім\'я: {user.customer_name}\n'
                     f'Номер телефону: {user.phone_number}\n'
                     f'Адреса доставки: {user.address}, {user.city}',
                     reply_markup=keyboard)


def create_new_order(obj, bot):
    user_id = obj.from_user.id
    add_state_user(user_id)

    if cart_changed(obj, bot):
        return

    order = create_order(user_id)
    if order:
        bot.send_message(user_id, f'Замовлення №{order.pk} успішно створенний!', reply_markup=kb.main_keyboard())
    else:
        bot.send_message(user_id,
                         'Можливо замовлення вже створено, чи корзина порожня.',
                         reply_markup=kb.main_keyboard())


def search_nova_poshta(search, query, bot):
    inlines = []
    response = requests.post('https://api.novaposhta.ua/v2.0/json/', json={
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "CityName": search
        },
        "apiKey": get_nova_poshta_api()
    })

    nova_poshta_posts = response.json()['data']
    offset = int(query.offset) if query.offset else 0

    for result in nova_poshta_posts:
        inlines.append(types.InlineQueryResultArticle(
            id=result['Ref'],
            title=result['ShortAddress'],
            description=result['Description'],
            input_message_content=types.InputVenueMessageContent(
                latitude=float(result['Latitude']),
                longitude=float(result['Longitude']),
                title=result['Description'],
                address=result['ShortAddress']
            )
        ))

    next_offset = f"{offset + 10}"
    bot.answer_inline_query(
        inline_query_id=query.id,
        results=inlines[offset: offset + 10],
        cache_time=0,
        next_offset=next_offset
    )


def search_city(search, query, bot):
    inlines = []
    response = requests.post('https://api.novaposhta.ua/v2.0/json/', json={
        "modelName": "AddressGeneral",
        "calledMethod": "getSettlements",
        "methodProperties": {
            "FindByString": search
        },
        "apiKey": get_nova_poshta_api()
    })

    cities = response.json()['data']
    offset = int(query.offset) if query.offset else 0

    for result in cities:
        title = f'{result["Description"]} ({result["SettlementTypeDescription"]})'

        if result['RegionsDescription']:
            description = f'{result["RegionsDescription"]}, {result["AreaDescription"]}'
        else:
            description = f'{result["AreaDescription"]}'

        inlines.append(types.InlineQueryResultArticle(
            id=f'{result["Ref"]}|{result["Description"]}',
            title=title,
            description=description,
            input_message_content=types.InputVenueMessageContent(
                latitude=float(result['Latitude']),
                longitude=float(result['Longitude']),
                title=result['Description'],
                address=f'{result["Description"]}, {result["AreaDescription"]}'
            )
        ))

    next_offset = f"{offset + 10}"
    bot.answer_inline_query(
        inline_query_id=query.id,
        results=inlines[offset: offset + 10],
        cache_time=0,
        next_offset=next_offset
    )


def new_order_skip(obj, bot):
    add_state_user(user_id=obj.from_user.id)
    bot.send_message(obj.from_user.id, '🛒 Корзина', reply_markup=kb.main_keyboard())
    show_cart(obj, bot)


def show_user_orders(obj, bot, page_num=1):
    user_id = obj.from_user.id

    orders = Order.objects.filter(customer=user_id)
    paginator = Paginator(orders, 5)
    orders_per_page = paginator.get_page(page_num)

    if not orders:
        bot.send_message(obj.from_user.id, 'Ви поки що не нічого не купили.', reply_markup=kb.back_to_main_keyboard())
        return

    if page_num == 1:
        bot.send_message(user_id, 'Список Ваших замовлень:', reply_markup=kb.back_to_main_keyboard())

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for index, order in enumerate(orders_per_page, start=1):
        order_items = OrderItem.objects.filter(order=order.pk)
        text_message = f'<b>Замовлення №{order.pk}</b>\n\n'

        for index_item, order_item in enumerate(order_items, start=1):
            text_message += f'{index_item}. {order_item.product.title}\n' \
                            f'Сума: {order_item.total} ({order_item.price} x {order_item.quantity})\n'

        text_message += f'\n\n<b>Загальна сума замовлення:</b> {order.total}'

        if page_num != 1:
            bot.edit_message_reply_markup(obj.from_user.id, obj.message.message_id, reply_markup=keyboard)

        if index == len(orders_per_page) and orders_per_page.has_next():
            next_page = orders_per_page.next_page_number()
            keyboard.add(types.InlineKeyboardButton('Загрузити більше замовлень',
                                                    callback_data=f'orders_more|{next_page}'))

        bot.send_message(user_id, text_message, reply_markup=keyboard)


def show_about_shop(message, bot):
    about = Shop.objects.filter(is_active=True).first().about

    if about:
        bot.send_message(message.from_user.id, about, reply_markup=kb.back_to_main_keyboard())
    else:
        bot.send_message(message.from_user.id, 'Нажаль, поки немає інформації про магазин.',
                         reply_markup=kb.back_to_main_keyboard())


def show_search_button(message, bot):
    bot.send_message(message.from_user.id,
                     f'Для пошука товару в нашому магазині натисніть "Пошук" та введіть назву товару.',
                     reply_markup=kb.search_keyboard())


def search_product(search, query, bot):
    inlines = []
    results = Product.objects.filter(title__icontains=search, is_active=True)
    offset = int(query.offset) if query.offset else 0
    bot_url = BotConfig.objects.get(is_active=True).server_url

    for result in results:
        inlines.append(types.InlineQueryResultArticle(
            id=result.pk,
            title=result.title,
            description=result.excerpt,
            thumb_url=bot_url + result.image.url,
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


# Additional functions
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
            message_text += '\n<b>Нажаль, товару немає у наявності. Перед оформленням замовлення,' \
                            ' будь-ласка видаліть цей товар з корзини.</b>'

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
        keyboard = kb.item_control_keyboard(cart_item.pk, is_cart=True)

        subtotal_message, subtotal_keyboard = get_subtotal_text_and_keyboard(cart_item.cart)
        bot.edit_message_text(text=subtotal_message,
                              chat_id=obj.from_user.id,
                              message_id=cart_item.cart.total_message_id,
                              reply_markup=subtotal_keyboard)
    else:
        text_message = get_cart_item_text(product_title=cart_item.product.title,
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

            keyboard.add(types.InlineKeyboardButton('Зробити замовлення', callback_data='new_order'))
        else:
            keyboard.add(types.InlineKeyboardButton('Видалити неактуальні товари',
                                                    callback_data='remove_empty_products'))
            subtotal_message += '\n\n<b>Для того щоб почати оформлювати замовлення, видаліть з корзини ' \
                                'товари яких немає у наявності.</b>'
    else:
        subtotal_message = 'Вже немає чого купувати. Додайте щось і ми продовжимо.'
        keyboard = None

    return subtotal_message, keyboard


def cart_changed(obj, bot):
    user_id = obj.from_user.id

    if has_user_empty_products(user_id):
        bot.send_message(obj.from_user.id, '⛔ Вибачте, ми не зможемо оформити замовлення. '
                                           'Ви маєте товари в корзині яких немає в наявності')
        show_cart(obj, bot)
        return True

    if cart_total_changed(user_id):
        bot.send_message(obj.from_user.id, '⛔ Схоже ціни на товар змінилися, перевірте будь-ласка корзину.')
        show_cart(obj, bot)
        return True

    if cart_quantity_changed(user_id):
        bot.send_message(obj.from_user.id, '⛔ Схоже кількість наявних товарів змінилась, перевірте будь-ласка корзину.')
        show_cart(obj, bot)
        return True

    return False


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
