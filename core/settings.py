import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import logging

# Carrega as variáveis do arquivo .env
load_dotenv()

# Caminhos base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = BASE_DIR  # Usando BASE_DIR diretamente para evitar redundância

# SECRET_KEY e DEBUG
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("A chave SECRET_KEY é necessária no arquivo .env")

DEBUG = os.getenv('DEBUG', 'True') == 'True'  # Converte de string para booleano

# Hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS não está configurado corretamente.")

# Assets
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/')

# Função para testar conexão MySQL
def test_mysql_connection():
    """Tenta se conectar ao MySQL e retorna True se bem-sucedido"""
    connection = None  # Inicializa a variável connection antes do bloco try
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'appseed_db'),
            user=os.getenv('DB_USERNAME', 'appseed_db_usr'),
            password=os.getenv('DB_PASS', 'pass'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        if connection.is_connected():
            print("Conexão com MySQL bem-sucedida.")
            return True
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

# Função para configurar o banco de dados
def setup_database():
    """Configura o banco de dados com base na variável de ambiente DB_ENGINE"""
    db_engine = os.getenv('DB_ENGINE', 'mysql')

    if db_engine == 'mysql' and test_mysql_connection():
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.getenv('DB_NAME', 'appseed_db'),
                'USER': os.getenv('DB_USERNAME', 'appseed_db_usr'),
                'PASSWORD': os.getenv('DB_PASS', 'pass'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', 3306),
            }
        }
    else:
        # Se a conexão com MySQL falhar ou o DB_ENGINE for outro, use SQLite
        print("Falha ao conectar ao MySQL, configurando o banco de dados SQLite...")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, os.getenv('SQLITE_DB_PATH', 'db.sqlite3')),
            }
        }
    
    return DATABASES

# Banco de dados (MySQL ou SQLite)
DATABASES = setup_database()

# Validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('pt', 'Portuguese'),
]

# Arquivos estáticos
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(CORE_DIR, 'apps/static')]

# Arquivos de mídia (caso use uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(CORE_DIR, 'apps/media')

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# TinyMCE
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'menubar': False,
    'plugins': [
        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'codesample', 'print',
        'preview', 'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'media', 'table', 'textcolor', 'paste', 'help', 'wordcount'
    ],
    'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright | '
               'bullist numlist | link image media | code | fullscreen preview | '
               'wordcount | help',
    'contextmenu': 'formats | link image',
    'statusbar': True,
    'content_style': 'body { font-family: Helvetica, Arial, sans-serif; font-size: 14px; }',
}

# Modelo de usuário customizado
AUTH_USER_MODEL = 'accounts.CustomUser'

# Redirecionamento após login/logout
LOGIN_REDIRECT_URL = "pages"
LOGOUT_REDIRECT_URL = "pages"

# Diretório de templates global (base.html, etc.)
TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")

# Configuração de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],       # Diretório global
        'APP_DIRS': True,             # Templates por app (ex: apps/clientes/templates/clientes/)
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.cfg_assets_root',
            ],
        },
    },
]

# Apps instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'widget_tweaks',
    'tinymce',
    'crispy_forms',
    'crispy_bootstrap5',
    'axes',

    # Seus apps
    'apps.accounts',
    'apps.pages',
    'apps.config',
    'apps.articles',
    'apps.clientes',
    'apps.fornecedores',
    'apps.enderecos',
    'apps.produtos',
    'apps.estoque',
    'apps.compras',
    'apps.vendas',
    'apps.itens_venda',
    'apps.caixa',
    'apps.servicos',
    'apps.pedidos',
    'apps.financeiro',
    'apps.projetos',
    'apps.veiculos',
    'apps.motoristas',
    
    'apps.chatbot',
    
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'apps.accounts.middleware.AxesRedirectMiddleware',  # ← Ativar isso aqui
    
]

# Arquivo de template que será exibido para erro 403
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Segurança adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True  # Só envia o cookie via HTTPS
SESSION_COOKIE_SECURE = True  # Só envia o cookie via HTTPS

# Define o número máximo de tentativas de login falhadas antes de bloquear o usuário
AXES_FAILURE_LIMIT = 5

# Define o período de tempo em que as tentativas de login falhadas são registradas (em segundos)
AXES_COOLOFF_TIME = 1 * 60  # 1 minuto

# Expirando o bloqueio após X minutos de inatividade
AXES_LOCK_OUT_AT_FAILURE = True  # Ativa o bloqueio de usuário após tentativas de login falhas

# Enviar emails de alerta quando um IP é bloqueado ou um usuário
AXES_EMAIL_ALERTS = True

#

# URLs e WSGI
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

# Arquivos estáticos
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(CORE_DIR, 'media')

# Configuração de backends de autenticação para django-axes
AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesStandaloneBackend',  # Backend de autenticação do django-axes
    'django.contrib.auth.backends.ModelBackend',  # Backend padrão do Django
)