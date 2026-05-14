# Frontend Auth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a frontend authentication flow for registration, login, token persistence, current-user restore, and protected page access.

**Architecture:** Add an auth API module that calls the existing FastAPI auth endpoints. Extend Pinia state with async auth actions. Add `/auth` route and a route guard for chat/trips. Update the app header to show login or current user/logout.

**Tech Stack:** Vue 3, TypeScript, Pinia, Vue Router, FastAPI auth API.

---

### Task 1: Auth API and Store

**Files:**
- Create: `frontend/src/api/auth.ts`
- Modify: `frontend/src/stores/app.ts`

- [ ] Add typed auth API calls for register, login, and current-user lookup.
- [ ] Add store actions for register, login, restore current user, and logout.

### Task 2: Auth Page and Routing

**Files:**
- Create: `frontend/src/views/AuthView.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/App.vue`

- [ ] Add `/auth` route.
- [ ] Add auth guard for chat and trips.
- [ ] Update header with login/logout user state.

### Task 3: Protected Page Messaging

**Files:**
- Modify: `frontend/src/views/ChatView.vue`
- Modify: `frontend/src/views/TripsView.vue`

- [ ] Replace manual token warning text with clear login guidance.

### Task 4: Documentation and Verification

**Files:**
- Modify: `Carryout.md`

- [ ] Add concise Round 8 summary.
- [ ] Run backend tests and frontend build.
