from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Motorista
from .forms import MotoristaForm
from django.urls import reverse_lazy

# Lista de motoristas
class MotoristaListView(ListView):
    model = Motorista
    template_name = 'motoristas/motorista_list.html'
    context_object_name = 'motoristas'

# Detalhes de um motorista específico
class MotoristaDetailView(DetailView):
    model = Motorista
    template_name = 'motoristas/motorista_detail.html'
    context_object_name = 'motorista'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

# Criação de um novo motorista
class MotoristaCreateView(CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motoristas/motorista_form.html'
    success_url = reverse_lazy('motoristas:lista_motoristas')

# Edição de um motorista existente
class MotoristaUpdateView(UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motoristas/motorista_form.html'
    success_url = reverse_lazy('motoristas:lista_motoristas')
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

# Exclusão de um motorista
class MotoristaDeleteView(DeleteView):
    model = Motorista
    template_name = 'motoristas/confirm_delete.html'
    success_url = reverse_lazy('motoristas:lista_motoristas')
    slug_url_kwarg = 'slug'
    slug_field = 'slug'