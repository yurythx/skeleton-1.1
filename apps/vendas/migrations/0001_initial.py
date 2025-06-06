# Generated by Django 5.2 on 2025-04-25 18:00

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0009_cliente_cnpj_alter_cliente_cpf'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_venda', models.DateTimeField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')], default='pendente', max_length=15)),
                ('desconto', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('valor_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendas', to='clientes.cliente')),
            ],
        ),
    ]
