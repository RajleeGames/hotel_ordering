# Generated by Django 5.1.7 on 2025-03-29 04:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read_by',
            field=models.ManyToManyField(blank=True, related_name='read_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
