# Auth System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first user system for the travel assistant with registration, login, JWT issuance, and authenticated current-user lookup.

**Architecture:** The backend will gain a SQLAlchemy SQLite persistence layer, a `User` model, Pydantic auth schemas, password hashing utilities, JWT utilities, and versioned auth routes under `/api/auth`. Tests will use an isolated SQLite database override so auth behavior is repeatable and does not depend on local development data.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Pydantic, passlib bcrypt, python-jose, pytest.

---

### Task 1: Auth Tests

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Create test database fixture**

Use a temporary SQLite database and override `get_db` for FastAPI tests.

- [ ] **Step 2: Write registration, duplicate registration, login, and current-user tests**

Test these behaviors:

- `POST /api/auth/register` creates a user and returns a token.
- duplicate email registration returns HTTP 409.
- `POST /api/auth/login` returns a token for valid credentials.
- invalid login returns HTTP 401.
- `GET /api/auth/me` returns the authenticated user when a bearer token is supplied.

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_auth.py -v`

Expected: fail because auth modules and routes do not exist yet.

### Task 2: Persistence Layer

**Files:**
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/models/user.py`

- [ ] **Step 1: Create SQLAlchemy engine and session dependency**

Provide `engine`, `SessionLocal`, and `get_db`.

- [ ] **Step 2: Create declarative base**

Expose `Base` for all ORM models.

- [ ] **Step 3: Create user ORM model**

Fields: `id`, `username`, `email`, `password_hash`, `is_guest`, `guest_uid`, `created_at`, `updated_at`.

### Task 3: Auth Schemas and Services

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/services/auth_service.py`

- [ ] **Step 1: Define Pydantic schemas**

Create request and response models for register, login, token, and user output.

- [ ] **Step 2: Add security helpers**

Implement bcrypt password hashing, password verification, JWT creation, JWT decoding, and authenticated user dependency.

- [ ] **Step 3: Add auth service functions**

Implement user lookup, register, and authenticate logic.

### Task 4: Auth Routes and App Registration

**Files:**
- Create: `backend/app/api/routes/auth.py`
- Modify: `backend/app/main.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Register dependencies**

Add SQLAlchemy, passlib bcrypt, python-jose, and email-validator.

- [ ] **Step 2: Create auth router**

Expose:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

- [ ] **Step 3: Include auth router in app**

Register auth routes and create database tables on startup for the current learning phase.

- [ ] **Step 4: Run tests**

Run: `python -m pytest`

Expected: all backend tests pass.

### Task 5: Documentation Log

**Files:**
- Modify: `Carryout.md`

- [ ] **Step 1: Add Round 2 section**

Document:

- What changed.
- Why each file was added.
- How registration, login, JWT, and `/me` work.
- What was tested.

- [ ] **Step 2: Run final verification**

Run:

- `python -m pytest`
- `npm run build`

Expected: backend tests pass and frontend build succeeds.
