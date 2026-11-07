#!/usr/bin/env sh
set -eu
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker no está instalado o no está disponible en PATH." >&2
  exit 1
fi
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Archivo .env creado. Edita las contraseñas y DJANGO_SECRET_KEY antes de iniciar." >&2
  exit 1
fi
docker compose up --build -d
docker compose ps
printf '\nFrontend: http://localhost:5173\nAdmin: http://localhost:8000/admin/\n'
printf 'Si es la primera vez: docker compose exec api python manage.py createsuperuser\n'
