from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup database after application startup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--wait',
            type=int,
            default=30,
            help='Wait time in seconds before attempting database setup'
        )
        parser.add_argument(
            '--retries',
            type=int,
            default=5,
            help='Number of retry attempts for database connection'
        )

    def handle(self, *args, **options):
        wait_time = options['wait']
        max_retries = options['retries']
        
        self.stdout.write(f'Waiting {wait_time} seconds before database setup...')
        time.sleep(wait_time)
        
        # Try to connect to database with retries
        for attempt in range(max_retries):
            try:
                self.stdout.write(f'Attempt {attempt + 1}: Testing database connection...')
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                self.stdout.write(self.style.SUCCESS('Database connection successful!'))
                break
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Database connection failed (attempt {attempt + 1}): {e}')
                )
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    self.stdout.write(
                        self.style.ERROR('Database connection failed after all retries. Exiting.')
                    )
                    return
        
        # Run migrations
        try:
            self.stdout.write('Running database migrations...')
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('Migrations completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {e}'))
            return
        
        # Populate agents
        try:
            self.stdout.write('Populating agents...')
            call_command('populate_agents')
            self.stdout.write(self.style.SUCCESS('Agents populated successfully!'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Agent population warning: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Database setup completed!'))