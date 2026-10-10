#!/bin/sh
set -e

echo "Aplicando migraciones (alembic upgrade head)..."
alembic upgrade head

if [ -n "$SEED_ADMIN_USERNAME" ]; then
  echo "Creando usuarios semilla (seed.py)..."
  python seed.py
else
  echo "SEED_* no definidos; se omite seed.py."
fi

echo "Iniciando API en 0.0.0.0:8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
