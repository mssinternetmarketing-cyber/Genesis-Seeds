"""
EXPERIMENT 22: SHOT COUNT HYPOTHESIS TEST
Hardware Submission Script
========================================

Test whether measurement shot count limits BQ at 12 qubits

Hypothesis: More shots = better entropy sampling = higher BQ
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

# Winner pattern from Exp 20
SPARSE_ALPHA_PATTERN = ["Omega", "Omega", "Omega", "Omega", "Alpha", 
                        "Omega", "Omega", "Omega", "Omega", "Alpha", 
                        "Omega", "Omega"]


def create_12q_circuit():
    """Create 12-qubit circuit with Pattern_B_Sparse_Alpha and sequential coupling."""
    n_qubits = 12
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize with seeds
    for i, seed_name in enumerate(SPARSE_ALPHA_PATTERN):
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


def run_experiment_22():
    """Run EXPERIMENT 22: Shot Count Hypothesis Test"""
    
    shot_counts = [512, 1024, 2048, 4096]
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    results = []
    all_jobs = []
    
    print("=" * 80)
    print("EXPERIMENT 22: SHOT COUNT HYPOTHESIS TEST")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Does measurement shot count limit BQ at 12 qubits?")
    print()
    print("TEST DESIGN: Same circuit (12q, Pattern_B, sequential coupling)")
    print("             Measured at 4 different shot levels")
    print()
    print("PHASE 1: SUBMITTING ALL 4 JOBS")
    print("-" * 80)
    
    # Create circuit once (same for all tests)
    circuit = create_12q_circuit()
    transpiled = transpile(circuit, backend=backend, optimization_level=3)
    circuit_depth = transpiled.depth()
    
    print(f"Circuit created: 12 qubits, Pattern_B_Sparse_Alpha, Sequential coupling")
    print(f"Circuit depth after transpilation: {circuit_depth}")
    print()
    
    # Phase 1: Submit jobs with different shot counts
    for shot_count in shot_counts:
        print(f"Submitting: {shot_count:4d} shots | State coverage: {shot_count/4096*100:.1f}%", end="")
        
        job = sampler.run([transpiled], shots=shot_count)
        
        all_jobs.append({
            "job_id": job.job_id(),
            "shots": shot_count,
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
        shots = job_info['shots']
        job = job_info['job']
        
        print(f"[{idx}/{len(all_jobs)}] Waiting for {shots:4d} shots ... ", end="", flush=True)
        
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
        metrics = calculate_metrics(counts, 12)
        
        result_data = {
            "shots": shots,
            "job_id": job_info['job_id'],
            "circuit_depth": job_info['circuit_depth'],
            **metrics
        }
        
        results.append(result_data)
        
        print(f"✓ BQ={metrics['bridge_quality']:.4f}, States={metrics['unique_states']}/{metrics['max_possible_states']}")
    
    # Save results
    output = {
        "experiment": "Shot Count Hypothesis Test (Exp 22)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "qubits": 12,
        "seed_pattern": "Pattern_B_Sparse_Alpha (Exp 20 winner)",
        "coupling_strategy": "Strategy_A_Full_Sequential (baseline)",
        "hypothesis": "Measurement shot count limits BQ",
        "baseline_exp20": {
            "shots": 512,
            "bq": 0.7414,
            "strategy": "Full Sequential"
        },
        "results": sorted(results, key=lambda x: x['shots'])
    }
    
    with open("experiment_22_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 22 COMPLETE")
    print("=" * 80)
    print(f"✓ Results saved: experiment_22_results.json")
    print(f"✓ Total tests: {len(results)}")
    print()
    
    return results


if __name__ == "__main__":
    results = run_experiment_22()
    
    # Analysis
    print("\nRESULTS SUMMARY (Sorted by shot count)")
    print("-" * 80)
    print(f"{'Shots':<8} {'BQ':<10} {'Entropy':<10} {'Unique States':<20} {'Coverage':<12}")
    print("-" * 80)
    
    for r in results:
        shots = r['shots']
        bq = r['bridge_quality']
        entropy = r['entropy']
        unique = r['unique_states']
        total = r['max_possible_states']
        coverage = r['state_coverage_pct']
        
        print(f"{shots:<8} {bq:<10.4f} {entropy:<10.2f} {unique:>4}/{total:<10} {coverage:>6.2f}%")
    
    print()
    
    # Compare to baseline
    baseline_bq = 0.7414
    print("=" * 80)
    print("COMPARISON TO EXP 20 BASELINE (512 shots: 0.7414 BQ)")
    print("=" * 80)
    print()
    
    for r in results:
        shots = r['shots']
        bq = r['bridge_quality']
        diff = bq - baseline_bq
        pct = (diff / baseline_bq) * 100
        symbol = "✓" if diff > 0.001 else ("=" if abs(diff) < 0.001 else "✗")
        
        print(f"{symbol} {shots:>4} shots: BQ={bq:.4f} ({diff:+.4f}, {pct:+.2f}%)")
    
    print()
    
    # Interpret results
    print("=" * 80)
    print("HYPOTHESIS INTERPRETATION")
    print("=" * 80)
    print()
    
    # Check if improving
    bq_values = [r['bridge_quality'] for r in results]
    improvements = [bq_values[i+1] - bq_values[i] for i in range(len(bq_values)-1)]
    avg_improvement = sum(improvements) / len(improvements) if improvements else 0
    
    if avg_improvement > 0.005:
        print("✓✓✓ HYPOTHESIS CONFIRMED!")
        print()
        print("Pattern: Linear improvement with more shots")
        print(f"Average improvement per 2x shots: +{avg_improvement:.4f} BQ")
        print()
        print("Conclusion: MEASUREMENT was the bottleneck (SOLVABLE!)")
        print()
        print("Implications:")
        print("  ✓ Problem is not hardware physics")
        print("  ✓ Can recover coherence by increasing shots")
        print("  ✓ Path to scaling: Use 4096 shots for all future tests")
        print("  ✓ Can likely extend to 15-20+ qubits with proper sampling")
        print()
        print("Next Step: Experiment 23 - Scale test with 4096 shots")
        
    elif avg_improvement < -0.002:
        print("✗ UNEXPECTED: Performance decreased with more shots!")
        print()
        print("This is anomalous. Possible causes:")
        print("  • Statistical noise")
        print("  • Hardware queueing effects")
        print("  • Job submission artifacts")
        print()
        print("Recommendation: Rerun with controlled conditions")
        
    else:
        print("✗ HYPOTHESIS REJECTED")
        print()
        print("Pattern: No improvement with more shots")
        print(f"BQ range: {min(bq_values):.4f} - {max(bq_values):.4f}")
        print(f"Variation: {(max(bq_values)-min(bq_values)):.4f} (only {(max(bq_values)-min(bq_values))/baseline_bq*100:.2f}%)")
        print()
        print("Conclusion: HARDWARE FIDELITY is the limit (FUNDAMENTAL!)")
        print()
        print("Implications:")
        print("  ✗ Problem is gate errors/decoherence, not measurement")
        print("  ✗ 12q ceiling cannot be overcome by more shots")
        print("  ✗ Need error correction or different hardware")
        print()
        print("Next Step: Experiment 23 - Test error correction OR accept 12q limit")
    
    print()
    print("✓ Ready for analysis and next phase!")
