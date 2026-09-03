from qst.core.bb84_protocol import BB84Protocol


def test_bit_basis_generation_length():
    protocol = BB84Protocol()
    result = protocol.run_key_exchange(10, 42)
    assert len(result.alice_bits) == 10
    assert len(result.alice_bases) == 10
    assert len(result.bob_bits) == 10
    assert len(result.bob_bases) == 10


def test_reproducibility_with_seed():
    p1 = BB84Protocol(eve_intercept_probability=0.5)
    r1 = p1.run_key_exchange(50, seed=123)

    p2 = BB84Protocol(eve_intercept_probability=0.5)
    r2 = p2.run_key_exchange(50, seed=123)

    assert r1.alice_bits == r2.alice_bits
    assert r1.alice_bases == r2.alice_bases
    assert r1.bob_bits == r2.bob_bits
    assert r1.bob_bases == r2.bob_bases
    assert r1.sifted_key == r2.sifted_key


def test_sifting_discards_mismatched_bases():
    protocol = BB84Protocol()
    result = protocol.run_key_exchange(20, seed=42)

    for i, original_index in enumerate(result.sifted_indices):
        assert result.alice_bases[original_index] == result.bob_bases[original_index]
        # In absence of Eve, the bits must perfectly match
        assert result.alice_bits[original_index] == result.bob_bits[original_index]
        assert result.sifted_key[i] == result.bob_bits[original_index]


def test_eve_interception_repreparation_correctness():
    # If Eve is 100%, she measures in a random basis and reprepares.
    # We can check that the sifted key has roughly 25% error compared to Alice's bits.
    protocol = BB84Protocol(eve_intercept_probability=1.0)
    result = protocol.run_key_exchange(200, seed=123)

    mismatches = 0
    for idx, bob_bit in zip(result.sifted_indices, result.sifted_key, strict=False):
        if bob_bit != result.alice_bits[idx]:
            mismatches += 1

    # QBER should be around 25%. We just check it's strictly > 0 and < 50% for this test.
    # The statistical check will be in test_qber_full_eve.
    assert mismatches > 0
    assert (mismatches / len(result.sifted_key)) < 0.5
