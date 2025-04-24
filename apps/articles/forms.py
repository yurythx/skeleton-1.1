from django import forms
from .models import Article, Comment

class ArticleForm(forms.ModelForm):
    # Usando o Textarea padrão para o campo 'content'
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={'cols': 30, 'rows': 10, 'class': 'form-control', 'id': 'id_content'}
        )
    )

    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'imagem_article', 'content', 'category', 'created_by', 'is_published']

    # Validação para o título do artigo
    def clean_title(self):
        title = self.cleaned_data.get('title')  # Corrigido para 'title' em vez de 'Titulo'
        if not title:
            raise forms.ValidationError("O título não pode estar vazio.")
        return title

    # Validação para o resumo (excerpt) do artigo
    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt')
        
        # Verifique se 'excerpt' não é None antes de aplicar len()
        if excerpt is not None and len(excerpt) > 100:
            raise forms.ValidationError("O resumo não pode ter mais de 100 caracteres.")
        
        return excerpt  # Corrigido para retornar apenas o valor de 'excerpt'
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'text']