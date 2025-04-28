from django.urls import path
from .views import (
    VeiculoListView,
    VeiculoCreateView,
    VeiculoUpdateView,
    VeiculoDeleteView,
    VeiculoDetailView,
)

app_name = 'veiculos'

urlpatterns = [
    path('', VeiculoListView.as_view(), name='lista_veiculos'),
    path('detalhes/<slug:slug>/', VeiculoDetailView.as_view(), name='detalhes_veiculo'),
    path('novo/', VeiculoCreateView.as_view(), name='novo_veiculo'),
    path('<slug:slug>/editar/', VeiculoUpdateView.as_view(), name='editar_veiculo'),
    path('<slug:slug>/excluir/', VeiculoDeleteView.as_view(), name='excluir_veiculo'),
]