# Deployment preparation

## Status

The remediated application was verified locally with Docker Compose.

Cloud deployment is tracked separately in the VulnLab-Cloud repo.

## Design

- Gunicorn serves Flask with two application workers.
- Gunicorn control socket is disabled.
- VULNLAB_SECRET_KEY supplies the session signing secret at runtime.
- Normal startup does not take in missing secrets or values shorter than 32 characters.
- Redis stores shared login attempt counters.
- SQLite stores users and notes in the vulnlab-data volume.
- Access to the app is only on 127.0.0.1:5000.
- Redis has no published host port.

## Runtime secret

Before starting Compose, run on your local machine:

```bash
export VULNLAB_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

This generates a random secret but does not print its value.
The variable remains available only for the current terminal session.

Reuse the same secret to preserve existing sessions across restarts.
Do not commit secret values or include them in container images.

## Rate limit storage

POST requests on logins are limited to five attempts per minute for each client address. All Gunicorn workers use the same Redis counters.

If Redis is unavailable, login requests fail rather than falling back to separate memory counters or bypassing the limit. The current response is HTTP 500.

## Verification

Verification completed on September 25, 2026:

- Application and security tests
  - 20 passed
- Gunicorn startup
  - Two workers; no control-socket error
- Login attempts
  - Five HTTP 200 responses, followed by HTTP 429
- Container replacement
  - Subsequent login attempt remained HTTP 429
- Database persistence
  - Previously created note remained available
- Redis unavailable
  - Login request returned HTTP 500
- Redis restarted
  - Both containers healthy; /health returned ok

Run the regression commands from the repository root:

```bash
docker compose run --rm --no-deps vulnlab python -m pytest -q -p no:cacheprovider
```

This pipeline also runs Bandit, a dependency audit, and Trivy scans
of the application + Redis images.

## Limitations

The /health endpoint checks that Flask responds. It does not verify
database access if Redis is availabile.
