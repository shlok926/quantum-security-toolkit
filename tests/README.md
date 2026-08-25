# Tests

- `unit/` -- fast, isolated tests (docs/14_TESTING_STRATEGY.md §3)
- `integration/` -- full SimulationOrchestrator.run() end-to-end tests (§4)
- `golden/` -- fixed-seed golden dataset regression tests (§8)

Minimum required unit tests before Phase 1 is "Done" (docs/00_PROJECT_CONSTITUTION.md §8)
are listed in docs/14_TESTING_STRATEGY.md §3 -- start there.

Critical: any change to qst.core.BB84Protocol or qst.core.Eavesdropper MUST
pass the regression tests tied to docs/11_SECURITY_ARCHITECTURE.md §4
before merge. These are blocking, not optional.
