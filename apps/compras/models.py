from django.db import models, transaction
from apps.fornecedores.models import Fornecedor
from apps.estoque.models import Estoque
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal
from django.conf import settings

class Motorista(models.Model):
    """Modelo para cadastro de motoristas."""
    nome = models.CharField(max_length=100)
    cnh = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.cnh}"

class Veiculo(models.Model):
    """Modelo para cadastro de veículos."""
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    ano = models.PositiveIntegerField()
    cor = models.CharField(max_length=30)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.placa} - {self.modelo} {self.marca}"

class Compra(models.Model):
    """Modelo para registrar as compras de produtos aos fornecedores."""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('entregue', 'Entregue'),
        ('faturada', 'Faturada'),
        ('paga', 'Paga'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('avista', 'À Vista'),
        ('prazo', 'A Prazo'),
        ('boleto', 'Boleto'),
        ('cartao', 'Cartão de Crédito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência Bancária'),
    ]

    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='compras')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE, related_name='compras')
    quantidade = models.PositiveIntegerField()
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data_compra = models.DateTimeField(default=timezone.now)
    data_entrega = models.DateTimeField(null=True, blank=True)
    descricao = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Campos financeiros
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, default='avista')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    numero_parcelas = models.PositiveIntegerField(default=1)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Campos de controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)
    usuario_criacao = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='compras_criadas')
    usuario_atualizacao = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='compras_atualizadas')

    # Campos de nota fiscal e transporte
    numero_nota_fiscal = models.CharField(max_length=20, blank=True, null=True)
    serie_nota_fiscal = models.CharField(max_length=10, blank=True, null=True)
    data_emissao_nf = models.DateField(blank=True, null=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_seguro = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_outras_despesas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    motorista = models.ForeignKey('motoristas.Motorista', on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    veiculo = models.ForeignKey('veiculos.Veiculo', on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    data_chegada = models.DateTimeField(blank=True, null=True)
    data_saida = models.DateTimeField(blank=True, null=True)
    placa_veiculo = models.CharField(max_length=10, blank=True, null=True)
    uf_veiculo = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['data_compra']),
            models.Index(fields=['fornecedor']),
            models.Index(fields=['produto']),
            models.Index(fields=['numero_nota_fiscal']),
            models.Index(fields=['motorista']),
            models.Index(fields=['veiculo']),
            models.Index(fields=['usuario_criacao']),
            models.Index(fields=['usuario_atualizacao']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(valor_total__gte=0),
                name='compra_valor_total_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(desconto__gte=0),
                name='compra_desconto_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(valor_final__gte=0),
                name='compra_valor_final_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(valor_frete__gte=0),
                name='compra_valor_frete_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(valor_seguro__gte=0),
                name='compra_valor_seguro_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(valor_outras_despesas__gte=0),
                name='compra_valor_outras_despesas_nao_negativo'
            ),
        ]

    def __str__(self):
        return f"Compra de {self.quantidade} unidades de {self.produto.nome} de {self.fornecedor.nome} em {self.data_compra.strftime('%d/%m/%Y')}"

    def calcular_valores(self):
        """Calcula os valores totais da compra."""
        self.valor_total = Decimal(str(self.quantidade)) * self.custo_unitario
        self.valor_final = self.valor_total - self.desconto + self.valor_frete + self.valor_seguro + self.valor_outras_despesas
        
        if self.forma_pagamento == 'prazo' and self.numero_parcelas > 1:
            self.valor_parcela = self.valor_final / Decimal(str(self.numero_parcelas))
        else:
            self.valor_parcela = self.valor_final

    @transaction.atomic
    def criar_movimentacao_financeira(self):
        """Cria a movimentação financeira relacionada à compra."""
        from apps.financeiro.models import MovimentacaoFinanceira, Caixa
        
        caixa = Caixa.objects.filter(status='aberto').first()
        if not caixa:
            raise ValidationError("Não há caixa aberto para registrar a movimentação.")

        movimentacao = MovimentacaoFinanceira(
            tipo='saida',
            valor=self.valor_final,
            data=self.data_compra,
            descricao=f"Compra de {self.quantidade} unidades de {self.produto.nome}",
            categoria='produto',
            status=self.status,
            compra=self,
            fornecedor=self.fornecedor,
            caixa=caixa,
            usuario=self.usuario_criacao
        )
        movimentacao.save()
        return movimentacao

    @transaction.atomic
    def criar_parcelas(self):
        """Cria as parcelas da compra se for a prazo."""
        from apps.financeiro.models import Parcela
        
        if self.forma_pagamento == 'prazo' and self.numero_parcelas > 1:
            movimentacao = self.criar_movimentacao_financeira()
            
            for i in range(self.numero_parcelas):
                data_vencimento = self.data_compra + timezone.timedelta(days=30 * (i + 1))
                Parcela.objects.create(
                    movimentacao=movimentacao,
                    numero=i + 1,
                    valor=self.valor_parcela,
                    data_vencimento=data_vencimento,
                    usuario=self.usuario_criacao
                )

    @transaction.atomic
    def atualizar_estoque(self):
        """Atualiza o estoque com base na compra."""
        try:
            estoque, created = Estoque.objects.get_or_create(produto=self.produto)
            estoque.atualizar(
                quantidade=self.quantidade,
                custo_unitario=Decimal(str(self.custo_unitario))
            )
            self.registrar_movimento_estoque(estoque)
        except Exception as e:
            raise ValidationError(f"Erro ao atualizar o estoque: {str(e)}")

    def registrar_movimento_estoque(self, estoque):
        """Registra o movimento de entrada no estoque."""
        from apps.estoque.models import MovimentoEstoque

        movimento = MovimentoEstoque(
            produto=self.produto,
            tipo=MovimentoEstoque.TIPO_ENTRADA,
            quantidade=self.quantidade,
            custo_unitario=Decimal(str(self.custo_unitario)),
            descricao=f"Compra de {self.quantidade} unidades de {self.produto.nome} de {self.fornecedor.nome}",
            usuario=self.usuario_criacao
        )
        movimento.save()

    def clean(self):
        """Validações do modelo."""
        super().clean()
        
        if self.data_entrega and self.data_entrega < self.data_compra:
            raise ValidationError("A data de entrega não pode ser anterior à data da compra.")
        
        if self.desconto < 0:
            raise ValidationError("O desconto não pode ser negativo.")
        
        if self.desconto > self.valor_total:
            raise ValidationError("O desconto não pode ser maior que o valor total.")
        
        if self.forma_pagamento == 'prazo' and self.numero_parcelas < 2:
            raise ValidationError("Para pagamento a prazo, o número de parcelas deve ser maior que 1.")
        
        if self.valor_total < 0:
            raise ValidationError("O valor total não pode ser negativo.")
        
        if self.valor_final < 0:
            raise ValidationError("O valor final não pode ser negativo.")
        
        if self.quantidade <= 0:
            raise ValidationError("A quantidade deve ser maior que zero.")
        
        if self.custo_unitario <= 0:
            raise ValidationError("O custo unitário deve ser maior que zero.")

        if self.data_chegada and self.data_saida and self.data_chegada > self.data_saida:
            raise ValidationError("A data de chegada não pode ser posterior à data de saída.")

        if self.valor_frete < 0:
            raise ValidationError("O valor do frete não pode ser negativo.")

        if self.valor_seguro < 0:
            raise ValidationError("O valor do seguro não pode ser negativo.")

        if self.valor_outras_despesas < 0:
            raise ValidationError("O valor de outras despesas não pode ser negativo.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir a atualização automática."""
        if not self.slug:
            # Se o objeto ainda não tem ID, salva primeiro para obter o ID
            if not self.id:
                super().save(*args, **kwargs)
            
            # Gera o slug com o ID e outros dados
            self.slug = slugify(f"compra-{self.id}-{self.produto.nome}-{self.fornecedor.nome}")
        
        self.calcular_valores()
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        if self.status == 'confirmada':
            self.atualizar_estoque()
            if self.forma_pagamento == 'prazo':
                self.criar_parcelas()
            else:
                self.criar_movimentacao_financeira()