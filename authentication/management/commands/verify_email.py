from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Manually verify user email address'
    
    def add_arguments(self, parser):
        parser.add_argument('email', help='User email address to verify')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force verification even if already verified',
        )
    
    def handle(self, *args, **options):
        email = options['email']
        force = options['force']
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified and not force:
                self.stdout.write(
                    self.style.WARNING(f"Email {email} is already verified!")
                )
                self.stdout.write("Use --force to override")
                return
            
            # Manually verify the email
            user.email_verified = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Successfully verified email: {email}")
            )
            self.stdout.write(f"User: {user.username}")
            self.stdout.write(f"Email verified: {user.email_verified}")
            
            # Clean up any existing verification tokens
            from authentication.models import EmailVerificationToken
            tokens = EmailVerificationToken.objects.filter(user=user, is_used=False)
            token_count = tokens.count()
            if token_count > 0:
                tokens.update(is_used=True)
                self.stdout.write(f"🧹 Cleaned up {token_count} unused verification tokens")
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ User with email '{email}' not found!")
            )
            
            # Show available users
            all_users = User.objects.all()
            if all_users.exists():
                self.stdout.write("\nAvailable users:")
                for user in all_users:
                    status = "✅ Verified" if user.email_verified else "❌ Unverified"
                    self.stdout.write(f"  - {user.email} ({user.username}) - {status}")
            else:
                self.stdout.write("No users found in database")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error verifying email: {str(e)}")
            )