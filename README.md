# Backend (Django + DRF)

Django 6.1, Django REST Framework, django-cors-headers. SQLite default.

## Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Run

```
python manage.py runserver 8001
```

Port 8000 reserved by another local project — this backend defaults to **8001**. Adjust `frontend/.env.local` (`NEXT_PUBLIC_API_URL`) if you change it.

## Endpoints

- `GET /api/health/` — connectivity check, returns `{"status": "ok", "service": "django-backend"}`
- `/admin/` — Django admin (create superuser with `python manage.py createsuperuser`)

## Env vars (`.env`)

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS` (comma-separated)
- `CORS_ALLOWED_ORIGINS` (comma-separated, defaults to `http://localhost:3000`)
