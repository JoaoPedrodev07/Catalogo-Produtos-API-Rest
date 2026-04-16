import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalogo.settings')
django.setup()

User = get_user_model()

username = 'admin'
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('Superuser created.')
else:
    print('Superuser already exists.')
