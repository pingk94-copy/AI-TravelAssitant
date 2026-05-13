from fastapi.testclient import TestClient


def test_register_creates_user_and_returns_token(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "traveler",
            "email": "traveler@example.com",
            "password": "StrongPass123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"] == {
        "id": 1,
        "username": "traveler",
        "email": "traveler@example.com",
        "is_guest": False,
    }


def test_register_rejects_duplicate_email(client: TestClient):
    payload = {
        "username": "traveler",
        "email": "traveler@example.com",
        "password": "StrongPass123",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered"


def test_login_returns_token_for_valid_credentials(client: TestClient):
    client.post(
        "/api/auth/register",
        json={
            "username": "traveler",
            "email": "traveler@example.com",
            "password": "StrongPass123",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "traveler@example.com",
            "password": "StrongPass123",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "traveler@example.com"


def test_login_rejects_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "missing@example.com",
            "password": "WrongPass123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_returns_current_user_with_bearer_token(client: TestClient):
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "traveler",
            "email": "traveler@example.com",
            "password": "StrongPass123",
        },
    )
    token = register_response.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "traveler",
        "email": "traveler@example.com",
        "is_guest": False,
    }
