# Agent Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor trip planning MVP into a clear Planner Agent + three Search Agents architecture.

**Architecture:** Add lightweight rule-based agents under `backend/app/agents`. The Planner Agent coordinates Weather, POI, and Route agents, then builds the structured itinerary. The trip service will delegate itinerary generation to the Planner Agent so later LangChain/LangGraph integration can replace internals without changing API routes.

**Tech Stack:** Python, FastAPI, Pydantic, pytest.

---

### Task 1: Agent Tests

**Files:**
- Create: `backend/tests/test_trip_agents.py`
- Modify: `backend/tests/test_trips.py`

- [ ] **Step 1: Write direct agent tests**

Assert Planner Agent returns weather, POI, route, daily itinerary, and `agent_trace`.

- [ ] **Step 2: Extend trip API test**

Assert trip planning response includes `agent_trace` metadata.

- [ ] **Step 3: Verify tests fail**

Run: `python -m pytest tests/test_trip_agents.py tests/test_trips.py -v`.

### Task 2: Agent Implementation

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/search_agents.py`
- Create: `backend/app/agents/planner_agent.py`
- Modify: `backend/app/schemas/trip.py`
- Modify: `backend/app/services/trip_service.py`

- [ ] **Step 1: Add search agents**

Wrap weather, place, and route tool calls as separate agent classes.

- [ ] **Step 2: Add planner agent**

Coordinate search agents and build final itinerary result.

- [ ] **Step 3: Add agent trace to itinerary schema**

Expose which agents ran and what each contributed.

- [ ] **Step 4: Wire trip service to planner**

Replace direct tool assembly with Planner Agent.

### Task 3: Documentation and Verification

**Files:**
- Modify: `Carryout.md`

- [ ] **Step 1: Add Round 6 summary**

State purpose and list files briefly.

- [ ] **Step 2: Verify**

Run backend tests and frontend build.
