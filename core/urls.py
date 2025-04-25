from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin route

    path('accounts/', include('apps.accounts.urls', namespace='accounts')),  # Custom users app

    path('', include('apps.pages.urls')),
    path('config/', include('apps.config.urls')),
    path('articles/', include('apps.articles.urls')),
    path('enderecos/', include('apps.enderecos.urls')),
    path('clientes/', include('apps.clientes.urls', namespace='clientes')),
    path('fornecedores/', include('apps.fornecedores.urls', namespace='fornecedores')),
    path('produtos/', include('apps.produtos.urls', namespace='produtos')),
    path('estoque/', include('apps.estoque.urls', namespace='estoque')),
    path('vendas/', include('apps.vendas.urls', namespace='vendas')),
    path('caixa/', include('apps.caixa.urls', namespace='caixa')),
    path('compras/', include('apps.compras.urls', namespace='compras')),
    path('financeiro/', include('apps.financeiro.urls', namespace='financeiro')),
    path('itens_venda/', include('apps.itens_venda.urls', namespace='itens_venda')),
    path('pedidos/', include('apps.pedidos.urls', namespace='pedidos')),
    path('veiculos/', include('apps.veiculos.urls', namespace='veiculos')),
    path('motoristas/', include('apps.motoristas.urls', namespace='motoristas')),

    
    path('projetos/', include('apps.projetos.urls', namespace='projetos')),
    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)