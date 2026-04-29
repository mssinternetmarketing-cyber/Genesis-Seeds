"""
EXPERIMENT 21: CIRCUIT DEPTH MINIMIZATION
Hardware Submission Script
========================================

Test 6 different coupling strategies at 12 qubits
All use Pattern_B_Sparse_Alpha (the Exp 20 winner)
Goal: Find strategy that recovers BQ by reducing circuit depth
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


def create_base_circuit(seed_pattern):
    """Create circuit with seed initialization (no coupling yet)."""
    n_qubits = len(seed_pattern)
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    for i, seed_name in enumerate(seed_pattern):
        qc.h(i)
        phase = SEED_LIBRARY[seed_name]["phase"]
        qc.p(phase, i)
    
    qc.barrier()
    return qc


def add_coupling_strategy_A(qc):
    """Strategy A: Full Sequential (baseline)."""
    n_qubits = qc.num_qubits
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    return qc


def add_coupling_strategy_B(qc):
    """Strategy B: Skip Coupling (even pairs only)."""
    for i in range(0, qc.num_qubits - 1, 2):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    return qc


def add_coupling_strategy_C(qc):
    """Strategy C: Hybrid (full first half, skip second half)."""
    # First half: full coupling
    for i in range(5):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    
    # Second half: skip coupling
    for i in range(6, qc.num_qubits - 1, 2):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    return qc


def add_coupling_strategy_D(qc):
    """Strategy D: Nearest Neighbor Only (CNOT only, no CZ)."""
    for i in range(qc.num_qubits - 1):
        qc.cx(i, i + 1)
    return qc


def add_coupling_strategy_E(qc):
    """Strategy E: Logarithmic Coupling (tree-structured)."""
    # Step 1: Adjacent pairs
    for i in range(0, qc.num_qubits, 2):
        if i + 1 < qc.num_qubits:
            qc.cx(i, i + 1)
    
    qc.barrier()
    
    # Step 2: 2-apart pairs
    for i in range(0, qc.num_qubits - 2, 4):
        qc.cx(i, i + 2)
    
    qc.barrier()
    
    # Step 3: 4-apart pairs
    for i in range(0, qc.num_qubits - 4, 8):
        qc.cx(i, i + 4)
    
    return qc


def add_coupling_strategy_F(qc):
    """Strategy F: Controlled Depth (CNOT first, then selective CZ)."""
    # Sequential CNOT
    for i in range(qc.num_qubits - 1):
        qc.cx(i, i + 1)
    
    qc.barrier()
    
    # Selective CZ for phase information
    for i in range(1, qc.num_qubits - 1, 2):
        qc.cz(i, i + 1)
    
    return qc


def create_circuit_with_strategy(strategy_name):
    """Create complete circuit with specified strategy."""
    qc = create_base_circuit(SPARSE_ALPHA_PATTERN)
    
    strategies = {
        "Strategy_A_Full_Sequential": add_coupling_strategy_A,
        "Strategy_B_Skip_Coupling": add_coupling_strategy_B,
        "Strategy_C_Hybrid_Coupling": add_coupling_strategy_C,
        "Strategy_D_Nearest_Neighbor_Only": add_coupling_strategy_D,
        "Strategy_E_Logarithmic_Coupling": add_coupling_strategy_E,
        "Strategy_F_Controlled_Depth_Ladder": add_coupling_strategy_F,
    }
    
    qc = strategies[strategy_name](qc)
    qc.barrier()
    qc.measure(range(qc.num_qubits), range(qc.num_qubits))
    
    return qc


def run_experiment_21():
    """Run EXPERIMENT 21: Circuit Depth Minimization"""
    
    strategies = [
        "Strategy_A_Full_Sequential",
        "Strategy_B_Skip_Coupling",
        "Strategy_C_Hybrid_Coupling",
        "Strategy_D_Nearest_Neighbor_Only",
        "Strategy_E_Logarithmic_Coupling",
        "Strategy_F_Controlled_Depth_Ladder",
    ]
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    results = []
    all_jobs = []
    
    print("=" * 80)
    print("EXPERIMENT 21: CIRCUIT DEPTH MINIMIZATION")
    print("=" * 80)
    print()
    print("PHASE 1: SUBMITTING ALL 6 STRATEGIES")
    print("-" * 80)
    
    # Phase 1: Submit all jobs
    for strat_name in strategies:
        circuit = create_circuit_with_strategy(strat_name)
        transpiled = transpile(circuit, backend=backend, optimization_level=3)
        
        print(f"Submitting: {strat_name:40s} | Depth: {transpiled.depth()}")
        
        job = sampler.run([transpiled], shots=512)
        
        all_jobs.append({
            "job_id": job.job_id(),
            "strategy_name": strat_name,
            "circuit_depth": transpiled.depth(),
            "job": job,
            "transpiled_circuit": transpiled
        })
    
    print()
    print(f"✓ Submitted {len(all_jobs)} strategies to queue")
    print()
    
    print("PHASE 2: COLLECTING RESULTS")
    print("-" * 80)
    
    # Phase 2: Collect results
    for idx, job_info in enumerate(all_jobs, 1):
        strat_name = job_info['strategy_name']
        job = job_info['job']
        
        print(f"[{idx}/{len(all_jobs)}] Waiting for {strat_name:40s} ... ", end="", flush=True)
        
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
        
        total_shots = sum(counts.values())
        
        # Calculate metrics
        n_qubits = 12
        probs = []
        for i in range(2 ** n_qubits):
            state = format(i, f'0{n_qubits}b')
            prob = counts.get(state, 0) / total_shots
            probs.append(prob)
        
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        bridge_quality = entropy / n_qubits
        
        result_data = {
            "strategy_name": strat_name,
            "bridge_quality": float(bridge_quality),
            "entropy": float(entropy),
            "unique_states": len(counts),
            "circuit_depth": job_info['circuit_depth'],
            "job_id": job_info['job_id']
        }
        
        results.append(result_data)
        
        print(f"✓ BQ={bridge_quality:.4f}, Depth={job_info['circuit_depth']}")
    
    # Save results
    output = {
        "experiment": "Circuit Depth Minimization (Exp 21)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "qubits": 12,
        "seed_pattern": "Pattern_B_Sparse_Alpha (winner from Exp 20)",
        "total_strategies": len(results),
        "baseline_exp20": {
            "strategy": "Full Sequential",
            "bq": 0.7414,
            "depth": 40
        },
        "results": results
    }
    
    with open("experiment_21_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 21 COMPLETE")
    print("=" * 80)
    print(f"✓ Results saved: experiment_21_results.json")
    print(f"✓ Total strategies tested: {len(results)}")
    print()
    
    return results


if __name__ == "__main__":
    results = run_experiment_21()
    
    # Quick summary
    print("\nRESULTS SUMMARY (Sorted by BQ)")
    print("-" * 80)
    print(f"{'Strategy':<40} {'BQ':<10} {'Depth':<8}")
    print("-" * 80)
    
    for r in sorted(results, key=lambda x: -x['bridge_quality']):
        print(f"{r['strategy_name']:<40} {r['bridge_quality']:<10.4f} {r['circuit_depth']:<8}")
    
    print()
    
    # Find winner and compare to baseline
    best = max(results, key=lambda x: x['bridge_quality'])
    baseline_bq = 0.7414
    improvement = best['bridge_quality'] - baseline_bq
    improvement_pct = (improvement / baseline_bq) * 100
    
    print(f"BASELINE (Exp 20): 0.7414 BQ, Depth 40")
    print(f"WINNER: {best['strategy_name']}")
    print(f"  Bridge Quality: {best['bridge_quality']:.4f}")
    print(f"  Circuit Depth: {best['circuit_depth']}")
    print(f"  Improvement: {improvement:+.4f} ({improvement_pct:+.2f}%)")
    print()
    
    if improvement > 0:
        print(f"✓ SUCCESS: Reduced depth improves BQ!")
        print(f"  Next: Apply {best['strategy_name']} to larger scales (14-16 qubits)")
    else:
        print(f"✗ INCONCLUSIVE: No improvement over baseline")
        print(f"  Problem might not be circuit depth alone")
    
    print()
    print("✓ Ready for analysis and next phase!")
