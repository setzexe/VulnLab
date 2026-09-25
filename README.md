# VulnLab

[![Security pipeline](https://github.com/setzexe/VulnLab/actions/workflows/tests.yml/badge.svg)](https://github.com/setzexe/VulnLab/actions/workflows/tests.yml)

VulnLab is a controlled Flask application security project that showcases the lifecycle of building an application, exploiting vulnerabilities locally, remediating their roots / causes, and hardening security through automated testing.

```text
Build -> Attack -> Fix -> Automate
```

The secured application base is showcased and maintained on `main`. The vulnerable version is preserved under the [`v0.1.0-vulnerable`](https://github.com/setzexe/VulnLab/tree/v0.1.0-vulnerable) Git tag and must *only* be run locally.

## Project Highlights

- Flask application with registration, authentication, private notes, and administrator authorization
- Four controlled security vulnerability scenarios
- Local Python proof of concept (PoC) scripts
- Root cause and impact analysis + OWASP and CWE links
- Hardening remediations and pytest regression tests
- Reproducible Docker environment
- GitHub Actions security pipeline using pytest, Bandit, pip-audit, and Trivy
- Professional penetration test report and demonstration guide

## Vulnerabilities

| Vulnerability | Impact | Remediation |
| --- | --- | --- |
| [SQL injection](docs/vulnerabilities/sql-injection.md) | Other user's can see unauthorized notes | Parameterized SQL queries |
| [IDOR](docs/vulnerabilities/idor.md) | Unauthorized private note access | Server side ownership validation |
| [Weak authentication](docs/vulnerabilities/weak-authentication.md) | Account compromise through password guessing | Password requirements and login rate limiting |
| [Information exposure](docs/vulnerabilities/information-exposure.md) | Secret key + internal path disclosure | Configuration diagnostic endpoint removed |

All four vulnerabilities are remediated on `main` and covered by security regression tests.

## Architecture

VulnLab intentionally uses the following tech stack:

- Python 3.12 and Flask
- SQLite database
- Server rendered HTML
- Session based authentication
- PBKDF2 password hashing
- Flask-Limiter login protection
- Docker with Docker Compose
- GitHub Actions CI/CD security checks

Using `sqlite3` ensures real world data is not tampered with.

## Start

### Requirements

- Git
- Docker Desktop

Clone and enter the repository:

```bash
git clone https://github.com/setzexe/VulnLab.git
cd VulnLab
```

Generate a runtime session secret in the current terminal:

```bash
export VULNLAB_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

Build and start the application and Redis:

```bash
docker compose up -d --build --wait
```

On first use with an empty database, initialize its tables:

```bash
docker compose exec vulnlab python -m flask --app run init-db
```

The init-db command drops and recreates application tables. Don't rerun this against data you want to keep.

Check out [Deployment preparation](docs/deployment-preparation.md)
for configuration, storage behavior, and verification.

Open:

```text
http://127.0.0.1:5000
```

To check the container status:

```bash
docker compose ps
```

And to stop the application:

```bash
docker compose down
```

Add `-v` to delete the local database instance:

```bash
docker compose down -v
```

## Testing

Run the complete test suite inside Docker:

```bash
docker compose run --rm vulnlab pytest -v -p no:cacheprovider
```

The testing suite covers:

- Registration, login, logout, and password hashing
- Authentication requirements
- Private note creation and access
- Administrator authorization
- SQL injection prevention
- IDOR authorization
- Weak password rejection
- Login rate limiting
- Sensitive endpoint removal

## Security Pipeline

Every push to `main` and pull to `main` runs:

| Job | Role |
| --- | --- |
| Pytest | Application and security regression testing |
| Bandit | Python static security analysis |
| Pip-audit | Known Python dependency vulnerability detection |
| Docker and Trivy | Container build verification and HIGH/CRITICAL vulnerability scanning |

The pipeline prevents changes from accidentally or silently reintroducing known vulnerabilities or shipping dangerous dependency and container findings.

## Documentation

- [Project scope](docs/project-scope.md)
- [Architecture and threat model](docs/architecture-threat-model.md)
- [Penetration-test report](docs/pentest-report.md)
- [Demonstration and reproduction guide](docs/demo-guide.md)
- [Vulnerability documentation](docs/vulnerabilities/)
- [Proof-of-concept scripts](pocs/)

## Repository Structure

```text
app/                         Flask application
docs/                        Scope, threat model, report, and findings
docs/evidence/               Local vulnerability evidence
docs/vulnerabilities/        Detailed vulnerability write ups
pocs/                        Local Python proof of concept scripts
tests/                       Application and security regression tests
.github/workflows/           Automated security pipeline
Dockerfile                   Container image definition
compose.yaml                 Local and isolated environment
```

## Safe Use and Bounds

VulnLab is meant to be education and for local use. The vulnerable version can not be publicly deployed. The PoC scripts use localhost targets with fake data. No real credentials, personal information, secrets, or external systems are used.

Only the remediated / secure version can be used for deployment.

## License

This project is available under the [MIT License](LICENSE).
