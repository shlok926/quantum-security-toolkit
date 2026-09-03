import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def predict(seed: int, n_qubits: int, eve_prob: float):
    rng = np.random.default_rng(seed)
    simulator = AerSimulator()
    
    alice_bits = [int(x) for x in rng.integers(0, 2, size=n_qubits)]
    alice_bases = ['X' if rng.random() < 0.5 else 'Z' for _ in range(n_qubits)]
    
    eve_bits = [None] * n_qubits
    eve_bases = [None] * n_qubits
    eve_seeds = [None] * n_qubits
    if eve_prob > 0.0:
        for i in range(n_qubits):
            if rng.random() < eve_prob:
                eve_bases[i] = 'X' if rng.random() < 0.5 else 'Z'
                eve_seeds[i] = int(rng.integers(0, 2**31 - 1))
                
    state_before_bob = rng.bit_generator.state['state']['state']
    
    bob_bases = ['X' if rng.random() < 0.5 else 'Z' for _ in range(n_qubits)]
    bob_seeds = [int(rng.integers(0, 2**31 - 1)) for _ in range(n_qubits)]
    
    bob_bits = []
    
    for i in range(n_qubits):
        qc = QuantumCircuit(1, 1)
        if alice_bits[i] == 1: qc.x(0)
        if alice_bases[i] == 'X': qc.h(0)
        
        if eve_bases[i] is not None:
            if eve_bases[i] == 'X': qc.h(0)
            qc.measure(0, 0)
            res = simulator.run(qc, shots=1, seed_simulator=eve_seeds[i]).result()
            measured = int(list(res.get_counts().keys())[0].strip())
            eve_bits[i] = measured
            
            qc = QuantumCircuit(1, 1)
            if measured == 1: qc.x(0)
            if eve_bases[i] == 'X': qc.h(0)
            
        if bob_bases[i] == 'X': qc.h(0)
        qc.measure(0, 0)
        res = simulator.run(qc, shots=1, seed_simulator=bob_seeds[i]).result()
        bob_bits.append(int(list(res.get_counts().keys())[0].strip()))
        
    alice_sifted = []
    bob_sifted = []
    sifted_indices = []
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            alice_sifted.append(alice_bits[i])
            bob_sifted.append(bob_bits[i])
            sifted_indices.append(i)
            
    if len(sifted_indices) > 0:
        sample_size = int(len(sifted_indices) * 0.5)
        sample_indices = rng.choice(len(sifted_indices), size=sample_size, replace=False)
    else:
        sample_indices = []
        
    mismatches = sum(1 for idx in sample_indices if alice_sifted[idx] != bob_sifted[idx])
    qber = mismatches / len(sample_indices) if len(sample_indices) > 0 else 0.0
    
    sample_set = set(sample_indices)
    final_key = [bob_sifted[i] for i in range(len(sifted_indices)) if i not in sample_set]
    
    return {
        "state_before_bob": state_before_bob,
        "sifted_key": bob_sifted,
        "final_key": final_key,
        "final_key_length": len(final_key),
        "qber": qber
    }

if __name__ == "__main__":
    print("=== PREDICTED (Eve = 0.0) ===")
    p0 = predict(42, 20, 0.0)
    print(p0)
    
    print("\n=== PREDICTED (Eve = 1.0) ===")
    p1 = predict(42, 20, 1.0)
    print(p1)
