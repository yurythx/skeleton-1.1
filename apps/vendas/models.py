# vendas/models.py
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.clientes.models import Cliente

class Venda(models.Model):
    """Modelo para registrar as vendas de produtos aos clientes."""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('entregue', 'Entregue'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('avista', 'À Vista'),
        ('prazo', 'A Prazo'),
        ('boleto', 'Boleto'),
        ('cartao', 'Cartão de Crédito'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vendas")
    data_venda = models.DateTimeField(default=timezone.now)
    data_entrega = models.DateTimeField(null=True, blank=True)
    
    # Campos financeiros
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, default='avista')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    numero_parcelas = models.PositiveIntegerField(default=1)
    
    # Campos de controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['data_venda']),
            models.Index(fields=['cliente']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(valor_total__gte=0),
                name='venda_valor_total_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(desconto__gte=0),
                name='venda_desconto_nao_negativo'
            ),
            models.CheckConstraint(
                check=models.Q(valor_final__gte=0),
                name='venda_valor_final_nao_negativo'
            ),
        ]

    def __str__(self):
        return f"Venda {self.id} - Cliente: {self.cliente.nome} - Total: R${self.valor_final}"

    def calcular_valores(self):
        """Calcula os valores totais da venda."""
        if not self.itens.exists():
            self.valor_total = 0
            self.valor_final = 0
            return
        self.valor_total = sum([item.total_item() for item in self.itens.all()])
        self.valor_final = self.valor_total - self.desconto

    @transaction.atomic
    def criar_movimentacao_financeira(self):
        """Cria a movimentação financeira relacionada à venda."""
        from apps.financeiro.models import MovimentacaoFinanceira, Caixa
        
        caixa = Caixa.objects.filter(status='aberto').first()
        if not caixa:
            raise ValidationError("Não há caixa aberto para registrar a movimentação.")

        movimentacao = MovimentacaoFinanceira(
            tipo='entrada',
            valor=self.valor_final,
            data=self.data_venda,
            descricao=f"Venda para {self.cliente.nome}",
            categoria='produto',
            status=self.status,
            venda=self,
            cliente=self.cliente,
            caixa=caixa
        )
        movimentacao.save()
        return movimentacao

    @transaction.atomic
    def criar_parcelas(self):
        """Cria as parcelas da venda se for a prazo."""
        from apps.financeiro.models import Parcela
        
        if self.forma_pagamento == 'prazo' and self.numero_parcelas > 1:
            valor_parcela = self.valor_final / self.numero_parcelas
            movimentacao = self.criar_movimentacao_financeira()
            
            for i in range(self.numero_parcelas):
                data_vencimento = self.data_venda + timezone.timedelta(days=30 * (i + 1))
                Parcela.objects.create(
                    movimentacao=movimentacao,
                    numero=i + 1,
                    valor=valor_parcela,
                    data_vencimento=data_vencimento
                )

    @transaction.atomic
    def atualizar_estoque(self):
        """Atualiza o estoque com base na venda."""
        from apps.estoque.models import Estoque
        
        try:
            for item in self.itens.all():
                estoque = Estoque.objects.get(produto=item.produto)
                if estoque.quantidade < item.quantidade:
                    raise ValidationError(f"Estoque insuficiente para o produto {item.produto.nome}")
                
                estoque.atualizar(quantidade=-item.quantidade)
                self.registrar_movimento_estoque(estoque, item)
        except Exception as e:
            raise ValidationError(f"Erro ao atualizar o estoque: {str(e)}")

    def registrar_movimento_estoque(self, estoque, item):
        """Registra o movimento de saída no estoque."""
        from apps.estoque.models import MovimentoEstoque
        
        movimento = MovimentoEstoque(
            produto=item.produto,
            tipo=MovimentoEstoque.TIPO_SAIDA,
            quantidade=item.quantidade,
            custo_unitario=item.preco_unitario,
            descricao=f"Venda de {item.quantidade} unidades de {item.produto.nome} para {self.cliente.nome}",
        )
        movimento.save()

    def clean(self):
        """Validações do modelo."""
        super().clean()
        
        if self.data_entrega and self.data_entrega < self.data_venda:
            raise ValidationError("A data de entrega não pode ser anterior à data da venda.")
        
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

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir a atualização automática."""
        self.calcular_valores()
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        if self.status == 'confirmada':
            self.atualizar_estoque()
            if self.forma_pagamento == 'prazo':
                self.criar_parcelas()
            else:
                self.criar_movimentacao_financeira()