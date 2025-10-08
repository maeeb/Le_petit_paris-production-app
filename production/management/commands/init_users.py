# production/management/commands/init_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from production.models import UserProfile

class Command(BaseCommand):
    help = 'Crée les utilisateurs de démonstration avec profils et horaires'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Création des utilisateurs...')

        # ---------------------------
        # Création de l'admin
        # ---------------------------
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
            self.stdout.write(self.style.SUCCESS('✅ Admin créé'))
        else:
            self.stdout.write('ℹ️  Admin existe déjà')

        # ---------------------------
        # Création des opérateurs
        # ---------------------------
        # Code horaire = correspond exactement aux choix HORAIRES_CHOICES
        operateurs = [
            ('op_matin', '6-14', 'matin2025'),
            ('op_aprem', '14-22', 'aprem2025'),
            ('op_nuit', '22-6', 'nuit2025'),
        ]

        for username, horaire_code, password in operateurs:
            if not User.objects.filter(username=username).exists():
                # Crée l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=f'Opérateur {horaire_code}',
                    email=f'{username}@comocap.tn'
                )
                # Crée le profil associé avec l'horaire
                UserProfile.objects.create(user=user, horaire_equipe=horaire_code)
                self.stdout.write(self.style.SUCCESS(f'✅ {username} créé avec horaire {horaire_code}'))
            else:
                # Mise à jour si l'utilisateur existe déjà
                user = User.objects.get(username=username)
                user.first_name = f'Opérateur {horaire_code}'
                user.save()
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.horaire_equipe = horaire_code
                profile.save()
                self.stdout.write(f'ℹ️  {username} existe déjà, horaire mis à jour à {horaire_code}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Tous les utilisateurs sont prêts !'))
        self.stdout.write('Admin : admin / admin2025')
        self.stdout.write('Opérateurs : op_matin, op_aprem, op_nuit')
