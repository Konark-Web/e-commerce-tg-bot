# Generated by Django 4.0.1 on 2022-02-03 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_alter_order_post_number_alter_orderitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='total_price',
            field=models.FloatField(default=0),
        ),
    ]
