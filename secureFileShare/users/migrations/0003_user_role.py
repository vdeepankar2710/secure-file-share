# Generated by Django 5.1.4 on 2025-01-05 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_otp_user_otp_expiry'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'ADMIN'), ('REGULAR', 'REGULAR'), ('GUEST', 'GUEST')], default='GUEST', max_length=10),
        ),
    ]
