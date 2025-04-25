# servicos/models.py
from django.db import models
from django.utils import timezone
from apps.clientes.models import Cliente
#from apps.funcionarios.models import Funcionario  # Supondo que exista um app de Funcionários

class Servico(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="servicos")
    descricao = models.TextField()
    data_inicio = models.DateTimeField(default=timezone.now)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pendente', 'Pendente'), ('em_andamento', 'Em Andamento'), ('concluido', 'Concluído'), ('cancelado', 'Cancelado')],
        default='pendente'
    )
    #funcionario_responsavel = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True, related_name="servicos")
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def calcular_valor_total(self):
        """Aqui pode haver um cálculo do valor total do serviço, como custo de materiais ou horas trabalhadas."""
        # Exemplo de cálculo (se houver algum fator extra de custo)
        pass  # Esse método pode ser personalizado conforme a lógica de preços do seu sistema.

    def __str__(self):
        return f"Serviço {self.id} - Cliente: {self.cliente.nome} - Status: {self.status}"

    class Meta:
        ordering = ['-data_inicio']  # Ordena pelo início do serviço