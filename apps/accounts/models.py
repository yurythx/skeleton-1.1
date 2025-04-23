from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re


# Gerenciador de Usuários Customizado
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e retorna um usuário com email normalizado.
        O método cria o usuário com o email, normaliza o e-mail e define a senha.
        """
        if not email:
            raise ValueError('O usuário deve ter um email')
        email = self.normalize_email(email)  # Normaliza o email para garantir uniformidade
        user = self.model(email=email, **extra_fields)  # Cria a instância do usuário
        user.set_password(password)  # Define a senha de forma segura
        user.save(using=self._db)  # Salva no banco de dados
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e retorna um superusuário com as permissões apropriadas.
        O superusuário tem permissões adicionais como 'is_staff' e 'is_superuser'.
        """
        extra_fields.setdefault('is_staff', True)  # Garante que o superusuário tem acesso à administração
        extra_fields.setdefault('is_superuser', True)  # Garante que o superusuário tenha todas as permissões

        return self.create_user(email, password, **extra_fields)  # Chama a função que cria o usuário normal


# Modelo Customizado de Usuário
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Campos essenciais do usuário
    email = models.EmailField(unique=True)  # O email será único para cada usuário
    nome = models.CharField(max_length=255)  # Nome do usuário, com limite de 255 caracteres
    slug = models.SlugField(unique=True, blank=True, null=True)  # Slug gerado a partir do nome, usado para URLs amigáveis
    telefone = models.CharField(max_length=15, blank=True, null=True)  # Telefone do usuário, pode ser opcional
    data_nascimento = models.DateField(null=True, blank=True)  # Data de nascimento do usuário
    imagem_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True)  # Imagem de perfil do usuário
    is_active = models.BooleanField(default=True)  # Campo que determina se o usuário está ativo
    is_staff = models.BooleanField(default=False)  # Se o usuário tem permissões de staff (acesso ao admin)
    date_joined = models.DateTimeField(default=timezone.now)  # Data e hora que o usuário se registrou
    data_atualizacao = models.DateTimeField(auto_now=True)  # Data e hora da última atualização do usuário

    # Gerenciador de usuários customizado
    objects = CustomUserManager()

    # Definições do modelo para autenticação
    USERNAME_FIELD = 'email'  # O campo de login será o email
    REQUIRED_FIELDS = ['nome']  # Campos obrigatórios na criação do usuário (além do email e senha)

    def save(self, *args, **kwargs):
        """
        Método que gera o slug a partir do nome do usuário.
        Se o slug não for fornecido, o sistema gera automaticamente.
        """
        if not self.slug:
            self.slug = self._generate_slug()  # Chama a função privada para gerar o slug
        super().save(*args, **kwargs)  # Chama o método save original do Django

    def _generate_slug(self):
        """
        Gera um slug amigável e limpo para URLs.
        O slug é baseado no nome do usuário, removendo caracteres especiais.
        """
        slug = slugify(self.nome)  # Cria o slug baseado no nome
        # Limpeza do slug para remover qualquer caractere não alfanumérico
        return re.sub(r'[^a-z0-9-]', '', slug)  

    def get_full_name(self):
        """
        Retorna o nome completo do usuário.
        Método utilizado para obter o nome completo do usuário (usado em algumas interfaces).
        """
        return f"{self.nome}"

    def ativar_usuario(self):
        """
        Ativa o usuário, alterando o campo 'is_active' para True.
        O método só salva a instância se o estado for realmente alterado.
        """
        if not self.is_active:
            self.is_active = True
            self.save()  # Salva a instância com a alteração

    def desativar_usuario(self):
        """
        Desativa o usuário, alterando o campo 'is_active' para False.
        O método só salva a instância se o estado for realmente alterado.
        """
        if self.is_active:
            self.is_active = False
            self.save()  # Salva a instância com a alteração

    def __str__(self):
        """
        Retorna uma representação em string do usuário.
        Aqui, retorna o email como identificador principal.
        """
        return self.email

    def clean(self):
        """
        Valida campos personalizados do modelo.
        Aqui, é realizada a validação de nome, telefone e data de nascimento.
        """
        # Validação do nome: deve ter pelo menos 3 caracteres
        if len(self.nome) < 3:
            raise ValidationError("O nome do usuário deve ter pelo menos 3 caracteres.")
        
        # Validação do telefone: se fornecido, deve ser um número válido
        if self.telefone and not re.match(r'^\+?\d{10,15}$', self.telefone):
            raise ValidationError("O telefone deve ser válido (formato: +1234567890).")
        
        # Validação da data de nascimento: não pode ser maior que a data atual
        if self.data_nascimento and self.data_nascimento > timezone.now().date():
            raise ValidationError("A data de nascimento não pode ser no futuro.")
        
        # Validação do e-mail: verifica se o e-mail está em um formato válido
        from django.core.validators import EmailValidator
        email_validator = EmailValidator()
        email_validator(self.email)  # Aplica a validação do Django para e-mails

        # Validação da senha
        if self.password:
            validate_password(self.password)  # Verifica se a senha está conforme as políticas de segurança do Django