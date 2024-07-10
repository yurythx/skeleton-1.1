

from django.urls import path 
from pages import views

urlpatterns = [
    
    path('entrar/', views.login_view, name='login'), 
    path('criar-conta/', views.register_view, name='register'), 
    path('timeout/',  views.timeout_view, name='timeout'),
    
]


