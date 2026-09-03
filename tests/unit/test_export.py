import csv
import json
import os

import pytest

from qst.cli.main import write_export
from qst.exceptions import ExportError
from qst.orchestration import SimulationResult


def test_json_export(tmp_path):
    result = SimulationResult(
        qber=0.05,
        final_key_length=100,
        key_rate=0.5,
        sifted_key=[0, 1, 0, 1],
        n_qubits=200,
        seed=42,
        eve_intercept_probability=0.0,
        warnings=[],
    )

    out_file = tmp_path / "out.json"
    write_export([result], str(out_file), "json", include_key=False)

    with open(out_file) as f:
        data = json.load(f)

    assert data["qber"] == 0.05
    assert "sifted_key" not in data


def test_csv_export(tmp_path):
    result1 = SimulationResult(
        qber=0.05,
        final_key_length=100,
        key_rate=0.5,
        sifted_key=[0, 1],
        n_qubits=200,
        seed=42,
        eve_intercept_probability=0.0,
        warnings=["Test warning"],
    )
    result2 = SimulationResult(
        qber=0.10,
        final_key_length=90,
        key_rate=0.45,
        sifted_key=[1, 1],
        n_qubits=200,
        seed=43,
        eve_intercept_probability=0.1,
        warnings=[],
    )

    out_file = tmp_path / "out.csv"
    write_export([result1, result2], str(out_file), "csv", include_key=False)

    with open(out_file, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert len(rows) == 3  # header + 2 rows
    assert rows[0] == [
        "run_index",
        "n_qubits",
        "seed",
        "eve_intercept_probability",
        "qber",
        "final_key_length",
        "key_rate",
        "warnings",
    ]
    assert rows[1][0] == "0"
    assert rows[1][4] == "0.05"
    assert rows[1][7] == "Test warning"
    assert rows[2][0] == "1"
    assert rows[2][4] == "0.1"


def test_export_failure():
    result = SimulationResult(
        qber=0.0,
        final_key_length=0,
        key_rate=0.0,
        sifted_key=[],
        n_qubits=0,
        seed=0,
        eve_intercept_probability=0.0,
        warnings=[],
    )

    # Trying to export to a directory should raise an ExportError
    if os.name == "nt":
        bad_path = "C:\\Windows\\System32\\this_should_fail.json"  # No permissions
    else:
        bad_path = "/root/this_should_fail.json"

    with pytest.raises(ExportError):
        write_export([result], bad_path, "json", include_key=False)
