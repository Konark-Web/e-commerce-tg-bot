# Generated by Django 4.0.1 on 2022-02-01 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_alter_cart_total_message_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0, verbose_name='Ціна')),
                ('quantity', models.IntegerField(default=0, verbose_name='Кількість товару')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.customer')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.product')),
            ],
        ),
    ]
