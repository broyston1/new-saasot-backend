# Generated by Django 4.2.1 on 2023-06-20 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productservicetype',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
