# SockBoi Agent Security Policy

## Supported release

The current developer preview is not suitable for production or exposure to untrusted networks. It has no authentication, authorization middleware for users, tenant isolation, durable storage, or scanner execution layer.

## Reporting

Please report suspected vulnerabilities privately through GitHub Security Advisories for this repository when enabled. Include affected version, reproduction steps, impact, and a safe proof of concept. Do not publish secrets or third-party data.

## Operational rules

- Only assess assets with explicit written authorization.
- Keep active checks behind human approval and a narrowly defined scope.
- Do not enable destructive, denial-of-service, credential theft, persistence, or unrestricted command execution.
- Do not store real credentials or customer evidence in source control.
