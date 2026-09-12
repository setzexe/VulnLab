# VulnLab

A deliberately vulnerable Flask application demonstrating security testing, remediation, and DevSecOps workflows.

## Development code for running

```docker compose up -d``` to run the app.

Open localhost at port 5000.

```docker compose up -d --build``` after changing python code.

```docker compose run --rm vulnlab pytest -v -p no:cacheprovider``` to run tests.

```docker compose exec vulnlab flask --app run init-db``` to initialize the database when neccesary (to reset or make a new one)

```docker compose down``` to stop the app. Add ```-v``` to also delete the database.
