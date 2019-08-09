# Generated by Django 2.2.3 on 2019-08-08 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0017_auto_20190808_2314'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagetemplate',
            old_name='context_str',
            new_name='context_template_str',
        ),
        migrations.RemoveField(
            model_name='messagetemplate',
            name='file_name',
        ),
        migrations.AddField(
            model_name='messagetemplate',
            name='name',
            field=models.CharField(choices=[('BaseMessageTemplate', 'BaseMessageTemplate')], default='BaseMessageTemplate', max_length=128),
        ),
    ]
