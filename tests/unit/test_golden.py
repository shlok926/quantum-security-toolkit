import json
from dataclasses import asdict
from pathlib import Path

import pytest

from qst.orchestration import SimulationOrchestrator


@pytest.mark.golden
def test_golden_dataset():
    golden_path = Path(__file__).parent.parent / "golden" / "dataset.json"

    with open(golden_path) as f:
        expected_cases = json.load(f)

    orchestrator = SimulationOrchestrator()
    for expected in expected_cases:
        result = orchestrator.run(
            n_qubits=expected["n_qubits"],
            seed=expected["seed"],
            eve_intercept_probability=expected["eve_intercept_probability"],
        )

        result_dict = asdict(result)

        assert result_dict["qber"] == expected["qber"]
        assert result_dict["final_key_length"] == expected["final_key_length"]
        assert result_dict["key_rate"] == expected["key_rate"]
        assert result_dict["sifted_key"] == expected["sifted_key"]
        assert result_dict["warnings"] == expected["warnings"]
