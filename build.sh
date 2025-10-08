#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Créer automatiquement le superuser si pas existant
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@comocap.tn', 'admin2025')
    print('✅ Superuser créé')
else:
    print('ℹ️ Superuser existe déjà')
EOF

echo "Build terminé avec succès !"
