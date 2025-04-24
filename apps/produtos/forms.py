from django import forms
from .models import Produto, ImagemProduto


class ProdutoForm(forms.ModelForm):
    """Formulário para criação e edição de produtos."""

    class Meta:
        model = Produto
        exclude = ['slug']  # O slug será gerado automaticamente no método save()
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'largura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'profundidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'status_message': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'visivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocao_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'promocao_fim': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'produtos_relacionados': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class ImagemProdutoForm(forms.ModelForm):
    """Formulário para adicionar imagens extras ao produto."""

    class Meta:
        model = ImagemProduto
        fields = ['imagem', 'legenda']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'legenda': forms.TextInput(attrs={'class': 'form-control'}),
        }