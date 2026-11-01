# Changelog

## [0.3.1] - 2026-11-01

### Fixed
- Corrected the approval-binding regression test by including both test targets in the engagement's explicit scope. This allows the test to reach and verify the exact-target approval check instead of failing earlier at scope validation.

### Changed
- Bumped the package and runtime version from 0.3.0 to 0.3.1.

### Security
- No policy checks were weakened or bypassed. Targets must still be explicitly in scope, and active actions still require approval bound to the engagement, exact target, and technique.
