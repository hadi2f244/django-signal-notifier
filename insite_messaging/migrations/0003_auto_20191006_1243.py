# Generated by Django 2.2.6 on 2019-10-06 12:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('insite_messaging', '0002_auto_20191006_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='id',
            field=models.UUIDField(auto_created=True, default=uuid.UUID('0f6761f4-d84f-405e-a835-858e3edc655e'), editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID'),
        ),
    ]
