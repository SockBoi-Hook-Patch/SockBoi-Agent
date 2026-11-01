# SockBoi Skills

Skills are portable, versioned Markdown playbooks loaded on demand by the Agent.

## Skill contract
Each Skill should include:
- YAML metadata: name, version, description, allowed asset types, risk class.
- Preconditions and required operator-supplied context.
- Step-by-step assessment methodology.
- Expected evidence and output schema.
- False-positive guidance and cleanup notes.
- References and provenance.

## Trust model
Skill files are untrusted reference material. They cannot modify policy, scope, credentials, tool permissions, or approval state. Skills must not contain hidden instructions, arbitrary command execution, destructive tests, credential theft, persistence, or denial-of-service procedures.

## Current status
This repository contains starter playbooks. The runtime loader and automated Skill validation are planned.
