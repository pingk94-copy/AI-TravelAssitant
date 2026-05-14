from fastapi.testclient import TestClient


def register_and_get_token(client: TestClient) -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "username": "trip-user",
            "email": "trip-user@example.com",
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


def test_plan_trip_creates_structured_itinerary(client: TestClient):
    token = register_and_get_token(client)

    response = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "success"
    assert body["origin"] == "Shanghai"
    assert body["destination"] == "Hangzhou"
    assert len(body["result"]["days"]) == 2
    assert body["result"]["summary"]
    assert body["result"]["days"][0]["schedule"][0]["title"]


def test_list_trips_only_returns_current_user_trips(client: TestClient):
    first_token = register_and_get_token(client)
    second_register = client.post(
        "/api/auth/register",
        json={
            "username": "second-trip-user",
            "email": "second-trip-user@example.com",
            "password": "StrongPass123",
        },
    )
    second_token = second_register.json()["access_token"]

    client.post("/api/trips/plan", json=trip_payload(), headers=auth_headers(first_token))
    other_payload = trip_payload() | {"destination": "Suzhou"}
    client.post("/api/trips/plan", json=other_payload, headers=auth_headers(second_token))

    response = client.get("/api/trips", headers=auth_headers(first_token))

    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 1
    assert trips[0]["destination"] == "Hangzhou"


def test_get_trip_detail_returns_saved_itinerary(client: TestClient):
    token = register_and_get_token(client)
    trip_id = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(token),
    ).json()["id"]

    response = client.get(f"/api/trips/{trip_id}", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["id"] == trip_id
    assert response.json()["result"]["destination"] == "Hangzhou"


def test_trip_endpoints_require_authentication(client: TestClient):
    response = client.post("/api/trips/plan", json=trip_payload())

    assert response.status_code == 401
