from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Crée les utilisateurs de démonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Création des utilisateurs...')

        # Admin
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
                self.stdout.write(self.style.SUCCESS('✅ Admin créé'))
            else:
                self.stdout.write('ℹ️  Admin existe déjà')
        except IntegrityError:
            self.stdout.write(self.style.WARNING('⚠️ Admin existe déjà'))

        # Opérateurs
        operateurs = [
            ('operateur-matin-ligne1', 'Mohamed', 'Gharbi'),
            ('operateur-matin-ligne2', 'Ahmed', 'Ben Ali'),
            ('operateur-matin-ligne3', 'Salah', 'Trabelsi'),
            ('operateur-aprem-ligne1', 'Karim', 'Sassi'),
            ('operateur-aprem-ligne2', 'Youssef', 'Mejri'),
            ('operateur-aprem-ligne3', 'Mehdi', 'Hamdi'),
            ('operateur-nuit-ligne1', 'Farouk', 'Chaabani'),
            ('operateur-nuit-ligne2', 'Riadh', 'Karray'),
            ('operateur-nuit-ligne3', 'Hassen', 'Bouaziz'),
        ]

        for username, prenom, nom in operateurs:
            try:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(
                        username=username,
                        password='demo2025',
                        first_name=prenom,
                        last_name=nom,
                        email=f'{username}@comocap.tn'
                    )
                    self.stdout.write(self.style.SUCCESS(f'✅ {username} créé'))
                else:
                    self.stdout.write(f'ℹ️  {username} existe déjà')
            except IntegrityError:
                self.stdout.write(self.style.WARNING(f'⚠️ {username} existe déjà'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Utilisateurs prêts !'))
        self.stdout.write('Admin : admin / admin2025')
        self.stdout.write('Opérateurs : [nom] / demo2025')