from django.contrib import admin
from .models import Fornecedor

class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cpf', 'cnpj', 'data_fundacao', 'data_cadastro')
    search_fields = ('nome', 'email', 'cpf', 'cnpj')
    list_filter = ('data_fundacao',)
    prepopulated_fields = {'slug': ('nome',)}

    # Campos para o formulário de criação/edição no admin
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'email', 'telefone', 'cpf', 'cnpj', 'data_fundacao')
        }),
        ('Endereço', {
            'fields': ('endereco',)
        }),
        ('Data e Slug', {
            'fields': ('slug', 'data_cadastro')
        }),
    )

    readonly_fields = ('data_cadastro',)

    def save_model(self, request, obj, form, change):
        """Override do método de salvar para garantir que o slug seja criado corretamente."""
        if not obj.slug:
            obj.slug = f'{obj.nome.lower().replace(" ", "-")}'
        super().save_model(request, obj, form, change)

    def get_search_results(self, request, queryset, search_term):
        """
        Modifica a busca para melhorar os resultados de busca de fornecedores, 
        considerando campos como nome, email, CPF e CNPJ.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

# Registrando o modelo e o admin
admin.site.register(Fornecedor, FornecedorAdmin)