

from django.urls import path 
from pages import views

urlpatterns = [
    path('', views.index_base, name='home'), 
]


