from django.urls import path
from . import views

app_name = 'motoristas'

urlpatterns = [
    # URL para a lista de motoristas
    path('', views.MotoristaListView.as_view(), name='motorista_list'),
    
    # URL para o cadastro de novo motorista
    path('novo/', views.MotoristaCreateView.as_view(), name='motorista_create'),
    
    # URL para visualizar os detalhes de um motorista específico
    path('<slug:slug>/', views.MotoristaDetailView.as_view(), name='motorista_detail'),
    
    # URL para editar um motorista
    path('<slug:slug>/editar/', views.MotoristaUpdateView.as_view(), name='motorista_edit'),
]