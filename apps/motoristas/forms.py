from django import forms
from .models import Motorista

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'cpf', 'cnh', 'data_validade_cnh', 'endereco', 'telefone', 'email', 'veiculo']

    def clean_cnh(self):
        cnh = self.cleaned_data['cnh']
        if len(cnh) < 11:  # Supondo que a CNH tenha 11 caracteres, você pode ajustar conforme necessário.
            raise forms.ValidationError("A CNH deve conter pelo menos 11 caracteres.")
        return cnh