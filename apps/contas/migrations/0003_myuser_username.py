# Generated by Django 5.0.6 on 2024-07-13 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0002_alter_myuser_options_alter_myuser_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='username',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]