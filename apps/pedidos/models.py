# pedidos/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.clientes.models import Cliente

User = get_user_model()

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('entregue', 'Entregue'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pedidos")
    data_pedido = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos_criados")
    atualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos_atualizados")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome} - Status: {self.get_status_display()}"

    def atualizar_valor_total(self):
        """Método para atualizar o valor total do pedido com base nos itens de venda."""
        itens = self.itens_venda.all()
        total = sum([item.total_item() for item in itens])
        self.valor_total = total - (self.desconto or 0)
        self.save()
