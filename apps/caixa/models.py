from django.db import models

class Caixa(models.Model):
    nome = models.CharField(max_length=100)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def atualizar_saldo(self):
        # Lógica para recalcular o saldo de caixa com base nas movimentações
        total_entradas = self.movimentacoes_entradas.aggregate(models.Sum('valor'))['valor__sum'] or 0
        total_saidas = self.movimentacoes_saidas.aggregate(models.Sum('valor'))['valor__sum'] or 0
        self.saldo_atual = total_entradas - total_saidas
        self.save()

    def __str__(self):
        return f"Caixa {self.nome} - Saldo: R${self.saldo_atual}"

    @property
    def movimentacoes_entradas(self):
        return self.movimentacoes.filter(tipo='entrada')

    @property
    def movimentacoes_saidas(self):
        return self.movimentacoes.filter(tipo='saida')