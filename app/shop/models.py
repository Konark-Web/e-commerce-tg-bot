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

    class Meta:
        verbose_name = 'Категорія товару'
        verbose_name_plural = 'Категорії товарів'
