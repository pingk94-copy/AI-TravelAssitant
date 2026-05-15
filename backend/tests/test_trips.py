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
    assert body["result"]["agent_trace"] == [
        "weather_search_agent",
        "poi_search_agent",
        "route_search_agent",
        "planner_agent",
    ]
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


def test_delete_trip_removes_only_current_user_trip(client: TestClient):
    token = register_and_get_token(client)
    trip_id = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(token),
    ).json()["id"]

    response = client.delete(f"/api/trips/{trip_id}", headers=auth_headers(token))

    assert response.status_code == 204
    assert client.get("/api/trips", headers=auth_headers(token)).json() == []
    assert client.get(f"/api/trips/{trip_id}", headers=auth_headers(token)).status_code == 404


def test_delete_trip_cannot_delete_other_users_trip(client: TestClient):
    first_token = register_and_get_token(client)
    trip_id = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(first_token),
    ).json()["id"]
    second_register = client.post(
        "/api/auth/register",
        json={
            "username": "delete-trip-user",
            "email": "delete-trip-user@example.com",
            "password": "StrongPass123",
        },
    )
    second_token = second_register.json()["access_token"]

    response = client.delete(f"/api/trips/{trip_id}", headers=auth_headers(second_token))

    assert response.status_code == 404
    assert client.get(f"/api/trips/{trip_id}", headers=auth_headers(first_token)).status_code == 200


def test_favorite_trip_is_idempotent_and_listed_for_current_user(client: TestClient):
    token = register_and_get_token(client)
    trip_id = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(token),
    ).json()["id"]

    first_response = client.post(f"/api/trips/{trip_id}/favorite", headers=auth_headers(token))
    second_response = client.post(f"/api/trips/{trip_id}/favorite", headers=auth_headers(token))
    list_response = client.get("/api/trips/favorites", headers=auth_headers(token))

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert first_response.json()["trip"]["id"] == trip_id
    assert second_response.json()["trip"]["id"] == trip_id
    favorites = list_response.json()
    assert len(favorites) == 1
    assert favorites[0]["trip"]["id"] == trip_id


def test_favorite_trip_is_limited_to_owner(client: TestClient):
    first_token = register_and_get_token(client)
    trip_id = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(first_token),
    ).json()["id"]
    second_register = client.post(
        "/api/auth/register",
        json={
            "username": "favorite-other-user",
            "email": "favorite-other-user@example.com",
            "password": "StrongPass123",
        },
    )
    second_token = second_register.json()["access_token"]

    response = client.post(f"/api/trips/{trip_id}/favorite", headers=auth_headers(second_token))

    assert response.status_code == 404


def test_unfavorite_trip_removes_favorite_only_for_current_user(client: TestClient):
    token = register_and_get_token(client)
    trip_id = client.post(
        "/api/trips/plan",
        json=trip_payload(),
        headers=auth_headers(token),
    ).json()["id"]
    client.post(f"/api/trips/{trip_id}/favorite", headers=auth_headers(token))

    response = client.delete(f"/api/trips/{trip_id}/favorite", headers=auth_headers(token))

    assert response.status_code == 204
    assert client.get("/api/trips/favorites", headers=auth_headers(token)).json() == []


def test_trip_endpoints_require_authentication(client: TestClient):
    response = client.post("/api/trips/plan", json=trip_payload())

    assert response.status_code == 401
