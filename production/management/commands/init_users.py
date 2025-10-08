# production/management/commands/init_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from production.models import UserProfile

class Command(BaseCommand):
    help = 'Crée les utilisateurs de démonstration avec profils et horaires'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Création des utilisateurs...')

        # ---------------------------
        # Création ou mise à jour de l'admin
        # ---------------------------
        admins = [
            ('admin', 'admin@comocap.tn', 'admin2025'),
        ]
        for username, email, password in admins:
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Admin {username} créé'))
            else:
                self.stdout.write(f'ℹ️  Admin {username} existe déjà')
            # Assurer que UserProfile existe
            profile, prof_created = UserProfile.objects.get_or_create(user=user)
            if prof_created:
                self.stdout.write(f'✅ Profil créé pour {username}')

        # ---------------------------
        # Création ou mise à jour des opérateurs
        # ---------------------------
        operateurs = [
            ('op_matin', '6-14', 'matin2025'),
            ('op_aprem', '14-22', 'aprem2025'),
            ('op_nuit', '22-6', 'nuit2025'),
        ]

        for username, horaire_code, password in operateurs:
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@comocap.tn'})
            if created:
                user.set_password(password)
                user.first_name = f'Opérateur {horaire_code}'
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ {username} créé'))
            else:
                self.stdout.write(f'ℹ️  {username} existe déjà, mise à jour horaire')
                user.first_name = f'Opérateur {horaire_code}'
                user.save()
            # Créer ou mettre à jour le profil et l’horaire
            profile, prof_created = UserProfile.objects.get_or_create(user=user)
            profile.horaire_equipe = horaire_code
            profile.save()
            if prof_created:
                self.stdout.write(f'✅ Profil créé pour {username}')
            self.stdout.write(f'ℹ️  Horaire mis à jour pour {username}: {horaire_code}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Tous les utilisateurs et profils sont prêts !'))
        self.stdout.write('Admins : ' + ', '.join([a[0] for a in admins]))
        self.stdout.write('Opérateurs : ' + ', '.join([o[0] for o in operateurs]))
