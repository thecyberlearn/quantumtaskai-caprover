from django.contrib import admin
from .models import WalletTransaction


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'agent_slug', 'created_at', 'id')
    list_filter = ('type', 'created_at', 'agent_slug')
    search_fields = ('user__username', 'user__email', 'description', 'agent_slug')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'type', 'amount', 'description')
        }),
        ('Agent Information', {
            'fields': ('agent_slug',)
        }),
        ('Payment Information', {
            'fields': ('stripe_session_id',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'type', 'amount')
        return self.readonly_fields
