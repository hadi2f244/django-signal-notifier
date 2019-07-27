# Generated by Django 2.2.3 on 2019-07-27 13:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0004_auto_20190727_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='receiver_users',
            field=models.ManyToManyField(blank=True, help_text='Users that are related to this subscription.', to=settings.AUTH_USER_MODEL, verbose_name='Receiver_Users'),
        ),
    ]
