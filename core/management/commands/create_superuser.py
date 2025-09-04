from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser for production deployment'

    def handle(self, *args, **options):
        """Create superuser with predefined credentials for production"""
        
        email = "admin@quantumtaskai.com"
        username = "admin"
        password = "QuantumAdmin2024!"
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists')
                    )
                    return
                
                # Create superuser
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.is_staff = True
                user.is_superuser = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser: {email}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Password: {password}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )