

from django.urls import include, path 
from apps.contas.views import atualizar_usuario
from contas import views


urlpatterns = [
    
    path("", include("django.contrib.auth.urls")),  # Django auth
    path('sair/', views.logout_view, name='logout'),
    path('entrar/', views.login_view, name='login'), 
    path('criar-conta/', views.register_view, name='register'), 
    path('atualizar-usuario/', views.atualizar_meu_usuario, name='atualizar_meu_usuario'),
    path('atualizar-usuario/<int:user_id>/', atualizar_usuario, name='atualizar_usuario'),
    path('timeout/',  views.timeout_view, name='timeout'),
    
]


