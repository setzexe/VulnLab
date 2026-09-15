from app import create_app
import pytest

def test_health_endpoint():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

@pytest.mark.xfail(reason="Diagnostic config is intentionally exposed for card #9", strict=True,)
def test_debug_config_is_not_exposed(client):
    response = client.get("/debug/config")
    assert response.status_code == 404
    assert b"test-key" not in response.data