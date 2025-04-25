# itens_venda/urls.py
from django.urls import path
from . import views

app_name = 'itens_venda'

urlpatterns = [
    path('itens_venda/', views.ItemVendaListView.as_view(), name='item_venda_list'),
    path('item_venda/<slug:slug>/', views.ItemVendaDetailView.as_view(), name='item_venda_detail'),
    path('item_venda/criar/', views.ItemVendaCreateView.as_view(), name='item_venda_create'),
    path('item_venda/atualizar/<slug:slug>/', views.ItemVendaUpdateView.as_view(), name='item_venda_update'),
]