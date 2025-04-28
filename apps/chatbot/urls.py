from django.urls import path
from .views import ChatPageView, ChatbotResponseView

app_name = 'chatbot'

urlpatterns = [
    path('', ChatPageView.as_view(), name='chat'),
    path('responder/', ChatbotResponseView.as_view(), name='chatbot_response'),
    path('api/responder/', ChatbotResponseView.as_view(), name='api_chatbot_response'),
] 