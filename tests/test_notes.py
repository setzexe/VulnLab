from app.db import get_db


def test_notes_require_login(client):
    response = client.get("/notes/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_user_sees_only_own_notes(client, auth):
    auth.login("alice")

    response = client.get("/notes/")

    assert response.status_code == 200
    assert b"Alice note" in response.data
    assert b"Bob note" not in response.data


def test_create_note(client, auth, app):
    auth.login("alice")

    response = client.post("/notes/create",
        data={
            "title": "New note",
            "body": "New private content",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"New note" in response.data

    with app.app_context():
        note = get_db().execute(
            "SELECT * FROM note WHERE title = ?",
            ("New note",),
        ).fetchone()

        assert note is not None
        assert note["owner_id"] == 1


def test_owner_can_view_note(client, auth):
    auth.login("alice")

    response = client.get("/notes/1")

    assert response.status_code == 200
    assert b"Alice private body" in response.data


def test_idor_is_blocked(client, auth):
    auth.login("alice")

    response = client.get("/notes/2")

    assert response.status_code == 403
    assert b"Bob private body" not in response.data


def test_admin_route_requires_admin(client, auth):
    auth.login("alice")

    response = client.get("/admin/")
    assert response.status_code == 403

    auth.logout()
    auth.login("admin")

    response = client.get("/admin/")

    assert response.status_code == 200
    assert b"alice" in response.data
    assert b"bob" in response.data
    assert b"admin" in response.data