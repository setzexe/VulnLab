from flask import session
from werkzeug.security import check_password_hash
from app.db import get_db

def test_register(client, app):
    response = client.post("/auth/register",
        data={
            "username": "charlie",
            "password": "securepass123",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")

    with app.app_context():
        user = get_db().execute(
            "SELECT * FROM user WHERE username = ?",
            ("charlie",),
        ).fetchone()

        assert user is not None
        assert user["password_hash"] != "securepass123"
        assert check_password_hash(
            user["password_hash"],
            "securepass123",
        )

def test_duplicate_username(client):
    response = client.post("/auth/register",
        data={
            "username": "alice",
            "password": "anotherpass123",
        },
        follow_redirects=True,
    )

    assert b"already registered" in response.data

def test_login_and_logout(client, auth):
    with client:
        response = auth.login()

        assert response.status_code == 200
        assert session["user_id"] == 1
        assert b"alice" in response.data

        response = auth.logout()

        assert "user_id" not in session
        assert b"Log in" in response.data

def test_registration_rejects_weak_password(client, app):
    response = client.post("/auth/register",
        data={
            "username": "weak_auth_user",
            "password": "letmein",
        },
    )

    assert response.status_code == 200

    with app.app_context():
        user = get_db().execute(
            "SELECT * FROM user WHERE username = ?",
            ("weak_auth_user",),
        ).fetchone()

        assert user is None

def test_repeated_login_attempts_are_limited(client):
    for _ in range(5):
        response = client.post("/auth/login",
            data={
                "username": "alice",
                "password": "incorrect-password",
            },
        )
        assert response.status_code == 200

    blocked_response = client.post("/auth/login",
        data={
            "username": "alice",
            "password": "incorrect-password",
        },
    )
    assert blocked_response.status_code == 429

def test_login_page_views_do_not_consume_rate_limit(client):
    for _ in range(6):
        response = client.get("/auth/login")
        assert response.status_code == 200