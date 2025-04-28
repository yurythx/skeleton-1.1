from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.financeiro.models import MovimentacaoFinanceira, Parcela
from apps.vendas.models import Venda
from apps.compras.models import Compra
from apps.servicos.models import Servico

User = get_user_model()

class Caixa(models.Model):
    """Modelo para controle de caixa e fluxo de caixa."""

    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('fechado', 'Fechado'),
    ]

    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Campos de controle
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    
    # Campos de auditoria
    aberto_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='caixas_abertos')
    fechado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='caixas_fechados')
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Caixa {self.nome} - Saldo: R${self.saldo_atual}"

    def atualizar_saldo(self):
        """Atualiza o saldo do caixa com base nas movimentações."""
        total_entradas = MovimentacaoFinanceira.objects.filter(
            caixa=self,
            tipo='entrada',
            status='confirmada',
            data__gte=self.data_abertura,
            data__lte=self.data_fechamento or timezone.now()
        ).aggregate(models.Sum('valor'))['valor__sum'] or 0
        
        total_saidas = MovimentacaoFinanceira.objects.filter(
            caixa=self,
            tipo='saida',
            status='confirmada',
            data__gte=self.data_abertura,
            data__lte=self.data_fechamento or timezone.now()
        ).aggregate(models.Sum('valor'))['valor__sum'] or 0
        
        self.saldo_atual = self.saldo_inicial + total_entradas - total_saidas
        self.save()

    def abrir_caixa(self, usuario, saldo_inicial=0):
        """Abre o caixa com um saldo inicial."""
        if self.status == 'aberto':
            raise ValidationError("Este caixa já está aberto.")
        
        self.status = 'aberto'
        self.data_abertura = timezone.now()
        self.data_fechamento = None
        self.saldo_inicial = saldo_inicial
        self.saldo_atual = saldo_inicial
        self.aberto_por = usuario
        self.fechado_por = None
        self.save()

    def fechar_caixa(self, usuario):
        """Fecha o caixa e registra o saldo final."""
        if self.status == 'fechado':
            raise ValidationError("Este caixa já está fechado.")
        
        self.atualizar_saldo()
        self.status = 'fechado'
        self.data_fechamento = timezone.now()
        self.fechado_por = usuario
        self.save()

    def registrar_movimentacao(self, tipo, valor, descricao, categoria, status='confirmada', **kwargs):
        """Registra uma movimentação no caixa."""
        if self.status == 'fechado':
            raise ValidationError("Não é possível registrar movimentações em um caixa fechado.")
        
        movimentacao = MovimentacaoFinanceira(
            tipo=tipo,
            valor=valor,
            data=timezone.now(),
            descricao=descricao,
            categoria=categoria,
            status=status,
            caixa=self,
            **kwargs
        )
        movimentacao.save()
        self.atualizar_saldo()
        return movimentacao

    def registrar_venda(self, venda):
        """Registra uma venda no caixa."""
        if venda.status != 'confirmada':
            raise ValidationError("Apenas vendas confirmadas podem ser registradas no caixa.")
        
        return self.registrar_movimentacao(
            tipo='entrada',
            valor=venda.valor_final,
            descricao=f"Venda para {venda.cliente.nome}",
            categoria='produto',
            venda=venda,
            cliente=venda.cliente
        )

    def registrar_compra(self, compra):
        """Registra uma compra no caixa."""
        if compra.status != 'confirmada':
            raise ValidationError("Apenas compras confirmadas podem ser registradas no caixa.")
        
        return self.registrar_movimentacao(
            tipo='saida',
            valor=compra.valor_final,
            descricao=f"Compra de {compra.fornecedor.nome}",
            categoria='produto',
            compra=compra,
            fornecedor=compra.fornecedor
        )

    def registrar_servico(self, servico):
        """Registra um serviço no caixa."""
        if servico.status != 'concluido':
            raise ValidationError("Apenas serviços concluídos podem ser registrados no caixa.")
        
        return self.registrar_movimentacao(
            tipo='entrada',
            valor=servico.valor_final,
            descricao=f"Serviço para {servico.cliente.nome}",
            categoria='servico',
            servico=servico,
            cliente=servico.cliente
        )

    def registrar_parcela(self, parcela):
        """Registra o pagamento de uma parcela no caixa."""
        if parcela.quitado:
            raise ValidationError("Esta parcela já foi quitada.")
        
        movimentacao = self.registrar_movimentacao(
            tipo='entrada' if parcela.movimentacao.tipo == 'entrada' else 'saida',
            valor=parcela.valor_total,
            descricao=f"Pagamento da parcela {parcela.numero} de {parcela.movimentacao}",
            categoria=parcela.movimentacao.categoria,
            cliente=parcela.movimentacao.cliente,
            fornecedor=parcela.movimentacao.fornecedor
        )
        
        parcela.quitar()
        return movimentacao

    class Meta:
        ordering = ['-data_abertura']
        verbose_name = 'Caixa'
        verbose_name_plural = 'Caixas'