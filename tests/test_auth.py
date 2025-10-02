from fastapi.testclient import TestClient
from wscraping.main import app

client = TestClient(app)

def test_register_and_login():
    email = "test@example.com"
    username = "tester"
    password = "secret123"

    r = client.post("/auth/register", json={"email": email, "username": username, "password": password})
    assert r.status_code == 200
    data = r.json()
    assert "id" in data

    r = client.post("/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r.status_code == 200
    me = r.json()
    assert me["username"] == username
