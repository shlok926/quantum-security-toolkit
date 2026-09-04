import matplotlib.pyplot as plt

from qst.orchestration.results import SimulationResult


class Visualizer:
    """
    Visualization tools for QST simulations.
    Reference: specs/VISUALIZATION_SPEC.md
    """

    # Truncation threshold for the basis table to avoid excessive CLI output
    MAX_ROWS = 20

    @classmethod
    def render_basis_table(cls, result: SimulationResult) -> str:
        """
        Render a text-based table showing per-qubit basis match/mismatch.
        """
        lines = []
        lines.append("=== Qubit Measurement Basis Table ===")
        lines.append(
            f"{'Qubit':<8} | {'Alice Basis':<13} | {'Bob Basis':<11} | {'Match?':<8} | {'Alice Bit':<11} | {'Bob Bit':<9}"
        )
        lines.append("-" * 75)

        n_display = min(result.n_qubits, cls.MAX_ROWS)
        for i in range(n_display):
            a_basis = result.alice_bases[i] if i < len(result.alice_bases) else "-"
            b_basis = result.bob_bases[i] if i < len(result.bob_bases) else "-"
            a_bit = str(result.alice_bits[i]) if i < len(result.alice_bits) else "-"
            b_bit = str(result.bob_bits[i]) if i < len(result.bob_bits) else "-"
            match = (
                "Yes" if i < len(result.sifted_mask) and result.sifted_mask[i] else "No"
            )

            lines.append(
                f"{i:<8} | {a_basis:<13} | {b_basis:<11} | {match:<8} | {a_bit:<11} | {b_bit:<9}"
            )

        if result.n_qubits > cls.MAX_ROWS:
            lines.append(f"... {result.n_qubits - cls.MAX_ROWS} more rows")

        return "\n".join(lines)

    @classmethod
    def plot_qber_vs_interception(cls, results: list[SimulationResult]):
        """
        Plot QBER vs. Eve Interception Probability.
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Sort results by x-axis to ensure line plots connect properly
        sorted_results = sorted(results, key=lambda r: r.eve_intercept_probability)

        x_vals = [r.eve_intercept_probability for r in sorted_results]
        y_vals = [r.qber * 100 for r in sorted_results]

        ax.scatter(x_vals, y_vals, label="Empirical QBER", color="blue", marker="o")
        ax.plot(x_vals, y_vals, color="blue", alpha=0.5)

        # Theoretical reference line: QBER = 25% * interception_prob
        theoretical_y = [25.0 * x for x in x_vals]
        ax.plot(
            x_vals,
            theoretical_y,
            label="Theoretical Reference (~25% at 1.0) [Illustrative]",
            color="gray",
            linestyle="--",
        )

        ax.set_title("QBER vs. Eve Interception Probability")
        ax.set_xlabel("Interception Probability (0.0–1.0)")
        ax.set_ylabel("QBER (%)")

        # Accessibility: text annotation for pass/fail interpretation
        ax.text(
            0.02,
            0.98,
            "Note: High QBER indicates potential eavesdropping.",
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white"),
        )

        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower right")

        return fig
