

from django.urls import include, path 
#from apps.contas.views import atualizar_usuario
from contas import views


urlpatterns = [
    
    path("", include("django.contrib.auth.urls")),  # Django auth
    path('sair/', views.logout_view, name='logout'),
    path('entrar/', views.login_view, name='login'), 
    path('criar-conta/', views.register_view, name='register'), 
    path('atualizar-usuario/', views.atualizar_meu_usuario, name='atualizar_meu_usuario'),
    path('atualizar-usuario/<slug:username>/',  views.atualizar_usuario, name='atualizar_usuario'),
    path('timeout/',  views.timeout_view, name='timeout'),
    path('lista-usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('adicionar-usuario/',  views.adicionar_usuario, name='adicionar_usuario'),
    path('nova-senha/', views.force_password_change_view, name='force_password_change'),
]


