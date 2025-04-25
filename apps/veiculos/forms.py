from django import forms
from .models import Veiculo

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'marca',
            'modelo',
            'ano',
            'placa',
            'cor',
            'tipo',
            'chassi',
            'renavam',
            'observacoes',
        ]
        widgets = {
            'ano': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'renavam': 'RENAVAM',
            'chassi': 'Chassi',
        }

    def clean_placa(self):
        placa = self.cleaned_data['placa'].upper()
        if len(placa) < 7:
            raise forms.ValidationError("A placa deve ter pelo menos 7 caracteres.")
        return placa