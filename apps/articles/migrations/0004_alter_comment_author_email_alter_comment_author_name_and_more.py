# Generated by Django 5.2 on 2025-04-06 19:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author_email',
            field=models.EmailField(max_length=254, verbose_name='Seu E-mail'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author_name',
            field=models.CharField(max_length=100, verbose_name='Seu Nome'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Criado em'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(validators=[django.core.validators.MaxLengthValidator(1000)], verbose_name='Comentário'),
        ),
    ]
