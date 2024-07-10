from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect




def timeout_view(request):
    return render(request, 'timeout.html')
# Create your views here.
from email.headerregistry import Group
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from apps.contas.forms import CustomUserCreationForm

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
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_valid = False
            usuario.save()
            
            usuario = form.save(commit=False)
            usuario.is_valid = False
            usuario.save()

            group = Group.objects.get(name='usuario')
            usuario.groups.add(group)
            
            messages.success(request, 'Registrado. Agora faça o login para começar!')
            return redirect('login')
        else:
            # Tratar quando usuario já existe, senhas... etc...
            messages.error(request, 'A senha deve ter pelo menos 1 caractere maiúsculo, \
                1 caractere especial e no minimo 8 caracteres.')
    form = CustomUserCreationForm()
    return render(request, "register.html",{"form": form})


def index_pages(request):
    
    context ={
        'message': messages.debug(request, 'Esta é uma mensagem de debug!'),
        'message': messages.info(request, 'Esta é uma mensagem de informaçãp!'),
        'message': messages.success(request, 'Esta é uma mensagem de sucesso!'),
        'message': messages.warning(request, 'Esta é uma mensagem de Perigo!'),
        'message': messages.error(request, 'Esta é uma mensagem de erro!')
           
        
    }
    
    
    return render(request, 'index.html')