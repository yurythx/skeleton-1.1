# Importações padrão do Django para views genéricas e manipulação de requisições
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
import logging
from django.core.exceptions import ValidationError

# Importa o modelo e os formulários utilizados
from .models import Compra
from .forms import CompraForm
from apps.produtos.forms import ProdutoForm  # Caso utilize formulário para produto, por exemplo
from apps.fornecedores.forms import FornecedorForm

# Função auxiliar para detectar requisições AJAX modernas
def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


# Mixin reutilizável para views de listagem que precisam retornar HTML parcial via AJAX
class AjaxListMixin:
    partial_template_name = None  # Template usado para renderização AJAX

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request) and self.partial_template_name:
            return render(self.request, self.partial_template_name, context)
        return super().render_to_response(context, **response_kwargs)


# View de listagem de compras com filtro e suporte AJAX
class CompraListView(AjaxListMixin, ListView):
    model = Compra
    template_name = 'compras/lista_compras.html'
    partial_template_name = 'compras/_lista_compras.html'
    context_object_name = 'compras'

    def get_queryset(self):
        # Obtém filtros da requisição
        fornecedor_busca = self.request.GET.get('fornecedor', '')
        produto_busca = self.request.GET.get('produto', '')

        queryset = Compra.objects.all()
        # Aplica filtros se fornecidos
        if fornecedor_busca:
            queryset = queryset.filter(fornecedor__nome__icontains=fornecedor_busca)
        if produto_busca:
            queryset = queryset.filter(produto__nome__icontains=produto_busca)
        return queryset


# Mixin que facilita manipulação de formulários via AJAX
class AjaxFormMixin:
    template_name_ajax = None  # Template para renderização AJAX de formulários

    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        # Em caso de DeleteView, executa a exclusão diretamente
        if isinstance(self, DeleteView):
            return self.delete(self.request)

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


# View para criação de compras
class CompraCreateView(AjaxFormMixin, CreateView):
    model = Compra
    form_class = CompraForm
    template_name = 'compras/form_compra.html'
    success_url = reverse_lazy('compras:lista_compras')

    def form_valid(self, form):
        """Após salvar a compra, realiza a atualização de estoque."""
        try:
            with transaction.atomic():
                # Salva o formulário
                self.object = form.save(commit=False)
                
                # Preenche os campos de usuário
                self.object.usuario_criacao = self.request.user
                self.object.usuario_atualizacao = self.request.user
                
                # Calcula os valores antes de salvar
                self.object.calcular_valores()
                
                # Valida o objeto antes de salvar
                self.object.full_clean()
                
                # Salva o objeto
                self.object.save()
                
                # Se a compra estiver confirmada, atualiza o estoque e cria movimentações
                if self.object.status == 'confirmada':
                    try:
                        # Verifica se há caixa aberto antes de prosseguir
                        from apps.financeiro.models import Caixa
                        caixa = Caixa.objects.filter(status='aberto').first()
                        if not caixa and self.object.forma_pagamento != 'prazo':
                            raise ValidationError("Não há caixa aberto para registrar a movimentação financeira.")

                        # Atualiza o estoque
                        self.object.atualizar_estoque()
                        
                        # Cria as movimentações financeiras
                        if self.object.forma_pagamento == 'prazo':
                            self.object.criar_parcelas()
                        else:
                            self.object.criar_movimentacao_financeira()
                            
                    except ValidationError as e:
                        logger.error(f"Erro ao processar compra confirmada: {str(e)}")
                        raise
                    except Exception as e:
                        logger.error(f"Erro inesperado ao processar compra confirmada: {str(e)}")
                        raise ValidationError(f"Erro ao processar compra confirmada: {str(e)}")

            if is_ajax(self.request):
                return JsonResponse({
                    'success': True, 
                    'message': 'Compra criada com sucesso!',
                    'redirect_url': self.success_url
                })
            messages.success(self.request, 'Compra criada com sucesso!')
            return redirect(self.success_url)
            
        except ValidationError as e:
            logger.error(f"Erro de validação ao criar compra: {str(e)}")
            if is_ajax(self.request):
                return JsonResponse({
                    'success': False,
                    'message': str(e),
                    'errors': {'__all__': [str(e)]}
                }, status=400)
            messages.error(self.request, str(e))
            return self.form_invalid(form)
            
        except Exception as e:
            logger.error(f"Erro inesperado ao criar compra: {str(e)}")
            if is_ajax(self.request):
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao criar compra: {str(e)}'
                }, status=400)
            messages.error(self.request, f'Erro ao criar compra: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error(f"Erros de validação do formulário: {form.errors}")
        if is_ajax(self.request):
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Por favor, corrija os erros abaixo.'
            }, status=400)
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if is_ajax(request):
            return self.form_valid(form) if form.is_valid() else self.form_invalid(form)
        return super().post(request, *args, **kwargs)


# View para atualização de compras
class CompraUpdateView(AjaxFormMixin, UpdateView):
    model = Compra
    form_class = CompraForm
    template_name = 'compras/form_compra.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        """Após salvar a compra, realiza a atualização de estoque."""
        try:
            with transaction.atomic():
                # Salva o formulário
                self.object = form.save(commit=False)
                
                # Atualiza o usuário de atualização
                self.object.usuario_atualizacao = self.request.user
                
                # Calcula os valores antes de salvar
                self.object.calcular_valores()
                
                # Valida o objeto antes de salvar
                self.object.full_clean()
                
                # Salva o objeto
                self.object.save()
                
                # Atualiza o estoque
                self.object.atualizar_estoque()

            if is_ajax(self.request):
                return JsonResponse({
                    'success': True,
                    'message': 'Compra atualizada com sucesso!',
                    'redirect_url': reverse_lazy('compras:lista_compras')
                })
            messages.success(self.request, 'Compra atualizada com sucesso!')
            return redirect('compras:lista_compras')
            
        except ValidationError as e:
            logger.error(f"Erro de validação ao atualizar compra: {str(e)}")
            if is_ajax(self.request):
                return JsonResponse({
                    'success': False,
                    'message': str(e),
                    'errors': {'__all__': [str(e)]}
                }, status=400)
            messages.error(self.request, str(e))
            return self.form_invalid(form)
            
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar compra: {str(e)}")
            if is_ajax(self.request):
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao atualizar compra: {str(e)}'
                }, status=400)
            messages.error(self.request, f'Erro ao atualizar compra: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error(f"Erros de validação do formulário: {form.errors}")
        if is_ajax(self.request):
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Por favor, corrija os erros abaixo.'
            }, status=400)
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if is_ajax(request):
            return self.form_valid(form) if form.is_valid() else self.form_invalid(form)
        return super().post(request, *args, **kwargs)


# View para exibir detalhes da compra (usado para modal)
class CompraDetailView(DetailView):
    model = Compra
    template_name = 'compras/detalhes_compra_modal.html'
    context_object_name = 'compra'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        try:
            return get_object_or_404(Compra, slug=self.kwargs['slug'])
        except Exception as e:
            logger.error(f"Erro ao buscar compra: {str(e)}")
            raise

    def get(self, request, *args, **kwargs):
        try:
            if is_ajax(request):
                self.object = self.get_object()
                context = self.get_context_data()
                return render(request, self.template_name, context)
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Erro ao renderizar detalhes da compra: {str(e)}")
            if is_ajax(request):
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao carregar detalhes: {str(e)}'
                }, status=500)
            raise


# View para exclusão de compras
# Inicializando o logger
logger = logging.getLogger(__name__)

class CompraDeleteView(DeleteView):
    model = Compra
    template_name = 'compras/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('compras:lista_compras')

    def get_object(self, queryset=None):
        # Obter a compra com base no slug
        slug = self.kwargs.get('slug')
        logger.debug(f"Slug recebido: {slug}")
        compra = get_object_or_404(Compra, slug=slug)
        return compra

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.debug(f"Contexto para renderização: {context}")
        return context

    def get(self, request, *args, **kwargs):
        # Chamando get_object e get_context_data para processar o GET
        self.object = self.get_object()
        context = self.get_context_data()
        logger.debug(f"Requisição GET para excluir compra {self.object.id}")

        if is_ajax(request):
            # Se for uma requisição AJAX, renderiza o template diretamente
            return render(request, self.template_name, context)
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Chamando get_object novamente para garantir que estamos lidando com o objeto correto
        self.object = self.get_object()
        id_compra = self.object.id
        logger.debug(f"Iniciando exclusão da compra: {id_compra}")

        try:
            self.object.delete()
            logger.debug(f"Compra {id_compra} excluída com sucesso")
            success_message = f'Compra de ID "{id_compra}" excluída com sucesso!'
            
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': success_message})

            # Caso contrário, exibe a mensagem de sucesso e redireciona
            messages.success(request, success_message)
            return redirect(self.success_url)
        
        except Exception as e:
            logger.error(f"Erro ao excluir compra {id_compra}: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Erro ao excluir compra.'})