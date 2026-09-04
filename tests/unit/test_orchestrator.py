import pytest

from qst.exceptions import ValidationError
from qst.orchestration import SimulationOrchestrator


def test_invalid_parameter_validation():
    orchestrator = SimulationOrchestrator()
    with pytest.raises(ValidationError):
        orchestrator.run(n_qubits=-5)
    with pytest.raises(ValidationError):
        orchestrator.run(n_qubits=100, eve_intercept_probability=1.5)


def test_qber_zero_eve():
    orchestrator = SimulationOrchestrator()
    # Run multiple times to ensure QBER stays near 0 (simulator noise floor)
    for seed in range(5):
        result = orchestrator.run(
            n_qubits=100, seed=seed, eve_intercept_probability=0.0
        )
        assert result.qber == 0.0


@pytest.mark.critical
def test_qber_full_eve():
    orchestrator = SimulationOrchestrator()
    qbers = []
    # Run enough trials to get statistical confidence
    for seed in range(20):
        result = orchestrator.run(
            n_qubits=200, seed=seed, eve_intercept_probability=1.0
        )
        qbers.append(result.qber)

    mean_qber = sum(qbers) / len(qbers)
    # Theoretically ~25%. We check it falls between 20% and 30% for a reasonable N.
    assert 0.20 <= mean_qber <= 0.30


def test_callback_ordering():
    orchestrator = SimulationOrchestrator()

    order = []

    def on_bits_generated(bits, bases):
        order.append("bits")

    def on_qubits_prepared():
        order.append("prepared")

    def on_eve_intercepted(bits, bases):
        order.append("eve")

    def on_measured(bits, bases):
        order.append("measured")

    def on_sifted(key, indices):
        order.append("sifted")

    def on_qber_estimated(qber):
        order.append("qber")

    def on_key_finalized(key):
        order.append("key")

    callbacks = {
        "on_bits_generated": on_bits_generated,
        "on_qubits_prepared": on_qubits_prepared,
        "on_eve_intercepted": on_eve_intercepted,
        "on_measured": on_measured,
        "on_sifted": on_sifted,
        "on_qber_estimated": on_qber_estimated,
        "on_key_finalized": on_key_finalized,
    }

    orchestrator.run(
        n_qubits=10, seed=42, eve_intercept_probability=1.0, callbacks=callbacks
    )

    assert order == ["bits", "prepared", "eve", "measured", "sifted", "qber", "key"]


def test_batch_continuation():
    orchestrator = SimulationOrchestrator()

    param_sweep = [
        {"n_qubits": 10, "seed": 42},
        {"n_qubits": -5, "seed": 42},  # invalid
        {"n_qubits": 10, "seed": 43},
    ]

    results = orchestrator.run_research_batch(param_sweep, on_error="continue")

    assert len(results) == 3
    assert results[0].final_key_length > 0 or results[0].qber == 0.0
    assert results[1].final_key_length == 0
    assert "Run failed" in results[1].warnings[0]
    assert results[2].final_key_length > 0 or results[2].qber == 0.0


def test_result_schema_consistency():
    orchestrator = SimulationOrchestrator()
    result = orchestrator.run(n_qubits=50, seed=123, eve_intercept_probability=0.2)

    assert hasattr(result, "qber")
    assert hasattr(result, "final_key_length")
    assert hasattr(result, "key_rate")
    assert hasattr(result, "sifted_key")
    assert hasattr(result, "warnings")
    assert hasattr(result, "metadata")
    assert hasattr(result, "alice_bits")
    assert hasattr(result, "alice_bases")
    assert hasattr(result, "bob_bases")
    assert hasattr(result, "bob_bits")
    assert hasattr(result, "sifted_mask")

    assert isinstance(result.qber, float)
    assert isinstance(result.final_key_length, int)
    assert isinstance(result.key_rate, float)
    assert isinstance(result.sifted_key, list)
    assert isinstance(result.warnings, list)
    assert isinstance(result.metadata, dict)
    assert isinstance(result.alice_bits, list)
    assert isinstance(result.alice_bases, list)
    assert isinstance(result.bob_bases, list)
    assert isinstance(result.bob_bits, list)
    assert isinstance(result.sifted_mask, list)


def test_visualization_contract_fields():
    orchestrator = SimulationOrchestrator()
    n_qubits = 20
    result = orchestrator.run(
        n_qubits=n_qubits, seed=777, eve_intercept_probability=0.0
    )

    # Check that lengths match n_qubits exactly
    assert len(result.alice_bits) == n_qubits
    assert len(result.alice_bases) == n_qubits
    assert len(result.bob_bases) == n_qubits
    assert len(result.bob_bits) == n_qubits
    assert len(result.sifted_mask) == n_qubits

    # Check exact types to ensure no silent conversions (e.g. bases remain strings)
    assert all(isinstance(b, int) for b in result.alice_bits)
    assert all(isinstance(b, str) for b in result.alice_bases)
    assert all(isinstance(b, str) for b in result.bob_bases)
    assert all(isinstance(b, int) for b in result.bob_bits)
    assert all(isinstance(m, bool) for m in result.sifted_mask)

    # Verify the sifted_mask correctly flags matches between Alice and Bob's bases
    for i in range(n_qubits):
        expected_match = result.alice_bases[i] == result.bob_bases[i]
        assert result.sifted_mask[i] == expected_match
