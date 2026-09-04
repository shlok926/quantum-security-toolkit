from collections.abc import Callable
from typing import Any

import numpy as np

from qst.analytics.security_analytics import SecurityAnalytics
from qst.core.bb84_protocol import BB84Protocol
from qst.core.protocol_interface import ProtocolInterface
from qst.exceptions import QSTError, SimulationError, ValidationError
from qst.orchestration.results import SimulationResult

# Planned reference shape: dict-based registry
PROTOCOL_REGISTRY: dict[str, type[ProtocolInterface]] = {
    "bb84": BB84Protocol,
}


class SimulationOrchestrator:
    """
    Coordinates simulation runs across protocol, attack, and analytics modules.
    Reference: specs/SIMULATION_SPEC.md
    """

    def __init__(self, protocol_name: str = "bb84", **kwargs):
        if protocol_name not in PROTOCOL_REGISTRY:
            raise ValidationError(f"Unknown protocol: {protocol_name}")
        self.protocol_name = protocol_name
        self.protocol_kwargs = kwargs

    def run(
        self,
        n_qubits: int,
        seed: int | None = None,
        eve_intercept_probability: float = 0.0,
        callbacks: dict[str, Callable[..., None]] | None = None,
    ) -> SimulationResult:
        """
        Run a single simulation trial.
        """
        # Validate parameters (FR-13)
        if not isinstance(n_qubits, int) or n_qubits <= 0:
            raise ValidationError("n_qubits must be a positive integer")
        if not (0.0 <= eve_intercept_probability <= 1.0):
            raise ValidationError(
                "eve_intercept_probability must be between 0.0 and 1.0"
            )

        # Determine a seed if none provided to ensure we can track it
        if seed is None:
            seed = np.random.SeedSequence().entropy

        warnings = []

        # Construct Protocol (step 2)
        try:
            protocol_cls = PROTOCOL_REGISTRY[self.protocol_name]
            protocol = protocol_cls(
                eve_intercept_probability=eve_intercept_probability,
                **self.protocol_kwargs,
            )
        except Exception as e:
            raise SimulationError(f"Failed to instantiate protocol: {e}") from e

        # Execute protocol
        try:
            protocol_result = protocol.run_key_exchange(
                n_qubits=n_qubits, seed=seed, callbacks=callbacks
            )
        except Exception as e:
            raise SimulationError(f"Simulation backend failed: {e}") from e

        # Security Analytics
        analytics = SecurityAnalytics(protocol_result.rng)

        # We need to extract the sifted keys for Alice and Bob
        # In BB84, Bob's bits were collected in protocol_result.sifted_key.
        # Let's rebuild Alice's sifted bits from protocol_result
        alice_sifted = [
            protocol_result.alice_bits[i] for i in protocol_result.sifted_indices
        ]
        bob_sifted = protocol_result.sifted_key

        qber, alice_final, bob_final = analytics.compute_qber(alice_sifted, bob_sifted)

        if (
            callbacks
            and "on_qber_estimated" in callbacks
            and callbacks["on_qber_estimated"] is not None
        ):
            callbacks["on_qber_estimated"](qber)

        final_key_length = len(alice_final)
        key_rate = analytics.compute_key_rate(final_key_length, n_qubits)

        if (
            callbacks
            and "on_key_finalized" in callbacks
            and callbacks["on_key_finalized"] is not None
        ):
            callbacks["on_key_finalized"](alice_final)

        if final_key_length == 0:
            warnings.append(
                "No bits survived sifting and sampling — try a larger qubit count"
            )

        sifted_mask = [False] * n_qubits
        for idx in protocol_result.sifted_indices:
            sifted_mask[idx] = True

        return SimulationResult(
            qber=qber if qber is not None else 0.0,
            final_key_length=final_key_length,
            key_rate=key_rate,
            sifted_key=bob_final,
            n_qubits=n_qubits,
            seed=seed,
            eve_intercept_probability=eve_intercept_probability,
            warnings=warnings,
            metadata={},
            alice_bits=protocol_result.alice_bits,
            alice_bases=protocol_result.alice_bases,
            bob_bases=protocol_result.bob_bases,
            bob_bits=protocol_result.bob_bits,
            sifted_mask=sifted_mask,
        )

    def run_research_batch(
        self, param_sweep: list[dict[str, Any]], on_error: str = "continue"
    ) -> list[SimulationResult]:
        """
        Run a batch of simulations for research parameter sweeps.

        Args:
            param_sweep: List of parameter dictionaries for each run.
            on_error: Policy for handling errors ("continue" or "abort").

        Returns:
            List of SimulationResult objects.
        """
        results = []
        for params in param_sweep:
            try:
                results.append(self.run(**params))
            except QSTError as e:
                if on_error == "abort":
                    raise
                # Create an error result
                results.append(
                    SimulationResult(
                        qber=0.0,
                        final_key_length=0,
                        key_rate=0.0,
                        sifted_key=[],
                        n_qubits=params.get("n_qubits", 0),
                        seed=params.get("seed", 0),
                        eve_intercept_probability=params.get(
                            "eve_intercept_probability", 0.0
                        ),
                        warnings=[f"Run failed: {str(e)}"],
                        metadata={"error": str(e)},
                    )
                )
        return results
