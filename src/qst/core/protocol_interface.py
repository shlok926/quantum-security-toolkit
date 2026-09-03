from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ProtocolRunData:
    """Raw output from a protocol run before analytics are applied."""

    alice_bits: list[int]
    alice_bases: list[str]
    bob_bits: list[int]
    bob_bases: list[str]
    sifted_key: list[int]
    sifted_indices: list[int]  # Keep track of which original qubits made it
    rng: Any  # np.random.Generator, passed out to share the same sequence


class ProtocolInterface(Protocol):
    """
    Interface for quantum key distribution protocols.

    # SPEC AMBIGUITY: docs/07_SYSTEM_ARCHITECTURE.md §8 specifies that ProtocolInterface
    # returns SimulationResult. However, returning SimulationResult (which includes QBER)
    # from core/ violates the dependency rule that core/ must not depend on analytics/
    # (which computes QBER), and SIMULATION_SPEC.md explicitly states Orchestrator collects
    # protocol output and passes it to SecurityAnalytics. I chose to return a `ProtocolRunData`
    # object from `run_key_exchange` and let Orchestrator assemble the final `SimulationResult`
    # using `SecurityAnalytics`.
    """

    def run_key_exchange(
        self, n_qubits: int, seed: int, callbacks: dict = None
    ) -> ProtocolRunData:
        """
        Run the key exchange protocol.

        Args:
            n_qubits: Number of qubits to simulate.
            seed: Seed for reproducibility.
            callbacks: Optional dictionary of callback functions for step boundaries.

        Returns:
            ProtocolRunData containing the raw key exchange outcome.
        """
        ...
