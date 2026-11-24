"""Generate a local .env without overwriting an existing one."""

from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
target = root / ".env"
if target.exists():
    raise SystemExit(".env already exists; edit it manually if needed.")
text = (
    (root / ".env.example")
    .read_text()
    .replace("SECRET_KEY=", "SECRET_KEY=" + secrets.token_urlsafe(48), 1)
    .replace("POSTGRES_PASSWORD=", "POSTGRES_PASSWORD=" + secrets.token_urlsafe(32), 1)
)
target.write_text(text)
target.chmod(0o600)
print("Created .env. Next: docker compose up --build -d")
