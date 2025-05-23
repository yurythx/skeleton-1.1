# Generated by Django 5.2 on 2025-04-28 05:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0006_alter_compra_motorista_alter_compra_veiculo'),
        ('fornecedores', '0003_alter_fornecedor_options_and_more'),
        ('motoristas', '0002_remove_motorista_motoristas__slug_885285_idx_and_more'),
        ('produtos', '0004_remove_produto_estoque'),
        ('veiculos', '0002_alter_veiculo_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='compra',
            name='placa_veiculo',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='compra',
            name='uf_veiculo',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='compra',
            name='usuario_atualizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='compras_atualizadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='compra',
            name='usuario_criacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='compras_criadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='compra',
            name='valor_frete',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='compra',
            name='valor_outras_despesas',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='compra',
            name='valor_parcela',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='compra',
            name='valor_seguro',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='compra',
            name='forma_pagamento',
            field=models.CharField(choices=[('avista', 'À Vista'), ('prazo', 'A Prazo'), ('boleto', 'Boleto'), ('cartao', 'Cartão de Crédito'), ('pix', 'PIX'), ('transferencia', 'Transferência Bancária')], default='avista', max_length=20),
        ),
        migrations.AlterField(
            model_name='compra',
            name='status',
            field=models.CharField(choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('entregue', 'Entregue'), ('faturada', 'Faturada'), ('paga', 'Paga')], default='pendente', max_length=20),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['usuario_criacao'], name='compras_com_usuario_4ed9e7_idx'),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['usuario_atualizacao'], name='compras_com_usuario_121163_idx'),
        ),
        migrations.AddConstraint(
            model_name='compra',
            constraint=models.CheckConstraint(condition=models.Q(('valor_frete__gte', 0)), name='compra_valor_frete_nao_negativo'),
        ),
        migrations.AddConstraint(
            model_name='compra',
            constraint=models.CheckConstraint(condition=models.Q(('valor_seguro__gte', 0)), name='compra_valor_seguro_nao_negativo'),
        ),
        migrations.AddConstraint(
            model_name='compra',
            constraint=models.CheckConstraint(condition=models.Q(('valor_outras_despesas__gte', 0)), name='compra_valor_outras_despesas_nao_negativo'),
        ),
    ]
