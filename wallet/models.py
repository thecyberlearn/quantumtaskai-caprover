from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('top_up', 'Top Up'),
        ('agent_usage', 'Agent Usage'),
        ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField()
    agent_slug = models.CharField(max_length=100, blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    # Handle stripe_payment_intent_id field if it exists in database (migration issue)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),  # For user transaction history
            models.Index(fields=['type', '-created_at']),  # For filtering by transaction type
            models.Index(fields=['stripe_session_id']),  # For duplicate payment checks
            models.Index(fields=['user', 'type']),  # For aggregation queries
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} AED ({self.type})"
