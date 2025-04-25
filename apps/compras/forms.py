from django import forms
from .models import Compra
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto

class CompraForm(forms.ModelForm):
    """Formulário para criação e atualização de compras."""

    class Meta:
        model = Compra
        fields = ['fornecedor', 'produto', 'quantidade', 'custo_unitario', 'data_compra', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'data_compra': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def __init__(self, *args, **kwargs):
        """Adiciona classes aos campos do formulário para estilização."""
        super().__init__(*args, **kwargs)
        self.fields['fornecedor'].widget.attrs.update({'class': 'form-control'})
        self.fields['produto'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantidade'].widget.attrs.update({'class': 'form-control'})
        self.fields['custo_unitario'].widget.attrs.update({'class': 'form-control'})
        self.fields['data_compra'].widget.attrs.update({'class': 'form-control'})
        self.fields['descricao'].widget.attrs.update({'class': 'form-control'})

    def clean_quantidade(self):
        """Valida a quantidade para garantir que seja positiva."""
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade <= 0:
            raise forms.ValidationError("A quantidade deve ser maior que zero.")
        return quantidade

    def clean_custo_unitario(self):
        """Valida o custo unitário para garantir que seja maior que zero."""
        custo_unitario = self.cleaned_data.get('custo_unitario')
        if custo_unitario <= 0:
            raise forms.ValidationError("O custo unitário deve ser maior que zero.")
        return custo_unitario