from django.contrib import admin
from .models import AgentExecution, ChatSession, ChatMessage

@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ['agent_name', 'agent_slug', 'user', 'status', 'fee_charged', 'created_at']
    list_filter = ['status', 'agent_slug', 'created_at']
    search_fields = ['agent_name', 'agent_slug', 'user__email']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'agent_name', 'agent_slug', 'user', 'status', 'fee_charged', 'created_at']
    list_filter = ['status', 'agent_slug', 'created_at']
    search_fields = ['session_id', 'agent_name', 'agent_slug', 'user__email']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'completed_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['session__session_id', 'content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
