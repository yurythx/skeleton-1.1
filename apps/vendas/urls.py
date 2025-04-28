from django.urls import path
from .views import (
    VendaListView,
    VendaCreateView,
    VendaUpdateView,
    VendaDeleteView,
    VendaDetailView,
)

app_name = 'vendas'

urlpatterns = [
    path('', VendaListView.as_view(), name='lista_vendas'),
    path('detalhes/<slug:slug>/', VendaDetailView.as_view(), name='detalhes_venda'),
    path('nova/', VendaCreateView.as_view(), name='nova_venda'),
    path('<slug:slug>/editar/', VendaUpdateView.as_view(), name='editar_venda'),
    path('<slug:slug>/excluir/', VendaDeleteView.as_view(), name='excluir_venda'),
]