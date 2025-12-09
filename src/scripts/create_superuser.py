import os
import django
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL")
NAME = os.getenv("DJANGO_SUPERUSER_NAME")
PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(email=EMAIL).exists():
    User.objects.create_superuser(
        email=EMAIL,
        password=PASSWORD,
        name=NAME
    )
    print("Superusuário criado com sucesso.")
else:
    print("Superusuário já existe.")

