from django import template
from django.template.loader import render_to_string
from django.conf import settings

register = template.Library()

@register.simple_tag
def chatbot_widget():
    context = {
        'chatbot_avatar': '/static/img/isa-avatar.png',
        'chatbot_sounds': {
            'send': '/static/sounds/send.mp3',
            'receive': '/static/sounds/receive.mp3'
        }
    }
    return render_to_string('chatbot/chat.html', context) 