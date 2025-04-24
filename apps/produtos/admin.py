from django.contrib import admin
from django.utils.html import format_html  # Para marcar o HTML como seguro
from .models import Produto, Categoria, ImagemProduto


class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.imagem.url)
        return "-"
    preview.short_description = "Pré-visualização"


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sku', 'categoria', 'preco', 'estoque', 'visivel', 'status', 'em_promocao')
    list_filter = ('categoria', 'status', 'visivel', 'marca')
    search_fields = ('nome', 'sku', 'descricao')
    # Remover prepopulated_fields, já que o slug é gerado automaticamente no modelo
    inlines = [ImagemProdutoInline]
    readonly_fields = ('status', 'em_promocao', 'data_cadastro', 'slug')  # slug pode ser readonly se necessário
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'sku', 'slug', 'descricao', 'imagem', 'categoria', 'marca')
        }),
        ('Valores e Estoque', {
            'fields': ('preco', 'estoque', 'estoque_minimo', 'status', 'status_message')
        }),
        ('Promoções', {
            'fields': ('promocao_inicio', 'promocao_fim', 'em_promocao')
        }),
        ('Dimensões', {
            'fields': ('peso', 'largura', 'altura', 'profundidade')
        }),
        ('Outros', {
            'fields': ('visivel', 'produtos_relacionados', 'data_cadastro')
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(ImagemProduto)
class ImagemProdutoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'legenda', 'preview')
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.imagem.url)
        return "-"
    preview.short_description = "Pré-visualização"