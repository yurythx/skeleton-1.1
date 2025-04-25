from django.test import TestCase
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto
from apps.compras.models import Compra
from apps.estoque.models import Estoque, MovimentoEstoque
from decimal import Decimal
from django.core.exceptions import ValidationError
import uuid

class CompraModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Cria dados compartilhados entre os testes."""
        # Criação de um fornecedor com slug único (evita conflito com UNIQUE)
        cls.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            slug=f"fornecedor-teste-{uuid.uuid4()}"[:50]  # Slug único com UUID
        )

        # Criação de um produto
        cls.produto = Produto.objects.create(
            nome="Produto Teste",
            preco=Decimal('10.00')
        )

    def test_atualizar_estoque_com_estoque_existente(self):
        """Testa a atualização do estoque quando o estoque já existe."""
        estoque = Estoque.objects.create(
            produto=self.produto,
            quantidade=10,
            minimo=5,
            custo_medio=Decimal('10.00')
        )

        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=5,
            custo_unitario=Decimal('12.00')
        )

        compra.atualizar_estoque()

        estoque.refresh_from_db()
        self.assertEqual(estoque.quantidade, 15)
        self.assertEqual(estoque.custo_medio, Decimal('10.50'))

    def test_atualizar_estoque_com_estoque_novo(self):
        """Testa a criação de um novo estoque quando não há estoque existente."""
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=10,
            custo_unitario=Decimal('15.00')
        )

        compra.atualizar_estoque()

        estoque = Estoque.objects.get(produto=self.produto)
        self.assertEqual(estoque.quantidade, 10)
        self.assertEqual(estoque.custo_medio, Decimal('15.00'))

    def test_atualizar_estoque_com_quantidade_negativa(self):
        """Testa se o estoque não pode ser atualizado para um valor negativo."""
        Estoque.objects.create(
            produto=self.produto,
            quantidade=10,
            minimo=5,
            custo_medio=Decimal('10.00')
        )

        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=15,
            custo_unitario=Decimal('12.00')
        )

        with self.assertRaises(ValidationError):
            compra.atualizar_estoque()

    def test_registrar_movimento_estoque(self):
        """Testa o registro de um movimento de entrada no estoque."""
        Estoque.objects.create(
            produto=self.produto,
            quantidade=10,
            minimo=5,
            custo_medio=Decimal('10.00')
        )

        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=5,
            custo_unitario=Decimal('12.00')
        )

        compra.atualizar_estoque()

        movimento = MovimentoEstoque.objects.filter(
            produto=self.produto,
            tipo=MovimentoEstoque.TIPO_ENTRADA
        ).last()

        self.assertIsNotNone(movimento)
        self.assertEqual(movimento.quantidade, 5)
        self.assertEqual(movimento.custo_unitario, Decimal('12.00'))
        self.assertIn("Compra de 5 unidades", movimento.descricao)

    def test_registrar_movimento_estoque_sem_quantidade(self):
        """Testa se um movimento de estoque não é registrado quando não há quantidade na compra."""
        Estoque.objects.create(
            produto=self.produto,
            quantidade=10,
            minimo=5,
            custo_medio=Decimal('10.00')
        )

        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=0,
            custo_unitario=Decimal('12.00')
        )

        compra.atualizar_estoque()

        movimento = MovimentoEstoque.objects.filter(
            produto=self.produto,
            tipo=MovimentoEstoque.TIPO_ENTRADA
        ).last()

        self.assertIsNone(movimento)