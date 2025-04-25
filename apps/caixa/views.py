# apps/caixas/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Caixa

# View para listar todos os caixas
class CaixaListView(ListView):
    model = Caixa
    template_name = 'caixas/caixa_list.html'  # Template para exibir a lista de caixas
    context_object_name = 'caixas'  # Nome do contexto para a lista de caixas

    # Você pode adicionar filtros ou outras configurações se necessário
    # Exemplo de filtro por nome
    # def get_queryset(self):
    #     return Caixa.objects.filter(nome__icontains=self.request.GET.get('q', ''))

# View para detalhes de um caixa específico
class CaixaDetailView(DetailView):
    model = Caixa
    template_name = 'caixas/caixa_detail.html'  # Template para exibir detalhes do caixa
    context_object_name = 'caixa'  # Nome do contexto para um único caixa

# View para criar um novo caixa
class CaixaCreateView(CreateView):
    model = Caixa
    template_name = 'caixas/caixa_form.html'  # Template para o formulário de criação de caixa
    fields = ['nome', 'slug', 'saldo_atual']  # Campos do formulário (pode adicionar mais campos)
    success_url = reverse_lazy('caixa_list')  # Redireciona para a lista de caixas após a criação

# View para atualizar um caixa existente
class CaixaUpdateView(UpdateView):
    model = Caixa
    template_name = 'caixas/caixa_form.html'  # Template para o formulário de atualização de caixa
    fields = ['nome', 'slug', 'saldo_atual']  # Campos do formulário (pode adicionar mais campos)
    success_url = reverse_lazy('caixa_list')  # Redireciona para a lista de caixas após a atualização