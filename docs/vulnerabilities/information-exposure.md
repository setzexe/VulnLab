# Information Exposure Through a Diagnostic Endpoint

## Status

Remediated in card #10. The intentionally vulnerable base app is preserved under the `v0.1.0-vulnerable` Git tag.

## Summary

VulnLab exposes an unauthenticated diagnostic endpoint at `/debug/config`. The endpoint returns internal information revolving around configuration, including the application’s database path and Flask secret key. Anyone capable of reaching the application can retrieve these values without registering or logging in.

## Affected Component

- Route: `GET /debug/config`
- Source: `app/debug.py`
- Required access: None
- Vulnerability type: Information exposure
- Environment: Local VulnLab environment

## Proof of Concept

The PoC:

1. Confirms that VulnLab is running.
2. Requests `/debug/config` without authentication or a session cookie.
3. Confirms that the database path and secret key were exposed.
4. Prints the information returned.

Run:

```bash
python pocs/information_exposure.py
```

An equivalent manual request is:

```bash
curl http://127.0.0.1:5000/debug/config
```

Example vulnerable response:

```json
{
  "application": "VulnLab",
  "database_path": "/app/instance/vulnlab.sqlite",
  "debug_mode": false,
  "secret_key": "local-docker-dev-key",
  "testing_mode": false
}
```

## Evidence

The PoC output confirms that:

- The endpoint responds without any authentication check.
- The internal SQLite database path is returned.
- The Flask secret key is returned.

The secret shown by VulnLab is limited to the local environment.

## Root Cause

The application registers a diagnostic blueprint:

```python
from . import auth, admin, notes, debug

app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(notes.bp)
app.register_blueprint(debug.bp)
```

The blueprint gives a route accessible publicly:

```python
@bp.get("/config")
def config():
    return {
        "application": "VulnLab",
        "database_path": current_app.config["DATABASE"],
        "debug_mode": current_app.debug,
        "secret_key": current_app.config["SECRET_KEY"],
        "testing_mode": current_app.testing,
    }
```

The route has no authentication or authorization check. More importantly, information such as a secret key should not be returned to a client at all, even if the route were restricted to an administrator.

The vulnerability occurs because values retrieved from the configuration are inserted directly into an HTTP response.

## Why the Secret Key Matters

Flask uses secret key's to cryptographically sign session cookies. The signature allows the server to detect whether the session data was modified by a client.

VulnLab stores the authenticated user’s ID inside the session:

```python
session["user_id"] = user["id"]
```

If an attacker obtains the secret key, they may be able to create a session cookie and impersonate another user. Signing does not encrypt the session contents. Its purpose is to protect their integrity. Once the signing secret is exposed, the content's no longer can be trusted.

The PoC is focused on demonstrating the information exposure.

## Why the Database Path Matters

The path:

```text
/app/instance/vulnlab.sqlite
```

does not directly provide the database contents. However, it reveals information about the application’s internal filesystem and storage structure. This information could make another vulnerability easier to exploit, such as:

- Path traversal
- Arbitrary file download
- Unsafe backup exposure
- Local file inclusion

Information exposure often increases the effectiveness of other attacks because it provides useful internal knowledge.

## Attack Sequence

1. An unauthenticated client discovers or guesses `/debug/config`.
2. The client sends a normal `GET` request.
3. Flask loads the active application configuration.
4. The route places sensitive values into a JSON response.
5. The response is returned without an authorization check.
6. The client learns the secret key and internal database path.

## Impact

The demonstrated impact includes:

- Disclosure of the Flask secret key
- Disclosure of an internal filesystem path
- Loss of configuration confidentiality
- Potential session forgery and account impersonation
- Additional reconnaissance for chained attacks

## Existing Positive Controls

The Docker configuration binds VulnLab to localhost only:

```text
127.0.0.1:5000
```

The `/health` endpoint also only showcases:

```json
{"status": "ok"}
```

## Classification

- [OWASP Top 10:2021 — A05: Security Misconfiguration](https://top10.owasp.org/2021/A05_2021-Security_Misconfiguration/)
- [CWE-215 — Insertion of Sensitive Information Into Debugging Code](https://cwe.mitre.org/data/definitions/215.html)
- [CWE-200 — Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html)

## Remediation

Card #10 removed the diagnostic endpoint completely:

- `app/debug.py` was deleted.
- The debug blueprint import and registration was removed.
- `/debug/config` now returns `404 Not Found`.

Restricting the endpoint to administrators would not have been enough. Application secrets should not be returned through HTTP responses at all.

## Regression Test

The `test_debug_config_is_not_exposed` regression test confirms that:

- `/debug/config` returns `404 Not Found`.

The original information-exposure PoC now exits unsuccessfully when it receives the `404` response.

## Before and After

| State      | Diagnostic Endpoint | Sensitive Values                      | Result                           |
| ---------- | ------------------- | ------------------------------------- | -------------------------------- |
| Vulnerable | Publicly accessible | Secret key and database path returned | Information exposed              |
| Remediated | Removed             | No configuration returned             | Request receives `404 Not Found` |

