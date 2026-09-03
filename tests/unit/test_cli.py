import sys
from unittest.mock import patch

import pytest

from qst.cli.main import main


def test_cli_simulate_invalid_qubits(capsys):
    test_args = ["qst", "simulate", "--qubits", "-5"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "ValidationError [QST-VAL-001]" in captured.err


@patch("qst.cli.main.write_export")
@patch("qst.orchestration.SimulationOrchestrator.run_research_batch")
def test_cli_batch_range_parsing(mock_run, mock_export):
    test_args = [
        "qst",
        "batch",
        "--qubits",
        "10",
        "--eve-prob-range",
        "0.0:1.0:0.25",
        "--output",
        "out.json",
        "--format",
        "json",
    ]
    with patch.object(sys, "argv", test_args):
        main()

    # Check that it generated 5 sweep points
    mock_run.assert_called_once()
    param_sweep = mock_run.call_args[0][0]

    assert len(param_sweep) == 5
    probs = [p["eve_intercept_probability"] for p in param_sweep]
    assert probs == [0.0, 0.25, 0.5, 0.75, 1.0]


def test_cli_version(capsys):
    test_args = ["qst", "--version"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "QST" in captured.out
    assert "Qiskit" in captured.out
