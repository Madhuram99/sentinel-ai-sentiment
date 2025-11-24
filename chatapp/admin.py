from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'text', 'sentiment_label', 'sentiment_score', 'timestamp')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'started_at', 'message_count')
    inlines = [MessageInline] # Shows messages inside the Conversation view

    def message_count(self, obj):
        return obj.messages.count()
    