from django.urls import path
from .views import (
    ServicoListView,
    ServicoCreateView,
    ServicoUpdateView,
    ServicoDeleteView,
    ServicoDetailView,
)

app_name = 'servicos'

urlpatterns = [
    path('', ServicoListView.as_view(), name='lista_servicos'),
    path('detalhes/<slug:slug>/', ServicoDetailView.as_view(), name='detalhes_servico'),
    path('novo/', ServicoCreateView.as_view(), name='novo_servico'),
    path('<slug:slug>/editar/', ServicoUpdateView.as_view(), name='editar_servico'),
    path('<slug:slug>/excluir/', ServicoDeleteView.as_view(), name='excluir_servico'),
]