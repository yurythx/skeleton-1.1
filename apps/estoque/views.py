from django.http import JsonResponse
from django.views.generic import TemplateView, View
from .models import Estoque, MovimentoEstoque
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class EstoqueDetailView(View):
    """
    View para exibir detalhes do estoque de um produto específico.
    """
    def get(self, request, slug):
        estoque = get_object_or_404(Estoque, produto__slug=slug)
        return JsonResponse({
            'produto': estoque.produto.nome,
            'quantidade': estoque.quantidade,
            'custo_medio': str(estoque.custo_medio),
            'minimo': estoque.minimo,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AtualizarEstoqueView(View):
    """
    View para atualizar o estoque de um produto específico via AJAX.
    """
    def post(self, request, slug):
        produto = get_object_or_404(Estoque, produto__slug=slug)
        quantidade = int(request.POST.get('quantidade', 0))
        custo_unitario = request.POST.get('custo_unitario', None)
        usuario = request.user
        descricao = request.POST.get('descricao', None)

        try:
            produto.atualizar(quantidade, custo_unitario, usuario, descricao)
            return JsonResponse({'status': 'success', 'message': 'Estoque atualizado com sucesso!'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


class MovimentoEstoqueListView(TemplateView):
    """
    View para listar os movimentos de estoque de um produto específico.
    """
    template_name = 'estoque/movimentos_estoque_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produto_slug = kwargs.get('slug')
        produto = get_object_or_404(Estoque, produto__slug=produto_slug)
        movimentos = MovimentoEstoque.objects.filter(produto=produto.produto).order_by('-data')
        context['movimentos'] = movimentos
        return context