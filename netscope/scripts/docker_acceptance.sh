#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up --build -d --wait
docker compose exec -T backend python manage.py test monitoring --verbosity 1
docker compose exec -T backend python manage.py demo_acceptance
# No down -v: the history must survive a restart.
docker compose restart backend worker frontend
docker compose up -d --wait
docker compose exec -T backend python manage.py demo_acceptance --verify
