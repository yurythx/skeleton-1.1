# servicos/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Servico
from .forms import ServicoForm  # Vamos criar um form para o serviço mais adiante

class ServicoListView(ListView):
    model = Servico
    template_name = 'servicos/servico_list.html'  # Template para a lista de serviços
    context_object_name = 'servicos'  # Definindo a variável que será acessada no template
    paginate_by = 10  # Paginação, se necessário

class ServicoDetailView(DetailView):
    model = Servico
    template_name = 'servicos/servico_detail.html'  # Template para exibir os detalhes de um serviço
    context_object_name = 'servico'

class ServicoCreateView(CreateView):
    model = Servico
    form_class = ServicoForm  # Formulário que será usado para criar o serviço
    template_name = 'servicos/servico_form.html'  # Template para criar um serviço
    success_url = reverse_lazy('servico_list')  # Redireciona para a lista de serviços após criar

class ServicoUpdateView(UpdateView):
    model = Servico
    form_class = ServicoForm  # Formulário para atualizar o serviço
    template_name = 'servicos/servico_form.html'  # Template para editar um serviço
    success_url = reverse_lazy('servico_list')  # Redireciona para a lista de serviços após atualizar