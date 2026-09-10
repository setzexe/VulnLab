# VulnLab Project Scope

## Purpose

VulnLab is a controlled application-security project meant to demonstrate the complete process of building a web application, identifying vulnerabilities, exploiting them locally, remediating their root causes, and preventing them from returning through automated testing. 

The project follows this path of development:

Build --> Attack --> Fix --> Automate --> Deploy

## Scope for Version 1

VulnLab v1 will include:

- A small Python Flask application
- User registration + authentication
- Basic administration role
- SQLite database
- A reproducable local Docker environment
- Four vulnerability scenarios:
    - SQL Injection
    - Broken access control / IDOR
    - Weak authentication
    - Information exposure
- Local Python PoC (proof of concept) scripts
- Secure remediations for each vulnerability
- Automated regression tests
- A GitHub Actions security pipeline
- A penetration testing report
- Clear setup and reproduction instructions

## Out of Scope / For Further Update

Version 1 will not include:

- Public deployment for the vulnerable application
- Real users, credentials, or production data
- A complex / highly polished frontend
- Cloud infrastructure or microservices
- Vulnerabilities beyond the four planned ones

## Safety Boundary

The vulnerable application and proof-of-concept scripts are intended exclusively for an isolated local environment owned and managed by the developer. 

The vulnerable version will not be deployed. No real credentials, personal information, API keys,  or other secrets will be stored in the repository. 


