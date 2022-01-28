# Generated by Django 4.0.1 on 2022-01-26 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_shop'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shop',
            options={'verbose_name_plural': 'Інформація про магазин'},
        ),
        migrations.AddField(
            model_name='shop',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]