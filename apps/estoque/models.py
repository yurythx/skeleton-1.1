from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings  # Importando settings para usar o modelo de usuário customizado
from apps.produtos.models import Produto

class Estoque(models.Model):
    """Modelo responsável pelo controle de estoque e cálculos de custo médio."""
    
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='estoque_produto')
    # Alterando o related_name para evitar conflito
    
    quantidade = models.PositiveIntegerField(default=0)
    # Quantidade atual do produto em estoque.
    
    minimo = models.PositiveIntegerField(default=0)
    # Quantidade mínima necessária para o estoque. Um alerta de reabastecimento pode ser acionado se o estoque atingir este número.
    
    custo_medio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # O custo médio do produto no estoque. Esse valor é recalculado com base no custo unitário das entradas de estoque.

    def atualizar(self, quantidade, custo_unitario=None, usuario=None, descricao=None):
        """
        Atualiza o estoque, recalcula o custo médio se houver custo informado.
        Parâmetros:
        - quantidade: Quantidade a ser adicionada ou subtraída do estoque.
        - custo_unitario: Custo unitário, usado para recalcular o custo médio (apenas para entradas).
        - usuario: Usuário responsável pela movimentação (para registrar no histórico).
        - descricao: Descrição opcional do motivo da movimentação (para registrar no histórico).
        """
        
        novo_estoque = self.quantidade + quantidade
        # Calcula o novo estoque, somando ou subtraindo a quantidade informada.
        
        if novo_estoque < 0:
            raise ValidationError("Estoque não pode ficar negativo.")
        # Impede que o estoque fique negativo.

        # Recalcula o custo médio apenas para entradas de estoque
        if quantidade > 0 and custo_unitario is not None:
            total_atual = self.quantidade * self.custo_medio
            total_novo = quantidade * custo_unitario
            self.custo_medio = (total_atual + total_novo) / (self.quantidade + quantidade)
        # Se a quantidade for positiva (entrada), recalcula o custo médio com o novo valor de custo unitário.

        self.quantidade = novo_estoque
        self.save()
        # Atualiza a quantidade no banco de dados.

        # Cria o histórico automaticamente (movimento de entrada ou saída)
        tipo_movimento = 'entrada_fornecedor' if quantidade > 0 else 'saida_venda'
        # Define o tipo de movimento com base na quantidade (entrada ou saída).
        
        MovimentoEstoque.objects.create(
            produto=self.produto,
            quantidade=quantidade,
            tipo=tipo_movimento,
            custo_unitario=custo_unitario or self.custo_medio,
            usuario=usuario,  # Armazena o usuário que fez o movimento (se necessário).
            descricao=descricao,  # Armazena uma descrição do motivo do movimento (se necessário).
        )

        # Verifica se o estoque ficou abaixo do mínimo, e pode gerar um alerta para reabastecimento.
        if self.quantidade <= self.minimo:
            # Aqui você pode adicionar a lógica para disparar um alerta de reabastecimento, como enviar um e-mail ou notificação.
            pass

    def __str__(self):
        # Método para exibir uma representação amigável do estoque do produto.
        return f"{self.produto.nome} - {self.quantidade} unidades"


class MovimentoEstoque(models.Model):
    """Modelo para registrar o histórico de entradas e saídas de estoque."""
    
    TIPO_ENTRADA = 'entrada'
    TIPO_SAIDA = 'saida'
    TIPO_AJUSTE = 'ajuste'  # Tipo de ajuste manual de estoque.

    TIPOS = [
        (TIPO_ENTRADA, 'Entrada'),
        (TIPO_SAIDA, 'Saída'),
        (TIPO_AJUSTE, 'Ajuste'),
    ]
    # Define os tipos de movimentos possíveis: entrada, saída e ajuste manual.

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentos_estoque')
    # Relaciona cada movimento a um produto específico.
    
    data = models.DateTimeField(default=timezone.now)
    # A data do movimento. O valor padrão é o momento da criação.

    tipo = models.CharField(max_length=10, choices=TIPOS)
    # Tipo de movimento: entrada, saída ou ajuste. Usamos o campo `choices` para garantir que apenas esses valores sejam usados.

    quantidade = models.IntegerField()
    # A quantidade de produtos que foram movimentados (entrada ou saída).

    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # O custo unitário do produto na operação.

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    # Alterando para usar o modelo de usuário customizado
    
    descricao = models.TextField(blank=True, null=True)
    # Descrição opcional sobre o motivo ou detalhe do movimento.

    class Meta:
        ordering = ['-data']
    # Ordena os registros por data decrescente, ou seja, os movimentos mais recentes aparecerão primeiro.

    def __str__(self):
        # Método para exibir uma representação amigável do movimento de estoque.
        return f"{self.get_tipo_display()} de {self.quantidade} em {self.produto.nome} ({self.data.strftime('%d/%m/%Y')})"