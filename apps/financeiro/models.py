from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.exceptions import ValidationError

User = get_user_model()

# Enum para tipo de movimentação (entrada ou saída)
class TipoMovimentacao(models.TextChoices):
    ENTRADA = 'entrada', 'Entrada'
    SAIDA = 'saida', 'Saída'

# Enum para categoria financeira
class CategoriaFinanceira(models.TextChoices):
    PRODUTO = 'produto', 'Produto'
    SERVICO = 'servico', 'Serviço'
    COMISSAO = 'comissao', 'Comissão'
    OUTROS = 'outros', 'Outros'

# Modelo de plano de contas (contabilidade)
class PlanoDeContas(models.Model):
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TipoMovimentacao.choices)
    categoria = models.CharField(max_length=20, choices=CategoriaFinanceira.choices)

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

# Modelo de Caixa (fluxo de caixa)
class Caixa(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('aberto', 'Aberto'), ('fechado', 'Fechado')],
        default='aberto'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def atualizar_saldo(self):
        from apps.financeiro.models import MovimentacaoFinanceira
        
        total_entradas = MovimentacaoFinanceira.objects.filter(
            tipo='entrada',
            data__gte=self.data_abertura,
            data__lte=self.data_fechamento or timezone.now()
        ).aggregate(models.Sum('valor'))['valor__sum'] or 0
        
        total_saidas = MovimentacaoFinanceira.objects.filter(
            tipo='saida',
            data__gte=self.data_abertura,
            data__lte=self.data_fechamento or timezone.now()
        ).aggregate(models.Sum('valor'))['valor__sum'] or 0
        
        self.saldo_atual = total_entradas - total_saidas
        self.save()

    def fechar_caixa(self):
        if self.status == 'aberto':
            self.data_fechamento = timezone.now()
            self.status = 'fechado'
            self.save()

    def __str__(self):
        return f"Caixa {self.nome} - Saldo: R${self.saldo_atual}"

# Modelo de Movimentação Financeira
class MovimentacaoFinanceira(models.Model):
    tipo = models.CharField(
        max_length=10,
        choices=TipoMovimentacao.choices,
        help_text="Tipo de movimentação: entrada (recebimento) ou saída (pagamento)"
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(default=timezone.now)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaFinanceira.choices,
        default=CategoriaFinanceira.OUTROS
    )
    status = models.CharField(
        max_length=15,
        choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')],
        default='pendente'
    )

    # Relacionamentos opcionais
    compra = models.ForeignKey('compras.Compra', on_delete=models.SET_NULL, blank=True, null=True, related_name='movimentacoes_financeiras')
    venda = models.ForeignKey('vendas.Venda', on_delete=models.SET_NULL, blank=True, null=True, related_name='movimentacoes_financeiras')
    servico = models.ForeignKey('servicos.Servico', on_delete=models.SET_NULL, blank=True, null=True, related_name='movimentacoes_financeiras')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, blank=True, null=True, related_name='movimentacoes_financeiras')
    fornecedor = models.ForeignKey('fornecedores.Fornecedor', on_delete=models.SET_NULL, blank=True, null=True, related_name='movimentacoes_financeiras')
    plano_conta = models.ForeignKey(PlanoDeContas, on_delete=models.SET_NULL, null=True, blank=True)
    caixa = models.ForeignKey(Caixa, on_delete=models.CASCADE, related_name='movimentacoes')

    # Auditoria
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mov_fin_criados")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mov_fin_atualizados")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    # Slug para a movimentação
    slug = models.SlugField(unique=True, blank=True)

    def clean(self):
        super().clean()
        relacionados = [self.compra, self.venda, self.servico]
        
        # Verificar se está relacionado a no máximo um dos itens
        if sum([1 for r in relacionados if r is not None]) > 1:
            raise ValidationError("A movimentação deve estar relacionada apenas a compra, venda ou serviço, não múltiplos.")
        
        # Garantir que ao menos um relacionamento seja fornecido
        if not any(relacionado is not None for relacionado in relacionados):
            raise ValidationError("A movimentação deve estar relacionada a uma compra, venda ou serviço.")
        
        # Validar valor positivo
        if self.valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        
        # Validar data
        if self.data > timezone.now():
            raise ValidationError("A data não pode ser futura.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"movimentacao-{self.tipo}-{self.valor}-{self.data}")
        super().save(*args, **kwargs)

    def __str__(self):
        direcao = "Recebido de" if self.tipo == 'entrada' else "Pago para"
        if self.compra:
            contexto = f"compra #{self.compra.id}"
        elif self.venda:
            contexto = f"venda #{self.venda.id}"
        elif self.servico:
            contexto = f"serviço #{self.servico.id}"
        else:
            contexto = "movimentação geral"
        
        parceiro = self.cliente or self.fornecedor or "não especificado"
        return f"{self.get_tipo_display()} de R${self.valor} - {direcao} {parceiro} ({contexto}) em {self.data.strftime('%d/%m/%Y')}"

# Sinal para atualizar saldo de caixa após movimentação
@receiver(post_save, sender=MovimentacaoFinanceira)
def atualizar_fluxo_caixa(sender, instance, created, **kwargs):
    if created and instance.status == 'confirmada':
        instance.caixa.atualizar_saldo()

# Modelo de Parcela (para controle de parcelamento de pagamento)
class Parcela(models.Model):
    movimentacao = models.ForeignKey(MovimentacaoFinanceira, on_delete=models.CASCADE, related_name='parcelas')
    numero = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    quitado = models.BooleanField(default=False)
    juros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    multa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Parcela {self.numero} - R${self.valor} - Vencimento: {self.data_vencimento}"

    def calcular_valor_total(self):
        """Calcula o valor total da parcela incluindo juros e multa."""
        self.valor_total = self.valor + self.juros + self.multa

    def quitar(self, data_pagamento=None):
        """Quita a parcela."""
        if not data_pagamento:
            data_pagamento = timezone.now().date()
        
        self.data_pagamento = data_pagamento
        self.quitado = True
        self.save()

    def save(self, *args, **kwargs):
        self.calcular_valor_total()
        super().save(*args, **kwargs)