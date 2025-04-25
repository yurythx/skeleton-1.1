from django.contrib import admin
from .models import Projeto, Tarefa

# Registro do modelo Projeto
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'descricao')
    prepopulated_fields = {'slug': ('titulo',)}  # Gera automaticamente o slug a partir do título

# Registro do modelo Tarefa
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'projeto')
    list_filter = ('status', 'projeto')
    search_fields = ('titulo', 'descricao')
    raw_id_fields = ('projeto',)  # Use um campo de pesquisa para o campo Projeto

# Registrar os modelos no admin
admin.site.register(Projeto, ProjetoAdmin)
admin.site.register(Tarefa, TarefaAdmin)