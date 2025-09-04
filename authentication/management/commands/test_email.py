from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from authentication.models import User

class Command(BaseCommand):
    help = 'Test email configuration on Railway'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing email configuration...")
        
        # Check settings
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Get email to send to
        email = options.get('email') or settings.EMAIL_HOST_USER
        self.stdout.write(f"Sending test email to: {email}")
        
        try:
            send_mail(
                'Railway Email Test',
                'This is a test email from Railway deployment to verify email functionality.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email sent successfully to {email}!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send email: {str(e)}')
            )