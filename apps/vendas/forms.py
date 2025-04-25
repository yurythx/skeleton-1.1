# vendas/forms.py
from django import forms
from .models import Venda

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente', 'data_venda', 'valor_total', 'status', 'desconto']