#!/bin/bash
set -e

echo "🚀 Mise à jour de pip et installation des dépendances..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🗃️ Application des migrations..."
python manage.py migrate --no-input

echo "👤 Création/Mise à jour des utilisateurs..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
    print('✅ Admin créé : admin / admin2025')
else:
    print('ℹ️ Admin existe déjà')

# Superviseurs avec QR codes
superviseurs = [
    ('op_matin', 'matin2025', 'Équipe Matin'),
    ('op_aprem', 'aprem2025', 'Équipe Après-midi'),
    ('op_nuit', 'nuit2025', 'Équipe Nuit'),
]

for username, password, nom in superviseurs:
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.first_name = nom
        user.email = f'{username}@comocap.tn'
        user.save()
        print(f'✅ {username} créé : {nom}')
    else:
        # Mettre à jour le first_name même si l'utilisateur existe
        if not user.first_name:
            user.first_name = nom
            user.save()
            print(f'✅ {username} mis à jour avec : {nom}')
        else:
            print(f'ℹ️ {username} existe déjà')

print('✅ Tous les utilisateurs sont prêts!')
EOF

echo "✅ Build terminé avec succès !"