import logging

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages

from .models import Cidade, Estado
from .forms import CidadeForm

logger = logging.getLogger(__name__)

# Utilitário para detectar requisições AJAX
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

# View para retornar cidades de um estado via AJAX
class CidadesPorEstadoView(View):
    def get(self, request, estado_id):
        estado = get_object_or_404(Estado, id=estado_id)
        cidades = estado.cidades.all().values('id', 'nome')
        return JsonResponse({'cidades': list(cidades)})

# Mixins para AJAX
class AjaxListMixin:
    partial_template_name = None

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request) and self.partial_template_name:
            return render(self.request, self.partial_template_name, context)
        return super().render_to_response(context, **response_kwargs)

class AjaxFormMixin:
    template_name_ajax = None

    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        if is_ajax(self.request):
            return JsonResponse({'success': True})
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            try:
                self.object = self.get_object()
            except AttributeError:
                self.object = None
            context = self.get_context_data()
            return render(request, self.template_name_ajax or self.template_name, context)
        return super().get(request, *args, **kwargs)

# Listagem de cidades
class CidadeListView(AjaxListMixin, ListView):
    model = Cidade
    template_name = 'enderecos/cidades/lista_cidades.html'
    partial_template_name = 'enderecos/cidades/_lista_cidades.html'
    context_object_name = 'cidades'

    def get_queryset(self):
        nome = self.request.GET.get('nome', '')
        estado_id = self.request.GET.get('estado', '')

        qs = Cidade.objects.select_related('estado')

        if nome:
            qs = qs.filter(nome__icontains=nome)
        if estado_id:
            qs = qs.filter(estado__id=estado_id)

        return qs

# Criação de cidade
class CidadeCreateView(AjaxFormMixin, CreateView):
    model = Cidade
    form_class = CidadeForm
    template_name = 'enderecos/cidades/form_cidade.html'
    template_name_ajax = 'enderecos/cidades/form_cidade.html'
    success_url = reverse_lazy('enderecos:cidades/lista_cidades')

# Edição de cidade
class CidadeUpdateView(AjaxFormMixin, UpdateView):
    model = Cidade
    form_class = CidadeForm
    template_name = 'cidades/form_cidade.html'
    template_name_ajax = 'cidades/includes/form_modal.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('cidades:lista_cidades')

# Detalhes de cidade
class CidadeDetailView(DetailView):
    model = Cidade
    template_name = 'cidades/includes/detalhes_modal.html'
    context_object_name = 'cidade'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        return get_object_or_404(Cidade, slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            self.object = self.get_object()
            context = self.get_context_data()
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

# Exclusão de cidade
class CidadeDeleteView(DeleteView):
    model = Cidade
    template_name = 'cidades/includes/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('cidades:lista_cidades')

    def get_object(self):
        return get_object_or_404(Cidade, slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if is_ajax(request):
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        nome = self.object.nome
        try:
            self.object.delete()
            msg = f'Cidade "{nome}" excluída com sucesso!'
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': msg})
            messages.success(request, msg)
            return redirect(self.success_url)
        except Exception as e:
            logger.error(f"Erro ao excluir cidade '{nome}': {e}")
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': 'Erro ao excluir cidade.'}, status=500)
            messages.error(request, 'Erro ao excluir cidade.')
            return redirect(self.success_url)