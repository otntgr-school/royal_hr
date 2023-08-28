# Generated by Django 4.0.5 on 2022-12-06 14:27

from django.db import migrations
from django.db.models import Count


class Migration(migrations.Migration):

    def _fix_data(apps, schema):
        User = apps.get_model('core', 'User')
        users = User.objects.values('phone_number').annotate(count=Count('id')).filter(count__gt=1)
        for user in users:
            phone_number = user['phone_number']
            User.objects.filter(phone_number=phone_number).update(phone_number=None)

    dependencies = [
        ('core', '0021_auto_20221206_1426'),
    ]

    operations = [
        migrations.RunPython(_fix_data)
    ]