# Generated by Django 2.2.3 on 2019-08-08 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_signal_notifier', '0015_auto_20190808_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='verb',
            field=models.CharField(choices=[('pre_init', 'pre_init'), ('post_init', 'post_init'), ('pre_save', 'pre_save'), ('post_save', 'post_save'), ('pre_delete', 'pre_delete'), ('post_delete', 'post_delete'), ('m2m_changed', 'm2m_changed'), ('pre_migrate', 'pre_migrate'), ('post_migrate', 'post_migrate')], db_index=True, max_length=128),
        ),
    ]