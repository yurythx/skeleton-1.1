# Generated by Django 5.2 on 2025-04-25 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Veiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.CharField(max_length=100)),
                ('modelo', models.CharField(max_length=100)),
                ('ano', models.PositiveIntegerField()),
                ('placa', models.CharField(max_length=10, unique=True)),
                ('cor', models.CharField(max_length=50)),
                ('tipo', models.CharField(choices=[('carro', 'Carro'), ('moto', 'Moto'), ('caminhao', 'Caminhão'), ('outro', 'Outro')], default='carro', max_length=20)),
                ('chassi', models.CharField(max_length=50, unique=True)),
                ('renavam', models.CharField(max_length=20, unique=True)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Veículo',
                'verbose_name_plural': 'Veículos',
                'ordering': ['marca', 'modelo', 'ano'],
                'indexes': [models.Index(fields=['slug'], name='veiculos_ve_slug_ee61ff_idx'), models.Index(fields=['placa'], name='veiculos_ve_placa_9de55e_idx')],
            },
        ),
    ]
