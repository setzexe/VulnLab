# Weak Authentication Through Predictable Passwords

## Status

Remediated in card #10. The intentionally vulnerable base app is preserved under the `v0.1.0-vulnerable` Git tag.

## Summary

VulnLab allows users to register with predictable passwords and allows repeated login attempts without limiting, delay, or lockout.

A local attacker who knows a username can repeatedly test common passwords until one successfully works.

Password hashing remains on. This shows that secure password storage can't compensate for weak passwords and unrestricted guessing attempts.

## Affected Components

- Routes: `POST /auth/register` and `POST /auth/login`
- Source: `app/auth.py`
- Template: `app/templates/auth/register.html`
- Required access: None
- Vulnerability type: Weak authentication
- Environment: Local VulnLab instance

## Proof of Concept

The PoC performs the following:

1. Creates a victim account with the predictable password `letmein`.
2. Starts a separate unauthenticated attacker session.
3. Attempts several common passwords against the victim’s username.
4. Detects the successful login redirect.
5. Verifies that the attacker session is authenticated as the victim.

Run:

```bash
python pocs/weak_authentication.py
```

The script targets only:

```text
http://127.0.0.1:5000
```

It does not accept an external target and uses only accounts created inside the isolated VulnLab environment.

## Evidence

The terminal output demonstrates that:

- Several incorrect passwords are processed without restriction.
- No cooldown, lockout, or `429 Too Many Requests` response occurs.
- The predictable password `letmein` successfully works.
- The attack completes after only a few requests.

## Root Cause

### Weak Password Requirements

The secure registration required a minimum password length:

```python
elif len(password) < 8:
    error = "Password must contain at least 8 characters."
```

The vulnerable version checks only whether a password exists:

```python
if not username:
    error = "Username is required."
elif not password:
    error = "Password is required."
```

There is no server-side length or predictable-password check, so the account can use a password such as `letmein`.

The browser’s `minlength` attribute was also removed from the registration form. However, browser validation is not a fix all because an attacker can bypass it by sending an HTTP request directly. Server side validation is required for actual enforcement.

### Unrestricted Login Attempts

The login route retrieves the user and checks each submitted password:

```python
user = get_db().execute(
    "SELECT * FROM user WHERE username = ?",
    (username,),
).fetchone()
```

```python
elif not check_password_hash(
    user["password_hash"],
    password,
):
    error = "Incorrect username or password."
```

The app does not track:

- Failed login counts
- How often qttempts are made
- Temporary account lockouts

Every submitted password is processed regardless of how many previous attempts failed.

## Attack Sequence

1. A victim registers with a predictable password.
2. The attacker learns / guesses the victim’s username.
3. The attacker submits common passwords to the login route.
4. VulnLab processes every attempt without restriction.
5. One password matches the victim’s password hash.
6. VulnLab creates an authenticated session for the attacker.

## Impact

A successful attack allows an attacker to take control of another user's account and potentially access all info of that user. Possible consequences include:

- Account compromise
- Unauthorized access to private information
- Actions performed under another user

The demonstration does not access an external system, real account, or real password. All accounts and data are fictional and exist only inside the local VulnLab environment.

## Existing Security Controls

The login page uses the same error message for an unknown username and an incorrect password:

```text
Incorrect username or password.
```

This helps avoid directly revealing whether a username exists.
Passwords are also stored as PBKDF2 hashes rather than plaintext.

## Classification

- [OWASP Top 10:2021 — A07: Identification and Authentication Failures](https://top10.owasp.org/2021/A07_2021-Identification_and_Authentication_Failures/)
- [CWE-521 — Weak Password Requirements](https://cwe.mitre.org/data/definitions/521.html)
- [CWE-307 — Improper Restriction of Excessive Authentication Attempts](https://cwe.mitre.org/data/definitions/307.html)

## Remediation

Card #10 hardened both parts of the authentication flow. Registration now enforces a server side minimum password length:

```python
elif len(password) < 8:
    error = "Password must contain at least 8 characters."
```

The registration form also includes `minlength="8"` as a browser side hint. The Python validation is the actual security control.

Login requests are limited with Flask-Limiter:

```python
@bp.route("/login", methods=("GET", "POST"))
@limiter.limit("5 per minute", methods=["POST"])
def login():
```

The local lab uses in mmemory rate limit storage. A multi process public deployment would require shared storage such as Redis.

Only login submissions are counted. The first five requests from a client IP are processed, while another request inside the same window receives:

```http
HTTP/1.1 429 Too Many Requests
```

PBKDF2 password hashing and generic login error messages remain enabled.

## Regression Tests

Two security regression tests verify:

- `test_registration_rejects_weak_password` confirms that `letmein` is rejected and no account is created.
- `test_repeated_login_attempts_are_limited` confirms that excessive login requests receive `429 Too Many Requests`.

Both tests pass normally without `xfail` markers.

The original PoC now stops when VulnLab refuses to create the predictable-password victim account.

## Before and After

| State      | Password Behavior              | Login Attempt Behavior           | Result                           |
| ---------- | ------------------------------ | -------------------------------- | -------------------------------- |
| Vulnerable | Predictable passwords accepted | Attempts unrestricted            | Dictionary attack succeeds       |
| Remediated | Weak passwords rejected        | Excessive attempts receive `429` | Original attack chain is blocked |
