# Generated by Django 2.2.3 on 2019-08-04 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0010_auto_20190804_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(default='base.html', max_length=255),
        ),
    ]