# vendas/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Venda
from .forms import VendaForm  # Supondo que você tenha um formulário para a venda

class VendaListView(ListView):
    model = Venda
    template_name = 'vendas/venda_list.html'
    context_object_name = 'vendas'
    paginate_by = 10  # Se você quiser paginação

class VendaDetailView(DetailView):
    model = Venda
    template_name = 'vendas/venda_detail.html'
    context_object_name = 'venda'

class VendaCreateView(CreateView):
    model = Venda
    form_class = VendaForm  # Formulário para criar a venda
    template_name = 'vendas/venda_form.html'
    success_url = reverse_lazy('venda_list')

class VendaUpdateView(UpdateView):
    model = Venda
    form_class = VendaForm  # Formulário para editar a venda
    template_name = 'vendas/venda_form.html'
    success_url = reverse_lazy('venda_list')