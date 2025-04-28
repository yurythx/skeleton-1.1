# estoque/urls.py

from django.urls import path
from .views import (
    EstoqueListView,
    EstoqueCreateView,
    EstoqueUpdateView,
    EstoqueDeleteView,
    EstoqueDetailView,
)

app_name = 'estoque'

urlpatterns = [
    path('', EstoqueListView.as_view(), name='lista_estoque'),
    path('detalhes/<slug:slug>/', EstoqueDetailView.as_view(), name='detalhes_estoque'),
    path('novo/', EstoqueCreateView.as_view(), name='novo_estoque'),
    path('<slug:slug>/editar/', EstoqueUpdateView.as_view(), name='editar_estoque'),
    path('<slug:slug>/excluir/', EstoqueDeleteView.as_view(), name='excluir_estoque'),
]