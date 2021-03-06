# Generated by Django 4.0.1 on 2022-01-25 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_category_options_remove_category_order_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.CharField(max_length=100, verbose_name='Telegram ID')),
                ('username', models.CharField(blank=True, default=None, max_length=200, null=True, verbose_name='Username користувача')),
                ('customer_name', models.CharField(max_length=255, null=True, verbose_name='ФІО користувача')),
                ('phone_number', models.CharField(blank=True, default='', max_length=64, verbose_name='Номер телефону')),
                ('city', models.CharField(blank=True, default='', max_length=200, verbose_name='Місто')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Дата реєстрації')),
                ('state', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Клієнт',
                'verbose_name_plural': 'Клієнти',
            },
        ),
    ]
