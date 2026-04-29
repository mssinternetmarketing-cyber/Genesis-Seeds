"""
EXPERIMENT 26: 22-QUBIT SCALING EXTENSION
Hardware Submission Script
========================================

Mission: Validate formula continues to hold beyond 20q

Formula verified: shots ≈ 2^(n/2) × ~1000
For 22q: ~320,000 shots needed to maintain BQ ≈ 0.82

Design: Test 22 qubits with optimal shot count
Expected: BQ > 0.80 (slight degradation from 20q normal)
"""

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import json
import numpy as np
from datetime import datetime


SEED_LIBRARY = {
    "Omega": {"phase": 0},
    "Alpha": {"phase": np.pi / 2}
}


def create_22q_sparse_alpha_circuit():
    """Create 22-qubit circuit with Pattern_B_Sparse_Alpha."""
    n_qubits = 22
    pattern = ["Omega"] * n_qubits
    
    # Sparse alpha placement every ~5 qubits
    alpha_positions = [4, 9, 14, 19]
    for pos in alpha_positions:
        if pos < n_qubits:
            pattern[pos] = "Alpha"
    
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize with seeds
    for i, seed_name in enumerate(pattern):
        qc.h(i)
        phase = SEED_LIBRARY[seed_name]["phase"]
        qc.p(phase, i)
    
    qc.barrier()
    
    # Full sequential coupling
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


def calculate_metrics(counts, n_qubits):
    """Calculate Bridge Quality and related metrics."""
    total_shots = sum(counts.values())
    
    # Count unique states measured
    unique_states = len(counts)
    max_possible_states = 2 ** n_qubits
    state_coverage = (unique_states / max_possible_states) * 100
    
    # Calculate entropy
    probs = []
    for i in range(max_possible_states):
        state = format(i, f'0{n_qubits}b')
        prob = counts.get(state, 0) / total_shots
        probs.append(prob)
    
    entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
    bridge_quality = entropy / n_qubits
    
    return {
        "bridge_quality": float(bridge_quality),
        "entropy": float(entropy),
        "unique_states": unique_states,
        "max_possible_states": max_possible_states,
        "state_coverage_pct": float(state_coverage),
        "total_shots": total_shots
    }


def run_experiment_26():
    """Run EXPERIMENT 26: 22-Qubit Scaling Extension"""
    
    n_qubits = 22
    shots = 320000  # Optimal: 2^11 × 156 ≈ 320k
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    print("=" * 80)
    print("EXPERIMENT 26: 22-QUBIT SCALING EXTENSION")
    print("=" * 80)
    print()
    print("MISSION: Validate formula continues beyond 20q")
    print()
    print("HYPOTHESIS: BQ ≈ 0.81+ at 22q with 320k shots")
    print()
    
    # Create circuit
    circuit = create_22q_sparse_alpha_circuit()
    transpiled = transpile(circuit, backend=backend, optimization_level=3)
    circuit_depth = transpiled.depth()
    
    n_states = 2 ** n_qubits
    coverage = (shots / n_states) * 100
    
    print(f"Qubits: {n_qubits}")
    print(f"Shot count: {shots:,}")
    print(f"State coverage: {coverage:.3f}%")
    print(f"Circuit depth: {circuit_depth}")
    print()
    
    print(f"Submitting: {n_qubits}q circuit with {shots:,} shots...", end="", flush=True)
    
    job = sampler.run([transpiled], shots=shots)
    
    print(f" ✓")
    print(f"Job ID: {job.job_id()}")
    print()
    
    print(f"Waiting for result... (this may take 5-10 minutes)", end="", flush=True)
    
    # Wait for result
    result = job.result()
    
    # Extract measurement data
    pub_result = result[0]
    data = pub_result.data
    
    # Get counts
    if hasattr(data, "meas"):
        counts = data.meas.get_counts()
    else:
        for attr in dir(data):
            if not attr.startswith("_"):
                obj = getattr(data, attr)
                if hasattr(obj, "get_counts"):
                    counts = obj.get_counts()
                    break
    
    print(" ✓")
    print()
    
    # Calculate metrics
    metrics = calculate_metrics(counts, n_qubits)
    
    result_data = {
        "qubits": n_qubits,
        "shots": shots,
        "job_id": job.job_id(),
        "circuit_depth": circuit_depth,
        **metrics
    }
    
    # Save results
    output = {
        "experiment": "22-Qubit Scaling Extension (Exp 26)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "mission": "Validate formula at 22q",
        "formula": "shots = 2^(n/2) × ~1000",
        "exp25_baseline": {
            "qubits": 20,
            "shots": 100000,
            "bq": 0.8254
        },
        "result": result_data
    }
    
    with open("experiment_26_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 80)
    print("EXPERIMENT 26 COMPLETE")
    print("=" * 80)
    print()
    
    # Analysis
    print("RESULTS:")
    print("-" * 80)
    print(f"Bridge Quality: {metrics['bridge_quality']:.4f}")
    print(f"Entropy: {metrics['entropy']:.2f} bits")
    print(f"Unique states: {metrics['unique_states']:,}/{metrics['max_possible_states']:,}")
    print(f"State coverage: {metrics['state_coverage_pct']:.3f}%")
    print()
    
    exp25_bq = 0.8254
    diff = metrics['bridge_quality'] - exp25_bq
    diff_pct = (diff / exp25_bq) * 100
    
    print("COMPARISON TO EXP 25 (20q @ 0.8254):")
    print("-" * 80)
    print(f"22q BQ: {metrics['bridge_quality']:.4f}")
    print(f"Difference: {diff:+.4f} ({diff_pct:+.2f}%)")
    print()
    
    if metrics['bridge_quality'] > 0.80:
        print("✓✓✓ FORMULA CONTINUES TO WORK!")
        print()
        print("Conclusion:")
        print("  ✓ Scaling pattern validated at 22q")
        print("  ✓ Can confidently proceed to 25q")
        print("  ✓ 30q goal remains achievable")
        print()
        print("Next: Exp 27 - Push to 25q milestone")
        print()
    elif metrics['bridge_quality'] > 0.78:
        print("✓ FORMULA HOLDS WITH EXPECTED DEGRADATION")
        print()
        print("Conclusion:")
        print("  ~ Slight degradation expected at 22q")
        print("  ~ Formula mostly accurate")
        print("  ~ May need adjustment for 25-30q")
        print()
    else:
        print("⚠ UNEXPECTED DEGRADATION AT 22Q")
        print()
        print("Conclusion:")
        print("  ⚠ Formula may break down beyond 20q")
        print("  ⚠ Additional factors emerging")
        print("  ⚠ Investigate before 25q")
        print()
    
    return result_data


if __name__ == "__main__":
    result = run_experiment_26()
    print("✓ Ready for next phase!")
