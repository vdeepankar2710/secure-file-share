# Generated by Django 5.1.4 on 2025-01-06 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='salt',
            field=models.CharField(default=24345346546, max_length=50),
            preserve_default=False,
        ),
    ]
