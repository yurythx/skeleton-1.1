from django.urls import path
from .views import (
    FinanceiroListView,
    FinanceiroCreateView,
    FinanceiroUpdateView,
    FinanceiroDeleteView,
    FinanceiroDetailView,
    AbrirCaixaView,
    CaixaListView,
)

app_name = 'financeiro'

urlpatterns = [
    path('', FinanceiroListView.as_view(), name='lista_financeiro'),
    path('detalhes/<slug:slug>/', FinanceiroDetailView.as_view(), name='detalhes_financeiro'),
    path('novo/', FinanceiroCreateView.as_view(), name='novo_financeiro'),
    path('<slug:slug>/editar/', FinanceiroUpdateView.as_view(), name='editar_financeiro'),
    path('<slug:slug>/excluir/', FinanceiroDeleteView.as_view(), name='excluir_financeiro'),
    path('caixa/abrir/', AbrirCaixaView.as_view(), name='abrir_caixa'),
    path('caixa/', CaixaListView.as_view(), name='lista_caixas'),
]
