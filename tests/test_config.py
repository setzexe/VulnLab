import pytest
from app import create_app

@pytest.mark.parametrize(
    "secret",
    [None, "", "dev-key", "local-docker-dev-key"],
)

def test_normal_startup_rejects_invalid_secret(monkeypatch, secret):
    if secret is None:
        monkeypatch.delenv("VULNLAB_SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("VULNLAB_SECRET_KEY", secret)

    with pytest.raises(RuntimeError, match="VULNLAB_SECRET_KEY"):
        create_app()

def test_normal_startup_uses_runtime_secret(monkeypatch):
    secret = "test-only-runtime-secret-" + ("x" * 40)
    monkeypatch.setenv("VULNLAB_SECRET_KEY", secret)
    app = create_app()
    assert app.config["SECRET_KEY"] == secret
    assert app.testing is False
    assert app.debug is False
    assert app.test_client().get("/health").status_code == 200