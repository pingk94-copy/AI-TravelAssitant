from fastapi.testclient import TestClient


def register_and_get_token(client: TestClient) -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "username": "chat-user",
            "email": "chat-user@example.com",
            "password": "StrongPass123",
        },
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_chat_session_for_current_user(client: TestClient):
    token = register_and_get_token(client)

    response = client.post(
        "/api/chat/sessions",
        json={"title": "Hangzhou weekend"},
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Hangzhou weekend"


def test_list_chat_sessions_only_returns_current_user_sessions(client: TestClient):
    first_token = register_and_get_token(client)
    client.post(
        "/api/auth/register",
        json={
            "username": "other-user",
            "email": "other-user@example.com",
            "password": "StrongPass123",
        },
    )
    other_token = client.post(
        "/api/auth/login",
        json={"email": "other-user@example.com", "password": "StrongPass123"},
    ).json()["access_token"]

    client.post("/api/chat/sessions", json={"title": "Mine"}, headers=auth_headers(first_token))
    client.post("/api/chat/sessions", json={"title": "Other"}, headers=auth_headers(other_token))

    response = client.get("/api/chat/sessions", headers=auth_headers(first_token))

    assert response.status_code == 200
    assert [session["title"] for session in response.json()] == ["Mine"]


def test_stream_chat_reply_persists_user_and_assistant_messages(client: TestClient):
    token = register_and_get_token(client)
    session_id = client.post(
        "/api/chat/sessions",
        json={"title": "Trip idea"},
        headers=auth_headers(token),
    ).json()["id"]

    with client.stream(
        "POST",
        f"/api/chat/sessions/{session_id}/stream",
        json={"message": "Plan a slow trip to Hangzhou"},
        headers=auth_headers(token),
    ) as response:
        streamed_text = "".join(response.iter_text())

    assert response.status_code == 200
    assert "event: token" in streamed_text
    assert "Hangzhou" in streamed_text
    assert "event: done" in streamed_text

    messages_response = client.get(
        f"/api/chat/sessions/{session_id}/messages",
        headers=auth_headers(token),
    )

    assert messages_response.status_code == 200
    messages = messages_response.json()
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[0]["content"] == "Plan a slow trip to Hangzhou"
    assert "Hangzhou" in messages[1]["content"]
