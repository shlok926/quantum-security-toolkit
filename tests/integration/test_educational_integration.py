import subprocess
import sys
from pathlib import Path


def test_cli_simulate_educational_end_to_end(tmp_path: Path):
    """
    Test that the CLI 'simulate --mode educational' runs successfully,
    prints the narration hooks, prints the basis table, and optionally saves
    the plot if --output-dir is given.
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
        "--output-dir",
        str(out_dir),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0

    # Narration hooks
    assert "Alice generated bits and bases." in result.stdout
    assert "Alice prepared qubits." in result.stdout
    assert "Bob measured the received qubits." in result.stdout
    assert "Sifting complete." in result.stdout
    assert "QBER estimated" in result.stdout
    assert "Key finalized." in result.stdout

    # Visualizer table output
    assert "=== Qubit Measurement Basis Table ===" in result.stdout
    assert "Match?" in result.stdout

    # Check if plot was saved
    assert out_dir.exists()
    assert (out_dir / "qber_plot.png").exists()
