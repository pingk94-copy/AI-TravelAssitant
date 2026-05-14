from fastapi.testclient import TestClient


def register_and_get_token(client: TestClient) -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "username": "tool-user",
            "email": "tool-user@example.com",
            "password": "StrongPass123",
        },
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_place_search_returns_normalized_results(client: TestClient):
    token = register_and_get_token(client)

    response = client.post(
        "/api/tools/places/search",
        json={"keyword": "West Lake", "city": "Hangzhou"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] in {"amap", "fallback"}
    assert body["items"][0]["name"]
    assert "address" in body["items"][0]


def test_weather_lookup_returns_normalized_forecast(client: TestClient):
    token = register_and_get_token(client)

    response = client.post(
        "/api/tools/weather",
        json={"city": "Hangzhou"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] in {"amap", "fallback"}
    assert body["city"] == "Hangzhou"
    assert body["forecast"][0]["date"]
    assert body["forecast"][0]["weather"]


def test_route_planning_returns_normalized_steps(client: TestClient):
    token = register_and_get_token(client)

    response = client.post(
        "/api/tools/routes",
        json={
            "origin": "Hangzhou East Railway Station",
            "destination": "West Lake",
            "city": "Hangzhou",
            "mode": "walking",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] in {"amap", "fallback"}
    assert body["origin"] == "Hangzhou East Railway Station"
    assert body["destination"] == "West Lake"
    assert body["steps"][0]["instruction"]


def test_tool_endpoints_require_authentication(client: TestClient):
    response = client.post(
        "/api/tools/weather",
        json={"city": "Hangzhou"},
    )

    assert response.status_code == 401
