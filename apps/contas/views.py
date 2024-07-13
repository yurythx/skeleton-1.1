from django.contrib.auth.models import Group, User 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from apps.contas.forms import CustomUserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required


from django.shortcuts import get_object_or_404
from apps.contas.permissions import grupo_colaborador_required
from perfil.models import Perfil
from contas.models import MyUser


def timeout_view(request):
    return render(request, 'timeout.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email ou senha inválidos')
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_valid = False
            usuario.save()
            
            group = Group.objects.get(name='usuario')
            usuario.groups.add(group)
            
            Perfil.objects.create(usuario=usuario) # Cria instancia perfil do usuário
            
            messages.success(request, 'Registrado. Agora faça o login para começar!')
            return redirect('login')
        else:
            # Tratar quando usuario já existe, senhas... etc...
            messages.error(request, 'A senha deve ter pelo menos 1 caractere maiúsculo, \
                1 caractere especial e no minimo 8 caracteres.')
    form = CustomUserCreationForm()
    return render(request, "registration/register.html",{"form": form})

@login_required()
@grupo_colaborador_required(['administrador','colaborador'])

def atualizar_usuario(request, username):
    user = get_object_or_404(MyUser, username=username)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'O perfil de usuário foi atualizado com sucesso!')
            return redirect('home')
    else:
        form = UserChangeForm(request.POST, instance=user, user=request.user)
    return render(request, 'user_update.html', {'form': form})

@login_required()
@grupo_colaborador_required(['administrador','colaborador'])

def atualizar_meu_usuario(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('home')
    else:
        form = UserChangeForm(request.POST, instance=user, user=request.user)
        
    return render(request, 'user_update.html', {'form': form})