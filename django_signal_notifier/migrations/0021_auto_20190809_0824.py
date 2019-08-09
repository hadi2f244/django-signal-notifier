# Generated by Django 2.2.3 on 2019-08-09 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0020_remove_messagetemplate_context_template_str'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backend',
            name='message_template',
            field=models.CharField(choices=[('BaseMessageTemplate', 'BaseMessageTemplate')], default='BaseMessageTemplate', max_length=128),
        ),
    ]