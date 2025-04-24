# apps/estoque/forms.py
from django import forms
from .models import Estoque, MovimentoEstoque


class EstoqueUpdateForm(forms.ModelForm):
    """Formulário para atualizar os dados básicos do estoque."""
    class Meta:
        model = Estoque
        fields = ['quantidade', 'minimo']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class MovimentoEstoqueForm(forms.ModelForm):
    """Formulário para registrar manualmente entradas, saídas ou ajustes no estoque."""
    class Meta:
        model = MovimentoEstoque
        fields = ['produto', 'tipo', 'quantidade', 'custo_unitario', 'descricao']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'custo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        tipo = self.cleaned_data.get('tipo')

        if tipo == MovimentoEstoque.TIPO_SAIDA and quantidade < 0:
            raise forms.ValidationError("Para saídas, use valor positivo. O sistema converterá automaticamente.")
        if quantidade == 0:
            raise forms.ValidationError("A quantidade não pode ser zero.")

        return quantidade