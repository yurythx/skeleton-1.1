from django.contrib.auth.models import Group, User 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from apps.base.utils import add_form_errors_to_messages
from apps.contas.forms import CustomUserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required


from django.shortcuts import get_object_or_404
from apps.contas.permissions import grupo_colaborador_required
from apps.perfil.forms import PerfilForm
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
        
        if user is not None: login(request, user)
            
        if user.is_authenticated and user.requires_password_change(): # Verifica
            
                    msg = 'Olá '+user.first_name+', como você pode perceber atualmente \
                            a sua senha é 123 cadastrado. Recomendamos fortemente \
                            que você altere sua senha para garantir a segurança da sua conta. \
                            É importante escolher uma senha forte e única que não seja fácil de adivinhar. \
                            Obrigado pela sua atenção!' 
                    messages.warning(request, msg)
                    return redirect('force_password_change') # Vai para rota de alterar senha.
        else:
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
        form = CustomUserCreationForm(request.POST, user=request.user)
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
            add_form_errors_to_messages(request, form)
            
    form = CustomUserCreationForm()
    return render(request, "registration/register.html",{"form": form})

@login_required()
@grupo_colaborador_required(['Administrador','colaborador'])

def atualizar_usuario(request, username):
    user = get_object_or_404(MyUser, username=username)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'O perfil de usuário foi atualizado com sucesso!')
            return redirect('home')
        
        else:
            add_form_errors_to_messages(request, form)
            
    else:
        form = UserChangeForm(request.POST, instance=user, user=request.user)
    return render(request, 'user_update.html', {'form': form})

@login_required()
@grupo_colaborador_required(['Administrador','colaborador'])

def atualizar_meu_usuario(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('home')
        else:
            add_form_errors_to_messages(request, form)
    else:
        form = UserChangeForm(request.POST, user=request.user)
        
    return render(request, 'user_update.html', {'form': form})


@login_required
@grupo_colaborador_required(['Administrador','colaborador'])

def lista_usuarios(request): # Lista Cliente 
    lista_usuarios = MyUser.objects.select_related('perfil').filter(is_superuser=False) 
    return render(request, 'lista-usuarios.html', {'lista_usuarios': lista_usuarios})

@login_required
@grupo_colaborador_required(['Administrador','colaborador'])

def adicionar_usuario(request):
    user_form = CustomUserCreationForm(user=request.user)
    perfil_form = PerfilForm(user=request.user)

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST,user=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, user=request.user)

        if user_form.is_valid() and perfil_form.is_valid():
            # Salve o usuário
            usuario = user_form.save()

            #adiciona grupo usuario automaticamente
            group = Group.objects.get(name='usuario')
            usuario.groups.add(group)
            
            # Crie um novo perfil para o usuário
            perfil = perfil_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            
        else:
            
            add_form_errors_to_messages(request, user_form)
            add_form_errors_to_messages(request, perfil_form)

    context = {'user_form': user_form, 'perfil_form': perfil_form}
    return render(request, "adicionar-usuario.html", context)


# Mudança de Senha Force (first_login)
@login_required
def force_password_change_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.force_change_password = False # passa o parametro para False.
            user.save()
            update_session_auth_hash(request, user)
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form': form}
    return render(request, 'registration/password_force_change_form.html', context)