# Generated by Django 2.2.5 on 2019-09-18 21:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insite_notifications', '0003_auto_20190918_2134'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messages',
            old_name='user_receiver',
            new_name='user_receivers',
        ),
    ]
