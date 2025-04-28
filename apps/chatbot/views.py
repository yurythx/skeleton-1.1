from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Message, ConversationContext
from .ia import responder_com_memoria
import uuid
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class ChatPageView(TemplateView):
    template_name = 'chatbot/chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chat com ISA'
        return context

class ChatbotResponseView(View):
    def get(self, request, *args, **kwargs):
        try:
            user_message = request.GET.get('message', '').strip()
            session_id = request.GET.get('session_id', str(uuid.uuid4()))
            
            if not user_message:
                return JsonResponse({
                    'error': 'Por favor, digite uma mensagem.',
                    'status': 'error'
                }, status=400)

            # Obtém ou cria o contexto da conversa
            contexto, created = ConversationContext.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'context_data': {},
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )

            # Atualiza informações do contexto
            if not created:
                contexto.ip_address = self.get_client_ip(request)
                contexto.user_agent = request.META.get('HTTP_USER_AGENT', '')
                contexto.update_last_interaction()

            # Obtém o histórico de mensagens
            historico = Message.objects.filter(
                session_id=session_id,
                is_handled=True
            ).order_by('timestamp')[:10]

            # Processa a mensagem e obtém a resposta
            resultado = responder_com_memoria(
                user_message,
                [{'content': msg.user_message} for msg in historico],
                session_id
            )

            # Salva a mensagem e resposta no banco
            Message.objects.create(
                user_message=user_message,
                bot_response=resultado['response'],
                intent=resultado['intent'],
                confidence=resultado['confidence'],
                has_media=resultado['has_media'],
                media_url=resultado['media_url'],
                session_id=session_id,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            # Atualiza o contexto
            contexto.last_intent = resultado['intent']
            contexto.context_data.update(resultado['context'])
            contexto.save()

            return JsonResponse({
                'response': resultado['response'],
                'has_media': resultado['has_media'],
                'media_url': resultado['media_url'],
                'session_id': session_id,
                'status': 'success'
            })

        except ValidationError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return JsonResponse({
                'error': 'Erro de validação dos dados.',
                'status': 'error'
            }, status=400)

        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return JsonResponse({
                'error': 'Ocorreu um erro ao processar sua mensagem.',
                'status': 'error'
            }, status=500)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
