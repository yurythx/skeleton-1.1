from django.conf import settings

def chatbot_context(request):
    return {
        'chatbot_enabled': True,
        'chatbot_title': 'ISA - Assistente Virtual',
        'chatbot_avatar': settings.STATIC_URL + 'img/isa-avatar.png',
        'chatbot_sounds': {
            'send': settings.STATIC_URL + 'sounds/send.mp3',
            'receive': settings.STATIC_URL + 'sounds/receive.mp3'
        }
    } 