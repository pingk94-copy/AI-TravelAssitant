# Chat Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the basic AI chat foundation with chat sessions, persisted messages, and an SSE stream endpoint.

**Architecture:** Backend chat data will be persisted in `chat_sessions` and `chat_messages` tables tied to authenticated users. A small chat service will save user messages and produce a deterministic local assistant response for now, while the API exposes session creation, message history, and SSE streaming. The frontend chat page will call these APIs and display streamed content.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Pydantic, Server-Sent Events, Vue 3, Pinia.

---

### Task 1: Backend Chat Tests

**Files:**
- Create: `backend/tests/test_chat.py`

- [ ] **Step 1: Write tests**

Test authenticated users can create a chat session, list their sessions, fetch session messages, and receive a streamed assistant response.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest tests/test_chat.py -v`

Expected: fail because chat routes and models do not exist.

### Task 2: Backend Chat Implementation

**Files:**
- Create: `backend/app/models/chat.py`
- Create: `backend/app/schemas/chat.py`
- Create: `backend/app/services/chat_service.py`
- Create: `backend/app/api/routes/chat.py`
- Modify: `backend/app/db/base.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create chat ORM models**

Create `ChatSession` and `ChatMessage`.

- [ ] **Step 2: Create chat schemas**

Create request and response models for sessions, messages, and stream request payload.

- [ ] **Step 3: Create chat service**

Add session creation, session listing, message listing, and assistant response generation.

- [ ] **Step 4: Create chat routes**

Expose `POST /api/chat/sessions`, `GET /api/chat/sessions`, `GET /api/chat/sessions/{session_id}/messages`, and `POST /api/chat/sessions/{session_id}/stream`.

### Task 3: Frontend Chat Implementation

**Files:**
- Create: `frontend/src/api/http.ts`
- Create: `frontend/src/api/chat.ts`
- Modify: `frontend/src/stores/app.ts`
- Modify: `frontend/src/views/ChatView.vue`

- [ ] **Step 1: Add API helpers**

Create reusable backend URL and chat API functions.

- [ ] **Step 2: Update store**

Keep auth token and helper actions in Pinia for current development use.

- [ ] **Step 3: Build chat UI**

Allow users to create a session, type a message, send it, and render streamed assistant text.

### Task 4: Documentation and Verification

**Files:**
- Modify: `Carryout.md`

- [ ] **Step 1: Add concise Round 3 file summary**

Only list changed files and their role.

- [ ] **Step 2: Verify**

Run backend tests and frontend build.
