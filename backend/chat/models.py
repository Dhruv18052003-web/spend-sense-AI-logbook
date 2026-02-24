from django.db import models
from django.conf import settings
# Create your models here.

class ChatLogs(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.Case,
        related_name='chat_logs'
    )

    user_prompt = models.TextField()
    ai_response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.user_prompt} - {self.ai_response}"
