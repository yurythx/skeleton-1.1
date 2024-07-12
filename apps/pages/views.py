from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from apps.contas.forms import CustomUserCreationForm, UserChangeForm

from django.contrib.auth.decorators import login_required


from django.shortcuts import get_object_or_404
from apps.contas.permissions import grupo_colaborador_required
from contas.models import MyUser

from email.headerregistry import Group
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def index_pages(request):
    
   ## context ={
   ##     'message': messages.info(request, 'Esta é uma mensagem de informaçãp!'),
   ##     'message': messages.success(request, 'Esta é uma mensagem de sucesso!'),
   ##     'message': messages.warning(request, 'Esta é uma mensagem de Perigo!'),
   ##     'message': messages.error(request, 'Esta é uma mensagem de erro!')
           
        
   ## }
    
    
    return render(request, 'index.html')


