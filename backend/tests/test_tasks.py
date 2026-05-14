from fastapi.testclient import TestClient


def register_and_get_token(client: TestClient, email: str = "task-user@example.com") -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "username": "task-user",
            "email": email,
            "password": "StrongPass123",
        },
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def trip_payload() -> dict[str, object]:
    return {
        "origin": "Shanghai",
        "destination": "Hangzhou",
        "start_date": "2026-06-01",
        "days": 2,
        "budget": "3000",
        "preferences": ["food", "relaxed", "scenic"],
    }


def test_plan_async_returns_task_id_and_polling_returns_result(client: TestClient):
    token = register_and_get_token(client)

    submit_response = client.post(
        "/api/trips/plan-async",
        json=trip_payload(),
        headers=auth_headers(token),
    )

    assert submit_response.status_code == 202
    task_id = submit_response.json()["task_id"]
    assert submit_response.json()["status"] == "success"

    task_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers(token))

    assert task_response.status_code == 200
    task = task_response.json()
    assert task["id"] == task_id
    assert task["task_type"] == "trip_plan"
    assert task["status"] == "success"
    assert task["output"]["trip"]["destination"] == "Hangzhou"
    assert task["output"]["trip"]["result"]["agent_trace"][-1] == "planner_agent"


def test_tasks_are_isolated_by_user(client: TestClient):
    first_token = register_and_get_token(client, "first-task-user@example.com")
    second_token = register_and_get_token(client, "second-task-user@example.com")

    task_id = client.post(
        "/api/trips/plan-async",
        json=trip_payload(),
        headers=auth_headers(first_token),
    ).json()["task_id"]

    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers(second_token))

    assert response.status_code == 404


def test_task_polling_requires_authentication(client: TestClient):
    response = client.get("/api/tasks/1")

    assert response.status_code == 401
