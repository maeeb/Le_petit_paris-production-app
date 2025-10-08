from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from production.models import UserProfile

class Command(BaseCommand):
    help = 'Assigner les horaires d\'équipe aux utilisateurs'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nom d\'utilisateur')
        parser.add_argument('--shift', type=str, help='Horaire (6-14, 14-22, 22-6)')
    
    def handle(self, *args, **options):
        if options['username'] and options['shift']:
            try:
                user = User.objects.get(username=options['username'])
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.horaire_equipe = options['shift']
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Utilisateur {user.username} assigné à l\'équipe {options["shift"]}'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Utilisateur {options["username"]} introuvable')
                )
        else:
            # Mode interactif
            users = User.objects.filter(is_superuser=False, is_staff=False)
            
            for user in users:
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                if not profile.horaire_equipe:
                    self.stdout.write(f'\nUtilisateur: {user.username} ({user.get_full_name()})')
                    self.stdout.write('Horaires disponibles:')
                    self.stdout.write('1. 6-14 (Matin)')
                    self.stdout.write('2. 14-22 (Après-midi)')
                    self.stdout.write('3. 22-6 (Nuit)')
                    
                    choice = input('Choisir l\'équipe (1-3, ou s pour passer): ')
                    
                    if choice == '1':
                        profile.horaire_equipe = '6-14'
                        profile.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'{user.username} → Équipe du Matin')
                        )
                    elif choice == '2':
                        profile.horaire_equipe = '14-22'
                        profile.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'{user.username} → Équipe de l\'Après-midi')
                        )
                    elif choice == '3':
                        profile.horaire_equipe = '22-6'
                        profile.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'{user.username} → Équipe de Nuit')
                        )