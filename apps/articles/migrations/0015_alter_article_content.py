# Generated by Django 5.2 on 2025-04-23 13:56

import django_quill.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0014_alter_article_options_alter_comment_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=django_quill.fields.QuillField(),
        ),
    ]
