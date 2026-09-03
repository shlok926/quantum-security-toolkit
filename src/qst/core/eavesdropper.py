import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


class Eavesdropper:
    """
    Eavesdropper model implementing the intercept-resend attack.
    Reference: specs/BB84_SPEC.md §5
    """

    def __init__(self, intercept_probability: float, rng: np.random.Generator):
        self.intercept_probability = intercept_probability
        self.rng = rng
        self.simulator = AerSimulator()

    def intercept_and_resend(
        self, qubits: list[QuantumCircuit]
    ) -> tuple[list[QuantumCircuit], list[int | None], list[str | None]]:
        """
        Step E1-E5: For each qubit, randomly intercept, measure in random basis,
        and resend newly prepared qubit based on measurement outcome.

        Args:
            qubits: List of incoming QuantumCircuit objects from Alice.

        Returns:
            Tuple containing:
            - The list of forwarded QuantumCircuit objects to Bob.
            - List of Eve's bits (None if not intercepted).
            - List of Eve's bases (None if not intercepted).
        """
        forwarded_qubits = []
        eve_bits = []
        eve_bases = []

        for qc in qubits:
            # Step E1: Independent random choice to intercept
            if self.rng.random() < self.intercept_probability:
                # Step E2: Random basis
                basis = "X" if self.rng.random() < 0.5 else "Z"

                # Step E3: Measure the incoming qubit
                # Copy the circuit so we don't accidentally mutate the original in ways that break isolation
                intercepted_qc = qc.copy()

                # If X basis, apply H before measuring
                if basis == "X":
                    intercepted_qc.h(0)
                intercepted_qc.measure(0, 0)

                sim_seed = int(self.rng.integers(0, 2**31 - 1))
                result = self.simulator.run(
                    intercepted_qc, shots=1, seed_simulator=sim_seed
                ).result()
                counts = result.get_counts()
                # The bit string might look like "1" or "0"
                measured_bit_str = list(counts.keys())[0]
                # Qiskit sometimes returns bits with spaces depending on registers, but we have 1 classical bit
                measured_bit = int(measured_bit_str.strip())

                eve_bits.append(measured_bit)
                eve_bases.append(basis)

                # Step E4: Re-prepare NEW qubit based ONLY on Eve's outcome and basis
                new_qc = QuantumCircuit(1, 1)
                if measured_bit == 1:
                    new_qc.x(0)
                if basis == "X":
                    new_qc.h(0)

                forwarded_qubits.append(new_qc)
            else:
                # Step E5: Unmodified pass-through
                forwarded_qubits.append(qc)
                eve_bits.append(None)
                eve_bases.append(None)

        return forwarded_qubits, eve_bits, eve_bases
