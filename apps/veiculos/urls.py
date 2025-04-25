from django.urls import path
from .views import (
    VeiculoListView,
    VeiculoDetailView,
    VeiculoCreateView,
    VeiculoUpdateView,
    VeiculoDeleteView
)

app_name = 'veiculos'

urlpatterns = [
    path('', VeiculoListView.as_view(), name='veiculo_list'),
    path('novo/', VeiculoCreateView.as_view(), name='veiculo_create'),
    path('<slug:slug>/', VeiculoDetailView.as_view(), name='veiculo_detail'),
    path('<slug:slug>/editar/', VeiculoUpdateView.as_view(), name='veiculo_update'),
    path('<slug:slug>/excluir/', VeiculoDeleteView.as_view(), name='veiculo_delete'),
]