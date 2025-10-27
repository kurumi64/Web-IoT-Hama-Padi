# type: ignore
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create initial admin user for the monitoring system'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='kiki').exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists. Use Django admin or create a new user manually.')
            )
            return

        # Create admin user
        try:
            user = User.objects.create_user(
                username='kiki',
                email='adipamungkas.kiki@gmail.com',
                password='Kurumi64????',
                first_name='Super',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user:\n'
                    f'Username: admin\n'
                    f'Password: admin123\n'
                    f'Please change the password after first login!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create admin user: {e}')
            ) 