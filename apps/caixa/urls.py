from django.urls import path
from . import views

app_name = 'caixa'  # Define o app_name

urlpatterns = [
    path('caixas/', views.CaixaListView.as_view(), name='caixa_list'),
    path('caixa/<slug:slug>/', views.CaixaDetailView.as_view(), name='caixa_detail'),
    path('caixa/criar/', views.CaixaCreateView.as_view(), name='caixa_create'),
    path('caixa/atualizar/<slug:slug>/', views.CaixaUpdateView.as_view(), name='caixa_update'),
]