from django import forms
from .models import Compra
from apps.motoristas.models import Motorista
from apps.veiculos.models import Veiculo
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'cpf', 'cnh', 'data_validade_cnh', 'telefone', 'email', 'endereco', 'veiculo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'cnh': forms.TextInput(attrs={'class': 'form-control'}),
            'data_validade_cnh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'veiculo': forms.Select(attrs={'class': 'form-control'}),
        }

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'marca', 'ano', 'cor', 'tipo', 'chassi', 'renavam', 'observacoes']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'chassi': forms.TextInput(attrs={'class': 'form-control'}),
            'renavam': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CompraForm(forms.ModelForm):
    """Formulário para criação e atualização de compras."""

    class Meta:
        model = Compra
        fields = [
            'fornecedor', 'produto', 'quantidade', 'custo_unitario',
            'data_compra', 'status', 'forma_pagamento', 'numero_parcelas',
            'desconto', 'descricao', 'numero_nota_fiscal', 'serie_nota_fiscal',
            'data_emissao_nf', 'valor_frete', 'valor_seguro', 'valor_outras_despesas',
            'motorista', 'veiculo', 'placa_veiculo', 'uf_veiculo',
            'data_chegada', 'data_saida', 'observacoes'
        ]
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'custo_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_compra': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'numero_parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'numero_nota_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'serie_nota_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'data_emissao_nf': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_seguro': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_outras_despesas': forms.NumberInput(attrs={'class': 'form-control'}),
            'motorista': forms.Select(attrs={'class': 'form-control'}),
            'veiculo': forms.Select(attrs={'class': 'form-control'}),
            'placa_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_veiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_chegada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_saida': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """Adiciona classes aos campos do formulário para estilização."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            if not self.fields[field].required:
                self.fields[field].widget.attrs.update({'placeholder': 'Opcional'})

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

    def clean_desconto(self):
        """Valida o desconto para garantir que seja não negativo."""
        desconto = self.cleaned_data.get('desconto')
        if desconto < 0:
            raise forms.ValidationError("O desconto não pode ser negativo.")
        return desconto

    def clean_valor_frete(self):
        """Valida o valor do frete para garantir que seja não negativo."""
        valor_frete = self.cleaned_data.get('valor_frete')
        if valor_frete < 0:
            raise forms.ValidationError("O valor do frete não pode ser negativo.")
        return valor_frete

    def clean_valor_seguro(self):
        """Valida o valor do seguro para garantir que seja não negativo."""
        valor_seguro = self.cleaned_data.get('valor_seguro')
        if valor_seguro < 0:
            raise forms.ValidationError("O valor do seguro não pode ser negativo.")
        return valor_seguro

    def clean_valor_outras_despesas(self):
        """Valida o valor de outras despesas para garantir que seja não negativo."""
        valor_outras_despesas = self.cleaned_data.get('valor_outras_despesas')
        if valor_outras_despesas < 0:
            raise forms.ValidationError("O valor de outras despesas não pode ser negativo.")
        return valor_outras_despesas

    def clean_numero_parcelas(self):
        """Valida o número de parcelas."""
        numero_parcelas = self.cleaned_data.get('numero_parcelas')
        forma_pagamento = self.cleaned_data.get('forma_pagamento')
        
        if forma_pagamento == 'prazo' and numero_parcelas < 2:
            raise forms.ValidationError("Para pagamento a prazo, o número de parcelas deve ser maior que 1.")
        return numero_parcelas

    def clean(self):
        """Validações gerais do formulário."""
        cleaned_data = super().clean()
        quantidade = cleaned_data.get('quantidade')
        custo_unitario = cleaned_data.get('custo_unitario')
        desconto = cleaned_data.get('desconto')
        forma_pagamento = cleaned_data.get('forma_pagamento')
        numero_parcelas = cleaned_data.get('numero_parcelas')
        valor_frete = cleaned_data.get('valor_frete')
        valor_seguro = cleaned_data.get('valor_seguro')
        valor_outras_despesas = cleaned_data.get('valor_outras_despesas')
        
        if quantidade and custo_unitario:
            valor_total = quantidade * custo_unitario
            if desconto and desconto > valor_total:
                raise forms.ValidationError("O desconto não pode ser maior que o valor total.")
        
        if forma_pagamento == 'prazo' and numero_parcelas < 2:
            raise forms.ValidationError("Para pagamento a prazo, o número de parcelas deve ser maior que 1.")
        
        if valor_frete and valor_frete < 0:
            raise forms.ValidationError("O valor do frete não pode ser negativo.")
        
        if valor_seguro and valor_seguro < 0:
            raise forms.ValidationError("O valor do seguro não pode ser negativo.")
        
        if valor_outras_despesas and valor_outras_despesas < 0:
            raise forms.ValidationError("O valor de outras despesas não pode ser negativo.")
        
        return cleaned_data