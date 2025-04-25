from django.urls import path
from . import views

app_name = 'financeiro'  # Define o app_name

urlpatterns = [
    path('movimentacoes/', views.MovimentacaoListView.as_view(), name='movimentacao_list'),
    path('movimentacao/<slug:slug>/', views.MovimentacaoDetailView.as_view(), name='movimentacao_detail'),
    path('movimentacao/criar/', views.MovimentacaoCreateView.as_view(), name='movimentacao_create'),
    path('movimentacao/atualizar/<slug:slug>/', views.MovimentacaoUpdateView.as_view(), name='movimentacao_update'),
]
