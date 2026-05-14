# Travel Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add authenticated travel tool endpoints for place search, weather lookup, and route planning.

**Architecture:** The backend will expose `/api/tools/*` routes backed by a small Amap Web Service client. Tool services will return stable normalized responses and use fallback data when `AMAP_API_KEY` is missing or the upstream request fails.

**Tech Stack:** FastAPI, httpx, Pydantic, Amap Web Service API, pytest.

---

### Task 1: Tool Tests

**Files:**
- Create: `backend/tests/test_tools.py`

- [ ] **Step 1: Write authenticated tool endpoint tests**

Test place search, weather lookup, route planning, and unauthenticated rejection.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest tests/test_tools.py -v`

Expected: fail because tool routes do not exist.

### Task 2: Tool Implementation

**Files:**
- Create: `backend/app/schemas/tools.py`
- Create: `backend/app/tools/__init__.py`
- Create: `backend/app/tools/amap_client.py`
- Create: `backend/app/services/travel_tool_service.py`
- Create: `backend/app/api/routes/tools.py`
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add schemas**

Define request and response models for places, weather, and routes.

- [ ] **Step 2: Add Amap client**

Wrap place, weather, and route API calls with timeouts and fallback-safe behavior.

- [ ] **Step 3: Add service layer**

Normalize client output for API routes and future Agent tools.

- [ ] **Step 4: Add routes**

Expose `POST /api/tools/places/search`, `POST /api/tools/weather`, and `POST /api/tools/routes`.

### Task 3: Documentation and Verification

**Files:**
- Modify: `Carryout.md`

- [ ] **Step 1: Add concise Round 4 file summary**

Only list changed files and their role.

- [ ] **Step 2: Verify**

Run backend tests and frontend build.
