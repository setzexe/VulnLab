import json
import pytest
from app.security_events import logger

@pytest.fixture
def security_logs(caplog):
    logger.addHandler(caplog.handler)
    try:
        yield caplog
    finally:
        logger.removeHandler(caplog.handler)

def captured_security_events(caplog):
    return [
        json.loads(record.getMessage())
            for record in caplog.records
                if record.name == "vulnlab.security"
    ]

@pytest.mark.parametrize("username", ["alice", "unknown-user"])
def test_failed_login_emits_safe_event(client, security_logs, username):
    password = "incorrect-password-do-not-log"
    response = client.post("/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200

    events = captured_security_events(security_logs)
    assert len(events) == 1

    event = events[0]
    assert event["event"] == "auth.login_failed"
    assert event["outcome"] == "failure"
    assert event["timestamp"].endswith("+00:00")
    assert set(event) == {"timestamp", "event", "outcome"}

    serialized = json.dumps(event)
    assert username not in serialized
    assert password not in serialized


def test_successful_login_does_not_emit_failure(client, security_logs):
    response = client.post( "/auth/login",
        data={
            "username": "alice",
            "password": "password123",
        },
    )

    assert response.status_code == 302
    assert captured_security_events(security_logs) == []