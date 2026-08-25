# Quantum Security Toolkit (QST)

> An open-source toolkit for simulating, visualizing, and teaching quantum-secure communication — centered on the BB84 Quantum Key Distribution protocol, with attack simulation and security analytics.

**Project status: Pre-Development / Phase 1 not yet started.** This repository currently contains a complete design and documentation suite (`docs/`, `specs/`) but no implementation code yet. See [`docs/01_REPOSITORY_AUDIT.md`](docs/01_REPOSITORY_AUDIT.md) for the honest current state, and [`docs/15_ROADMAP.md`](docs/15_ROADMAP.md) for what's next.

## What This Is

QST simulates the BB84 quantum key distribution protocol using [Qiskit](https://www.ibm.com/quantum/qiskit), including:

- The full BB84 key-exchange protocol (qubit prep, measurement, sifting, error estimation)
- An intercept-resend eavesdropper model — so you can *see* why quantum eavesdropping is detectable, not just be told it is
- Security analytics (QBER, key rate, detection probability)
- Visualization of basis tables and QBER-vs-eavesdropping-probability

Built for students, researchers, security engineers, and quantum developers — see [`docs/02_PRODUCT_BLUEPRINT.md`](docs/02_PRODUCT_BLUEPRINT.md) for the full product vision and personas.

## Documentation

This project is documentation-first: a 33-document suite (`docs/00`–`32`) and 6 implementation contracts (`specs/`) exist and were written *before* any code, so every implementation decision has a pre-agreed target. Start here:

| If you want to... | Read |
|---|---|
| Understand the project's mission and principles | [`docs/00_PROJECT_CONSTITUTION.md`](docs/00_PROJECT_CONSTITUTION.md) |
| See the current honest state of the repo | [`docs/01_REPOSITORY_AUDIT.md`](docs/01_REPOSITORY_AUDIT.md) |
| Understand the architecture | [`docs/07_SYSTEM_ARCHITECTURE.md`](docs/07_SYSTEM_ARCHITECTURE.md) |
| Understand the math behind BB84 | [`docs/22_MATHEMATICAL_FOUNDATION.md`](docs/22_MATHEMATICAL_FOUNDATION.md) |
| Look up any term | [`docs/26_PROJECT_GLOSSARY.md`](docs/26_PROJECT_GLOSSARY.md) |
| Implement a specific component | the matching file in [`specs/`](specs/) |
| Contribute | [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/27_CONTRIBUTOR_GUIDE.md`](docs/27_CONTRIBUTOR_GUIDE.md) |
| See what's planned vs. built | [`docs/15_ROADMAP.md`](docs/15_ROADMAP.md) and [`docs/21_DOCUMENTATION_QUALITY_REPORT.md`](docs/21_DOCUMENTATION_QUALITY_REPORT.md) |

## Installation (once Phase 1 ships)

```bash
pip install quantum-security-toolkit
```

Not yet published — see [`docs/19_RELEASE_PLAN.md`](docs/19_RELEASE_PLAN.md).

## Development Setup

```bash
git clone https://github.com/shlok926/quantum-security-toolkit.git
cd quantum-security-toolkit
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev,viz]"
pre-commit install           # optional but recommended, see .pre-commit-config.yaml
pytest
```

## Project Structure

```
quantum-security-toolkit/
├── docs/          # Full documentation suite (00-32)
├── specs/         # Implementation contracts (BB84, QBER, Simulation, Visualization, Export, CLI)
├── src/qst/       # Implementation (Phase 1 in progress -- see docs/15_ROADMAP.md)
├── tests/         # Unit, integration, golden-dataset tests
├── examples/      # Educational walkthroughs, notebooks
├── benchmarks/    # Performance benchmark results (docs/28_PERFORMANCE_BENCHMARK_PLAN.md)
└── .github/       # Issue/PR templates, CI workflows
```

## License

MIT — see [`LICENSE`](LICENSE). *(Suggested default; not yet formally ratified as an ADR — see note in `pyproject.toml`. Confirm before first public release.)*

## Security

Please see [`SECURITY.md`](SECURITY.md) for how to report vulnerabilities — do not open a public issue.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
