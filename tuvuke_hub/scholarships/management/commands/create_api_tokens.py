from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create API tokens for all users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Create token for specific username'
        )
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Recreate tokens even if they exist'
        )
    
    def handle(self, *args, **options):
        username = options.get('username')
        recreate = options.get('recreate', False)
        
        if username:
            try:
                user = User.objects.get(username=username)
                token, created = Token.objects.get_or_create(user=user)
                
                if not created and recreate:
                    token.delete()
                    token = Token.objects.create(user=user)
                    created = True
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Token created for {username}: {token.key}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Token already exists for {username}: {token.key}')
                    )
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {username} does not exist')
                )
        else:
            # Create tokens for all users
            users = User.objects.all()
            created_count = 0
            updated_count = 0
            
            for user in users:
                token, created = Token.objects.get_or_create(user=user)
                
                if not created and recreate:
                    token.delete()
                    token = Token.objects.create(user=user)
                    updated_count += 1
                elif created:
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Tokens created: {created_count}, updated: {updated_count}'
                )
            )
