def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["providers"]["ocr"] == "mock"
    assert body["providers"]["email"] == "mock"


def test_send_and_verify_and_me(client):
    send = client.post("/auth/send-code", json={"email": "a@example.com"})
    assert send.status_code == 200
    code = send.json()["debug_code"]
    assert len(code) == 6

    again = client.post("/auth/send-code", json={"email": "a@example.com"})
    assert again.status_code == 429

    bad = client.post(
        "/auth/verify",
        json={"email": "a@example.com", "code": "000000", "device_id": "d1"},
    )
    assert bad.status_code == 400

    ok = client.post(
        "/auth/verify",
        json={"email": "a@example.com", "code": code, "device_id": "d1"},
    )
    assert ok.status_code == 200
    tokens = ok.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "a@example.com"

    refresh = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200
    reused = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401

    client.post("/auth/logout", json={"refresh_token": refresh.json()["refresh_token"]})
    after_logout = client.post(
        "/auth/refresh", json={"refresh_token": refresh.json()["refresh_token"]}
    )
    assert after_logout.status_code == 401


def test_unauthenticated_books(client):
    assert client.get("/books").status_code == 401
