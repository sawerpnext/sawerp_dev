# Backend Overview – ERP Shipping (Phase 1)

This document is for **frontend developers** and anyone who needs to
understand how the backend works at a high level.

It will keep evolving as we add more phases.

---

## 1. Tech Stack (Backend)

- **Framework:** Django 5 + Django REST Framework
- **Database:** PostgreSQL (configured via `DATABASE_URL` in `.env`)
- **Auth:** Token-based auth using Django REST Framework's `TokenAuthentication`
- **Main app:** `operations`
- **Base URL for APIs:** `/api/`

---

## 2. Folder Layout (Backend Side)

From the backend project root (where `manage.py` lives):

- `manage.py` – Django management script.
- `erpshipping/`
  - `settings.py` – project settings (DB, apps, auth, CORS).
  - `urls.py` – main URL routing (includes `/api/` paths and `/api/token-auth/`).
- `operations/`
  - `models.py` – database models (User, Customer, Agent, Project, etc.).
  - `serializers.py` – DRF serializers (how models are converted to JSON).
  - `views.py` – ViewSets / APIs for each model.
  - `urls.py` – routes for API endpoints under `/api/`.
  - `admin.py` – admin site registrations.
  - `tests.py` – automated tests (Phase 1 adds an auth smoke test).
- `docs/`
  - `backend_overview.md` – this file (backend documentation for frontend).

---

## 3. Authentication Flow (For Frontend)

### 3.1 Get a token

To log in and get a token:

- **URL:** `POST /api/token-auth/`
- **Body (JSON):**

  ```json
  {
    "username": "<your-username>",
    "password": "<your-password>"
  }
