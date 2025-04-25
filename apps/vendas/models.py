# vendas/models.py
from django.db import models
#from apps.pedidos.models import Pedido
#from apps.itens_venda.models import ItemVenda
from django.utils import timezone

class Venda(models.Model):
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name="vendas")
    data_venda = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=15,
        choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')],
        default='pendente'
    )

    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def calcular_total(self):
        self.total = sum([item.preco * item.quantidade for item in self.itens.all()])
        self.save()

    def __str__(self):
        return f"Venda {self.id} - Total: {self.total} - Status: {self.status}"