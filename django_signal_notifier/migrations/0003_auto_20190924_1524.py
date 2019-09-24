# Generated by Django 2.2.3 on 2019-09-24 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0002_auto_20190924_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backend',
            name='messenger',
            field=models.CharField(choices=[('SimplePrintMessenger', 'SimplePrintMessenger'), ('SimplePrintMessengerTemplateBased', 'SimplePrintMessengerTemplateBased'), ('SMTPEmailMessenger', 'SMTPEmailMessenger'), ('TelegramBotMessenger', 'TelegramBotMessenger'), ('NewMessenger', 'NewMessenger'), ('InsitMessagingMessenger', 'InsitMessagingMessenger')], default='BaseMessanger', max_length=128),
        ),
    ]
