# VulnLab Architecture + Threat Model

## System Overview

VulnLab is a locally hosted Flask web application where users can create accounts, authenticate, and manage private notes. A basic administrator role provides access to administrative functions.

The application will intentionally contained four controlled vulnerabilities. Local PoC (proof of concept) scripts will demonstrate each vulnerability before the underlying cause is remediated and covered by automated regression tests via GitHub Actions.

## Components

- Web browser
  - Provides user interface + HTTPS request ability
- PoC scripts
  - Send controlled results that reproduce documented vulnerabilities
- Flask application
  - Handles routes, authentication, authorization, and application logic.
- SQLite database
  - Stores users, password hashes, roles, and private notes
- Docker environment
  - Packages and runs the application on the local machine

This application consists of one Flask service and one SQLite database. No seperate frontend, cloud services, microservices, etc. are necessarily for version one.

## Data Flow

A normal request follows this path:

- A user sends a request through the browser.
- Flask receives and processes the request.
- Flask checks the user’s authentication and authorization when required.
- Flask reads or modifies data in SQLite.
- Flask returns an HTTP response to the browser.

The proof-of-concept scripts follow the same route but send specially constructed requests designed to demonstrate the planned vulnerabilities.

## Important Assets

The main assets that VulnLab must protect are:

- User password hashes
- Authentication sessions
- The Flask secret key
- Private user notes
- Administrator privileges
- Database contents
- Application configuration
- Security logs and test evidence

## Entry Points

Entry points are locations where users / scripts can provide information to the application. Planned entry points include:

- User registration
- User login and logout
- Note creation
- Note viewing by ID
- Note searching
- Administrator routes
- Session cookies
- URL parameters and form data

Any information entering from these locations must initially be treated as untrusted.

## Planned Threats & Security Controls

| Scneario | Planned Weaknesses | Potential Impact | Final Security Control |
| --- | --- | --- | --- |
| SQL Injection | User input is inserted directly into an SQL Query | Unauthorized reading / modification of database data | Parameterized SQL queries |
| Broken access control / IDOR | A note is retrieved by ID without verifying its owner | One user accesses another user's private note | Server side ownership and role checks |
| Weak authentication | Login attempts or sessions are improperly protected | Account compromise or session abuse | Password hashing, login limiting, and secure session settings |
| Information exposure | Debug information or sensitive configuration is revealed | Internal application details can assist an attacker | Generic errors, disable debug mode, sanitize logs |

## Assumptions / Notes

- The vulnerable application only runs in an isolated local environmnet.
- All accounts and notes contain fictional test data.
- PoC scripts target only the local VulnLab environment.
- Users may attempt to access resources they do not own.
- The final ``` main ``` branch represents the remediated application.
- Only the remediated application will eventually be deployed.
