from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Compra

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'fornecedor_link', 'produto_link', 'quantidade', 'valor_final', 'status', 'data_compra', 'forma_pagamento')
    list_filter = ('status', 'forma_pagamento', 'data_compra', 'fornecedor', 'produto')
    search_fields = ('fornecedor__nome', 'produto__nome', 'numero_nota_fiscal', 'observacoes')
    readonly_fields = ('usuario_criacao', 'usuario_atualizacao', 'data_criacao', 'data_atualizacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('fornecedor', 'produto', 'quantidade', 'custo_unitario', 'data_compra')
        }),
        ('Informações Financeiras', {
            'fields': ('status', 'forma_pagamento', 'numero_parcelas', 'desconto', 
                      'valor_frete', 'valor_seguro', 'valor_outras_despesas', 'valor_total', 'valor_final')
        }),
        ('Nota Fiscal', {
            'fields': ('numero_nota_fiscal', 'serie_nota_fiscal', 'data_emissao_nf')
        }),
        ('Transporte', {
            'fields': ('motorista', 'veiculo', 'placa_veiculo', 'uf_veiculo', 
                      'data_chegada', 'data_saida')
        }),
        ('Observações', {
            'fields': ('descricao', 'observacoes')
        }),
        ('Controle', {
            'fields': ('usuario_criacao', 'usuario_atualizacao', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

    def fornecedor_link(self, obj):
        url = reverse('admin:fornecedores_fornecedor_change', args=[obj.fornecedor.id])
        return format_html('<a href="{}">{}</a>', url, obj.fornecedor.nome)
    fornecedor_link.short_description = 'Fornecedor'

    def produto_link(self, obj):
        url = reverse('admin:produtos_produto_change', args=[obj.produto.id])
        return format_html('<a href="{}">{}</a>', url, obj.produto.nome)
    produto_link.short_description = 'Produto'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('fornecedor', 'produto', 'motorista', 'veiculo')

    def save_model(self, request, obj, form, change):
        if not change:  # Se for uma nova compra
            obj.usuario_criacao = request.user
        obj.usuario_atualizacao = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
