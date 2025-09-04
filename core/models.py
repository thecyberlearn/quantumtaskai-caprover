from django.db import models
from django.utils import timezone
import uuid


class ContactSubmission(models.Model):
    """Model for storing contact form submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=100, blank=True)
    message = models.TextField(max_length=1000)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Contact from {self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def mark_as_processed(self):
        """Mark submission as processed"""
        self.is_processed = True
        self.processed_at = timezone.now()
        self.save()
