from django.urls import path
from .views import (
    CompraListView,
    CompraCreateView,
    CompraUpdateView,
    CompraDeleteView,
    CompraDetailView,
)

app_name = 'compras'

urlpatterns = [
    path('', CompraListView.as_view(), name='lista_compras'),
    path('detalhes/<slug:slug>/', CompraDetailView.as_view(), name='detalhes_compra'),
    path('nova/', CompraCreateView.as_view(), name='nova_compra'),
    path('<slug:slug>/editar/', CompraUpdateView.as_view(), name='editar_compra'),
    path('<slug:slug>/excluir/', CompraDeleteView.as_view(), name='excluir_compra'),
]