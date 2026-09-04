import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("eve_prob", [0.0, 1.0])
def test_cli_simulate_educational_end_to_end(tmp_path: Path, eve_prob: float):
    """
    Test that the CLI 'simulate --mode educational' runs successfully,
    prints the narration hooks IN THE CORRECT ORDER (SIMULATION_SPEC.md §5),
    prints the basis table, and optionally saves the plot.
    """
    out_dir = tmp_path / "viz_out"

    cmd = [
        sys.executable,
        "-m",
        "qst.cli.main",
        "simulate",
        "--qubits",
        "10",
        "--mode",
        "educational",
        "--eve-prob",
        str(eve_prob),
        "--output-dir",
        str(out_dir),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0

    # Expected hook order
    expected_order = [
        "Alice generated bits and bases.",
        "Alice prepared qubits.",
    ]
    if eve_prob > 0.0:
        expected_order.append("Eve intercepted some qubits!")

    expected_order.extend(
        [
            "Bob measured the received qubits.",
            "Sifting complete.",
            "QBER estimated",
            "Key finalized.",
        ]
    )

    last_idx = -1
    for msg in expected_order:
        idx = result.stdout.find(msg)
        assert idx != -1, f"Missing narration: '{msg}'"
        assert idx > last_idx, f"Narration '{msg}' appeared out of order!"
        last_idx = idx

    # Visualizer table output
    assert "=== Qubit Measurement Basis Table ===" in result.stdout
    assert "Match?" in result.stdout

    # Check if plot was saved
    assert out_dir.exists()
    assert (out_dir / "qber_plot.png").exists()
