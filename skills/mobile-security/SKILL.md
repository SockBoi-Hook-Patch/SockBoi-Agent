---
name: mobile-application-review
version: 0.1.0
description: Review operator-provided mobile application packages and source/configuration evidence.
asset_types: [mobile_app, source_bundle]
risk: mixed
---

# Mobile Application Security Review

## Workflow
1. Confirm application identifier, platform, version, and test environment are authorized.
2. Review supplied source, manifest/plist, permissions, deep links, exported components, and network security configuration.
3. Review local data storage, cryptographic API usage, authentication/session handling, and certificate validation design.
4. Analyze static scan output and test evidence; distinguish static indicators from runtime-confirmed behavior.
5. Require explicit approval for dynamic tests against a live backend.

## Safety
Do not collect real user data, bypass device ownership controls, or test backend services outside scope.
