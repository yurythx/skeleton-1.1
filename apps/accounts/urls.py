from django.urls import path
from .views import LoginView, RegisterView, LogoutView, CustomUserListView, CustomUserCreateView, CustomUserUpdateView, CustomUserDeleteView, CustomUserDetailView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('usuarios/', CustomUserListView.as_view(), name='lista_usuarios'),
    path('usuario/novo/', CustomUserCreateView.as_view(), name='novo_usuario'),
    path('usuario/<slug:slug>/editar/', CustomUserUpdateView.as_view(), name='editar_usuario'),
    path('usuario/<slug:slug>/excluir/', CustomUserDeleteView.as_view(), name='excluir_usuario'),
    path('usuario/<slug:slug>/', CustomUserDetailView.as_view(), name='detalhes_usuario'),
]