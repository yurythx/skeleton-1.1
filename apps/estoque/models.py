from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings


class Estoque(models.Model):
    """Modelo responsável pelo controle de estoque e cálculos de custo médio."""

    produto = models.OneToOneField('produtos.Produto', on_delete=models.CASCADE, related_name='estoque_produto')
    quantidade = models.PositiveIntegerField(default=0)
    minimo = models.PositiveIntegerField(default=0)
    custo_medio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def atualizar(self, quantidade, custo_unitario=None):
        """Atualiza o estoque e o custo médio."""
        if quantidade == 0:
            return  # Nenhuma mudança

        novo_estoque = self.quantidade + quantidade
        if novo_estoque < 0:
            raise ValidationError("Estoque não pode ficar negativo.")

        if quantidade > 0:
            if custo_unitario is None:
                raise ValidationError("Entradas devem conter custo unitário.")
            # Cálculo do novo custo médio ponderado
            total_atual = self.quantidade * self.custo_medio
            total_novo = quantidade * custo_unitario
            if self.quantidade + quantidade == 0:
                self.custo_medio = 0
            else:
                self.custo_medio = (total_atual + total_novo) / (self.quantidade + quantidade)

        self.quantidade = novo_estoque
        self.save()

        # Alerta de estoque mínimo
        if self.quantidade <= self.minimo:
            print(f"[ALERTA] Estoque do produto '{self.produto.nome}' está abaixo ou igual ao mínimo ({self.quantidade} <= {self.minimo})")

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade} unidades"


class MovimentoEstoque(models.Model):
    """Modelo para registrar o histórico de entradas e saídas de estoque."""

    TIPO_ENTRADA = 'entrada'
    TIPO_SAIDA = 'saida'
    TIPO_AJUSTE = 'ajuste'

    TIPOS = [
        (TIPO_ENTRADA, 'Entrada'),
        (TIPO_SAIDA, 'Saída'),
        (TIPO_AJUSTE, 'Ajuste'),
    ]

    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE, related_name='movimentos_estoque')
    data = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    quantidade = models.IntegerField()
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} em {self.produto.nome} ({self.data.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para ajustar o estoque de forma automática."""

        estoque = self.produto.estoque_produto

        if self.tipo == self.TIPO_ENTRADA:
            if self.custo_unitario is None:
                raise ValidationError("Entradas devem conter custo unitário.")
            estoque.atualizar(quantidade=self.quantidade, custo_unitario=self.custo_unitario)

        elif self.tipo == self.TIPO_SAIDA:
            if self.quantidade > estoque.quantidade:
                raise ValidationError("Não há estoque suficiente para essa saída.")
            estoque.atualizar(quantidade=-self.quantidade)

        elif self.tipo == self.TIPO_AJUSTE:
            # Ajuste pode ser positivo ou negativo, com custo unitário opcional
            estoque.atualizar(quantidade=self.quantidade, custo_unitario=self.custo_unitario or 0)

        super().save(*args, **kwargs)