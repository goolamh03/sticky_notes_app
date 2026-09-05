# Sticky Notes Django Application

A Model-View-Template Django application implementing user authentication,
profile management, note CRUD, search, archive/restore, and staff monitoring.

## Setup on Windows 11

```powershell
cd sticky_notes_complete
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Staff dashboards are under `/staff/`, while
Django's administration site is available at `/admin/`.

## Quality checks

```powershell
python manage.py test
python -m flake8 .
```

## MVT mapping

- Model: `notes/models.py`
- Views: `notes/views.py`
- Templates: `templates/`
- Forms: `notes/forms.py`
- URL configuration: `sticky_notes/urls.py` and `notes/urls.py`
- Static styling: `notes/static/notes/css/style.css`
