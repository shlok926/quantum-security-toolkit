from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimulationResult:
    """The canonical return type for a QST simulation."""

    qber: float
    final_key_length: int
    key_rate: float
    sifted_key: list[int]
    n_qubits: int
    seed: int
    eve_intercept_probability: float
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Visualization contract fields (Phase 2)
    alice_bits: list[int] = field(default_factory=list)
    alice_bases: list[str] = field(default_factory=list)
    bob_bases: list[str] = field(default_factory=list)
    bob_bits: list[int] = field(default_factory=list)
    sifted_mask: list[bool] = field(default_factory=list)
