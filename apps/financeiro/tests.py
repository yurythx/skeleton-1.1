from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.clientes.models import Cliente
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto
from apps.vendas.models import Venda
from apps.compras.models import Compra
from apps.servicos.models import Servico
from apps.caixa.models import Caixa
from apps.estoque.models import Estoque
from .models import MovimentacaoFinanceira, Parcela

User = get_user_model()

class FluxoFinanceiroTest(TestCase):
    def setUp(self):
        # Criar usuário
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar cliente
        self.cliente = Cliente.objects.create(
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11999999999',
            cpf='123.456.789-00',
            limite_credito=Decimal('1000.00')
        )
        
        # Criar fornecedor
        self.fornecedor = Fornecedor.objects.create(
            nome='Fornecedor Teste',
            email='fornecedor@teste.com',
            telefone='11999999999',
            cnpj='12.345.678/0001-90',
            limite_credito=Decimal('5000.00')
        )
        
        # Criar produto
        self.produto = Produto.objects.create(
            nome='Produto Teste',
            descricao='Descrição do produto teste',
            preco_custo=Decimal('50.00'),
            preco_venda=Decimal('100.00')
        )
        
        # Criar estoque
        self.estoque = Estoque.objects.create(
            produto=self.produto,
            quantidade=100
        )
        
        # Criar caixa
        self.caixa = Caixa.objects.create(
            nome='Caixa Principal',
            saldo_inicial=Decimal('1000.00'),
            aberto_por=self.user
        )

    def test_fluxo_venda_cliente(self):
        """Testa o fluxo completo de uma venda para um cliente"""
        # Criar venda
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='prazo',
            numero_parcelas=3
        )
        
        # Adicionar item à venda
        venda.itens.create(
            produto=self.produto,
            quantidade=2,
            preco_unitario=Decimal('100.00')
        )
        
        # Verificar valores
        self.assertEqual(venda.valor_total, Decimal('200.00'))
        self.assertEqual(venda.valor_final, Decimal('200.00'))
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(venda=venda).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('200.00'))
        
        # Verificar parcelas
        parcelas = Parcela.objects.filter(movimentacao=movimentacao)
        self.assertEqual(parcelas.count(), 3)
        self.assertEqual(parcelas[0].valor, Decimal('66.67'))

    def test_fluxo_compra_fornecedor(self):
        """Testa o fluxo completo de uma compra de um fornecedor"""
        # Criar compra
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=10,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='prazo',
            numero_parcelas=2
        )
        
        # Verificar valores
        self.assertEqual(compra.valor_total, Decimal('500.00'))
        self.assertEqual(compra.valor_final, Decimal('500.00'))
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(compra=compra).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('500.00'))
        
        # Verificar parcelas
        parcelas = Parcela.objects.filter(movimentacao=movimentacao)
        self.assertEqual(parcelas.count(), 2)
        self.assertEqual(parcelas[0].valor, Decimal('250.00'))

    def test_fluxo_servico(self):
        """Testa o fluxo completo de um serviço"""
        # Criar serviço
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('300.00'),
            status='concluido',
            forma_pagamento='avista'
        )
        
        # Verificar valores
        self.assertEqual(servico.valor_final, Decimal('300.00'))
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('300.00'))

    def test_fluxo_estoque(self):
        """Testa o fluxo de estoque com vendas e compras"""
        # Compra inicial
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=50,
            custo_unitario=Decimal('50.00'),
            status='confirmada'
        )
        
        # Verificar estoque após compra
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 150)
        
        # Venda
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada'
        )
        venda.itens.create(
            produto=self.produto,
            quantidade=30,
            preco_unitario=Decimal('100.00')
        )
        
        # Verificar estoque após venda
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 120)

    def test_fluxo_caixa(self):
        """Testa o fluxo de caixa com diferentes operações"""
        # Venda à vista
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista'
        )
        venda.itens.create(
            produto=self.produto,
            quantidade=1,
            preco_unitario=Decimal('100.00')
        )
        
        # Verificar saldo do caixa
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('1100.00'))
        
        # Compra à vista
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=5,
            custo_unitario=Decimal('50.00'),
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Verificar saldo do caixa
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('850.00'))