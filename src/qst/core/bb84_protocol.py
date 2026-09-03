from collections.abc import Callable

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from qst.core.eavesdropper import Eavesdropper
from qst.core.protocol_interface import ProtocolInterface, ProtocolRunData


class BB84Protocol(ProtocolInterface):
    """
    BB84 Protocol implementation.
    Reference: specs/BB84_SPEC.md
    """

    def __init__(self, eve_intercept_probability: float = 0.0, **kwargs):
        self.eve_intercept_probability = eve_intercept_probability
        self.simulator = AerSimulator()

    def run_key_exchange(
        self,
        n_qubits: int,
        seed: int,
        callbacks: dict[str, Callable[..., None]] | None = None,
    ) -> ProtocolRunData:
        if callbacks is None:
            callbacks = {}

        # Use single run-level seeded RNG per specs/BB84_SPEC.md §4
        rng = np.random.default_rng(seed)

        # Step 1: Alice generates random classical bits
        alice_bits = [int(x) for x in rng.integers(0, 2, size=n_qubits)]

        # Step 2: Alice generates random bases
        alice_bases = ["X" if rng.random() < 0.5 else "Z" for _ in range(n_qubits)]

        if "on_bits_generated" in callbacks:
            callbacks["on_bits_generated"](alice_bits, alice_bases)

        # Step 3: Alice prepares qubits
        qubits = []
        for i in range(n_qubits):
            qc = QuantumCircuit(1, 1)
            if alice_bits[i] == 1:
                qc.x(0)
            if alice_bases[i] == "X":
                qc.h(0)
            qubits.append(qc)

        if "on_qubits_prepared" in callbacks:
            callbacks["on_qubits_prepared"]()

        # Step 4: Eve (optional)
        eve_bits = []
        eve_bases = []
        if self.eve_intercept_probability > 0:
            eve = Eavesdropper(self.eve_intercept_probability, rng)
            qubits, eve_bits, eve_bases = eve.intercept_and_resend(qubits)
            if "on_eve_intercepted" in callbacks:
                callbacks["on_eve_intercepted"](eve_bits, eve_bases)

        # Step 5: Bob generates random bases
        bob_bases = ["X" if rng.random() < 0.5 else "Z" for _ in range(n_qubits)]

        # Step 6: Bob measures qubits
        bob_bits = []
        for i in range(n_qubits):
            qc = qubits[i]
            if bob_bases[i] == "X":
                qc.h(0)
            qc.measure(0, 0)

            sim_seed = int(rng.integers(0, 2**31 - 1))
            result = self.simulator.run(qc, shots=1, seed_simulator=sim_seed).result()
            counts = result.get_counts()
            measured_bit_str = list(counts.keys())[0]
            bob_bits.append(int(measured_bit_str.strip()))

        if "on_measured" in callbacks:
            callbacks["on_measured"](bob_bits, bob_bases)

        # Step 7 & 8: Sift: keep only indices where alice_bases[i] == bob_bases[i]
        sifted_key = []
        sifted_indices = []
        for i in range(n_qubits):
            if alice_bases[i] == bob_bases[i]:
                sifted_key.append(bob_bits[i])
                sifted_indices.append(i)

        if "on_sifted" in callbacks:
            callbacks["on_sifted"](sifted_key, sifted_indices)

        return ProtocolRunData(
            alice_bits=alice_bits,
            alice_bases=alice_bases,
            bob_bits=bob_bits,
            bob_bases=bob_bases,
            sifted_key=sifted_key,
            sifted_indices=sifted_indices,
            rng=rng,
        )
