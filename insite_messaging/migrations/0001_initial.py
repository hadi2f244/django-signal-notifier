# Generated by Django 2.2.5 on 2019-09-25 18:58

from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdateMessages',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('d53ae1a1-e4f5-4a6b-b108-ef3eacbf7289'), editable=False, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(blank=True)),
                ('context', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.TextField(null=True)),
                ('user_receivers', models.ManyToManyField(related_name='UserMessages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
