# Generated by Django 3.0.2 on 2020-02-04 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0002_auto_20191201_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='enabled',
            field=models.BooleanField(default=True, help_text='To enable and disable the trigger'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='enabled',
            field=models.BooleanField(default=True, help_text='To enable and disable the subscription'),
        ),
    ]
