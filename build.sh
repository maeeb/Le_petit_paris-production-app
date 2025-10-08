#!/bin/bash
set -e

echo "🚀 Mise à jour de pip et installation des dépendances..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🗃️ Application des migrations..."
python manage.py migrate

echo "👤 Vérification / création du superutilisateur et opérateurs..."
python manage.py shell <<EOF
from django.contrib.auth.models import User

# -------------------------
# Superutilisateur
# -------------------------
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
    print('✅ Superuser créé : admin / admin2025')
else:
    print('ℹ️ Superuser existe déjà')

# -------------------------
# Opérateurs
# -------------------------
operateurs = [
    ('op_matin', 'Matin', 'matin2025'),
    ('op_aprem', 'Après-midi', 'aprem2025'),
    ('op_nuit', 'Nuit', 'nuit2025'),
]

for username, equipe, password in operateurs:
    user = User.objects.filter(username=username).first()
    if not user:
        User.objects.create_user(
            username=username,
            password=password,
            first_name=equipe,
            email=f'{username}@comocap.tn'
        )
        print(f'✅ {username} créé avec équipe {equipe}')
    else:
        # Met à jour le nom de l'équipe si nécessaire
        user.first_name = equipe
        user.save()
        print(f'ℹ️ {username} existant mis à jour avec équipe {equipe}')

EOF

echo "✅ Build terminé avec succès !"
