# Generated by Django 5.2 on 2025-04-28 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationContext',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('user_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_intent', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('context_data', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_message', models.TextField()),
                ('bot_response', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('intent', models.CharField(blank=True, max_length=50, null=True)),
                ('confidence', models.FloatField(default=0.0)),
                ('has_media', models.BooleanField(default=False)),
                ('media_url', models.URLField(blank=True, null=True)),
                ('session_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
