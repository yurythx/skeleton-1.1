from django.http import JsonResponse
from django.views.generic import TemplateView, View, ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Estoque, MovimentoEstoque
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

class EstoqueListView(ListView):
    model = Estoque
    template_name = 'estoque/estoque_list.html'
    context_object_name = 'estoques'

class EstoqueCreateView(CreateView):
    model = Estoque
    template_name = 'estoque/estoque_form.html'
    fields = ['produto', 'quantidade', 'minimo']
    success_url = reverse_lazy('estoque:lista_estoque')

class EstoqueUpdateView(UpdateView):
    model = Estoque
    template_name = 'estoque/estoque_form.html'
    fields = ['produto', 'quantidade', 'minimo']
    success_url = reverse_lazy('estoque:lista_estoque')
    slug_url_kwarg = 'slug'
    slug_field = 'produto__slug'

class EstoqueDeleteView(DeleteView):
    model = Estoque
    template_name = 'estoque/confirm_delete.html'
    success_url = reverse_lazy('estoque:lista_estoque')
    slug_url_kwarg = 'slug'
    slug_field = 'produto__slug'

class EstoqueDetailView(DetailView):
    model = Estoque
    template_name = 'estoque/estoque_detail.html'
    context_object_name = 'estoque'
    slug_url_kwarg = 'slug'
    slug_field = 'produto__slug'

@method_decorator(csrf_exempt, name='dispatch')
class AtualizarEstoqueView(View):
    """
    View para atualizar o estoque de um produto específico via AJAX.
    """
    def post(self, request, slug):
        estoque = get_object_or_404(Estoque, produto__slug=slug)
        quantidade = int(request.POST.get('quantidade', 0))
        custo_unitario = request.POST.get('custo_unitario', None)
        usuario = request.user
        descricao = request.POST.get('descricao', None)

        try:
            estoque.atualizar(quantidade, custo_unitario, usuario, descricao)
            return JsonResponse({'status': 'success', 'message': 'Estoque atualizado com sucesso!'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class MovimentoEstoqueListView(ListView):
    model = MovimentoEstoque
    template_name = 'estoque/movimentos_estoque_list.html'
    context_object_name = 'movimentos'

    def get_queryset(self):
        return MovimentoEstoque.objects.filter(produto__slug=self.kwargs['slug']).order_by('-data')