import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get credentials from env or use defaults
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        name = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'Administrator') # Name field

        if not User.objects.filter(email=email).exists():
            print(f"Creating superuser: {email}")
            user = User.objects.create_superuser(
                email=email,
                password=password,
                name=name
            )
            # Give some credits for testing
            user.credits = 100
            user.save()
            print(f"Superuser created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")
        else:
            print("Superuser already exists. Skipping creation.")
