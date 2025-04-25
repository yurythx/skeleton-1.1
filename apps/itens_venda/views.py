# itens_venda/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import ItemVenda
from .forms import ItemVendaForm  # Supondo que você tenha um formulário para o item de venda

class ItemVendaListView(ListView):
    model = ItemVenda
    template_name = 'itens_venda/item_venda_list.html'
    context_object_name = 'itens_venda'

class ItemVendaDetailView(DetailView):
    model = ItemVenda
    template_name = 'itens_venda/item_venda_detail.html'
    context_object_name = 'item_venda'

class ItemVendaCreateView(CreateView):
    model = ItemVenda
    form_class = ItemVendaForm  # Formulário para criar o item de venda
    template_name = 'itens_venda/item_venda_form.html'
    success_url = reverse_lazy('item_venda_list')

class ItemVendaUpdateView(UpdateView):
    model = ItemVenda
    form_class = ItemVendaForm  # Formulário para editar o item de venda
    template_name = 'itens_venda/item_venda_form.html'
    success_url = reverse_lazy('item_venda_list')