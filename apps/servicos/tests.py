from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from apps.clientes.models import Cliente
from apps.caixa.models import Caixa
from apps.financeiro.models import MovimentacaoFinanceira, Parcela
from .models import Servico

class FluxoServicosTest(TestCase):
    def setUp(self):
        # Criar cliente
        self.cliente = Cliente.objects.create(
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11999999999',
            cpf='123.456.789-00',
            limite_credito=Decimal('1000.00')
        )
        
        # Criar caixa
        self.caixa = Caixa.objects.create(
            nome='Caixa Principal',
            saldo_inicial=Decimal('1000.00')
        )

    def test_criar_servico_avista(self):
        """Testa a criação de um serviço à vista"""
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
        self.assertEqual(movimentacao.tipo, 'entrada')

    def test_criar_servico_prazo(self):
        """Testa a criação de um serviço a prazo"""
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('600.00'),
            status='concluido',
            forma_pagamento='prazo',
            numero_parcelas=3
        )
        
        # Verificar valores
        self.assertEqual(servico.valor_final, Decimal('600.00'))
        
        # Verificar parcelas
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        parcelas = Parcela.objects.filter(movimentacao=movimentacao)
        self.assertEqual(parcelas.count(), 3)
        self.assertEqual(parcelas[0].valor, Decimal('200.00'))

    def test_servico_com_desconto(self):
        """Testa a criação de um serviço com desconto"""
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('300.00'),
            desconto=Decimal('50.00'),
            status='concluido',
            forma_pagamento='avista'
        )
        
        # Verificar valores
        self.assertEqual(servico.valor_final, Decimal('250.00'))
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        self.assertEqual(movimentacao.valor, Decimal('250.00'))

    def test_cancelar_servico(self):
        """Testa o cancelamento de um serviço"""
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('300.00'),
            status='concluido',
            forma_pagamento='avista'
        )
        
        # Cancelar serviço
        servico.status = 'cancelado'
        servico.save()
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        self.assertEqual(movimentacao.status, 'cancelada')

    def test_servico_em_andamento(self):
        """Testa a criação de um serviço em andamento"""
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('300.00'),
            status='em_andamento',
            forma_pagamento='avista'
        )
        
        # Verificar que não há movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        self.assertIsNone(movimentacao)
        
        # Concluir serviço
        servico.status = 'concluido'
        servico.save()
        
        # Verificar movimentação financeira após conclusão
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.valor, Decimal('300.00'))

    def test_servico_com_data_conclusao(self):
        """Testa a criação de um serviço com data de conclusão"""
        data_inicio = timezone.now()
        data_conclusao = data_inicio + timezone.timedelta(days=7)
        
        servico = Servico.objects.create(
            cliente=self.cliente,
            descricao='Serviço de teste',
            valor=Decimal('300.00'),
            data_inicio=data_inicio,
            data_conclusao=data_conclusao,
            status='concluido',
            forma_pagamento='avista'
        )
        
        # Verificar datas
        self.assertEqual(servico.data_inicio, data_inicio)
        self.assertEqual(servico.data_conclusao, data_conclusao)
        
        # Verificar movimentação financeira
        movimentacao = MovimentacaoFinanceira.objects.filter(servico=servico).first()
        self.assertIsNotNone(movimentacao)
        self.assertEqual(movimentacao.data, data_inicio)
