# Generated by Django 4.2.1 on 2023-10-12 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0014_item_red_flag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='red_flag',
        ),
        migrations.AddField(
            model_name='transaction',
            name='red_flag',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
