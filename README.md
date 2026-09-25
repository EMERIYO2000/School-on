# SCHOOL ON Backend

API Django REST Framework de SCHOOL ON.

## Installation locale

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

API locale : `http://127.0.0.1:8000/api/`

## Variables d'environnement

Configurez `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` et `DATABASE_URL`. Les identifiants Blink, Bitlibera, Firebase, SMTP et les secrets webhook restent uniquement dans l'environnement du serveur.

## Production

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn school_on.wsgi:application
```

PostgreSQL est utilisé lorsque `DATABASE_URL` est défini. Les médias doivent être stockés sur un service persistant ou objet en production.

## Documentation API

- Health check : `/api/health/`
- Schema : `/schema/`
- Swagger : `/swagger/`
- ReDoc : `/redoc/`
