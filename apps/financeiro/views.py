# apps/movimentacoes/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from .models import MovimentacaoFinanceira, Caixa
from apps.compras.models import Compra
from apps.vendas.models import Venda
from apps.servicos.models import Servico
from django.contrib import messages
from django.http import JsonResponse

# View para listar todas as movimentações
class MovimentacaoListView(ListView):
    model = MovimentacaoFinanceira
    template_name = 'movimentacoes/movimentacao_list.html'  # Template para exibir a lista de movimentações
    context_object_name = 'movimentacoes'  # Nome do contexto para a lista de movimentações
    paginate_by = 10

    # Se necessário, pode adicionar filtros ou outras configurações
    # Exemplo de filtro por tipo
    def get_queryset(self):
        tipo = self.request.GET.get('tipo', '')
        return MovimentacaoFinanceira.objects.filter(tipo=tipo) if tipo else MovimentacaoFinanceira.objects.all()

# View para detalhes de uma movimentação específica
class MovimentacaoDetailView(DetailView):
    model = MovimentacaoFinanceira
    template_name = 'movimentacoes/movimentacao_detail.html'  # Template para exibir detalhes da movimentação
    context_object_name = 'movimentacao'  # Nome do contexto para uma única movimentação

# View para criar uma nova movimentação
class MovimentacaoCreateView(CreateView):
    model = MovimentacaoFinanceira
    template_name = 'movimentacoes/movimentacao_form.html'  # Template para o formulário de criação de movimentação
    fields = ['tipo', 'valor', 'data', 'descricao', 'categoria', 'status', 'compra', 'venda', 'servico', 'cliente', 'fornecedor', 'plano_conta']  # Campos do formulário

    def form_valid(self, form):
        # Validação para garantir que apenas um dos campos compra, venda ou serviço seja preenchido
        movimentacao = form.save(commit=False)
        if sum([bool(movimentacao.compra), bool(movimentacao.venda), bool(movimentacao.servico)]) > 1:
            form.add_error(None, "A movimentação deve estar relacionada a no máximo um dos campos: compra, venda ou serviço.")
            return self.form_invalid(form)
        return super().form_valid(form)

    success_url = reverse_lazy('movimentacao_list')  # Redireciona para a lista de movimentações após a criação

# View para atualizar uma movimentação existente
class MovimentacaoUpdateView(UpdateView):
    model = MovimentacaoFinanceira
    template_name = 'movimentacoes/movimentacao_form.html'  # Template para o formulário de atualização de movimentação
    fields = ['tipo', 'valor', 'data', 'descricao', 'categoria', 'status', 'compra', 'venda', 'servico', 'cliente', 'fornecedor', 'plano_conta']  # Campos do formulário

    def form_valid(self, form):
        # Validação para garantir que apenas um dos campos compra, venda ou serviço seja preenchido
        movimentacao = form.save(commit=False)
        if sum([bool(movimentacao.compra), bool(movimentacao.venda), bool(movimentacao.servico)]) > 1:
            form.add_error(None, "A movimentação deve estar relacionada a no máximo um dos campos: compra, venda ou serviço.")
            return self.form_invalid(form)
        return super().form_valid(form)

    success_url = reverse_lazy('movimentacao_list')  # Redireciona para a lista de movimentações após a atualização

class FinanceiroListView(ListView):
    model = MovimentacaoFinanceira
    template_name = 'financeiro/financeiro_list.html'
    context_object_name = 'movimentacoes'
    paginate_by = 10

    def get_queryset(self):
        tipo = self.request.GET.get('tipo', '')
        return MovimentacaoFinanceira.objects.filter(tipo=tipo) if tipo else MovimentacaoFinanceira.objects.all()

class FinanceiroDetailView(DetailView):
    model = MovimentacaoFinanceira
    template_name = 'financeiro/financeiro_detail.html'
    context_object_name = 'movimentacao'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

class FinanceiroCreateView(CreateView):
    model = MovimentacaoFinanceira
    template_name = 'financeiro/financeiro_form.html'
    fields = ['tipo', 'valor', 'data', 'descricao', 'categoria', 'status', 'compra', 'venda', 'servico', 'cliente', 'fornecedor', 'plano_conta']
    success_url = reverse_lazy('financeiro:lista_financeiro')

    def form_valid(self, form):
        movimentacao = form.save(commit=False)
        if sum([bool(movimentacao.compra), bool(movimentacao.venda), bool(movimentacao.servico)]) > 1:
            form.add_error(None, "A movimentação deve estar relacionada a no máximo um dos campos: compra, venda ou serviço.")
            return self.form_invalid(form)
        return super().form_valid(form)

class FinanceiroUpdateView(UpdateView):
    model = MovimentacaoFinanceira
    template_name = 'financeiro/financeiro_form.html'
    fields = ['tipo', 'valor', 'data', 'descricao', 'categoria', 'status', 'compra', 'venda', 'servico', 'cliente', 'fornecedor', 'plano_conta']
    success_url = reverse_lazy('financeiro:lista_financeiro')
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def form_valid(self, form):
        movimentacao = form.save(commit=False)
        if sum([bool(movimentacao.compra), bool(movimentacao.venda), bool(movimentacao.servico)]) > 1:
            form.add_error(None, "A movimentação deve estar relacionada a no máximo um dos campos: compra, venda ou serviço.")
            return self.form_invalid(form)
        return super().form_valid(form)

class FinanceiroDeleteView(DeleteView):
    model = MovimentacaoFinanceira
    template_name = 'financeiro/confirm_delete.html'
    success_url = reverse_lazy('financeiro:lista_financeiro')
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

class CaixaListView(ListView):
    model = Caixa
    template_name = 'financeiro/lista_caixas.html'
    context_object_name = 'caixas'

class AbrirCaixaView(CreateView):
    model = Caixa
    fields = ['nome']
    template_name = 'financeiro/abrir_caixa.html'
    success_url = reverse_lazy('financeiro:lista_caixas')

    def form_valid(self, form):
        # Verifica se já existe um caixa aberto
        if Caixa.objects.filter(status='aberto').exists():
            messages.error(self.request, 'Já existe um caixa aberto.')
            return self.form_invalid(form)
        
        # Cria o novo caixa
        caixa = form.save(commit=False)
        caixa.status = 'aberto'
        caixa.save()
        
        messages.success(self.request, 'Caixa aberto com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)