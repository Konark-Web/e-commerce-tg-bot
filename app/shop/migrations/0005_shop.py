# Generated by Django 4.0.1 on 2022-01-26 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_remove_customer_id_alter_customer_customer_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about', models.TextField(verbose_name='Про магазин')),
            ],
        ),
    ]
