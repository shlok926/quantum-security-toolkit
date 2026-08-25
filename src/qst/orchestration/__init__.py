"""SimulationOrchestrator -- composition root wiring core, analytics,
and visualization into single/batch run entrypoints.

Implementation contract: specs/SIMULATION_SPEC.md
This is the only layer allowed to depend on qst.core, qst.analytics,
and qst.visualization together (docs/07_SYSTEM_ARCHITECTURE.md §7).
"""
