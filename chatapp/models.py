from django.db import models

class Conversation(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Chat {self.id} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

class Message(models.Model):
    SENDER_CHOICES = [('user', 'User'), ('bot', 'AI')]
    
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    sentiment_label = models.CharField(max_length=20, null=True, blank=True)
    sentiment_score = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}..."