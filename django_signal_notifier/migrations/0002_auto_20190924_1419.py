# Generated by Django 2.2.3 on 2019-09-24 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backend',
            name='message_template',
            field=models.CharField(choices=[('BaseMessageTemplate', 'BaseMessageTemplate'), ('SimpleEmailMessageTemplate', 'SimpleEmailMessageTemplate'), ('SimpleTelegramMessageTemplate1', 'SimpleTelegramMessageTemplate1'), ('SimpleTelegramMessageTemplate2', 'SimpleTelegramMessageTemplate2'), ('NewMessageTemplate', 'NewMessageTemplate')], default='BaseMessageTemplate', max_length=128),
        ),
        migrations.AlterField(
            model_name='backend',
            name='messenger',
            field=models.CharField(choices=[('SimplePrintMessenger', 'SimplePrintMessenger'), ('SimplePrintMessengerTemplateBased', 'SimplePrintMessengerTemplateBased'), ('SMTPEmailMessenger', 'SMTPEmailMessenger'), ('TelegramBotMessenger', 'TelegramBotMessenger'), ('NewMessenger', 'NewMessenger')], default='BaseMessanger', max_length=128),
        ),
    ]
