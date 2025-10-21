# Rental Hub

## Structure

- `backend/` — Django API
- `frontend/` — React/Vue frontend
- `deploy/` — Docker, AWS configs
- `tests/` — Unit/integration tests
- `docs/` — Documentation

## Setup

### Backend

1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start server: `python manage.py runserver`

### Docker

Run: `cd deploy && docker-compose up --build`
