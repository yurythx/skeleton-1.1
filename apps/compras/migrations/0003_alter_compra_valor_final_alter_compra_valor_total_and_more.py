# Generated by Django 5.2 on 2025-04-28 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0002_compra_data_atualizacao_compra_data_criacao_and_more'),
        ('fornecedores', '0003_alter_fornecedor_options_and_more'),
        ('produtos', '0004_remove_produto_estoque'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='valor_final',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='compra',
            name='valor_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['status'], name='compras_com_status_255035_idx'),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['data_compra'], name='compras_com_data_co_26d5f8_idx'),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['fornecedor'], name='compras_com_fornece_73ae7d_idx'),
        ),
        migrations.AddIndex(
            model_name='compra',
            index=models.Index(fields=['produto'], name='compras_com_produto_a4b736_idx'),
        ),
        migrations.AddConstraint(
            model_name='compra',
            constraint=models.CheckConstraint(condition=models.Q(('valor_total__gte', 0)), name='compra_valor_total_nao_negativo'),
        ),
        migrations.AddConstraint(
            model_name='compra',
            constraint=models.CheckConstraint(condition=models.Q(('desconto__gte', 0)), name='compra_desconto_nao_negativo'),
        ),
        migrations.AddConstraint(
            model_name='compra',
            constraint=models.CheckConstraint(condition=models.Q(('valor_final__gte', 0)), name='compra_valor_final_nao_negativo'),
        ),
    ]
