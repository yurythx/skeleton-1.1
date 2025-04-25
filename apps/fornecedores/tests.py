from django.test import TestCase
from apps.fornecedores.models import Fornecedor
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from datetime import date


class FornecedorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial para os testes."""
        cls.fornecedor1 = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            email="fornecedor1@email.com",
            telefone="(11) 12345-6789",
            cnpj="12.345.678/0001-90",
            data_fundacao=date(2000, 1, 1)
        )

    def test_create_fornecedor_with_slug(self):
        """Testa a criação de fornecedor com slug gerado automaticamente."""
        fornecedor = Fornecedor.objects.get(nome="Fornecedor Teste")
        
        # Verifica se o slug foi gerado automaticamente
        self.assertEqual(fornecedor.slug, "fornecedor-teste")

    def test_create_fornecedor_with_unique_slug(self):
        """Testa a criação de fornecedores com o mesmo nome, garantindo slugs únicos."""
        # Cria o segundo fornecedor com nome semelhante
        fornecedor2 = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            email="fornecedor2@email.com",
            telefone="(11) 98765-4321",
            cnpj="98.765.432/0001-10",
            data_fundacao=date(2005, 5, 5)
        )

        # Verifica se o segundo fornecedor tem um slug único
        self.assertEqual(fornecedor2.slug, "fornecedor-teste-1")

    def test_create_fornecedor_with_invalid_cpf(self):
        """Testa a validação de CPF com formato inválido."""
        fornecedor = Fornecedor(
            nome="Fornecedor CPF Inválido",
            email="fornecedor3@email.com",
            telefone="(11) 11222-3344",
            cpf="123.456.789",  # CPF inválido
            cnpj=None,
            data_fundacao=date(2010, 10, 10)
        )

        # Verifica se a validação de CPF falha
        with self.assertRaises(ValidationError):
            fornecedor.clean()  # Chama o método clean para validação

    def test_create_fornecedor_with_valid_cpf(self):
        """Testa a validação de CPF com formato válido."""
        fornecedor = Fornecedor(
            nome="Fornecedor CPF Válido",
            email="fornecedor4@email.com",
            telefone="(11) 11222-3344",
            cpf="123.456.789-00",  # CPF válido
            cnpj=None,
            data_fundacao=date(2015, 5, 15)
        )

        # Não deve gerar exceção, pois o CPF é válido
        fornecedor.clean()  # Chama o método clean para validação sem erro

    def test_create_fornecedor_with_invalid_cnpj(self):
        """Testa a validação de CNPJ com formato inválido."""
        fornecedor = Fornecedor(
            nome="Fornecedor CNPJ Inválido",
            email="fornecedor5@email.com",
            telefone="(11) 33445-6677",
            cpf=None,
            cnpj="12345/6789",  # CNPJ inválido
            data_fundacao=date(2015, 5, 15)
        )

        # Verifica se a validação de CNPJ falha
        with self.assertRaises(ValidationError):
            fornecedor.clean()

    def test_create_fornecedor_with_valid_cnpj(self):
        """Testa a validação de CNPJ com formato válido."""
        fornecedor = Fornecedor(
            nome="Fornecedor CNPJ Válido",
            email="fornecedor6@email.com",
            telefone="(11) 99888-7766",
            cpf=None,
            cnpj="12.345.678/0001-90",  # CNPJ válido
            data_fundacao=date(2020, 6, 6)
        )

        # Não deve gerar exceção, pois o CNPJ é válido
        fornecedor.clean()  # Chama o método clean para validação sem erro

    def test_create_fornecedor_with_empty_cpf_and_cnpj(self):
        """Testa a criação de fornecedor sem CPF e CNPJ (quando ambos são opcionais)."""
        fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Sem CPF e CNPJ",
            email="fornecedor7@email.com",
            telefone="(11) 44444-5555",
            cpf=None,  # Nenhum CPF
            cnpj=None,  # Nenhum CNPJ
            data_fundacao=date(2021, 7, 7)
        )

        # Verifica se o fornecedor foi criado corretamente, sem CPF e CNPJ
        self.assertIsNone(fornecedor.cpf)
        self.assertIsNone(fornecedor.cnpj)

    def test_create_fornecedor_with_unique_email(self):
        """Testa a criação de fornecedores com e-mails únicos."""
        fornecedor2 = Fornecedor(
            nome="Fornecedor Email Único",
            email="fornecedor8@email.com",
            telefone="(11) 55555-6666",
            cnpj="12.345.678/0001-91",
            data_fundacao=date(2021, 1, 1)
        )

        # Verifica se o e-mail é único, criando um fornecedor com o mesmo e-mail
        with self.assertRaises(IntegrityError):
            fornecedor_duplicate = Fornecedor(
                nome="Fornecedor Email Duplicado",
                email="fornecedor8@email.com",  # Mesmo e-mail
                telefone="(11) 66666-7777",
                cnpj="12.345.678/0001-92",
                data_fundacao=date(2021, 5, 5)
            )
            fornecedor_duplicate.save()
