# estoque/urls.py

from django.urls import path
from .views import (
    EstoqueDetailView,
    AtualizarEstoqueView,
    MovimentoEstoqueListView,
)

app_name = 'estoque'  # Adicionando o app_name para definir o namespace

urlpatterns = [
    path('<slug:slug>/', EstoqueDetailView.as_view(), name='detalhes_estoque'),  # Visualizar estoque de um produto
    path('<slug:slug>/atualizar/', AtualizarEstoqueView.as_view(), name='editar_estoque'),  # Atualizar estoque via AJAX
    path('<slug:slug>/movimentos/', MovimentoEstoqueListView.as_view(), name='movimentos_estoque'),  # Listar movimentos de estoque de um produto
]