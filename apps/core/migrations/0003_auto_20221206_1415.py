# Generated by Django 4.0.5 on 2022-12-06 14:15

from django.contrib.auth.hashers import make_password
from django.db import migrations


class Migration(migrations.Migration):

    def create_superuser(apps, schema_editor):

        User = apps.get_model('core', 'User')
        User.objects.create(
            email='admin@yopmail.com',
            username='admin',
            phone_number=0000000,
            is_superuser=True,
            password=make_password("admin")
        )

    dependencies = [
        ('core', '0002_auto_20221206_1413'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]