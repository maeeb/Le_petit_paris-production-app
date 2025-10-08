from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crée les utilisateurs de démonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Création des utilisateurs...')

        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
            self.stdout.write(self.style.SUCCESS('✅ Admin créé'))
        else:
            self.stdout.write('ℹ️  Admin existe déjà')

        # Opérateurs
        operateurs = [
            ('op_matin', 'Matin', 'matin2025'),
            ('op_aprem', 'Après-midi', 'aprem2025'),
            ('op_nuit', 'Nuit', 'nuit2025'),
        ]

        for username, equipe, password in operateurs:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=equipe,  # <-- Nom exact de l'équipe
                    email=f'{username}@comocap.tn'
                )
                self.stdout.write(self.style.SUCCESS(f'✅ {username} créé avec équipe {equipe}'))
            else:
                # Si l'utilisateur existe déjà, on met à jour son équipe
                User.objects.filter(username=username).update(first_name=equipe)
                self.stdout.write(f'ℹ️  {username} existe déjà, équipe mise à jour à {equipe}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Utilisateurs prêts !'))
        self.stdout.write('Admin : admin / admin2025')
        self.stdout.write('Opérateurs : op_matin, op_aprem, op_nuit')
