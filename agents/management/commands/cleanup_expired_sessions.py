from django.core.management.base import BaseCommand
from django.utils import timezone
from agents.models import ChatSession

class Command(BaseCommand):
    help = 'Mark expired chat sessions as expired'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find active sessions that have expired
        expired_sessions = ChatSession.objects.filter(
            status='active',
            expires_at__lt=now
        )
        
        count = expired_sessions.count()
        
        if count > 0:
            # Mark them as expired
            expired_sessions.update(
                status='expired',
                completed_at=now
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Marked {count} expired sessions as expired')
            )
        else:
            self.stdout.write('✅ No expired sessions found')