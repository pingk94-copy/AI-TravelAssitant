# Trip Planning MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a synchronous MVP trip planning flow that accepts travel parameters, uses existing travel tools, stores the generated itinerary, and exposes it to the frontend.

**Architecture:** The backend will persist generated trips in a `trips` table tied to users. A trip planner service will combine weather, place, and route tool outputs into a structured itinerary JSON. The frontend trip page will submit a form, call the API, and render the returned itinerary.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Pydantic, Vue 3, TypeScript.

---

### Task 1: Backend Trip Tests

**Files:**
- Create: `backend/tests/test_trips.py`

- [ ] **Step 1: Write trip planning tests**

Test authenticated trip planning, trip listing, trip detail lookup, and unauthenticated rejection.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest tests/test_trips.py -v`

Expected: fail because trip routes do not exist.

### Task 2: Backend Trip Implementation

**Files:**
- Create: `backend/app/models/trip.py`
- Create: `backend/app/schemas/trip.py`
- Create: `backend/app/services/trip_service.py`
- Create: `backend/app/api/routes/trips.py`
- Modify: `backend/app/db/base.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create trip ORM model**

Persist trip request fields, status, and generated result JSON.

- [ ] **Step 2: Create trip schemas**

Define request/response models and structured itinerary fields.

- [ ] **Step 3: Create planner service**

Generate a basic itinerary using weather, place search, and route fallback tools.

- [ ] **Step 4: Create trip routes**

Expose `POST /api/trips/plan`, `GET /api/trips`, and `GET /api/trips/{trip_id}`.

### Task 3: Frontend Trip Page

**Files:**
- Create: `frontend/src/api/trips.ts`
- Modify: `frontend/src/views/TripsView.vue`

- [ ] **Step 1: Add trip API client**

Wrap plan/list/detail calls.

- [ ] **Step 2: Build planning form and itinerary display**

Render the MVP structured itinerary returned by backend.

### Task 4: Documentation and Verification

**Files:**
- Modify: `Carryout.md`

- [ ] **Step 1: Add Round 5 concise summary**

State the round purpose and list files with short roles.

- [ ] **Step 2: Verify**

Run backend tests and frontend build.
