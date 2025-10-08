#!/bin/bash
set -e

echo "🚀 Mise à jour de pip et installation des dépendances..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🗃️ Application des migrations..."
python manage.py migrate

echo "👤 Vérification / création du superutilisateur..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
    print('✅ Superuser créé : admin / admin2025')
else:
    print('ℹ️ Superuser existe déjà')
EOF

echo "✅ Build terminé avec succès !"
