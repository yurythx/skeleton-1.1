# servicos/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.clientes.models import Cliente
from apps.financeiro.models import MovimentacaoFinanceira, Parcela, Caixa
#from apps.funcionarios.models import Funcionario  # Supondo que exista um app de Funcionários

class Servico(models.Model):
    """Modelo para registrar os serviços prestados aos clientes."""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('avista', 'À Vista'),
        ('prazo', 'A Prazo'),
        ('boleto', 'Boleto'),
        ('cartao', 'Cartão de Crédito'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="servicos")
    descricao = models.TextField()
    data_inicio = models.DateTimeField(default=timezone.now)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    # Campos financeiros
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, default='avista')
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    numero_parcelas = models.PositiveIntegerField(default=1)
    
    # Campos de controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)

    def calcular_valor_total(self):
        """Aqui pode haver um cálculo do valor total do serviço, como custo de materiais ou horas trabalhadas."""
        # Exemplo de cálculo (se houver algum fator extra de custo)
        pass  # Esse método pode ser personalizado conforme a lógica de preços do seu sistema.

    def __str__(self):
        return f"Serviço {self.id} - Cliente: {self.cliente.nome} - Status: {self.status}"

    def calcular_valores(self):
        """Calcula os valores totais do serviço."""
        self.valor_final = self.valor - self.desconto

    def criar_movimentacao_financeira(self):
        """Cria a movimentação financeira relacionada ao serviço."""
        caixa = Caixa.objects.filter(status='aberto').first()
        if not caixa:
            raise ValidationError("Não há caixa aberto para registrar a movimentação.")

        movimentacao = MovimentacaoFinanceira(
            tipo='entrada',
            valor=self.valor_final,
            data=self.data_inicio,
            descricao=f"Serviço para {self.cliente.nome}: {self.descricao[:50]}...",
            categoria='servico',
            status=self.status,
            servico=self,
            cliente=self.cliente,
            caixa=caixa
        )
        movimentacao.save()
        return movimentacao

    def criar_parcelas(self):
        """Cria as parcelas do serviço se for a prazo."""
        if self.forma_pagamento == 'prazo' and self.numero_parcelas > 1:
            valor_parcela = self.valor_final / self.numero_parcelas
            movimentacao = self.criar_movimentacao_financeira()
            
            for i in range(self.numero_parcelas):
                data_vencimento = self.data_inicio + timezone.timedelta(days=30 * (i + 1))
                Parcela.objects.create(
                    movimentacao=movimentacao,
                    numero=i + 1,
                    valor=valor_parcela,
                    data_vencimento=data_vencimento
                )

    def clean(self):
        """Validações do modelo."""
        if self.data_conclusao and self.data_conclusao < self.data_inicio:
            raise ValidationError("A data de conclusão não pode ser anterior à data de início.")
        
        if self.desconto > self.valor:
            raise ValidationError("O desconto não pode ser maior que o valor do serviço.")
        
        if self.forma_pagamento == 'prazo' and self.numero_parcelas < 2:
            raise ValidationError("Para pagamento a prazo, o número de parcelas deve ser maior que 1.")

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir a atualização automática."""
        self.calcular_valores()
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        if self.status == 'concluido':
            if self.forma_pagamento == 'prazo':
                self.criar_parcelas()
            else:
                self.criar_movimentacao_financeira()

    class Meta:
        ordering = ['-data_inicio']  # Ordena pelo início do serviço