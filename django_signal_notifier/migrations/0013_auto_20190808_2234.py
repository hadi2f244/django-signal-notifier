# Generated by Django 2.2.3 on 2019-08-08 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0012_auto_20190804_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='verb',
            field=models.CharField(choices=[('a', 'a')], db_index=True, max_length=128),
        ),
    ]
