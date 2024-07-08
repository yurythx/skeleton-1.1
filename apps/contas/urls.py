

from django.urls import path 
from pages import views

urlpatterns = [
    path('timeout/',  views.timeout_view, name='timeout'),
    path('entrar/', views.login_view, name='login'),
]


