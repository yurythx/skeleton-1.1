# pedidos/urls.py
from django.urls import path
from .views import (
    PedidoListView,
    PedidoCreateView,
    PedidoUpdateView,
    PedidoDeleteView,
    PedidoDetailView,
)

app_name = 'pedidos'  # Define o app_name

urlpatterns = [
    path('', PedidoListView.as_view(), name='lista_pedidos'),
    path('detalhes/<slug:slug>/', PedidoDetailView.as_view(), name='detalhes_pedido'),
    path('novo/', PedidoCreateView.as_view(), name='novo_pedido'),
    path('<slug:slug>/editar/', PedidoUpdateView.as_view(), name='editar_pedido'),
    path('<slug:slug>/excluir/', PedidoDeleteView.as_view(), name='excluir_pedido'),
]