import numpy as np

from qst.analytics.security_analytics import SecurityAnalytics


def test_qber_sample_removal():
    rng = np.random.default_rng(42)
    analytics = SecurityAnalytics(rng)

    alice_sifted = [0, 1, 0, 1, 0, 1, 0, 1]
    bob_sifted = [0, 1, 0, 1, 0, 1, 0, 1]

    qber, alice_final, bob_final = analytics.compute_qber(alice_sifted, bob_sifted)

    # 50% of 8 is 4, so final length should be 4
    assert len(alice_final) == 4
    assert len(bob_final) == 4
    assert qber == 0.0


def test_empty_sifted_key_edge_case():
    rng = np.random.default_rng(42)
    analytics = SecurityAnalytics(rng)

    qber, alice_final, bob_final = analytics.compute_qber([], [])
    assert qber is None
    assert alice_final == []
    assert bob_final == []


def test_key_rate_calculation():
    rng = np.random.default_rng(42)
    analytics = SecurityAnalytics(rng)

    assert analytics.compute_key_rate(10, 100) == 0.1
    assert analytics.compute_key_rate(0, 100) == 0.0
    assert analytics.compute_key_rate(10, 0) == 0.0


def test_detection_probability():
    analytics = SecurityAnalytics(np.random.default_rng(42))

    # Clearly no eavesdropping: QBER matches noise floor
    assert analytics.detection_probability(0.01, 100, noise_floor=0.01) == 0.0

    # Boundary/edge cases
    assert analytics.detection_probability(None, 0) == 0.0
    assert analytics.detection_probability(0.25, 0) == 0.0
    assert analytics.detection_probability(0.25, 100, noise_floor=1.0) == 0.0

    # Clearly eavesdropping (small sample, exact binomial)
    prob_exact = analytics.detection_probability(0.25, 20, noise_floor=0.01)
    assert 0.99 < prob_exact <= 1.0  # highly confident

    # Clearly eavesdropping (large sample, normal approximation)
    prob_approx = analytics.detection_probability(0.25, 100, noise_floor=0.01)
    assert 0.999 < prob_approx <= 1.0  # extremely confident

    # Sigma zero edge case (noise_floor=0.0)
    assert analytics.detection_probability(0.25, 100, noise_floor=0.0) == 1.0
