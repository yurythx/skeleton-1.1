# pedidos/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Pedido
from .forms import PedidoForm  # Supondo que você tenha um formulário para o pedido

class PedidoListView(ListView):
    model = Pedido
    template_name = 'pedidos/pedido_list.html'
    context_object_name = 'pedidos'

class PedidoDetailView(DetailView):
    model = Pedido
    template_name = 'pedidos/pedido_detail.html'
    context_object_name = 'pedido'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

class PedidoCreateView(CreateView):
    model = Pedido
    form_class = PedidoForm  # Formulário para criar o pedido
    template_name = 'pedidos/pedido_form.html'
    success_url = reverse_lazy('pedidos:lista_pedidos')

class PedidoUpdateView(UpdateView):
    model = Pedido
    form_class = PedidoForm  # Formulário para editar o pedido
    template_name = 'pedidos/pedido_form.html'
    success_url = reverse_lazy('pedidos:lista_pedidos')
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

class PedidoDeleteView(DeleteView):
    model = Pedido
    template_name = 'pedidos/confirm_delete.html'
    success_url = reverse_lazy('pedidos:lista_pedidos')
    slug_url_kwarg = 'slug'
    slug_field = 'slug'