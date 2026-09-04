import argparse
import csv
import importlib.metadata
import json
import sys
from dataclasses import asdict
from pathlib import Path

import qiskit

from qst.exceptions import ExportError, SimulationError, ValidationError
from qst.orchestration import SimulationOrchestrator, SimulationResult


def get_version():
    try:
        return importlib.metadata.version("quantum-security-toolkit")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0-dev"


def write_export(
    results: list[SimulationResult], path: str, fmt: str, include_key: bool
):
    try:
        out_path = Path(path)

        # Prepare data
        def prepare_dict(res: SimulationResult) -> dict:
            d = asdict(res)
            if not include_key:
                d.pop("sifted_key", None)
            return d

        data = [prepare_dict(r) for r in results]

        if fmt == "json":
            out_data = (
                data[0] if len(data) == 1 else {"run_count": len(data), "results": data}
            )
            with open(out_path, "w") as f:
                json.dump(out_data, f, indent=2)
        elif fmt == "csv":
            with open(out_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "run_index",
                        "n_qubits",
                        "seed",
                        "eve_intercept_probability",
                        "qber",
                        "final_key_length",
                        "key_rate",
                        "warnings",
                    ]
                )
                for idx, r in enumerate(data):
                    warnings_str = ";".join(r["warnings"]) if r["warnings"] else ""
                    writer.writerow(
                        [
                            idx,
                            r["n_qubits"],
                            r["seed"],
                            r["eve_intercept_probability"],
                            r["qber"],
                            r["final_key_length"],
                            r["key_rate"],
                            warnings_str,
                        ]
                    )
    except Exception as e:
        raise ExportError(f"Failed to export to {path}: {str(e)}") from e


def build_parser():
    parser = argparse.ArgumentParser(
        prog="qst", description="Quantum Security Toolkit CLI"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"QST {get_version()} (Qiskit {qiskit.__version__})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # simulate
    sim_parser = subparsers.add_parser("simulate", help="Run a single BB84 simulation")
    sim_parser.add_argument(
        "--qubits", type=int, required=True, help="Number of qubits"
    )
    sim_parser.add_argument("--seed", type=int, default=None, help="Random seed")
    sim_parser.add_argument(
        "--eve-prob",
        type=float,
        default=0.0,
        help="Eavesdropper interception probability",
    )
    sim_parser.add_argument(
        "--mode",
        choices=["educational", "research"],
        default="educational",
        help="Narration vs quiet behavior",
    )
    sim_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save visual output (plots)",
    )
    sim_parser.add_argument(
        "--output", type=str, default=None, help="Export path (data)"
    )
    sim_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Export format"
    )
    sim_parser.add_argument(
        "--include-key", action="store_true", help="Include full sifted_key in export"
    )
    sim_parser.add_argument("--quiet", action="store_true", help="Suppress narration")

    # batch
    batch_parser = subparsers.add_parser(
        "batch", help="Run a parameter-sweep batch simulation"
    )
    batch_parser.add_argument(
        "--qubits", type=int, required=True, help="Number of qubits"
    )
    batch_parser.add_argument(
        "--eve-prob-range", type=str, required=True, help="Range start:stop:step"
    )
    batch_parser.add_argument("--seed", type=int, default=None, help="Random seed")
    batch_parser.add_argument(
        "--output", type=str, required=True, help="Export path (data)"
    )
    batch_parser.add_argument(
        "--format", choices=["json", "csv"], default="csv", help="Export format"
    )
    batch_parser.add_argument(
        "--on-error",
        choices=["continue", "abort"],
        default="continue",
        help="Error handling policy",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Import Visualizer lazily to prevent matplotlib overhead for non-visual commands
    try:
        from qst.visualization.visualizer import Visualizer

        has_viz = True
    except ImportError:
        has_viz = False

    try:
        orchestrator = SimulationOrchestrator()

        if args.command == "simulate":
            # Callbacks setup
            callbacks = {}
            if args.mode == "educational" and not args.quiet:

                def p(msg):
                    print(msg)

                callbacks = {
                    "on_bits_generated": lambda bits, bases: p(
                        "Alice generated bits and bases."
                    ),
                    "on_qubits_prepared": lambda: p("Alice prepared qubits."),
                    "on_eve_intercepted": lambda bits, bases: p(
                        "Eve intercepted some qubits!"
                    ),
                    "on_measured": lambda bits, bases: p(
                        "Bob measured the received qubits."
                    ),
                    "on_sifted": lambda key, idxs: p(
                        f"Sifting complete. Sifted key length: {len(key)}"
                    ),
                    "on_qber_estimated": lambda qber: p(
                        f"QBER estimated at {qber:.2%}"
                    ),
                    "on_key_finalized": lambda key: p(
                        f"Key finalized. Length: {len(key)}"
                    ),
                }

            result = orchestrator.run(
                n_qubits=args.qubits,
                seed=args.seed,
                eve_intercept_probability=args.eve_prob,
                callbacks=callbacks,
            )

            if not args.quiet and args.mode == "educational":
                if has_viz:
                    print("\n" + Visualizer.render_basis_table(result) + "\n")
                print(
                    f"Summary: QBER={result.qber:.2%}, Final Key Length={result.final_key_length}, Key Rate={result.key_rate:.2f}"
                )
            elif args.mode == "research" or args.quiet:
                if not args.output:
                    print(
                        f"Summary: QBER={result.qber:.2%}, Final Key Length={result.final_key_length}, Key Rate={result.key_rate:.2f}"
                    )

            if args.output_dir and has_viz:
                out_path = Path(args.output_dir)
                out_path.mkdir(parents=True, exist_ok=True)
                fig = Visualizer.plot_qber_vs_interception([result])
                fig.savefig(out_path / "qber_plot.png")
                print(f"Plot saved to {out_path / 'qber_plot.png'}")

            if args.output:
                write_export([result], args.output, args.format, args.include_key)

        elif args.command == "batch":
            try:
                parts = args.eve_prob_range.split(":")
                if len(parts) != 3:
                    raise ValueError("eve-prob-range must be start:stop:step")
                start, stop, step = map(float, parts)
            except Exception as e:
                raise ValidationError(f"Invalid eve-prob-range: {e}") from e

            # Parse eve_prob_range correctly
            count = int(round((stop - start) / step)) + 1
            eve_probs = [start + i * step for i in range(count)]

            param_sweep = [
                {
                    "n_qubits": args.qubits,
                    "seed": args.seed,
                    "eve_intercept_probability": p,
                }
                for p in eve_probs
            ]

            results = orchestrator.run_research_batch(
                param_sweep, on_error=args.on_error
            )
            write_export(results, args.output, args.format, include_key=False)

    except ValidationError as e:
        print(f"ValidationError [{e.code}]: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except SimulationError as e:
        print(f"SimulationError [{e.code}]: {str(e)}", file=sys.stderr)
        sys.exit(2)
    except ExportError as e:
        print(f"ExportError [{e.code}]: {str(e)}", file=sys.stderr)
        sys.exit(3)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
