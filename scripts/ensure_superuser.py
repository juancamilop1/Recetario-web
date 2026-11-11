import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recetario.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

if not username or not password:
    print('ensure_superuser: skipped (missing env vars)')
else:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_staff': True, 'is_superuser': True},
    )
    user.is_staff = True
    user.is_superuser = True
    if email:
        user.email = email
    user.set_password(password)
    user.save()
    print('ensure_superuser:', 'created' if created else 'updated', username)
