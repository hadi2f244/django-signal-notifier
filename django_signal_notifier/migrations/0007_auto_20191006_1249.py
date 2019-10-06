# Generated by Django 2.2.5 on 2019-10-06 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0006_auto_20191006_0735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='enabled',
        ),
        migrations.AlterField(
            model_name='subscription',
            name='trigger',
            field=models.ForeignKey(help_text='Trigger that is related to this subscription.', on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='django_signal_notifier.Trigger'),
        ),
    ]
