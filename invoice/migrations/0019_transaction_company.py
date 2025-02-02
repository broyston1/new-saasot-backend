# Generated by Django 4.2.1 on 2024-03-14 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_alter_customuser_role'),
        ('invoice', '0018_alter_arrgraceperiod_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_transaction', to='authentication.company'),
        ),
    ]
