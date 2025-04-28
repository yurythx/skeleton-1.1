from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from apps.compras.models import Compra
from apps.estoque.models import Estoque, MovimentoEstoque
from apps.financeiro.models import Caixa, MovimentacaoFinanceira, Parcela
from apps.produtos.models import Produto
from apps.fornecedores.models import Fornecedor

User = get_user_model()

class TesteIntegracaoComprasEstoqueFinanceiro(TestCase):
    def setUp(self):
        # Criar usuário
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Criar fornecedor
        self.fornecedor = Fornecedor.objects.create(
            nome='Fornecedor Teste',
            cnpj='12345678901234',
            email='fornecedor@teste.com',
            telefone='11999999999'
        )

        # Criar produto
        self.produto = Produto.objects.create(
            nome='Produto Teste',
            descricao='Descrição do produto teste',
            preco_custo=Decimal('100.00'),
            preco_venda=Decimal('150.00')
        )

        # Criar estoque do produto
        self.estoque = Estoque.objects.create(
            produto=self.produto,
            quantidade=0,
            minimo=5,
            custo_medio=Decimal('0.00')
        )

        # Criar caixa
        self.caixa = Caixa.objects.create(
            nome='Caixa Teste',
            saldo_atual=Decimal('1000.00')
        )

    def test_fluxo_completo_compra(self):
        """Testa o fluxo completo de uma compra com atualização de estoque e movimentação financeira."""
        
        # 1. Criar uma compra
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=10,
            custo_unitario=Decimal('100.00'),
            data_compra=timezone.now(),
            status='confirmada',
            forma_pagamento='avista',
            usuario_criacao=self.user,
            usuario_atualizacao=self.user
        )

        # 2. Verificar se o estoque foi atualizado
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 10)
        self.assertEqual(self.estoque.custo_medio, Decimal('100.00'))

        # 3. Verificar se o movimento de estoque foi criado
        movimento = MovimentoEstoque.objects.filter(
            produto=self.produto,
            tipo='entrada',
            quantidade=10
        ).first()
        self.assertIsNotNone(movimento)
        self.assertEqual(movimento.custo_unitario, Decimal('100.00'))

        # 4. Verificar se a movimentação financeira foi criada
        movimentacao = MovimentacaoFinanceira.objects.filter(
            compra=compra,
            tipo='saida',
            valor=Decimal('1000.00')  # 10 unidades * R$ 100,00
        ).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.status, 'confirmada')

        # 5. Verificar se o saldo do caixa foi atualizado
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('0.00'))  # R$ 1000,00 - R$ 1000,00

    def test_fluxo_completo_compra_parcelada(self):
        """Testa o fluxo completo de uma compra parcelada."""
        
        # 1. Criar uma compra parcelada
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=10,
            custo_unitario=Decimal('100.00'),
            data_compra=timezone.now(),
            status='confirmada',
            forma_pagamento='prazo',
            numero_parcelas=3,
            usuario_criacao=self.user,
            usuario_atualizacao=self.user
        )

        # 2. Verificar se o estoque foi atualizado
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 10)
        self.assertEqual(self.estoque.custo_medio, Decimal('100.00'))

        # 3. Verificar se as parcelas foram criadas
        parcelas = Parcela.objects.filter(
            movimentacao__compra=compra
        ).order_by('numero')
        self.assertEqual(parcelas.count(), 3)
        
        # Verificar valores das parcelas
        valor_parcela = Decimal('333.33')  # R$ 1000,00 / 3
        for parcela in parcelas:
            self.assertEqual(parcela.valor, valor_parcela)
            self.assertEqual(parcela.quitado, False)

        # 4. Verificar se a movimentação financeira foi criada
        movimentacao = MovimentacaoFinanceira.objects.filter(
            compra=compra,
            tipo='saida',
            valor=Decimal('1000.00')
        ).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.status, 'confirmada')

        # 5. Verificar se o saldo do caixa não foi alterado (pois é parcelado)
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('1000.00'))

    def test_compra_cancelada(self):
        """Testa o fluxo de uma compra cancelada."""
        
        # 1. Criar uma compra
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=10,
            custo_unitario=Decimal('100.00'),
            data_compra=timezone.now(),
            status='pendente',
            forma_pagamento='avista',
            usuario_criacao=self.user,
            usuario_atualizacao=self.user
        )

        # 2. Verificar que o estoque não foi alterado
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 0)
        self.assertEqual(self.estoque.custo_medio, Decimal('0.00'))

        # 3. Verificar que não há movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(compra=compra).first()
        self.assertIsNone(movimentacao)

        # 4. Cancelar a compra
        compra.status = 'cancelada'
        compra.save()

        # 5. Verificar que o estoque continua inalterado
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 0)
        self.assertEqual(self.estoque.custo_medio, Decimal('0.00'))

    def test_compra_com_desconto(self):
        """Testa o fluxo de uma compra com desconto."""
        
        # 1. Criar uma compra com desconto
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=self.produto,
            quantidade=10,
            custo_unitario=Decimal('100.00'),
            data_compra=timezone.now(),
            status='confirmada',
            forma_pagamento='avista',
            desconto=Decimal('100.00'),  # R$ 100,00 de desconto
            usuario_criacao=self.user,
            usuario_atualizacao=self.user
        )

        # 2. Verificar se o estoque foi atualizado
        self.estoque.refresh_from_db()
        self.assertEqual(self.estoque.quantidade, 10)
        self.assertEqual(self.estoque.custo_medio, Decimal('100.00'))

        # 3. Verificar se a movimentação financeira foi criada com o valor correto
        movimentacao = MovimentacaoFinanceira.objects.filter(
            compra=compra,
            tipo='saida'
        ).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('900.00'))  # R$ 1000,00 - R$ 100,00 de desconto

        # 4. Verificar se o saldo do caixa foi atualizado corretamente
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('100.00'))  # R$ 1000,00 - R$ 900,00 