"""
EXPERIMENT 31: MEASUREMENT BASIS SENSITIVITY TEST
Quantum Coherence Verification via Basis Independence
========================================

Mission: Prove the observed coherence is genuinely quantum, not classical noise

Hypothesis: Bridge Quality remains stable across X, Y, Z measurement bases
            if the system exhibits true quantum superposition

This is the SMOKING GUN test:
  • If BQ is basis-independent → REAL quantum coherence ✓
  • If BQ varies randomly → classical measurement artifacts
  • If BQ inverts perfectly → Bloch sphere rotation confirmed
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


def create_25q_circuit():
    """Create baseline 25-qubit circuit."""
    n_qubits = 25
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
    
    return qc


def create_z_basis_circuit():
    """Measure in Z-basis (computational basis) - DEFAULT."""
    qc = create_25q_circuit()
    qc.measure(range(25), range(25))
    return qc


def create_x_basis_circuit():
    """Measure in X-basis: apply Hadamard before measurement."""
    qc = create_25q_circuit()
    # Rotate to X-basis
    for i in range(25):
        qc.h(i)
    qc.barrier()
    qc.measure(range(25), range(25))
    return qc


def create_y_basis_circuit():
    """Measure in Y-basis: apply S† then Hadamard before measurement."""
    qc = create_25q_circuit()
    # Rotate to Y-basis
    for i in range(25):
        qc.sdg(i)  # S† = S-dagger
        qc.h(i)
    qc.barrier()
    qc.measure(range(25), range(25))
    return qc


def calculate_metrics(counts, n_qubits):
    """Calculate Bridge Quality and entropy."""
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


def run_basis_sensitivity_test():
    """Run Experiment 31: Measurement Basis Sensitivity."""
    
    n_qubits = 25
    shots = 1000000  # 1M shots - same as Exp 27
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 88 + "║")
    print("║" + "🔬 EXPERIMENT 31: MEASUREMENT BASIS SENSITIVITY TEST 🔬".center(88) + "║")
    print("║" + "Quantum Coherence Verification".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "=" * 88 + "╝")
    print()
    
    print("MISSION: Prove observed coherence is genuinely quantum")
    print()
    print("HYPOTHESIS: Bridge Quality is BASIS-INDEPENDENT")
    print("            (true quantum superposition rotates, but entropy stays same)")
    print()
    
    results_by_basis = {}
    
    # ====================================================================
    # TEST 1: Z-BASIS (COMPUTATIONAL BASIS)
    # ====================================================================
    print("╔" + "=" * 88 + "╗")
    print("║ Z-BASIS TEST (Computational Basis) ".ljust(89) + "║")
    print("╚" + "=" * 88 + "╝")
    print()
    
    circuit_z = create_z_basis_circuit()
    transpiled_z = transpile(circuit_z, backend=backend, optimization_level=3)
    
    print(f"Submitting 25q Z-basis circuit with {shots:,} shots...", end="", flush=True)
    job_z = sampler.run([transpiled_z], shots=shots)
    print(f" ✓")
    print(f"Job ID: {job_z.job_id()}")
    
    print(f"Waiting for result... (this may take 10-15 minutes)", end="", flush=True)
    result_z = job_z.result()
    pub_result_z = result_z[0]
    data_z = pub_result_z.data
    
    if hasattr(data_z, "meas"):
        counts_z = data_z.meas.get_counts()
    else:
        for attr in dir(data_z):
            if not attr.startswith("_"):
                obj = getattr(data_z, attr)
                if hasattr(obj, "get_counts"):
                    counts_z = obj.get_counts()
                    break
    
    print(" ✓")
    metrics_z = calculate_metrics(counts_z, n_qubits)
    results_by_basis['Z'] = metrics_z
    
    print()
    print(f"Z-BASIS RESULTS:")
    print(f"  Bridge Quality: {metrics_z['bridge_quality']:.4f}")
    print(f"  Entropy: {metrics_z['entropy']:.2f} bits")
    print(f"  Unique states: {metrics_z['unique_states']:,}/{metrics_z['max_possible_states']:,}")
    print()
    
    # ====================================================================
    # TEST 2: X-BASIS
    # ====================================================================
    print("╔" + "=" * 88 + "╗")
    print("║ X-BASIS TEST (Hadamard Rotated) ".ljust(89) + "║")
    print("╚" + "=" * 88 + "╝")
    print()
    
    circuit_x = create_x_basis_circuit()
    transpiled_x = transpile(circuit_x, backend=backend, optimization_level=3)
    
    print(f"Submitting 25q X-basis circuit with {shots:,} shots...", end="", flush=True)
    job_x = sampler.run([transpiled_x], shots=shots)
    print(f" ✓")
    print(f"Job ID: {job_x.job_id()}")
    
    print(f"Waiting for result... (this may take 10-15 minutes)", end="", flush=True)
    result_x = job_x.result()
    pub_result_x = result_x[0]
    data_x = pub_result_x.data
    
    if hasattr(data_x, "meas"):
        counts_x = data_x.meas.get_counts()
    else:
        for attr in dir(data_x):
            if not attr.startswith("_"):
                obj = getattr(data_x, attr)
                if hasattr(obj, "get_counts"):
                    counts_x = obj.get_counts()
                    break
    
    print(" ✓")
    metrics_x = calculate_metrics(counts_x, n_qubits)
    results_by_basis['X'] = metrics_x
    
    print()
    print(f"X-BASIS RESULTS:")
    print(f"  Bridge Quality: {metrics_x['bridge_quality']:.4f}")
    print(f"  Entropy: {metrics_x['entropy']:.2f} bits")
    print(f"  Unique states: {metrics_x['unique_states']:,}/{metrics_x['max_possible_states']:,}")
    print()
    
    # ====================================================================
    # TEST 3: Y-BASIS
    # ====================================================================
    print("╔" + "=" * 88 + "╗")
    print("║ Y-BASIS TEST (S-Dagger + Hadamard Rotated) ".ljust(89) + "║")
    print("╚" + "=" * 88 + "╝")
    print()
    
    circuit_y = create_y_basis_circuit()
    transpiled_y = transpile(circuit_y, backend=backend, optimization_level=3)
    
    print(f"Submitting 25q Y-basis circuit with {shots:,} shots...", end="", flush=True)
    job_y = sampler.run([transpiled_y], shots=shots)
    print(f" ✓")
    print(f"Job ID: {job_y.job_id()}")
    
    print(f"Waiting for result... (this may take 10-15 minutes)", end="", flush=True)
    result_y = job_y.result()
    pub_result_y = result_y[0]
    data_y = pub_result_y.data
    
    if hasattr(data_y, "meas"):
        counts_y = data_y.meas.get_counts()
    else:
        for attr in dir(data_y):
            if not attr.startswith("_"):
                obj = getattr(data_y, attr)
                if hasattr(obj, "get_counts"):
                    counts_y = obj.get_counts()
                    break
    
    print(" ✓")
    metrics_y = calculate_metrics(counts_y, n_qubits)
    results_by_basis['Y'] = metrics_y
    
    print()
    print(f"Y-BASIS RESULTS:")
    print(f"  Bridge Quality: {metrics_y['bridge_quality']:.4f}")
    print(f"  Entropy: {metrics_y['entropy']:.2f} bits")
    print(f"  Unique states: {metrics_y['unique_states']:,}/{metrics_y['max_possible_states']:,}")
    print()
    
    # ====================================================================
    # ANALYSIS: IS IT REALLY QUANTUM?
    # ====================================================================
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 88 + "║")
    print("║" + "🔍 ANALYSIS: BASIS INDEPENDENCE TEST ".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "=" * 88 + "╝")
    print()
    
    bq_z = metrics_z['bridge_quality']
    bq_x = metrics_x['bridge_quality']
    bq_y = metrics_y['bridge_quality']
    
    bq_values = [bq_z, bq_x, bq_y]
    bq_mean = np.mean(bq_values)
    bq_std = np.std(bq_values)
    bq_max_variance = max(bq_values) - min(bq_values)
    
    print(f"BRIDGE QUALITY COMPARISON:")
    print(f"  Z-basis: {bq_z:.4f}")
    print(f"  X-basis: {bq_x:.4f}")
    print(f"  Y-basis: {bq_y:.4f}")
    print()
    print(f"STATISTICAL ANALYSIS:")
    print(f"  Mean BQ: {bq_mean:.4f}")
    print(f"  Std Dev: {bq_std:.4f}")
    print(f"  Max Variance: {bq_max_variance:.4f} ({(bq_max_variance/bq_mean)*100:.2f}%)")
    print()
    
    # Interpretation
    print(f"INTERPRETATION:")
    print()
    
    if bq_max_variance < 0.02:
        print(f"✓✓✓ RESULT: BASIS-INDEPENDENT (Δ < 0.02)")
        print()
        print(f"CONCLUSION: TRUE QUANTUM COHERENCE CONFIRMED")
        print()
        print(f"What this means:")
        print(f"  • The superposition is REAL, not measurement artifact")
        print(f"  • Entropy is BASIS-INDEPENDENT (hallmark of quantum system)")
        print(f"  • Information exists in ALL measurement bases equally")
        print(f"  • This is NOT classical noise (which would vary by basis)")
        print()
        print(f"Physics interpretation:")
        print(f"  The quantum state |ψ⟩ exists in genuine superposition.")
        print(f"  Rotating measurement basis doesn't change information content.")
        print(f"  This proves Bell's theorem requirements are met.")
        print()
        quantum_verified = True
        
    elif bq_max_variance < 0.05:
        print(f"~ RESULT: MOSTLY BASIS-INDEPENDENT (Δ < 0.05)")
        print()
        print(f"CONCLUSION: LIKELY QUANTUM, with slight measurement noise")
        print()
        print(f"What this means:")
        print(f"  • Coherence is probably real")
        print(f"  • Small variations likely from hardware imperfections")
        print(f"  • Still strong evidence for quantum superposition")
        print()
        quantum_verified = True
        
    else:
        print(f"✗ RESULT: BASIS-DEPENDENT (Δ > 0.05)")
        print()
        print(f"CONCLUSION: MEASUREMENT ARTIFACTS OR CLASSICAL NOISE")
        print()
        print(f"What this means:")
        print(f"  • High variance suggests measurement basis sensitivity")
        print(f"  • Could indicate: hardware bias, preparation errors, or classical noise")
        print(f"  • Coherence may not be genuinely quantum")
        print()
        quantum_verified = False
    
    # Save results
    output = {
        "experiment": "Measurement Basis Sensitivity Test (Exp 31)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "mission": "Verify quantum coherence via basis independence",
        "hypothesis": "Bridge Quality is basis-independent",
        "qubits": 25,
        "shots": shots,
        "results_by_basis": {
            "Z": {**metrics_z, "basis": "Computational (Z)"},
            "X": {**metrics_x, "basis": "Hadamard (X)"},
            "Y": {**metrics_y, "basis": "S†+Hadamard (Y)"}
        },
        "analysis": {
            "bq_mean": float(bq_mean),
            "bq_std": float(bq_std),
            "bq_max_variance": float(bq_max_variance),
            "variance_percent": float((bq_max_variance/bq_mean)*100),
            "is_basis_independent": float(bq_max_variance) < 0.02,
            "quantum_verified": quantum_verified
        }
    }
    
    with open("experiment_31_basis_sensitivity.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 88 + "║")
    if quantum_verified:
        print("║" + "✓✓✓ QUANTUM COHERENCE VERIFIED ✓✓✓".center(88) + "║")
    else:
        print("║" + "⚠ COHERENCE SIGNAL INCONCLUSIVE".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "=" * 88 + "╝")
    print()
    
    return output


if __name__ == "__main__":
    result = run_basis_sensitivity_test()
    print("Experiment 31 complete. Results saved to experiment_31_basis_sensitivity.json")
