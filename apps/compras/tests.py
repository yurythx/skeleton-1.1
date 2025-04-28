from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto
from apps.estoque.models import Estoque
from apps.caixa.models import Caixa
from apps.financeiro.models import MovimentacaoFinanceira, Parcela
from .models import Compra

class FluxoComprasTest(TestCase):
    def setUp(self):
        # Criar fornecedor
        self.fornecedor = Fornecedor.objects.create(
            nome='Fornecedor Teste',
            email='fornecedor@teste.com',
            telefone='11999999999',
            cnpj='12.345.678/0001-90',
            limite_credito=Decimal('5000.00')
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

    def test_criar_compra_avista(self):
        """Testa a criação de uma compra à vista"""
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto1,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Verificar valores
        self.assertEqual(compra.valor_total, Decimal('500.00'))
        self.assertEqual(compra.valor_final, Decimal('500.00'))
        
        # Verificar estoque
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 110)
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(compra=compra).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('500.00'))
        self.assertEqual(movimentacao.tipo, 'saida')

    def test_criar_compra_prazo(self):
        """Testa a criação de uma compra a prazo"""
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto1,
            quantidade=20,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='prazo',
            numero_parcelas=2
        )
        
        # Verificar valores
        self.assertEqual(compra.valor_total, Decimal('1000.00'))
        self.assertEqual(compra.valor_final, Decimal('1000.00'))
        
        # Verificar parcelas
        movimentacao = MovimentacaoFinanceira.objects.filter(compra=compra).first()
        parcelas = Parcela.objects.filter(movimentacao=movimentacao)
        self.assertEqual(parcelas.count(), 2)
        self.assertEqual(parcelas[0].valor, Decimal('500.00'))

    def test_compra_com_desconto(self):
        """Testa a criação de uma compra com desconto"""
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto1,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='avista',
            desconto=Decimal('50.00')
        )
        
        # Verificar valores
        self.assertEqual(compra.valor_total, Decimal('500.00'))
        self.assertEqual(compra.valor_final, Decimal('450.00'))
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(compra=compra).first()
        self.assertEqual(movimentacao.valor, Decimal('450.00'))

    def test_cancelar_compra(self):
        """Testa o cancelamento de uma compra"""
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto1,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Cancelar compra
        compra.status = 'cancelada'
        compra.save()
        
        # Verificar estoque (deve voltar ao valor original)
        self.estoque1.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 100)
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(compra=compra).first()
        self.assertEqual(movimentacao.status, 'cancelada')

    def test_compra_multiplos_produtos(self):
        """Testa a criação de uma compra com múltiplos produtos"""
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto1,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Adicionar segundo produto
        compra2 = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto2,
            quantidade=5,
            custo_unitario=Decimal('75.00'),
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Verificar estoque
        self.estoque1.refresh_from_db()
        self.estoque2.refresh_from_db()
        self.assertEqual(self.estoque1.quantidade, 110)
        self.assertEqual(self.estoque2.quantidade, 55)
        
        # Verificar movimentações financeiras
        movimentacoes = MovimentacaoFinanceira.objects.filter(compra__in=[compra, compra2])
        self.assertEqual(movimentacoes.count(), 2)
        self.assertEqual(movimentacoes[0].valor + movimentacoes[1].valor, Decimal('875.00'))