# Generated by Django 4.2.1 on 2023-06-22 11:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_alter_productservice_productp_service_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='revenuetype',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
