import pytest
from werkzeug.security import generate_password_hash
from app import create_app
from app.db import get_db, init_db

@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test.sqlite"

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "DATABASE": str(database_path),
        }
    )

    with app.app_context():
        init_db()

        password_hash = generate_password_hash("password123", method="pbkdf2:sha256",)

        db = get_db()

        db.executemany(
            """
            INSERT INTO user (id, username, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, "alice", password_hash, "user"),
                (2, "bob", password_hash, "user"),
                (3, "admin", password_hash, "admin"),
            ],
        )

        db.executemany(
            """
            INSERT INTO note (id, owner_id, title, body)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, 1, "Alice note", "Alice private body"),
                (2, 2, "Bob note", "Bob private body"),
            ],
        )

        db.commit()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

class AuthActions:
    def __init__(self, client):
        self.client = client

    def login(self, username="alice", password="password123"):
        return self.client.post("/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self.client.get("/auth/logout", follow_redirects=True)

@pytest.fixture
def auth(client):
    return AuthActions(client)