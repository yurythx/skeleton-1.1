# apps/estoque/admin.py
from django.contrib import admin
from .models import Estoque, MovimentoEstoque


class MovimentoEstoqueInline(admin.TabularInline):
    model = MovimentoEstoque
    extra = 0
    readonly_fields = ('data', 'tipo', 'quantidade', 'custo_unitario', 'usuario', 'descricao')
    can_delete = False
    show_change_link = True
    verbose_name_plural = "Histórico de Movimentações"





@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ['produto', 'quantidade', 'minimo', 'custo_medio']
    search_fields = ['produto__nome']
    readonly_fields = ['custo_medio']



@admin.register(MovimentoEstoque)
class MovimentoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'custo_unitario', 'data', 'usuario')
    search_fields = ('produto__nome', 'usuario__username', 'descricao')
    list_filter = ('tipo', 'data', 'produto__categoria')
    date_hierarchy = 'data'
    readonly_fields = ('produto', 'tipo', 'quantidade', 'custo_unitario', 'data', 'usuario', 'descricao')