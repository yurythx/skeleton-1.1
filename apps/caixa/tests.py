from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.clientes.models import Cliente
from apps.fornecedores.models import Fornecedor
from apps.vendas.models import Venda
from apps.compras.models import Compra
from apps.servicos.models import Servico
from apps.financeiro.models import MovimentacaoFinanceira, Parcela
from .models import Caixa

User = get_user_model()

class FluxoCaixaTest(TestCase):
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
        
        # Criar caixa
        self.caixa = Caixa.objects.create(
            nome='Caixa Principal',
            saldo_inicial=Decimal('1000.00'),
            aberto_por=self.user
        )

    def test_abrir_caixa(self):
        """Testa a abertura de um caixa"""
        self.assertEqual(self.caixa.status, 'aberto')
        self.assertEqual(self.caixa.saldo_atual, Decimal('1000.00'))
        self.assertIsNotNone(self.caixa.data_abertura)
        self.assertIsNone(self.caixa.data_fechamento)

    def test_fechar_caixa(self):
        """Testa o fechamento de um caixa"""
        # Fechar caixa
        self.caixa.status = 'fechado'
        self.caixa.fechado_por = self.user
        self.caixa.save()
        
        # Verificar estado do caixa
        self.assertEqual(self.caixa.status, 'fechado')
        self.assertIsNotNone(self.caixa.data_fechamento)

    def test_registrar_venda(self):
        """Testa o registro de uma venda no caixa"""
        # Criar venda
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Registrar venda no caixa
        movimentacao = self.caixa.registrar_venda(venda)
        
        # Verificar movimentação
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.tipo, 'entrada')
        self.assertEqual(movimentacao.caixa, self.caixa)
        
        # Verificar saldo do caixa
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('1000.00'))

    def test_registrar_compra(self):
        """Testa o registro de uma compra no caixa"""
        # Criar compra
        compra = Compra.objects.create(
            fornecedor=self.fornecedor,
            produto=None,  # Não necessário para o teste
            quantidade=1,
            custo_unitario=Decimal('500.00'),
            status='confirmada',
            forma_pagamento='avista'
        )
        
        # Registrar compra no caixa
        movimentacao = self.caixa.registrar_compra(compra)
        
        # Verificar movimentação
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.tipo, 'saida')
        self.assertEqual(movimentacao.caixa, self.caixa)
        
        # Verificar saldo do caixa
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('500.00'))

    def test_registrar_servico(self):
        """Testa o registro de um serviço no caixa"""
        # Criar serviço
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('300.00'),
            status='concluido',
            forma_pagamento='avista'
        )
        
        # Registrar serviço no caixa
        movimentacao = self.caixa.registrar_servico(servico)
        
        # Verificar movimentação
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.tipo, 'entrada')
        self.assertEqual(movimentacao.caixa, self.caixa)
        
        # Verificar saldo do caixa
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('1300.00'))

    def test_registrar_parcela(self):
        """Testa o registro de uma parcela no caixa"""
        # Criar venda a prazo
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='prazo',
            numero_parcelas=3
        )
        
        # Registrar venda no caixa
        movimentacao = self.caixa.registrar_venda(venda)
        
        # Criar parcela
        parcela = Parcela.objects.create(
            movimentacao=movimentacao,
            numero=1,
            valor=Decimal('100.00'),
            data_vencimento=timezone.now()
        )
        
        # Registrar parcela no caixa
        movimentacao_parcela = self.caixa.registrar_parcela(parcela)
        
        # Verificar movimentação
        self.assertIsNotNone(movimentacao_parcela)
        self.assertEqual(movimentacao_parcela.tipo, 'entrada')
        self.assertEqual(movimentacao_parcela.caixa, self.caixa)
        
        # Verificar saldo do caixa
        self.caixa.refresh_from_db()
        self.assertEqual(self.caixa.saldo_atual, Decimal('1100.00'))

    def test_caixa_fechado(self):
        """Testa tentativa de registrar movimentação em caixa fechado"""
        # Fechar caixa
        self.caixa.status = 'fechado'
        self.caixa.fechado_por = self.user
        self.caixa.save()
        
        # Tentar registrar venda
        venda = Venda.objects.create(
            cliente=self.cliente,
            status='confirmada',
            forma_pagamento='avista'
        )
        
        with self.assertRaises(Exception):
            self.caixa.registrar_venda(venda)
