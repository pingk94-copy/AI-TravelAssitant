# Async Trip Tasks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a task-based trip planning API with `task_id` submission and polling.

**Architecture:** Introduce a `tasks` table and task service. The first version completes trip planning immediately but stores task input/output/status using the same contract a real async worker will use later.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Pydantic, pytest.

---

### Task 1: Task Tests

**Files:**
- Create: `backend/tests/test_tasks.py`

- [ ] **Step 1: Write tests**

Test async trip submission, task polling, result payload, user isolation, and auth rejection.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest tests/test_tasks.py -v`.

### Task 2: Task Backend

**Files:**
- Create: `backend/app/models/task.py`
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/services/task_service.py`
- Create: `backend/app/api/routes/tasks.py`
- Modify: `backend/app/db/base.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/routes/trips.py`

- [ ] **Step 1: Add task model and schemas**

Persist `task_type`, `status`, `input_json`, `output_json`, and `error_message`.

- [ ] **Step 2: Add task service**

Create task, complete task, fail task, and fetch task by user.

- [ ] **Step 3: Add task route**

Expose `GET /api/tasks/{task_id}`.

- [ ] **Step 4: Add async trip route**

Expose `POST /api/trips/plan-async`.

### Task 3: Documentation and Verification

**Files:**
- Modify: `Carryout.md`

- [ ] **Step 1: Add Round 7 summary**

State purpose and list files briefly.

- [ ] **Step 2: Verify**

Run backend tests and frontend build.
