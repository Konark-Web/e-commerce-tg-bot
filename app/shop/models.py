from django.db import models


class Customer(models.Model):
    telegram_id = models.CharField('Telegram ID', max_length=100, primary_key=True)
    username = models.CharField('Username', max_length=200,
                                blank=True, null=True, default=None)
    customer_name = models.CharField('ФІО користувача', max_length=255, default='')
    phone_number = models.CharField('Номер телефону', max_length=64, blank=True, default='')
    city = models.CharField('Місто', max_length=200, blank=True, default='')
    date_joined = models.DateTimeField('Дата реєстрації', auto_now_add=True)
    state = models.CharField(max_length=200, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.telegram_id} {self.username}'

    def get_state(self):
        return self.state

    class Meta:
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'


class Category(models.Model):
    name = models.CharField('Назва категорії', max_length=50, blank=False)
    priority = models.IntegerField('Пріоритет категорії',
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

    class Meta:
        verbose_name_plural = 'Інформація про магазин'


class Product(models.Model):
    title = models.CharField('Назва товару', max_length=100, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                 verbose_name='Категорія', related_name='product')
    excerpt = models.CharField('Короткий опис', max_length=200, blank=True)
    description = models.TextField('Повний опис')
    image = models.ImageField('Зображення', upload_to='product-img/', null=True, blank=True)
    price = models.FloatField('Ціна', default=0)
    quantity = models.IntegerField('Кількість товару', default=0)
    created = models.DateTimeField('Дата створення', auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, default=None, related_name='images')
    image = models.ImageField('Зображення', upload_to='product-img/', null=True, blank=True)

    def __str__(self):
        return self.product.title

