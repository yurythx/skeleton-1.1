# itens_venda/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.produtos.models import Produto
from apps.vendas.models import Venda
from apps.estoque.models import Estoque, MovimentoEstoque

class ItemVenda(models.Model):
    """Modelo para registrar os itens de uma venda."""

    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="itens_venda")
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    
    # Campos de controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('confirmado', 'Confirmado'),
            ('cancelado', 'Cancelado'),
            ('entregue', 'Entregue')
        ],
        default='pendente'
    )

    def __str__(self):
        return f"Item Venda #{self.id} - {self.produto.nome} - Quantidade: {self.quantidade}"

    def total_item(self):
        """Calcula o valor total do item (quantidade * preço unitário - desconto)."""
        return (self.quantidade * self.preco_unitario) - (self.desconto or 0)

    def verificar_estoque(self):
        """Verifica se há estoque suficiente para o item."""
        try:
            estoque = Estoque.objects.get(produto=self.produto)
            if estoque.quantidade < self.quantidade:
                raise ValidationError(f"Estoque insuficiente para o produto {self.produto.nome}. Disponível: {estoque.quantidade}")
            return True
        except Estoque.DoesNotExist:
            raise ValidationError(f"Produto {self.produto.nome} não possui registro de estoque.")

    def atualizar_estoque(self):
        """Atualiza o estoque com base na venda."""
        try:
            with models.transaction.atomic():
                estoque = Estoque.objects.get(produto=self.produto)
                if self.status == 'confirmado':
                    estoque.atualizar(quantidade=-self.quantidade)
                    self.registrar_movimento_estoque(estoque)
                elif self.status == 'cancelado':
                    estoque.atualizar(quantidade=self.quantidade)
                    self.registrar_movimento_estoque(estoque, tipo=MovimentoEstoque.TIPO_ENTRADA)
        except Exception as e:
            raise ValidationError(f"Erro ao atualizar o estoque: {str(e)}")

    def registrar_movimento_estoque(self, estoque, tipo=MovimentoEstoque.TIPO_SAIDA):
        """Registra o movimento de estoque."""
        movimento = MovimentoEstoque(
            produto=self.produto,
            tipo=tipo,
            quantidade=self.quantidade,
            custo_unitario=self.preco_unitario,
            descricao=f"{'Venda' if tipo == MovimentoEstoque.TIPO_SAIDA else 'Cancelamento'} de {self.quantidade} unidades de {self.produto.nome} para {self.venda.cliente.nome}",
        )
        movimento.save()

    def clean(self):
        """Validações do modelo."""
        # Validar quantidade
        if self.quantidade <= 0:
            raise ValidationError("A quantidade deve ser maior que zero.")
        
        # Validar preço
        if self.preco_unitario <= 0:
            raise ValidationError("O preço unitário deve ser maior que zero.")
        
        # Validar desconto
        if self.desconto and self.desconto < 0:
            raise ValidationError("O desconto não pode ser negativo.")
        
        if self.desconto and self.desconto > (self.quantidade * self.preco_unitario):
            raise ValidationError("O desconto não pode ser maior que o valor total do item.")
        
        # Verificar estoque
        if self.status == 'confirmado':
            self.verificar_estoque()

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir a atualização automática."""
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Atualiza o total da venda
        if self.venda:
            self.venda.calcular_valores()
            self.venda.save()
        
        # Atualiza o estoque
        self.atualizar_estoque()

    class Meta:
        ordering = ['-data_criacao']
        unique_together = ['venda', 'produto']  # Evita duplicação de produtos na mesma venda
