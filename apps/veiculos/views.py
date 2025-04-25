from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import VeiculoForm
from .models import Veiculo

class VeiculoListView(ListView):
    model = Veiculo
    template_name = 'veiculos/veiculo_list.html'
    context_object_name = 'veiculos'

class VeiculoDetailView(DetailView):
    model = Veiculo
    template_name = 'veiculos/veiculo_detail.html'
    context_object_name = 'veiculo'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class VeiculoCreateView(CreateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'veiculos/veiculo_form.html'
    success_url = reverse_lazy('veiculo_list')

class VeiculoUpdateView(UpdateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'veiculos/veiculo_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('veiculo_list')

class VeiculoDeleteView(DeleteView):
    model = Veiculo
    template_name = 'veiculos/veiculo_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('veiculo_list')