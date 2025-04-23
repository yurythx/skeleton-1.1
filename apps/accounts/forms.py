# apps/accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import CustomUser

# Formulário para criação de novo usuário
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'nome', 'telefone', 'data_nascimento', 'imagem_perfil')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

# Formulário para atualização de usuário existente
class CustomUserChangeForm(UserChangeForm):
    password = None  # Oculta o campo de senha, se não for necessário alterar por aqui

    class Meta:
        model = CustomUser
        fields = ('email', 'nome', 'telefone', 'data_nascimento', 'imagem_perfil', 'is_active', 'is_staff')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este e-mail já está em uso por outro usuário.")
        return email

# Formulário de login (para autenticação)
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )

# Formulário para criação de usuário (SignUp)
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password check", "class": "form-control"})
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')