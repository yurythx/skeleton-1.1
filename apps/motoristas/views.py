from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from .models import Motorista
from .forms import MotoristaForm
from django.urls import reverse_lazy

# Lista de motoristas
class MotoristaListView(ListView):
    model = Motorista
    template_name = 'motorista_list.html'
    context_object_name = 'motoristas'

# Detalhes de um motorista específico
class MotoristaDetailView(DetailView):
    model = Motorista
    template_name = 'motorista_detail.html'
    context_object_name = 'motorista'

# Criação de um novo motorista
class MotoristaCreateView(CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motorista_form.html'
    success_url = reverse_lazy('motorista_list')  # Redireciona para a lista de motoristas após o cadastro

# Edição de um motorista existente
class MotoristaUpdateView(UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motorista_form.html'
    success_url = reverse_lazy('motorista_list')  # Redireciona para a lista de motoristas após a edição