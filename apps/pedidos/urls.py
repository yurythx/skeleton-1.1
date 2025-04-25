# pedidos/urls.py
from django.urls import path
from . import views

app_name = 'pedidos'  # Define o app_name

urlpatterns = [
    path('pedidos/', views.PedidoListView.as_view(), name='pedido_list'),
    path('pedido/<slug:slug>/', views.PedidoDetailView.as_view(), name='pedido_detail'),
    path('pedido/criar/', views.PedidoCreateView.as_view(), name='pedido_create'),
    path('pedido/atualizar/<slug:slug>/', views.PedidoUpdateView.as_view(), name='pedido_update'),
]