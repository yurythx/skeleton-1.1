from django.db import models, transaction
from apps.fornecedores.models import Fornecedor  # Referência ao modelo Fornecedor
from apps.estoque.models import Estoque  # Referência ao modelo Estoque
from django.utils import timezone

class Compra(models.Model):
    """Modelo para registrar as compras de produtos aos fornecedores."""

    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='compras')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE, related_name='compras')
    quantidade = models.PositiveIntegerField()
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data_compra = models.DateTimeField(default=timezone.now)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Compra de {self.quantidade} unidades de {self.produto.nome} de {self.fornecedor.nome} em {self.data_compra.strftime('%d/%m/%Y')}"

    def atualizar_estoque(self):
        """Atualiza o estoque com base na compra."""
        # Usando transações para garantir a consistência de dados
        try:
            with transaction.atomic():
                # Verifica se já existe um estoque para o produto
                estoque, created = Estoque.objects.get_or_create(produto=self.produto)
                
                # Atualiza o estoque com a nova quantidade e o custo unitário
                estoque.atualizar(quantidade=self.quantidade, custo_unitario=self.custo_unitario)

                # Registra o movimento de entrada no estoque
                self.registrar_movimento_estoque(estoque)
        except Exception as e:
            # Se ocorrer algum erro, é importante garantir que não haja alteração no banco
            raise ValidationError(f"Erro ao atualizar o estoque: {str(e)}")

    def registrar_movimento_estoque(self, estoque):
        """Registra o movimento de entrada no estoque (para controle de histórico)."""
        from estoque.models import MovimentoEstoque

        movimento = MovimentoEstoque(
            produto=self.produto,
            tipo=MovimentoEstoque.TIPO_ENTRADA,
            quantidade=self.quantidade,
            custo_unitario=self.custo_unitario,
            usuario=None,  # Pode ser adaptado para o usuário autenticado, se necessário
            descricao=f"Compra de {self.quantidade} unidades de {self.produto.nome} de {self.fornecedor.nome}",
        )
        movimento.save()

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir a atualização automática do estoque."""
        super().save(*args, **kwargs)

        # Atualiza o estoque automaticamente após salvar a compra
        self.atualizar_estoque()