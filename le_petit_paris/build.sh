#!/usr/bin/env bash
set -o errexit

echo "🔄 Installation des dépendances..."
pip install -r requirements.txt

echo "🔄 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🔄 Exécution des migrations..."
python manage.py migrate

echo "🔄 Création des utilisateurs..."
python manage.py init_users || echo "⚠️ init_users non trouvé"

echo "✅ Build terminé avec succès !"