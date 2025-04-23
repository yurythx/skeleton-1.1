from django.urls import path
from .views import (
  CidadesPorEstadoView,
   CidadeListView, CidadeCreateView, CidadeUpdateView,
    CidadeDeleteView, CidadeDetailView, CidadesPorEstadoView
)


app_name = 'enderecos'  # Certifique-se de que este app está registrado com o namespace correto

urlpatterns = [
    path('cidades_por_estado/<int:estado_id>/', CidadesPorEstadoView.as_view(), name='cidades_por_estado'),



    path('cidades/', CidadeListView.as_view(), name='lista_cidades'),
    path('cidades/nova/', CidadeCreateView.as_view(), name='nova_cidade'),
    path('cidades/<slug:slug>/editar/', CidadeUpdateView.as_view(), name='editar_cidade'),
    path('cidades/<slug:slug>/detalhes/', CidadeDetailView.as_view(), name='detalhe_cidade'),
    path('cidades/<slug:slug>/deletar/', CidadeDeleteView.as_view(), name='deletar_cidade'),
    
]
    # Outros caminhos
