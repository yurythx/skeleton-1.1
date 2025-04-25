from django.urls import path
from . import views

app_name = 'vendas'  # Define o app_name

urlpatterns = [
    path('vendas/', views.VendaListView.as_view(), name='venda_list'),
    path('venda/<slug:slug>/', views.VendaDetailView.as_view(), name='venda_detail'),
    path('venda/criar/', views.VendaCreateView.as_view(), name='venda_create'),
    path('venda/atualizar/<slug:slug>/', views.VendaUpdateView.as_view(), name='venda_update'),
]