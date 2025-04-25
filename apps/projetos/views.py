from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from .models import Projeto, Tarefa
from django.views import View

# Lista de Projetos
class ProjetoListView(ListView):
    model = Projeto
    template_name = 'projeto_list.html'


# Detalhes de um Projeto com slug
class ProjetoDetailView(DetailView):
    model = Projeto
    template_name = 'projeto_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


# Atualizar o status de uma Tarefa via AJAX
class AtualizarStatusTarefa(View):
    def post(self, request, *args, **kwargs):
        tarefa_id = request.POST.get('tarefa_id')
        novo_status = request.POST.get('status')

        try:
            tarefa = Tarefa.objects.get(id=tarefa_id)
            tarefa.status = novo_status
            tarefa.save()

            return JsonResponse({'status': 'sucesso', 'novo_status': tarefa.status})
        except Tarefa.DoesNotExist:
            return JsonResponse({'status': 'erro', 'mensagem': 'Tarefa não encontrada'})