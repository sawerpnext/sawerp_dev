
This is your starting backend doc for the frontend dev.  
You’ll expand this later as models and APIs grow.

---

## Step 7 – Create `ReadMeBackend.md` as the backend phase log

This file sits in the **backend root** (same level as `manage.py` and `docs/`).

Create:

> `backend/ReadMeBackend.md`

Replace with the full content below.

### Full content of `ReadMeBackend.md`

```markdown
# ERP Shipping – Backend Development Log

This file is a simple log of what we have done on the **backend**,
phase by phase.

We will update it after every phase so anyone (including the frontend
developer) can quickly see where things stand.

---

## Project Tech Stack (Backend)

- **Framework:** Django 5 + Django REST Framework
- **Database:** PostgreSQL (configured via `DATABASE_URL` in `.env`)
- **Auth:** DRF Token Authentication (`rest_framework.authtoken`)
- **Main app:** `operations`
- **Base API prefix:** `/api/`

---

## Phase 1 – Baseline and Test Setup

**Branch:** `backend-domain-v1`

### What we did

1. **Created a dedicated backend branch**

   - Branch name: `backend-domain-v1`
   - Purpose: all backend domain work starts from this clean baseline.

2. **Verified migrations and database**

   - Ran `python manage.py makemigrations`
   - Ran `python manage.py migrate`
   - Confirmed that the Django project can run without errors.

3. **Added an authentication smoke test**

   - File: `operations/tests.py`
   - Test steps:
     - Create a test user.
     - Call `POST /api/token-auth/` to get a token.
     - Use that token to call `GET /api/users/me/`.
     - Assert:
       - `200 OK` from both calls.
       - `username` in `/api/users/me/` matches the test user.
   - Purpose:
     - Quick "does the backend still work?" check.
     - If this test fails, something is broken in auth or URL routing.

4. **Created backend documentation folder**

   - Folder: `docs/`
   - File: `docs/backend_overview.md`
   - Contains:
     - Short description of the backend tech stack.
     - Folder layout (where models, serializers, views live).
     - How authentication works (token flow).
     - Key API endpoints (for now: `/api/token-auth/`, `/api/users/me/`,
       basic CRUD for customers/agents/projects).

5. **Agreed workflow going forward**

   - After each phase:
     - Update this `ReadMeBackend.md` with what was added/changed.
     - Extend or add docs under `docs/` so the frontend developer can see
       new models and APIs.
     - Commit and push the branch.

### How to run the backend (current state)

From the backend root (where `manage.py` lives):

1. Activate virtualenv:

   ```bash
   source .venv/bin/activate
