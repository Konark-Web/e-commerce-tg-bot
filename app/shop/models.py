from django.db import models


class Customer(models.Model):
    telegram_id = models.CharField('Telegram ID', max_length=100,
                                   primary_key=True)
    username = models.CharField('Username', max_length=200, blank=True,
                                null=True, default=None)
    customer_name = models.CharField('ФІО користувача', max_length=255,
                                     blank=True, default='')
    phone_number = models.CharField('Номер телефону', max_length=64,
                                    blank=True, default='')
    city = models.CharField('Місто', max_length=200, blank=True, default='')
    address = models.CharField('Адреса доставки', max_length=255, blank=True,
                               default='')
    post_number = models.CharField('Номер відділення', max_length=32,
                                   blank=True, default='')
    date_joined = models.DateTimeField('Дата реєстрації', auto_now_add=True)
    state = models.CharField(max_length=200, blank=True, null=True,
                             default=None, editable=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.customer_name:
            return f'[{self.telegram_id}] {self.customer_name}'
        else:
            return f'[{self.telegram_id}] {self.username}'

    def get_state(self):
        return self.state

    class Meta:
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'


class Category(models.Model):
    name = models.CharField('Назва категорії', max_length=50, blank=False)
    priority = models.IntegerField(
        'Пріоритет категорії',
        help_text='Чим вище пріоритет, тим вище відображається категорія',
        default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорія товару'
        verbose_name_plural = 'Категорії товарів'
        ordering = ('-priority',)


class Shop(models.Model):
    about = models.TextField('Про магазин')
    is_active = models.BooleanField(default=True)

    def set_active_about(self):
        if self.is_active:
            other_active_about = Shop.objects.filter(is_active=True)
            for about in other_active_about:
                if about.pk != self.pk:
                    about.is_active = False
                    about.save()

    def save(self, *args, **kwargs):
        self.set_active_about()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_active:
            return f'Актуальная інформація про магазин [{self.pk}]'
        else:
            return f'Неактивна інформація про магазин [{self.pk}]'

    class Meta:
        verbose_name = 'Інфо'
        verbose_name_plural = 'Інформація про магазин'


class Product(models.Model):
    title = models.CharField('Назва товару', max_length=100, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, verbose_name='Категорія',
                                 related_name='product')
    excerpt = models.CharField('Короткий опис', max_length=200, blank=True)
    description = models.TextField('Повний опис')
    image = models.ImageField('Зображення', upload_to='product-img/',
                              null=True, blank=True)
    price = models.FloatField('Ціна', default=0)
    quantity = models.IntegerField('Кількість товару', default=0)
    created = models.DateTimeField('Дата створення', auto_now_add=True,
                                   editable=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ('-id', )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True,
                                default=None, related_name='images')
    image = models.ImageField('Зображення', upload_to='product-img/',
                              null=True, blank=True)

    def __str__(self):
        return self.product.title


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 verbose_name='Клієнт', related_name='cart')
    total_price = models.FloatField(default=0)
    total_message_id = models.CharField(max_length=200, null=True,
                                        editable=False)

    @property
    def get_subtotal(self):
        active_items = CartItem.objects.filter(cart=self.pk, is_active=True,
                                               product__quantity__gt=0)
        total_price = 0
        quantity = 0

        for item in active_items:
            total_price += item.get_total_price
            quantity += item.quantity

        return total_price, quantity


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,
                             related_name='cart_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='cart_item')
    quantity = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    @property
    def get_total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    CHOICES = (
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('pending', 'Pending payment'),
        ('refunded', 'Refunded')
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 related_name='order')
    customer_name = models.CharField('ФІО покупця', max_length=255, default='')
    phone_number = models.CharField('Номер телефону', max_length=64,
                                    default='')
    city = models.CharField('Місто', max_length=200, default='')
    address = models.CharField('Адреса доставки', max_length=255, default='')
    post_number = models.CharField('Номер відділення', blank=True,
                                   max_length=32, default='')
    total = models.FloatField('Загальна сума замовлення', default=0)
    status = models.CharField('Статус замовлення', max_length=25, null=False,
                              default='processing', choices=CHOICES)

    def __str__(self):
        return f'Замовлення №{self.pk}: {self.customer_name} ' \
               f'({self.total} грн.)'

    def update_price(self):
        order_items = OrderItem.objects.filter(order=self.pk)
        total = 0

        for order in order_items:
            total += order.price

        self.total = 5
        self.save()

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ('-id',)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                verbose_name='Товар', null=True)
    price = models.FloatField('Ціна', null=False, default=0)
    quantity = models.IntegerField(
        'Кількість товару',
        null=False,
        default=0,
        help_text='Коли даєте чи змінюєте замовлення, '
                  'переконайтесь що товар є на складі')
    total = models.FloatField('Загальна вартість', null=False, default=0)

    def __init__(self, *args, **kwargs):
        super(OrderItem, self).__init__(*args, **kwargs)
        self.old_quantity = self.quantity
        self.old_total = self.total

    def __str__(self):
        return f'{self.product.title} | Кількість: {self.quantity} | ' \
               f'Сумма: {self.total}'

    def changed_price_or_quantity(self):
        if self.price and self.quantity:
            self.total = self.quantity * self.price
            self.product.quantity = self.product.quantity - \
                                    (self.quantity - self.old_quantity)
            self.product.save()

    def add_new_cart_item(self):
        if not self.quantity and not self.price:
            self.price = self.product.price
            self.quantity = 1
            self.total = self.price * self.quantity
            self.product.quantity = self.product.quantity - 1
            self.product.save()

    def change_order_total(self):
        total_diff = self.total - self.old_total
        self.order.total = self.order.total + total_diff
        self.order.save()

    def delete(self, *args, **kwargs):
        self.order.total = self.order.total - self.total
        self.order.save()

        self.product.quantity = self.product.quantity + self.quantity
        self.product.save()

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.changed_price_or_quantity()
        self.add_new_cart_item()
        self.change_order_total()

        super().save(*args, **kwargs)
