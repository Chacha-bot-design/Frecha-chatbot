from django.contrib import admin
from .models import Conversation, Lead

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['user_message', 'language', 'timestamp']
    list_filter = ['language', 'timestamp']
    search_fields = ['user_message', 'bot_response']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'interest', 'status', 'timestamp']
    list_filter = ['status', 'interest', 'language', 'timestamp']
    search_fields = ['name', 'phone', 'location']