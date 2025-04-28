from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from unidecode import unidecode
import re

class Cliente(models.Model):
    """Modelo de Cliente com integração financeira."""

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-data_cadastro']

    # Informações básicas
    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=False, max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    endereco = models.OneToOneField('enderecos.Endereco', on_delete=models.CASCADE, null=True, blank=True)
    
    # Campos financeiros
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_devedor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=[
            ('ativo', 'Ativo'),
            ('inativo', 'Inativo'),
            ('bloqueado', 'Bloqueado'),
            ('pre_cadastro', 'Pré-cadastro')
        ],
        default='pre_cadastro'
    )
    
    # Campos de controle
    observacoes = models.TextField(blank=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ultima_compra = models.DateTimeField(null=True, blank=True)
    total_compras = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_servicos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nome

    def clean(self):
        """Validações e formatações personalizadas de CPF e CNPJ."""
        if self.cpf:
            cpf_numeros = re.sub(r'\D', '', self.cpf)
            if len(cpf_numeros) != 11:
                raise ValidationError({'cpf': "CPF deve conter 11 dígitos."})
            self.cpf = f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
        
        if self.cnpj:
            cnpj_numeros = re.sub(r'\D', '', self.cnpj)
            if len(cnpj_numeros) != 14:
                raise ValidationError({'cnpj': "CNPJ deve conter 14 dígitos."})
            self.cnpj = f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:]}"
        
        if not self.cpf and not self.cnpj:
            raise ValidationError("Informe pelo menos o CPF ou o CNPJ.")

    def save(self, *args, **kwargs):
        """Geração automática e segura de slug único."""
        if not self.slug:
            base_slug = slugify(unidecode(self.nome))
            slug = base_slug
            counter = 1
            while Cliente.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        self.full_clean()
        super().save(*args, **kwargs)

    def atualizar_saldo_devedor(self):
        """Atualiza o saldo devedor do cliente."""
        from apps.financeiro.models import MovimentacaoFinanceira, Parcela
        
        # Soma todas as parcelas não quitadas
        parcelas_nao_quitadas = Parcela.objects.filter(
            movimentacao__cliente=self,
            quitado=False
        ).aggregate(total=models.Sum('valor_total'))['total'] or 0
        
        self.saldo_devedor = parcelas_nao_quitadas
        self.save()

    def verificar_limite_credito(self, valor):
        """Verifica se o cliente tem limite de crédito suficiente."""
        if self.status != 'ativo':
            raise ValidationError("Cliente não está ativo para realizar compras.")
        
        if self.saldo_devedor + valor > self.limite_credito:
            raise ValidationError("Limite de crédito insuficiente para esta operação.")
        
        return True

    def registrar_compra(self, valor):
        """Registra uma compra do cliente."""
        self.verificar_limite_credito(valor)
        self.total_compras += valor
        self.ultima_compra = timezone.now()
        self.save()

    def registrar_servico(self, valor):
        """Registra um serviço prestado ao cliente."""
        self.verificar_limite_credito(valor)
        self.total_servicos += valor
        self.save()

    def registrar_pagamento(self, valor):
        """Registra um pagamento do cliente."""
        self.saldo_devedor -= valor
        if self.saldo_devedor < 0:
            self.saldo_devedor = 0
        self.save()

    def ativar(self):
        """Ativa o cliente."""
        self.status = 'ativo'
        self.save()

    def bloquear(self):
        """Bloqueia o cliente."""
        self.status = 'bloqueado'
        self.save()

    def inativar(self):
        """Inativa o cliente."""
        self.status = 'inativo'
        self.save()

    @property
    def tem_debito(self):
        """Verifica se o cliente tem débitos."""
        return self.saldo_devedor > 0

    @property
    def limite_disponivel(self):
        """Retorna o limite de crédito disponível."""
        return self.limite_credito - self.saldo_devedor

    @property
    def total_gasto(self):
        """Retorna o total gasto pelo cliente."""
        return self.total_compras + self.total_servicos
