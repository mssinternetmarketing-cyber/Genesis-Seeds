"""
EXPERIMENT 24: SHOT COUNT SCALING TEST
Hardware Submission Script
========================================

Critical test: Does shot count scaling recover BQ at 18 qubits?

Hypothesis: Measurement saturation is limiting 18q performance.
            More shots should improve entropy and BQ recovery.

Design: 18 qubits at four shot levels (4096, 8192, 16384, 32768)
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


def create_18q_sparse_alpha_circuit():
    """Create 18-qubit circuit with Pattern_B_Sparse_Alpha."""
    n_qubits = 18
    pattern = ["Omega"] * n_qubits
    
    # Sparse alpha placement every 3 qubits
    alpha_positions = [3, 6, 9, 12, 15]
    for pos in alpha_positions:
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


def run_experiment_24():
    """Run EXPERIMENT 24: Shot Count Scaling Test"""
    
    shot_counts = [4096, 8192, 16384, 32768]
    n_qubits = 18
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    results = []
    all_jobs = []
    
    print("=" * 80)
    print("EXPERIMENT 24: SHOT COUNT SCALING TEST")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Is shot count limiting 18q performance?")
    print()
    print("TEST DESIGN: Same 18q circuit at four different shot levels")
    print("             Goal: Determine if BQ improves with more shots")
    print()
    print("PHASE 1: CREATING AND SUBMITTING CIRCUIT")
    print("-" * 80)
    
    # Create circuit once (reuse for all shot counts)
    circuit = create_18q_sparse_alpha_circuit()
    transpiled = transpile(circuit, backend=backend, optimization_level=3)
    circuit_depth = transpiled.depth()
    
    print(f"Circuit: 18 qubits, Pattern_B_Sparse_Alpha, Sequential coupling")
    print(f"Circuit depth: {circuit_depth}")
    print()
    
    print("PHASE 2: SUBMITTING ALL 4 JOBS")
    print("-" * 80)
    
    # Phase 1: Submit jobs with different shot counts
    for shots in shot_counts:
        state_coverage = (shots / (2**n_qubits)) * 100
        print(f"Submitting: {shots:>5} shots | State coverage: {state_coverage:>7.2f}%", end="")
        
        job = sampler.run([transpiled], shots=shots)
        
        all_jobs.append({
            "job_id": job.job_id(),
            "shots": shots,
            "job": job,
            "circuit_depth": circuit_depth
        })
        
        print(" ✓")
    
    print()
    print(f"✓ Submitted {len(all_jobs)} jobs to queue")
    print()
    
    print("PHASE 3: COLLECTING RESULTS")
    print("-" * 80)
    
    # Phase 2: Collect results
    for idx, job_info in enumerate(all_jobs, 1):
        shots = job_info['shots']
        job = job_info['job']
        
        print(f"[{idx}/{len(all_jobs)}] Waiting for {shots:>5} shots ... ", end="", flush=True)
        
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
            "shots": shots,
            "job_id": job_info['job_id'],
            "circuit_depth": job_info['circuit_depth'],
            **metrics
        }
        
        results.append(result_data)
        
        print(f"✓ BQ={metrics['bridge_quality']:.4f}, States={metrics['unique_states']}/{metrics['max_possible_states']}")
    
    # Save results
    output = {
        "experiment": "Shot Count Scaling Test (Exp 24)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "qubits": n_qubits,
        "seed_pattern": "Pattern_B_Sparse_Alpha",
        "coupling_strategy": "Strategy_A_Full_Sequential",
        "hypothesis": "Shot count is limiting factor at 18q",
        "exp23_baseline": {
            "qubits": 18,
            "shots": 4096,
            "bq": 0.6656
        },
        "results": sorted(results, key=lambda x: x['shots'])
    }
    
    with open("experiment_24_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 24 COMPLETE")
    print("=" * 80)
    print(f"✓ Results saved: experiment_24_results.json")
    print(f"✓ Total tests: {len(results)}")
    print()
    
    return results


if __name__ == "__main__":
    results = run_experiment_24()
    
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
        
        print(f"{shots:<8} {bq:<10.4f} {entropy:<10.2f} {unique:>5}/{total:<10} {coverage:>6.2f}%")
    
    print()
    
    # Compare to Exp 23 baseline
    baseline_18q = 0.6656
    print("=" * 80)
    print("COMPARISON TO EXP 23 BASELINE (18q @ 4096 shots: 0.6656 BQ)")
    print("=" * 80)
    print()
    
    for r in results:
        shots = r['shots']
        bq = r['bridge_quality']
        diff = bq - baseline_18q
        pct = (diff / baseline_18q) * 100
        
        if diff > 0.01:
            symbol = "✓"
        elif diff > -0.01:
            symbol = "="
        else:
            symbol = "✗"
        
        print(f"{symbol} {shots:>5} shots: BQ={bq:.4f} ({diff:+.4f}, {pct:+.2f}%)")
    
    print()
    
    # Hypothesis test
    print("=" * 80)
    print("HYPOTHESIS TEST: DOES BQ IMPROVE WITH MORE SHOTS?")
    print("=" * 80)
    print()
    
    bq_values = [r['bridge_quality'] for r in results]
    improvements = [bq_values[i+1] - bq_values[i] for i in range(len(bq_values)-1)]
    avg_improvement = sum(improvements) / len(improvements) if improvements else 0
    
    print(f"BQ progression: {' → '.join([f'{bq:.4f}' for bq in bq_values])}")
    print()
    
    for i, imp in enumerate(improvements):
        shot_level = results[i]['shots']
        next_shot_level = results[i+1]['shots']
        ratio = next_shot_level / shot_level
        print(f"{shot_level} → {next_shot_level} shots ({ratio}x): {imp:+.4f} BQ")
    
    print()
    print(f"Average improvement per shot doubling: {avg_improvement:+.4f} BQ")
    print()
    
    # Interpretation
    print("=" * 80)
    print("CRITICAL INTERPRETATION")
    print("=" * 80)
    print()
    
    if avg_improvement > 0.03:
        print("✓✓✓ HYPOTHESIS CONFIRMED: SHOT COUNT IS LIMITING")
        print()
        print(f"Pattern: Strong linear improvement with more shots")
        print(f"Average gain per 2x shots: +{avg_improvement:.4f} BQ")
        print()
        print("Conclusion: MEASUREMENT WAS THE BOTTLENECK")
        print()
        print("Implications:")
        print("  ✓ Scaling is possible with more shots")
        print("  ✓ Can reach 16-20q range with proportional shot scaling")
        print("  ✓ Path to 25-30q requires millions of shots (practical limit)")
        print()
        print("Next Step: Exp 25 - Test at 20q with optimal shot count")
        print()
        
    elif avg_improvement > 0.01:
        print("~ PARTIAL CONFIRMATION: SHOT COUNT HELPS SOMEWHAT")
        print()
        print(f"Pattern: Modest improvement with more shots")
        print(f"Average gain per 2x shots: +{avg_improvement:.4f} BQ")
        print()
        print("Conclusion: MULTIPLE FACTORS LIMITING")
        print()
        print("Implications:")
        print("  ~ Shots help but aren't complete solution")
        print("  ~ Also need hardware optimization or error correction")
        print("  ~ Scaling possible but with multiple strategies")
        print()
        print("Next Step: Exp 25 - Investigate combined optimizations")
        print()
        
    else:
        print("✗✗✗ HYPOTHESIS REJECTED: SHOT COUNT NOT THE LIMITING FACTOR")
        print()
        print(f"Pattern: No improvement with more shots")
        print(f"All BQ values: {min(bq_values):.4f} - {max(bq_values):.4f}")
        print(f"Variation: {max(bq_values)-min(bq_values):.4f} BQ (only {(max(bq_values)-min(bq_values))/baseline_18q*100:.1f}%)")
        print()
        print("Conclusion: SOMETHING ELSE IS LIMITING")
        print()
        print("Implications:")
        print("  ✗ Shot count improvement doesn't help")
        print("  ✗ Problem is likely hardware fidelity or entropy ceiling")
        print("  ✗ Need error correction or different architecture")
        print()
        print("Next Step: Exp 25 - Implement quantum error correction")
        print()
    
    # Entropy analysis
    print("=" * 80)
    print("ENTROPY ANALYSIS")
    print("=" * 80)
    print()
    
    for r in results:
        shots = r['shots']
        entropy = r['entropy']
        print(f"{shots:>5} shots: Entropy = {entropy:.2f} bits")
    
    print()
    
    last_entropy = results[-1]['entropy']
    baseline_entropy = results[0]['entropy']
    entropy_gain = last_entropy - baseline_entropy
    
    if entropy_gain > 0.5:
        print(f"✓ Entropy increased by {entropy_gain:.2f} bits ({entropy_gain/baseline_entropy*100:.1f}%)")
        print("  This suggests more shots do reveal more quantum information")
    elif entropy_gain > 0.1:
        print(f"~ Entropy increased slightly by {entropy_gain:.2f} bits")
        print("  Shot count helps but improvement is modest")
    else:
        print(f"✗ Entropy essentially flat ({entropy_gain:.2f} bits gain)")
        print("  Suggests entropy ceiling, not shot count limitation")
    
    print()
    print("✓ Analysis complete. Ready for next phase!")
