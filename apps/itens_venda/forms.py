from django import forms
from .models import ItemVenda

class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ['venda', 'produto', 'quantidade', 'preco_unitario', 'desconto']

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        if quantidade <= 0:
            raise forms.ValidationError("A quantidade deve ser um valor positivo.")
        return quantidade

    def clean_preco_unitario(self):
        preco_unitario = self.cleaned_data['preco_unitario']
        if preco_unitario <= 0:
            raise forms.ValidationError("O preço unitário deve ser um valor positivo.")
        return preco_unitario

    def clean_desconto(self):
        desconto = self.cleaned_data['desconto']
        if desconto < 0:
            raise forms.ValidationError("O desconto não pode ser negativo.")
        return desconto