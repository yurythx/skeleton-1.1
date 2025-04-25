from django.urls import path
from . import views

app_name = 'servicos'  # Define o app_name

urlpatterns = [
    path('servicos/', views.ServicoListView.as_view(), name='servico_list'),
    path('servico/<slug:slug>/', views.ServicoDetailView.as_view(), name='servico_detail'),
    path('servico/criar/', views.ServicoCreateView.as_view(), name='servico_create'),
    path('servico/atualizar/<slug:slug>/', views.ServicoUpdateView.as_view(), name='servico_update'),
]