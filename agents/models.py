from django.db import models
import uuid

class AgentExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_slug = models.SlugField(max_length=100, help_text="Agent identifier from JSON config", default="unknown")
    agent_name = models.CharField(max_length=200, help_text="Agent name for display purposes", default="Unknown Agent")
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2)
    webhook_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    execution_time = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_slug', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent_name} - {self.user.email} - {self.status}"

class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True, help_text="Unique session identifier")
    agent_slug = models.SlugField(max_length=100, help_text="Agent identifier from JSON config", default="unknown")
    agent_name = models.CharField(max_length=200, help_text="Agent name for display purposes", default="Unknown Agent")
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    context_data = models.JSONField(default=dict, help_text="Session context and progress tracking")
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Session expiration time (30 minutes from last activity)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Set expires_at to 30 minutes from now if not set
        if not self.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['agent_slug', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['agent_slug', 'user', 'status']),  # For active session lookups
            models.Index(fields=['status', 'expires_at']),  # For cleanup operations
        ]
    
    def __str__(self):
        return f"{self.agent_name} - {self.user.email} - {self.session_id}"
    
    def is_expired(self):
        from django.utils import timezone
        if not self.expires_at:
            return False  # Sessions without expiration date are considered active
        return timezone.now() > self.expires_at
    
    def extend_session(self):
        """Extend session by 30 minutes from now"""
        from django.utils import timezone
        from datetime import timedelta
        self.expires_at = timezone.now() + timedelta(minutes=30)
        self.updated_at = timezone.now()
        self.save()

class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User Message'),
        ('agent', 'Agent Response'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, help_text="Additional message data like webhook responses")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['session', 'message_type']),  # For message counts by type
        ]
    
    def __str__(self):
        return f"{self.session.session_id} - {self.message_type} - {self.timestamp}"
