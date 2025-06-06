# Generated by Django 5.2 on 2025-04-28 01:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caixa', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='caixa',
            options={'ordering': ['-data_abertura'], 'verbose_name': 'Caixa', 'verbose_name_plural': 'Caixas'},
        ),
        migrations.AddField(
            model_name='caixa',
            name='aberto_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='caixas_abertos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='caixa',
            name='data_abertura',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='caixa',
            name='data_fechamento',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='caixa',
            name='fechado_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='caixas_fechados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='caixa',
            name='observacoes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='caixa',
            name='saldo_inicial',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AddField(
            model_name='caixa',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='caixa',
            name='status',
            field=models.CharField(choices=[('aberto', 'Aberto'), ('fechado', 'Fechado')], default='aberto', max_length=20),
        ),
    ]
