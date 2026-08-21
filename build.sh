#!/usr/bin/env bash

set -o errexit

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate --no-input

echo "Creating superuser..."

python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email},
    )

    if created:
        user.set_password(password)

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()

    print(f"Superuser '{username}' is ready.")
else:
    print("Superuser environment variables are missing.")
PY

echo "Deployment completed."
