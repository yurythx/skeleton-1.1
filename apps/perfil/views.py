from django.shortcuts import get_object_or_404, render
from contas.models import MyUser

def perfil_view(request, username):
    perfil = get_object_or_404(MyUser.objects.select_related('perfil'), username=username)
    context = {'obg': perfil}
    return render(request, 'perfil.html', context)

def atualizar_usuario(request, username):
    user = get_object_or_404(MyUser, username=username)