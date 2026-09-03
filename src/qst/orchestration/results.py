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
