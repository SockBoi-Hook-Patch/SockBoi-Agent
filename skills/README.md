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

## Android Skills

- [ADB Android Device](adb-android-device/SKILL.md): bounded device inventory, package metadata, approved APK install/launch, bounded Logcat, and evidence collection.
- [Frida Android Runtime](frida-android-runtime/SKILL.md): approval-gated attach/spawn and reviewed, hash-pinned observation scripts with redacted evidence.

Both are playbooks and adapter contracts only. The current repository does not execute ADB or Frida commands. See [Android Dynamic Assessment](../docs/android-dynamic-assessment.md) for architecture and release gates.

## Current status
This repository contains starter playbooks. The runtime loader and automated Skill validation are planned.
