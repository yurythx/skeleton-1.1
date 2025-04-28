from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from apps.produtos.models import Produto
from apps.vendas.models import Venda
from apps.compras.models import Compra
from apps.itens_venda.models import ItemVenda
from .models import Estoque, MovimentoEstoque

class FluxoEstoqueTest(TestCase):
    def setUp(self):
        # Criar produtos
        self.produto1 = Produto.objects.create(
            nome='Produto 1',
            descricao='Descrição do produto 1',
            preco_custo=Decimal('50.00'),
            preco_venda=Decimal('100.00')
        )
        
        self.produto2 = Produto.objects.create(
            nome='Produto 2',
            descricao='Descrição do produto 2',
            preco_custo=Decimal('75.00'),
            preco_venda=Decimal('150.00')
        )
        
        # Criar estoque
        self.estoque1 = Estoque.objects.create(
            produto=self.produto1,
            quantidade=100
        )
        
        self.estoque2 = Estoque.objects.create(
            produto=self.produto2,
            quantidade=50
        )

    def test_movimento_entrada(self):
        """Testa o movimento de entrada no estoque"""
        # Criar compra
        compra = Compra.objects.create(
            fornecedor=None,  # Não necessário para o teste
            produto=self.produto1,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada'
        )
        
        # Verificar estoque após entrada
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 110)
        
        # Verificar movimento de estoque
        movimento = MovimentoEstoque.objects.filter(
            produto=self.produto1,
            tipo=MovimentoEstoque.TIPO_ENTRADA
        ).last()
        
        self.assertIsNotNone(movimento)
        self.assertEqual(movimento.quantidade, 10)
        self.assertEqual(movimento.custo_unitario, Decimal('50.00'))

    def test_movimento_saida(self):
        """Testa o movimento de saída no estoque"""
        # Criar venda
        venda = Venda.objects.create(
            cliente=None,  # Não necessário para o teste
            status='confirmada'
        )
        
        # Adicionar item à venda
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=5,
            preco_unitario=Decimal('100.00')
        )
        
        # Verificar estoque após saída
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 95)
        
        # Verificar movimento de estoque
        movimento = MovimentoEstoque.objects.filter(
            produto=self.produto1,
            tipo=MovimentoEstoque.TIPO_SAIDA
        ).last()
        
        self.assertIsNotNone(movimento)
        self.assertEqual(movimento.quantidade, 5)
        self.assertEqual(movimento.custo_unitario, Decimal('100.00'))

    def test_movimento_multiplos_produtos(self):
        """Testa movimentos de estoque com múltiplos produtos"""
        # Criar compra com múltiplos produtos
        compra1 = Compra.objects.create(
            fornecedor=None,
            produto=self.produto1,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada'
        )
        
        compra2 = Compra.objects.create(
            fornecedor=None,
            produto=self.produto2,
            quantidade=5,
            custo_unitario=Decimal('75.00'),
            status='confirmada'
        )
        
        # Verificar estoque após entradas
        self.estoque1.refresh_from_db()
        self.estoque2.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 110)
        self.assertEqual(self.estoque2.quantidade, 55)
        
        # Criar venda com múltiplos produtos
        venda = Venda.objects.create(
            cliente=None,
            status='confirmada'
        )
        
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=3,
            preco_unitario=Decimal('100.00')
        )
        
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto2,
            quantidade=2,
            preco_unitario=Decimal('150.00')
        )
        
        # Verificar estoque após saídas
        self.estoque1.refresh_from_db()
        self.estoque2.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 107)
        self.assertEqual(self.estoque2.quantidade, 53)

    def test_cancelamento_movimento(self):
        """Testa o cancelamento de movimentos de estoque"""
        # Criar venda
        venda = Venda.objects.create(
            cliente=None,
            status='confirmada'
        )
        
        # Adicionar item à venda
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=5,
            preco_unitario=Decimal('100.00')
        )
        
        # Cancelar venda
        venda.status = 'cancelada'
        venda.save()
        
        # Verificar estoque após cancelamento
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 100)
        
        # Verificar movimento de estoque
        movimento = MovimentoEstoque.objects.filter(
            produto=self.produto1,
            tipo=MovimentoEstoque.TIPO_SAIDA
        ).last()
        
        self.assertIsNotNone(movimento)
        self.assertEqual(movimento.status, 'cancelado')

    def test_estoque_insuficiente(self):
        """Testa tentativa de saída com estoque insuficiente"""
        # Criar venda
        venda = Venda.objects.create(
            cliente=None,
            status='confirmada'
        )
        
        # Tentar adicionar item com quantidade maior que o estoque
        with self.assertRaises(Exception):
            ItemVenda.objects.create(
                venda=venda,
                produto=self.produto1,
                quantidade=150,
                preco_unitario=Decimal('100.00')
            )
        
        # Verificar que o estoque não foi alterado
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 100)
