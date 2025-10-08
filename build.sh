#!/bin/bash
set -e

echo "🚀 Mise à jour de pip et installation des dépendances..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🗃️ Application des migrations..."
python manage.py migrate --no-input

echo "👤 Création des utilisateurs..."
python manage.py init_users

echo "✅ Build terminé avec succès !"