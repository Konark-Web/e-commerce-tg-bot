# Generated by Django 4.0.1 on 2022-01-27 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_product_productimage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('-priority',), 'verbose_name': 'Категорія товару', 'verbose_name_plural': 'Категорії товарів'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Товар', 'verbose_name_plural': 'Товари'},
        ),
        migrations.AlterField(
            model_name='product',
            name='excerpt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Короткий опис'),
        ),
    ]
