# produto/urls.py
from django.urls import path
from .views import (
    ProdutoListView,
    ProdutoCreateView,
    ProdutoUpdateView,
    ProdutoDeleteView,
    ProdutoDetailView,
)

app_name = 'produtos'  # Define o app_name

urlpatterns = [
    path('', ProdutoListView.as_view(), name='lista_produtos'),  # Lista de produtos
    path('detalhes/<slug:slug>/', ProdutoDetailView.as_view(), name='detalhes_produto'),  # Visualizar produto específico
    path('novo/', ProdutoCreateView.as_view(), name='novo_produto'),  # Criar produto
    path('<slug:slug>/editar/', ProdutoUpdateView.as_view(), name='editar_produto'),  # Editar produto
    path('<slug:slug>/excluir/', ProdutoDeleteView.as_view(), name='excluir_produto'),  # Excluir produto
]