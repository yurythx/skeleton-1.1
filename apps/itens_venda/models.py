# itens_venda/models.py
from django.db import models
from apps.produtos.models import Produto
from apps.pedidos.models import Pedido

class ItemVenda(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens_venda")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="itens_venda")
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)

    def __str__(self):
        return f"Item Venda #{self.id} - {self.produto.nome} - Quantidade: {self.quantidade}"

    def total_item(self):
        """Calcula o valor total do item (quantidade * preço unitário - desconto)."""
        return (self.quantidade * self.preco_unitario) - (self.desconto or 0)
