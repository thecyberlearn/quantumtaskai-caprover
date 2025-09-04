from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'created_at', 'is_processed', 'ip_address']
    list_filter = ['is_processed', 'created_at']
    search_fields = ['name', 'email', 'company', 'message']
    readonly_fields = ['id', 'created_at', 'ip_address', 'user_agent']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'company')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Processing', {
            'fields': ('is_processed', 'processed_at')
        }),
        ('Technical Details', {
            'fields': ('id', 'ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processed']
    
    def mark_as_processed(self, request, queryset):
        for submission in queryset:
            submission.mark_as_processed()
        self.message_user(request, f'{queryset.count()} submissions marked as processed.')
    mark_as_processed.short_description = "Mark selected submissions as processed"
