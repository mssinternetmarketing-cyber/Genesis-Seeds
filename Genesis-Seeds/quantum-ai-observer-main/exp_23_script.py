"""
EXPERIMENT 23: SCALING VALIDATION TEST
Hardware Submission Script
========================================

Test: Can we scale beyond 12 qubits with 4096 shots?

Hypothesis: The 12q BQ improvement (0.74→0.93) was from better sampling.
            Larger qubit counts should also benefit from 4096 shots.

Design: Test at 14, 16, and 18 qubits with Pattern_B_Sparse_Alpha and 4096 shots
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


def create_sparse_alpha_pattern(n_qubits):
    """Create sparse Alpha pattern: place Alphas every ~5 qubits."""
    pattern = ["Omega"] * n_qubits
    
    # Place Alphas at regular intervals
    alpha_positions = []
    pos = n_qubits // 5  # First Alpha at 1/5 point
    while pos < n_qubits:
        pattern[pos] = "Alpha"
        alpha_positions.append(pos)
        pos += n_qubits // 5  # Maintain spacing
    
    return pattern, alpha_positions


def create_circuit_for_qubits(n_qubits):
    """Create n-qubit circuit with Pattern_B_Sparse_Alpha and sequential coupling."""
    pattern, alpha_pos = create_sparse_alpha_pattern(n_qubits)
    
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
    
    return qc, alpha_pos


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


def run_experiment_23():
    """Run EXPERIMENT 23: Scaling Validation Test"""
    
    qubit_counts = [14, 16, 18]
    shots = 4096  # Optimal from Exp 22
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    results = []
    all_jobs = []
    
    print("=" * 80)
    print("EXPERIMENT 23: SCALING VALIDATION TEST")
    print("=" * 80)
    print()
    print("HYPOTHESIS: With 4096 shots, can we scale beyond 12 qubits?")
    print()
    print(f"TEST DESIGN: Test at {qubit_counts} qubits")
    print(f"            All with Pattern_B_Sparse_Alpha, sequential coupling, {shots} shots")
    print()
    print("PHASE 1: SUBMITTING ALL 3 JOBS")
    print("-" * 80)
    
    # Phase 1: Create and submit circuits
    for n_qubits in qubit_counts:
        circuit, alpha_pos = create_circuit_for_qubits(n_qubits)
        transpiled = transpile(circuit, backend=backend, optimization_level=3)
        circuit_depth = transpiled.depth()
        
        print(f"Creating: {n_qubits}q circuit | Alphas at {alpha_pos} | Depth: {circuit_depth}", end="")
        
        job = sampler.run([transpiled], shots=shots)
        
        all_jobs.append({
            "job_id": job.job_id(),
            "qubits": n_qubits,
            "alpha_positions": alpha_pos,
            "job": job,
            "circuit_depth": circuit_depth
        })
        
        print(" ✓")
    
    print()
    print(f"✓ Submitted {len(all_jobs)} jobs to queue")
    print()
    
    print("PHASE 2: COLLECTING RESULTS")
    print("-" * 80)
    
    # Phase 2: Collect results
    for idx, job_info in enumerate(all_jobs, 1):
        n_qubits = job_info['qubits']
        job = job_info['job']
        
        print(f"[{idx}/{len(all_jobs)}] Waiting for {n_qubits}q ... ", end="", flush=True)
        
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
        
        # Calculate metrics
        metrics = calculate_metrics(counts, n_qubits)
        
        result_data = {
            "qubits": n_qubits,
            "shots": shots,
            "job_id": job_info['job_id'],
            "circuit_depth": job_info['circuit_depth'],
            "alpha_positions": job_info['alpha_positions'],
            **metrics
        }
        
        results.append(result_data)
        
        print(f"✓ BQ={metrics['bridge_quality']:.4f}, States={metrics['unique_states']}/{metrics['max_possible_states']}")
    
    # Save results
    output = {
        "experiment": "Scaling Validation Test (Exp 23)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "shots": shots,
        "seed_pattern": "Pattern_B_Sparse_Alpha (Exp 20 winner)",
        "coupling_strategy": "Strategy_A_Full_Sequential (baseline)",
        "hypothesis": "Can scale beyond 12q with 4096 shots",
        "exp22_baseline": {
            "qubits": 12,
            "shots": 4096,
            "bq": 0.9276
        },
        "results": sorted(results, key=lambda x: x['qubits'])
    }
    
    with open("experiment_23_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 23 COMPLETE")
    print("=" * 80)
    print(f"✓ Results saved: experiment_23_results.json")
    print(f"✓ Total tests: {len(results)}")
    print()
    
    return results


if __name__ == "__main__":
    results = run_experiment_23()
    
    # Analysis
    print("\nRESULTS SUMMARY (Sorted by qubit count)")
    print("-" * 80)
    print(f"{'Qubits':<8} {'BQ':<10} {'Entropy':<10} {'Unique States':<20} {'Depth':<8}")
    print("-" * 80)
    
    for r in results:
        qubits = r['qubits']
        bq = r['bridge_quality']
        entropy = r['entropy']
        unique = r['unique_states']
        total = r['max_possible_states']
        depth = r['circuit_depth']
        
        print(f"{qubits:<8} {bq:<10.4f} {entropy:<10.2f} {unique:>4}/{total:<10} {depth:<8}")
    
    print()
    
    # Compare to baseline
    baseline_12q_bq = 0.9276
    baseline_12q_qubits = 12
    
    print("=" * 80)
    print("COMPARISON TO EXP 22 BASELINE (12q @ 4096 shots: 0.9276 BQ)")
    print("=" * 80)
    print()
    
    for r in results:
        qubits = r['qubits']
        bq = r['bridge_quality']
        diff = bq - baseline_12q_bq
        pct = (diff / baseline_12q_bq) * 100
        qubit_diff = qubits - baseline_12q_qubits
        
        symbol = "✓" if diff > -0.05 else ("≈" if diff > -0.10 else "✗")
        
        print(f"{symbol} {qubits:>2}q: BQ={bq:.4f}  ({diff:+.4f}, {pct:+.2f}%)  |  +{qubit_diff}q from baseline")
    
    print()
    
    # Scaling analysis
    print("=" * 80)
    print("SCALING PATTERN ANALYSIS")
    print("=" * 80)
    print()
    
    bq_values = [r['bridge_quality'] for r in results]
    qubit_values = [r['qubits'] for r in results]
    
    # Calculate degradation per qubit
    degradation_per_qubit = []
    for i in range(len(results)-1):
        bq_loss = results[i]['bridge_quality'] - results[i+1]['bridge_quality']
        qubit_increase = results[i+1]['qubits'] - results[i]['qubits']
        degradation_per_qubit.append(bq_loss / qubit_increase)
    
    avg_degradation = sum(degradation_per_qubit) / len(degradation_per_qubit) if degradation_per_qubit else 0
    
    print(f"Baseline (12q @ 4096 shots): {baseline_12q_bq:.4f} BQ")
    print()
    
    for i, deg in enumerate(degradation_per_qubit):
        q1 = results[i]['qubits']
        q2 = results[i+1]['qubits']
        print(f"{q1}→{q2}q: {deg:.4f} BQ loss per qubit")
    
    print()
    print(f"Average degradation: {avg_degradation:.4f} BQ per qubit")
    print()
    
    # Projection
    if avg_degradation < 0.03:
        print("✓ EXCELLENT: Low degradation rate")
        print(f"  Projection to 20q: {baseline_12q_bq - avg_degradation*8:.4f} BQ")
        print(f"  Projection to 25q: {baseline_12q_bq - avg_degradation*13:.4f} BQ")
        print()
        print("  Conclusion: Can confidently scale to 20+ qubits with 4096 shots!")
        
    elif avg_degradation < 0.05:
        print("~ MODERATE: Moderate degradation rate")
        print(f"  Projection to 20q: {baseline_12q_bq - avg_degradation*8:.4f} BQ")
        print(f"  Projection to 25q: {baseline_12q_bq - avg_degradation*13:.4f} BQ")
        print()
        print("  Conclusion: Can scale to 15-20q; 25q might need additional optimization")
        
    else:
        print("✗ CONCERNING: High degradation rate")
        print(f"  Projection to 20q: {baseline_12q_bq - avg_degradation*8:.4f} BQ")
        print()
        print("  Conclusion: Rapid degradation; might need error correction sooner")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    
    if avg_degradation < 0.03:
        print("Path forward: Continue scaling with 4096 shots")
        print("  • Test at 20q, 22q, 24q to find maximum")
        print("  • Optimize seed patterns at each scale")
        print("  • Push toward 25-30q goal")
    else:
        print("Path forward: Investigate degradation cause")
        print("  • Test with 8192 shots for additional accuracy")
        print("  • Explore optimized coupling for larger systems")
        print("  • Consider error correction if degradation continues")
    
    print()
    print("✓ Ready for next phase!")
