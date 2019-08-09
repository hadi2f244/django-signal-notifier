# Generated by Django 2.2.3 on 2019-08-09 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0018_auto_20190808_2351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backend',
            name='template',
        ),
        migrations.AddField(
            model_name='backend',
            name='message_template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_signal_notifier.MessageTemplate'),
        ),
    ]
