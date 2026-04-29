"""
EXPERIMENT 28: 28-QUBIT SCALING VALIDATION
Hardware Submission Script
========================================

Mission: Validate degradation pattern continues smoothly to 28q

Formula: shots ≈ 2^(n/2) × ~1000
For 28q: ~3,200,000 shots (3.2M)

Design: Test 28 qubits with optimal shot count
Expected: BQ > 0.77 (confirms formula holds to 28q)
Impact: De-risks 30q final push
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


def create_28q_sparse_alpha_circuit():
    """Create 28-qubit circuit with Pattern_B_Sparse_Alpha."""
    n_qubits = 28
    pattern = ["Omega"] * n_qubits
    
    # Sparse alpha placement
    alpha_positions = [4, 9, 14, 19, 24]
    for pos in alpha_positions:
        if pos < n_qubits:
            pattern[pos] = "Alpha"
    
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    for i, seed_name in enumerate(pattern):
        qc.h(i)
        phase = SEED_LIBRARY[seed_name]["phase"]
        qc.p(phase, i)
    
    qc.barrier()
    
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


def calculate_metrics(counts, n_qubits):
    """Calculate Bridge Quality and related metrics."""
    total_shots = sum(counts.values())
    
    unique_states = len(counts)
    max_possible_states = 2 ** n_qubits
    state_coverage = (unique_states / max_possible_states) * 100
    
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


def run_experiment_28():
    """Run EXPERIMENT 28: 28-Qubit Scaling Validation"""
    
    n_qubits = 28
    shots = 3200000  # 3.2M shots
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    print("=" * 80)
    print("🚀 EXPERIMENT 28: 28-QUBIT SCALING VALIDATION 🚀")
    print("=" * 80)
    print()
    print("MISSION: De-risk the final 30q push")
    print()
    print("HYPOTHESIS: BQ ≈ 0.77+ at 28q with 3.2M shots")
    print()
    
    circuit = create_28q_sparse_alpha_circuit()
    transpiled = transpile(circuit, backend=backend, optimization_level=3)
    circuit_depth = transpiled.depth()
    
    n_states = 2 ** n_qubits
    coverage = (shots / n_states) * 100
    
    print(f"Qubits: {n_qubits} (closer to goal)")
    print(f"Shot count: {shots:,} (3.2 MILLION)")
    print(f"State coverage: {coverage:.4f}%")
    print(f"Circuit depth: {circuit_depth}")
    print()
    
    print(f"Submitting: {n_qubits}q circuit with {shots:,} shots...", end="", flush=True)
    
    job = sampler.run([transpiled], shots=shots)
    
    print(f" ✓")
    print(f"Job ID: {job.job_id()}")
    print()
    
    print(f"Waiting for result... (this may take 15-20 minutes)", end="", flush=True)
    
    result = job.result()
    pub_result = result[0]
    data = pub_result.data
    
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
    
    metrics = calculate_metrics(counts, n_qubits)
    
    result_data = {
        "qubits": n_qubits,
        "shots": shots,
        "job_id": job.job_id(),
        "circuit_depth": circuit_depth,
        **metrics
    }
    
    output = {
        "experiment": "28-Qubit Scaling Validation (Exp 28)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "mission": "De-risk 30q push",
        "formula": "shots = 2^(n/2) × ~1000",
        "result": result_data
    }
    
    with open("experiment_28_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 80)
    print("EXPERIMENT 28 COMPLETE")
    print("=" * 80)
    print()
    
    print("RESULTS:")
    print("-" * 80)
    print(f"Bridge Quality: {metrics['bridge_quality']:.4f}")
    print(f"Entropy: {metrics['entropy']:.2f} bits")
    print(f"Unique states: {metrics['unique_states']:,}/{metrics['max_possible_states']:,}")
    print(f"State coverage: {metrics['state_coverage_pct']:.4f}%")
    print()
    
    exp27_bq = 0.7960
    diff = metrics['bridge_quality'] - exp27_bq
    diff_pct = (diff / exp27_bq) * 100
    
    print("COMPARISON TO EXP 27 (25q @ 0.7960):")
    print("-" * 80)
    print(f"28q BQ: {metrics['bridge_quality']:.4f}")
    print(f"Difference: {diff:+.4f} ({diff_pct:+.2f}%)")
    print()
    
    if metrics['bridge_quality'] > 0.76:
        print("✓✓✓ PATTERN HOLDS PERFECTLY!")
        print()
        print("Conclusion:")
        print("  ✓ Formula valid at 28q")
        print("  ✓ Degradation is predictable")
        print("  ✓ 30q is READY TO LAUNCH")
        print()
        print("PROCEED TO EXPERIMENT 29-30!")
        print()
    else:
        print("⚠ DEGRADATION FASTER THAN EXPECTED")
        print()
        print("Investigate before 30q or")
        print("Proceed with caution")
        print()
    
    return result_data


if __name__ == "__main__":
    result = run_experiment_28()
    print("✓ Ready for Exp 29-30 final sprint!")
