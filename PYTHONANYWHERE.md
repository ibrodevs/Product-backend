# PythonAnywhere Deploy

This backend is ready to deploy on PythonAnywhere as a public Django/DRF API.

## What is already prepared

- Production settings are controlled through `.env`.
- `ALLOWED_HOSTS` supports PythonAnywhere domains by default.
- Public CORS headers are enabled for `/api/*`, so external frontend apps can call the API.
- `STATIC_ROOT` is configurable for `collectstatic`.
- A PythonAnywhere WSGI template is included at [deploy/pythonanywhere_wsgi.py](/Users/imac5/Desktop/projects/Product/backend/deploy/pythonanywhere_wsgi.py).
- This document is pre-filled for `https://product21.pythonanywhere.com/`.

## 1. Upload code

Clone or copy the project to PythonAnywhere, for example:

```bash
cd ~
git clone <your-repo-url> Product
cd Product/backend
```

PythonAnywhere's Django deployment flow is documented here:

- [Deploying an existing Django project on PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Environment variables for web apps](https://help.pythonanywhere.com/pages/EnvironmentVariables/)
- [Static files in Django on PythonAnywhere](https://helpdev.pythonanywhere.com/pages/DjangoStaticFiles)

## 2. Create a virtualenv and install dependencies

```bash
mkvirtualenv product-backend --python=/usr/bin/python3.13
cd ~/Product/backend
pip install -r requirements.txt
```

## 3. Create the environment file

```bash
cp .env.example .env
```

Then edit `.env` and set at minimum:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=product21.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://product21.pythonanywhere.com
DJANGO_CORS_ALLOW_ALL_ORIGINS=True
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_STATIC_ROOT=/home/product21/Product/backend/staticfiles
DJANGO_MEDIA_ROOT=/home/product21/Product/backend/media
DJANGO_DB_PATH=/home/product21/Product/backend/db.sqlite3
```

If your frontend will live on a separate domain and you want to restrict browser access, change:

```env
DJANGO_CORS_ALLOW_ALL_ORIGINS=False
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## 4. Run migrations and collect static

```bash
cd ~/Product/backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

## 5. Create the web app in PythonAnywhere

In the PythonAnywhere Web tab:

1. Create a new web app.
2. Choose **Manual configuration**.
3. Select the same Python version as your virtualenv.
4. Set the virtualenv path to something like:

```text
/home/product21/.virtualenvs/product-backend
```

## 6. Configure the WSGI file

Open the WSGI file for the web app and replace its contents with the template from:

- [deploy/pythonanywhere_wsgi.py](/Users/imac5/Desktop/projects/Product/backend/deploy/pythonanywhere_wsgi.py)

## 7. Configure static files

In the Web tab, add a static files mapping:

```text
URL: /static/
Directory: /home/product21/Product/backend/staticfiles
```

If you use media uploads later, add:

```text
URL: /media/
Directory: /home/product21/Product/backend/media
```

## 8. Reload the app

Press **Reload** in the Web tab.

## 9. Public API URL

Your backend will then be reachable at:

```text
https://product21.pythonanywhere.com/api/
```

Examples:

- `https://product21.pythonanywhere.com/api/health`
- `https://product21.pythonanywhere.com/api/auth/login`
- `https://product21.pythonanywhere.com/api/tasks`

## Frontend note

If your Next.js frontend is deployed elsewhere, point it to:

```env
NEXT_PUBLIC_API_BASE=https://product21.pythonanywhere.com/api
```

## Security note

`DJANGO_CORS_ALLOW_ALL_ORIGINS=True` makes the API callable from any website. That is convenient for a public API, but if you know the frontend domain, restrict it with `DJANGO_CORS_ALLOWED_ORIGINS`.
