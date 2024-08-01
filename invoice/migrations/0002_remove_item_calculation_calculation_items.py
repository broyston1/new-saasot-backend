# Generated by Django 4.2.1 on 2023-06-19 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='calculation',
        ),
        migrations.AddField(
            model_name='calculation',
            name='items',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='invoice.item'),
        ),
    ]
