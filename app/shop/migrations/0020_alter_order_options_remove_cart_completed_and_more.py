# Generated by Django 4.0.1 on 2022-02-04 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_orderitem_total'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-id',), 'verbose_name': 'Замовлення', 'verbose_name_plural': 'Замовлення'},
        ),
        migrations.RemoveField(
            model_name='cart',
            name='completed',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.product', verbose_name='Товар'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=0, help_text='Коли даєте чи змінюєте замовлення, переконайтесь що товар є на складі', verbose_name='Кількість товару'),
        ),
    ]
