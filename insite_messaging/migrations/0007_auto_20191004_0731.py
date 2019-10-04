# Generated by Django 2.2.5 on 2019-10-04 07:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('insite_messaging', '0006_auto_20191004_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='id',
            field=models.UUIDField(auto_created=True, default=uuid.UUID('8afa8a6e-30f1-40e9-b4f1-2467a800821a'), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='updatemessages',
            name='id',
            field=models.UUIDField(auto_created=True, default=uuid.UUID('98e6bf63-4c44-4c52-bb49-ed5a2952ea38'), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID'),
        ),
    ]
