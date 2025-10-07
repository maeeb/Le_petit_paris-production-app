#!/bin/bash
set -e
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
echo "Build terminé avec succès !"
