import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'le_petit_paris.settings')

application = get_wsgi_application()