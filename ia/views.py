# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from meu_chatbot.ia import responder  # importa sua IA

@csrf_exempt
def chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mensagem_usuario = data.get("message", "")
        resposta_ia = responder(mensagem_usuario)
        return JsonResponse({"response": resposta_ia})