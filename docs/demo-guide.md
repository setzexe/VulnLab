# VulnLab Demonstration Guide

## Safety Notice

VulnLab contains an intentionally vulnerable version for educational testing.

- Run this vulnerable version only on a local system *you* control. Never publicly deploy this vulnerable version.
- Use only fake accounts, passwords, and notes that do not reflect real world information.
- The proof of concept scripts target only `http://127.0.0.1:5000`.

The default `main` branch contains the remediated application.

## Requirements

- Git
- Docker Desktop
- Python 3.12 for running PoC scripts outside the container

Clone the repository:

```bash
git clone https://github.com/setzexe/VulnLab.git
cd VulnLab
```

## Run the Secured Application

Ensure `main` is checked out:

```bash
git switch main
git pull
```

Generate the runtime secret in the current terminal:

```bash
export VULNLAB_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

Reuse this secret when restarting the application. Check out [Deployment preparation](deployment-preparation.md).

Build + start VulnLab:

```bash
docker compose up -d --build
```

Initialize the SQLite database:

```bash
docker compose exec vulnlab python -m flask --app run init-db
```

Open:

```text
http://127.0.0.1:5000
```

Verify the health endpoint:

```bash
curl http://127.0.0.1:5000/health
```

You should receive something like:

```json
{"status":"ok"}
```

## Verify the Secured Version

Run the automated tests via pytest:

```bash
docker compose run --rm vulnlab pytest -v -p no:cacheprovider
```

The security regression tests show that:

- SQL injection does not show another user’s notes.
- Users cannot see notes they do not own.
- Weak passwords are rejected.
- Excessive login attempts receive `429 Too Many Requests`.
- The old configuration endpoint returns `404 Not Found`.

The PoC scripts can also be run against `main`:

```bash
python pocs/sql_injection.py
python pocs/idor.py
python pocs/weak_authentication.py
python pocs/information_exposure.py
```

The scripts should stop without successfully completing their attack.

## Reproduce the Vulnerable Environment / Version

First, stop the secured base and remove its local database instance:

```bash
docker compose down -v
```

Check out the intentionally vulnerable tag, build and initialize it:

```bash
git switch --detach v0.1.0-vulnerable
docker compose up -d --build
docker compose exec vulnlab python -m flask --app run init-db
```

Run the local PoCs individually:

```bash
python pocs/sql_injection.py
python pocs/idor.py
python pocs/weak_authentication.py
python pocs/information_exposure.py
```

Detailed explanations are available at:

- [SQL injection](vulnerabilities/sql-injection.md)
- [IDOR](vulnerabilities/idor.md)
- [Weak authentication](vulnerabilities/weak-authentication.md)
- [Information exposure](vulnerabilities/information-exposure.md)

## Return to the Secured Version

Stop and delete the vulnerable environment:

```bash
docker compose down -v
```

Switch to the secured branch:

```bash
git switch main
docker compose up -d --build
docker compose exec vulnlab python -m flask --app run init-db
```
