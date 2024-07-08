
from django.shortcuts import render
from django.contrib import messages


def timeout_view(request):
    return render(request, 'timeout.html')
# Create your views here.
def index_pages(request):
    
    context ={
        'message': messages.debug(request, 'Esta é uma mensagem de debug!'),
        'message': messages.info(request, 'Esta é uma mensagem de informaçãp!'),
        'message': messages.success(request, 'Esta é uma mensagem de sucesso!'),
        'message': messages.warning(request, 'Esta é uma mensagem de Perigo!'),
        'message': messages.error(request, 'Esta é uma mensagem de erro!')
           
        
    }
    
    
    return render(request, 'index.html')