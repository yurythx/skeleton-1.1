from django.db import models
from django.utils import timezone

class Message(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    has_media = models.BooleanField(default=False)
    media_url = models.URLField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    is_handled = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['intent']),
        ]

    def __str__(self):
        return f"{self.user_message[:20]}..."

class ConversationContext(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user_name = models.CharField(max_length=100, null=True, blank=True)
    last_intent = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    context_data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_interaction']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['last_interaction']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Contexto: {self.session_id}"

    def update_last_interaction(self):
        self.last_interaction = timezone.now()
        self.save(update_fields=['last_interaction'])
