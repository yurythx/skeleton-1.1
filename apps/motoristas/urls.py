from django.urls import path
from .views import (
    MotoristaListView,
    MotoristaCreateView,
    MotoristaUpdateView,
    MotoristaDeleteView,
    MotoristaDetailView,
)

app_name = 'motoristas'

urlpatterns = [
    path('', MotoristaListView.as_view(), name='lista_motoristas'),
    path('detalhes/<slug:slug>/', MotoristaDetailView.as_view(), name='detalhes_motorista'),
    path('novo/', MotoristaCreateView.as_view(), name='novo_motorista'),
    path('<slug:slug>/editar/', MotoristaUpdateView.as_view(), name='editar_motorista'),
    path('<slug:slug>/excluir/', MotoristaDeleteView.as_view(), name='excluir_motorista'),
]