"""
EXPERIMENT 25: 20-QUBIT SCALING VALIDATION
Hardware Submission Script
========================================

Mission: Validate the measurement-shot formula at 20 qubits

Formula discovered: shots ≈ 2^(n/2) × constant
For 20q: ~100,000 shots needed to maintain BQ ≈ 0.82+

Design: Test 20 qubits with optimal shot count
Expected outcome: BQ > 0.80 (proves formula works)
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


def create_20q_sparse_alpha_circuit():
    """Create 20-qubit circuit with Pattern_B_Sparse_Alpha."""
    n_qubits = 20
    pattern = ["Omega"] * n_qubits
    
    # Sparse alpha placement every ~4 qubits
    alpha_positions = [4, 8, 12, 16]
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
    
    # Full sequential coupling (Strategy A - baseline)
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


def run_experiment_25():
    """Run EXPERIMENT 25: 20-Qubit Scaling Validation"""
    
    n_qubits = 20
    shots = 100000  # Optimal based on formula: 2^(20/2) × 1000 ≈ 100k
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    print("=" * 80)
    print("EXPERIMENT 25: 20-QUBIT SCALING VALIDATION")
    print("=" * 80)
    print()
    print("MISSION: Validate measurement-shot formula at 20 qubits")
    print()
    print("HYPOTHESIS: Formula predicts BQ ≈ 0.82+ at 20q with 100k shots")
    print()
    print("=" * 80)
    print("CIRCUIT PREPARATION")
    print("-" * 80)
    
    # Create circuit
    circuit = create_20q_sparse_alpha_circuit()
    transpiled = transpile(circuit, backend=backend, optimization_level=3)
    circuit_depth = transpiled.depth()
    
    n_states = 2 ** n_qubits
    coverage = (shots / n_states) * 100
    
    print(f"Qubits: {n_qubits}")
    print(f"State space: 2^{n_qubits} = {n_states:,} possible states")
    print(f"Shot count: {shots:,}")
    print(f"State coverage: {coverage:.2f}% (aiming for 10%+)")
    print(f"Circuit depth: {circuit_depth}")
    print(f"Seed pattern: Pattern_B_Sparse_Alpha (alphas at [4,8,12,16])")
    print()
    
    print("=" * 80)
    print("PHASE 1: SUBMITTING CIRCUIT")
    print("-" * 80)
    
    print(f"Submitting: {n_qubits}q circuit with {shots:,} shots...", end="", flush=True)
    
    job = sampler.run([transpiled], shots=shots)
    
    print(f" ✓")
    print(f"Job ID: {job.job_id()}")
    print()
    
    print("=" * 80)
    print("PHASE 2: COLLECTING RESULT")
    print("-" * 80)
    
    print(f"Waiting for {n_qubits}q result... (this may take several minutes)", end="", flush=True)
    
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
        "experiment": "20-Qubit Scaling Validation (Exp 25)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "mission": "Validate measurement-shot formula",
        "formula": "shots = 2^(n/2) × 1000 (approximately)",
        "exp24_baseline": {
            "qubits": 18,
            "shots": 32768,
            "bq": 0.8262
        },
        "result": result_data
    }
    
    with open("experiment_25_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 80)
    print("EXPERIMENT 25 COMPLETE")
    print("=" * 80)
    print()
    
    # Analysis
    print("RESULTS:")
    print("-" * 80)
    print(f"Bridge Quality: {metrics['bridge_quality']:.4f}")
    print(f"Entropy: {metrics['entropy']:.2f} bits")
    print(f"Unique states: {metrics['unique_states']:,}/{metrics['max_possible_states']:,}")
    print(f"State coverage: {metrics['state_coverage_pct']:.2f}%")
    print()
    
    # Comparison
    exp24_18q_bq = 0.8262
    
    print("=" * 80)
    print("FORMULA VALIDATION")
    print("=" * 80)
    print()
    
    print(f"Exp 24 (18q @ 32k shots): BQ = {exp24_18q_bq:.4f}")
    print(f"Exp 25 (20q @ 100k shots): BQ = {metrics['bridge_quality']:.4f}")
    print()
    
    # Predict based on formula
    print("FORMULA PREDICTIONS:")
    print("-" * 80)
    print()
    print("If formula is correct:")
    print(f"  Expected 20q BQ: ~0.82 (same as 18q)")
    print(f"  Actual 20q BQ: {metrics['bridge_quality']:.4f}")
    print()
    
    bq_loss = exp24_18q_bq - metrics['bridge_quality']
    bq_loss_pct = (bq_loss / exp24_18q_bq) * 100
    
    if metrics['bridge_quality'] > 0.80:
        print("✓✓✓ FORMULA CONFIRMED!")
        print()
        print(f"BQ difference: {bq_loss:+.4f} ({bq_loss_pct:+.2f}%)")
        print()
        print("Conclusion:")
        print("  ✓ Measurement-shot formula works at 20q")
        print("  ✓ Can confidently scale to 22-25q with proportional shots")
        print("  ✓ 25-30q goal is achievable!")
        print()
        print("Next steps:")
        print("  → Exp 26: Test 22-24q range")
        print("  → Exp 27: Push to 25q with 1M shots")
        print("  → Exp 28: Validate 28-30q if time permits")
        print()
        
    elif metrics['bridge_quality'] > 0.75:
        print("~ PARTIAL CONFIRMATION")
        print()
        print(f"BQ difference: {bq_loss:+.4f} ({bq_loss_pct:+.2f}%)")
        print()
        print("Conclusion:")
        print("  ~ Formula mostly works but degradation faster than expected")
        print("  ~ Additional factors may limit scaling beyond 22q")
        print()
        print("Next steps:")
        print("  → Investigate degradation source")
        print("  → Test if more shots help further")
        print("  → Consider error correction for 25-30q")
        print()
        
    else:
        print("✗ FORMULA BREAKS DOWN")
        print()
        print(f"BQ difference: {bq_loss:+.4f} ({bq_loss_pct:+.2f}%)")
        print()
        print("Conclusion:")
        print("  ✗ Something other than measurement is limiting")
        print("  ✗ Hardware fidelity or entropy ceiling matters more")
        print()
        print("Next steps:")
        print("  → Test with even more shots (200k-500k)")
        print("  → Investigate error correction")
        print("  → Consider different coupling strategies")
        print()
    
    print("=" * 80)
    print("RESULTS SAVED: experiment_25_results.json")
    print("=" * 80)
    
    return result_data


if __name__ == "__main__":
    result = run_experiment_25()
    print()
    print("✓ Ready for analysis!")
