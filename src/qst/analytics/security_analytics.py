import math

import numpy as np

# QBER_SPEC.md §2: "pick a reasonable, named-constant sample ratio — document your
# choice with a comment referencing specs/QBER_SPEC.md §2"
# We use 0.5 (half the sifted key) as a standard convention to balance accurate
# estimation with leaving enough bits for the final key.
QBER_SAMPLE_RATIO = 0.5


class SecurityAnalytics:
    """
    Security analytics for BB84 simulation.
    Reference: specs/QBER_SPEC.md
    """

    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def compute_qber(
        self, alice_sifted: list[int], bob_sifted: list[int]
    ) -> tuple[float | None, list[int], list[int]]:
        """
        Compute Quantum Bit Error Rate (QBER) from a random sample of the sifted key.
        Returns the QBER, the final Alice key (after removing sample), and final Bob key.

        Args:
            alice_sifted: Sifted bits from Alice.
            bob_sifted: Sifted bits from Bob.

        Returns:
            Tuple of (QBER, alice_final_key, bob_final_key)
        """
        m = len(alice_sifted)
        if m == 0:
            return None, [], []

        k = int(m * QBER_SAMPLE_RATIO)
        if k == 0:
            # QBER_SPEC.md §6 Numerical Edge Cases: k = 0 -> qber = None or 0.0
            return None, alice_sifted.copy(), bob_sifted.copy()

        # Select sample indices uniformly at random
        sample_indices = self.rng.choice(m, size=k, replace=False)
        sample_indices_set = set(sample_indices)

        mismatches = 0
        for i in sample_indices:
            if alice_sifted[i] != bob_sifted[i]:
                mismatches += 1

        qber = mismatches / k

        alice_final = [alice_sifted[i] for i in range(m) if i not in sample_indices_set]
        bob_final = [bob_sifted[i] for i in range(m) if i not in sample_indices_set]

        return qber, alice_final, bob_final

    def compute_key_rate(self, final_key_length: int, n_qubits: int) -> float:
        """
        Compute the key rate: final_key_length / n_qubits
        """
        if n_qubits == 0:
            return 0.0
        return final_key_length / n_qubits

    def detection_probability(
        self, qber: float, sample_size: int, noise_floor: float = 0.01
    ) -> float:
        """
        Compute the statistical confidence that the observed QBER indicates eavesdropping,
        using a one-sided binomial test against an assumed baseline noise floor.

        We calculate the p-value: probability of observing at least `mismatches` errors
        under the null hypothesis that the true error rate is `noise_floor`.
        The detection probability is 1 - p-value (confidence we reject the null).

        Args:
            qber: The observed QBER.
            sample_size: The number of bits sampled to estimate QBER.
            noise_floor: Expected QBER from natural channel noise (default 1%).

        Returns:
            Confidence level [0.0, 1.0] that eavesdropping occurred.
        """
        if sample_size == 0 or qber is None:
            return 0.0

        mismatches = int(round(qber * sample_size))

        # If observed error is <= noise_floor, we have 0 confidence it's an attacker
        if qber <= noise_floor:
            return 0.0

        # Compute binomial tail probability: P(X >= mismatches) where X ~ Binomial(sample_size, noise_floor)
        # Using math library to compute exactly or via normal approximation if sample_size is large.

        # To avoid overflow/excessive computation for large sample_size, use normal approximation
        if sample_size > 50:
            # Normal approximation: mu = n*p, sigma = sqrt(n*p*(1-p))
            mu = sample_size * noise_floor
            sigma = math.sqrt(sample_size * noise_floor * (1 - noise_floor))
            if sigma == 0:
                return 1.0
            # Z-score for mismatches (using continuity correction)
            z = (mismatches - 0.5 - mu) / sigma

            # math.erfc gives 2 * P(Z > z), so we divide by 2
            p_value = 0.5 * math.erfc(z / math.sqrt(2))
        else:
            # Exact binomial CDF complement
            p_value = 0.0
            for i in range(mismatches, sample_size + 1):
                prob = (
                    math.comb(sample_size, i)
                    * (noise_floor**i)
                    * ((1 - noise_floor) ** (sample_size - i))
                )
                p_value += prob

        return 1.0 - p_value
