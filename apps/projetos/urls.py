from django.urls import path
from .views import ProjetoListView, ProjetoDetailView, AtualizarStatusTarefa

app_name = 'projetos'  # Adicione esta linha

urlpatterns = [
    path('', ProjetoListView.as_view(), name='projeto_list'),
    path('projeto/<slug:slug>/', ProjetoDetailView.as_view(), name='projeto_detail'),
    path('atualizar_status_tarefa/', AtualizarStatusTarefa.as_view(), name='atualizar_status_tarefa'),
]