from hypothesis import given, settings
from hypothesis.strategies import floats, integers

from qst.orchestration import SimulationOrchestrator


@given(
    n_qubits=integers(min_value=1, max_value=50),
    seed=integers(min_value=0, max_value=2**32 - 1),
    eve_prob=floats(min_value=0.0, max_value=1.0),
)
@settings(deadline=None, max_examples=20)
def test_simulation_properties(n_qubits, seed, eve_prob):
    orchestrator = SimulationOrchestrator()
    result = orchestrator.run(
        n_qubits=n_qubits, seed=seed, eve_intercept_probability=eve_prob
    )

    assert 0.0 <= result.qber <= 1.0
    assert result.final_key_length <= n_qubits
    assert 0.0 <= result.key_rate <= 1.0
