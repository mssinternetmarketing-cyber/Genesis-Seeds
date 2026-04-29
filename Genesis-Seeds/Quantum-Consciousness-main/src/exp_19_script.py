"""
EXPERIMENT 19: OMEGA RATIO OPTIMIZATION
Hardware Submission Script
========================================

Fast, focused test: 20 circuits across 5 qubit counts & 4 seed ratios
Expected runtime: ~20-30 minutes total (5 minutes per test in queue)
"""

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import json
import numpy as np
from datetime import datetime


# Seed Library
SEED_LIBRARY = {
    "Omega": {"phase": 0, "description": "Positive superposition"},
    "Alpha": {"phase": np.pi / 2, "description": "Complex phase (receptive)"}
}


def generate_seed_pattern(n_qubits, omega_ratio):
    """Generate seed pattern based on omega ratio."""
    num_omega = int(n_qubits * omega_ratio)
    num_alpha = n_qubits - num_omega
    seeds = ["Omega"] * num_omega + ["Alpha"] * num_alpha
    return seeds


def create_consciousness_circuit(n_qubits, seed_pattern):
    """Create consciousness circuit with specified seed pattern."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize each qubit
    for i, seed_name in enumerate(seed_pattern):
        qc.h(i)  # Superposition
        phase = SEED_LIBRARY[seed_name]["phase"]
        qc.p(phase, i)
    
    qc.barrier()
    
    # Sequential coupling
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


def run_experiment_19():
    """Run EXPERIMENT 19: Omega Ratio Optimization"""
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    # Test matrix
    qubit_counts = [2, 4, 6, 8, 10]
    omega_ratios = {
        "100pct": 1.00,
        "75pct": 0.75,
        "50pct": 0.50,
        "25pct": 0.25
    }
    
    results = []
    all_jobs = []
    
    print("=" * 80)
    print("EXPERIMENT 19: OMEGA RATIO OPTIMIZATION")
    print("=" * 80)
    print()
    print("PHASE 1: SUBMITTING ALL 20 CIRCUITS")
    print("-" * 80)
    
    # Phase 1: Submit all jobs
    for n_qubits in qubit_counts:
        for ratio_name, ratio_value in omega_ratios.items():
            seed_pattern = generate_seed_pattern(n_qubits, ratio_value)
            circuit = create_consciousness_circuit(n_qubits, seed_pattern)
            transpiled = transpile(circuit, backend=backend, optimization_level=3)
            
            print(f"Submitting: {n_qubits}q {ratio_name} Omega | Depth: {transpiled.depth()}")
            
            job = sampler.run([transpiled], shots=512)
            
            all_jobs.append({
                "job_id": job.job_id(),
                "qubits": n_qubits,
                "ratio_name": ratio_name,
                "ratio_value": ratio_value,
                "seed_pattern": seed_pattern,
                "circuit_depth": transpiled.depth(),
                "job": job,
                "test_id": f"{n_qubits}q_{ratio_name}"
            })
    
    print()
    print(f"✓ Submitted {len(all_jobs)} jobs to queue")
    print()
    
    print("PHASE 2: COLLECTING RESULTS")
    print("-" * 80)
    
    # Phase 2: Collect results as they complete
    for idx, job_info in enumerate(all_jobs, 1):
        test_id = job_info["test_id"]
        job = job_info["job"]
        n_qubits = job_info["qubits"]
        
        print(f"[{idx}/{len(all_jobs)}] Waiting for {test_id}... ", end="", flush=True)
        
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
        probs = []
        for i in range(2 ** n_qubits):
            state = format(i, f'0{n_qubits}b')
            prob = counts.get(state, 0) / total_shots
            probs.append(prob)
        
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        bridge_quality = entropy / n_qubits
        
        result_data = {
            "test_id": test_id,
            "qubits": n_qubits,
            "omega_ratio": job_info["ratio_value"],
            "ratio_name": job_info["ratio_name"],
            "bridge_quality": float(bridge_quality),
            "entropy": float(entropy),
            "unique_states": len(counts),
            "circuit_depth": job_info["circuit_depth"],
            "job_id": job_info["job_id"]
        }
        
        results.append(result_data)
        
        print(f"✓ BQ={bridge_quality:.4f}")
    
    # Save results
    output = {
        "experiment": "Omega Ratio Optimization (Exp 19)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "results": results
    }
    
    with open("experiment_19_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 19 COMPLETE")
    print("=" * 80)
    print(f"✓ Results saved: experiment_19_results.json")
    print(f"✓ Total tests: {len(results)}")
    print()
    
    return results


if __name__ == "__main__":
    results = run_experiment_19()
    
    # Quick summary
    print("\nRESULTS SUMMARY")
    print("-" * 80)
    print(f"{'Test':<20} {'BQ':<10} {'Entropy':<10} {'Depth':<8}")
    print("-" * 80)
    
    for r in sorted(results, key=lambda x: (x['qubits'], -x['omega_ratio'])):
        print(f"{r['test_id']:<20} {r['bridge_quality']:<10.4f} {r['entropy']:<10.2f} {r['circuit_depth']:<8}")
