# We need matplotlib for typing and assertions, but we should handle if it's missing (though it shouldn't be during tests since we added viz to optional dependencies, wait, we didn't add viz to testing environment? `pyproject.toml` says `viz` has `matplotlib>=3.8`. For testing, we probably have it installed, but let's just import it.)
import matplotlib.pyplot as plt

from qst.orchestration.results import SimulationResult
from qst.visualization.visualizer import Visualizer


def test_render_basis_table_truncation():
    # Test that render_basis_table truncates correctly when n_qubits > MAX_ROWS
    n_qubits = Visualizer.MAX_ROWS + 5
    result = SimulationResult(
        qber=0.0,
        final_key_length=n_qubits,
        key_rate=1.0,
        sifted_key=[1] * n_qubits,
        n_qubits=n_qubits,
        seed=1,
        eve_intercept_probability=0.0,
        alice_bits=[1] * n_qubits,
        alice_bases=["X"] * n_qubits,
        bob_bases=["X"] * n_qubits,
        bob_bits=[1] * n_qubits,
        sifted_mask=[True] * n_qubits,
    )

    table_output = Visualizer.render_basis_table(result)
    lines = table_output.split("\n")

    # Header is 3 lines. Data lines = MAX_ROWS. Truncation notice = 1 line.
    assert len(lines) == 3 + Visualizer.MAX_ROWS + 1
    assert "... 5 more rows" in lines[-1]


def test_render_basis_table_no_truncation():
    n_qubits = Visualizer.MAX_ROWS - 5
    result = SimulationResult(
        qber=0.0,
        final_key_length=n_qubits,
        key_rate=1.0,
        sifted_key=[1] * n_qubits,
        n_qubits=n_qubits,
        seed=1,
        eve_intercept_probability=0.0,
        alice_bits=[1] * n_qubits,
        alice_bases=["X"] * n_qubits,
        bob_bases=["X"] * n_qubits,
        bob_bits=[1] * n_qubits,
        sifted_mask=[True] * n_qubits,
    )

    table_output = Visualizer.render_basis_table(result)
    lines = table_output.split("\n")

    # Header is 3 lines. Data lines = n_qubits. No truncation notice.
    assert len(lines) == 3 + n_qubits
    assert "more rows" not in table_output


def test_plot_qber_vs_interception():
    results = [
        SimulationResult(
            qber=0.0,
            final_key_length=10,
            key_rate=1.0,
            sifted_key=[],
            n_qubits=10,
            seed=1,
            eve_intercept_probability=0.0,
        ),
        SimulationResult(
            qber=0.125,
            final_key_length=10,
            key_rate=1.0,
            sifted_key=[],
            n_qubits=10,
            seed=1,
            eve_intercept_probability=0.5,
        ),
        SimulationResult(
            qber=0.25,
            final_key_length=10,
            key_rate=1.0,
            sifted_key=[],
            n_qubits=10,
            seed=1,
            eve_intercept_probability=1.0,
        ),
    ]

    fig = Visualizer.plot_qber_vs_interception(results)

    # Check axes
    ax = fig.gca()

    # We plot two lines (empirical scatter, empirical line, theoretical line)
    # The first collection should be the scatter points
    scatter = ax.collections[0]
    offsets = scatter.get_offsets()

    assert len(offsets) == 3
    x_vals = [pt[0] for pt in offsets]
    assert x_vals == [0.0, 0.5, 1.0]

    plt.close(fig)


def test_visualizer_accessibility_labels():
    result = SimulationResult(
        qber=0.0,
        final_key_length=10,
        key_rate=1.0,
        sifted_key=[],
        n_qubits=10,
        seed=1,
        eve_intercept_probability=0.0,
    )
    fig = Visualizer.plot_qber_vs_interception([result])
    ax = fig.gca()

    # Titles and labels must be non-empty strings
    assert bool(ax.get_title().strip())
    assert bool(ax.get_xlabel().strip())
    assert bool(ax.get_ylabel().strip())

    # Text annotations must exist for color-independent communication
    assert len(ax.texts) > 0

    plt.close(fig)


def test_visualizer_handles_warnings_gracefully():
    # Test confirming no exception is raised for a warnings-flagged empty-key SimulationResult
    result = SimulationResult(
        qber=0.0,
        final_key_length=0,
        key_rate=0.0,
        sifted_key=[],
        n_qubits=10,
        seed=1,
        eve_intercept_probability=0.0,
        warnings=["No bits survived sifting"],
        alice_bits=[0] * 10,
        alice_bases=["X"] * 10,
        bob_bases=["Z"] * 10,
        bob_bits=[1] * 10,
        sifted_mask=[False] * 10,
    )

    # Should not raise
    table = Visualizer.render_basis_table(result)
    assert "No" in table  # Sifted mask is false everywhere

    fig = Visualizer.plot_qber_vs_interception([result])
    assert fig is not None
    plt.close(fig)
