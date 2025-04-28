from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from apps.estoque.models import Estoque
from apps.caixa.models import Caixa
from apps.financeiro.models import MovimentacaoFinanceira, Parcela
from .models import Venda
from apps.itens_venda.models import ItemVenda

class FluxoVendasTest(TestCase):
    def setUp(self):
        # Criar cliente
        self.cliente = Cliente.objects.create(
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11999999999',
            cpf='123.456.789-00',
            limite_credito=Decimal('1000.00')
        )
        
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
        
        # Criar caixa
        self.caixa = Caixa.objects.create(
            nome='Caixa Principal',
            saldo_inicial=Decimal('1000.00')
        )

    def test_criar_venda_avista(self):
        """Testa a criação de uma venda à vista"""
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Adicionar itens
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=2,
            preco_unitario=Decimal('100.00')
        )
        
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto2,
            quantidade=1,
            preco_unitario=Decimal('150.00')
        )
        
        # Verificar valores
        self.assertEqual(venda.valor_total, Decimal('350.00'))
        self.assertEqual(venda.valor_final, Decimal('350.00'))
        
        # Verificar estoque
        self.estoque1.refresh_from_db()
        self.estoque2.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 98)
        self.assertEqual(self.estoque2.quantidade, 49)
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(venda=venda).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('350.00'))
        self.assertEqual(movimentacao.tipo, 'entrada')

    def test_criar_venda_prazo(self):
        """Testa a criação de uma venda a prazo"""
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='prazo',
            numero_parcelas=3
        )
        
        # Adicionar item
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=3,
            preco_unitario=Decimal('100.00')
        )
        
        # Verificar valores
        self.assertEqual(venda.valor_total, Decimal('300.00'))
        self.assertEqual(venda.valor_final, Decimal('300.00'))
        
        # Verificar parcelas
        movimentacao = MovimentacaoFinanceira.objects.filter(venda=venda).first()
        parcelas = Parcela.objects.filter(movimentacao=movimentacao)
        self.assertEqual(parcelas.count(), 3)
        self.assertEqual(parcelas[0].valor, Decimal('100.00'))

    def test_venda_com_desconto(self):
        """Testa a criação de uma venda com desconto"""
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista',
            desconto=Decimal('50.00')
        )
        
        # Adicionar item
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=2,
            preco_unitario=Decimal('100.00')
        )
        
        # Verificar valores
        self.assertEqual(venda.valor_total, Decimal('200.00'))
        self.assertEqual(venda.valor_final, Decimal('150.00'))
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(venda=venda).first()
        self.assertEqual(movimentacao.valor, Decimal('150.00'))

    def test_venda_estoque_insuficiente(self):
        """Testa tentativa de venda com estoque insuficiente"""
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Tentar adicionar item com quantidade maior que o estoque
        with self.assertRaises(Exception):
            ItemVenda.objects.create(
                venda=venda,
                produto=self.produto1,
                quantidade=150,
                preco_unitario=Decimal('100.00')
            )

    def test_cancelar_venda(self):
        """Testa o cancelamento de uma venda"""
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Adicionar item
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto1,
            quantidade=2,
            preco_unitario=Decimal('100.00')
        )
        
        # Cancelar venda
        venda.status = 'cancelada'
        venda.save()
        
        # Verificar estoque (deve voltar ao valor original)
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 100)
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(venda=venda).first()
        self.assertEqual(movimentacao.status, 'cancelada')
