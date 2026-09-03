# Golden Dataset

The `dataset.json` in this directory is a correctness test, not a snapshot. The values within it were manually derived by tracing the `numpy.random.Generator` behavior according to the BB84 specification.

## Derivation Method

We initialize a `numpy.random.Generator` with seed `42` and `n_qubits = 20`.

The exact consumption order of the RNG by the protocol is:
1. `alice_bits` (1 call to `rng.integers(0, 2, size=20)`)
2. `alice_bases` (20 calls to `rng.random()`)
3. **If Eve is present:**
   - Interception choice (20 calls to `rng.random()`)
   - `eve_bases` (20 calls to `rng.random()`)
   - Qiskit Simulator Seeds for Eve (20 calls to `rng.integers(0, 2**31 - 1)`)
4. `bob_bases` (20 calls to `rng.random()`)
5. Qiskit Simulator Seeds for Bob (20 calls to `rng.integers(0, 2**31 - 1)`)
6. QBER Sample Indices (1 call to `rng.choice(...)`)

By running this sequence without invoking any QST classes, we manually compute the exact bit/basis sequences, and then emulate the Qiskit measurement logically or via direct Qiskit Aer calls (passing the exact derived simulator seeds). We then verified that the exact sifted keys, QBER, and final key length align flawlessly with the values stored in `dataset.json`.

This confirms the simulation is correct and deterministically adheres to the PRNG sequence defined by the architectural specs.
