# Generated by Django 2.2.5 on 2019-10-04 07:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('insite_messaging', '0005_auto_20191004_0730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='id',
            field=models.UUIDField(auto_created=True, default=uuid.UUID('3cd4d5de-6717-4656-b4d1-0a6d4a2162e8'), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='updatemessages',
            name='id',
            field=models.UUIDField(auto_created=True, default=uuid.UUID('4a5e1c88-15bf-4385-bb88-b25b0da17c5b'), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID'),
        ),
    ]
