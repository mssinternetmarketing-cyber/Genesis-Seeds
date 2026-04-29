"""
EXPERIMENT 20: ADAPTIVE ALPHA PLACEMENT
Hardware Submission Script
========================================

Test Alpha as DECOHERENCE BUFFERS using strategic placement patterns
"""

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import json
import numpy as np
from datetime import datetime


SEED_LIBRARY = {
    "Omega": {"phase": 0, "description": "Presence - constructive"},
    "Alpha": {"phase": np.pi / 2, "description": "Receptivity - phase reset"}
}


def create_consciousness_circuit_from_pattern(pattern):
    """
    Create circuit from explicit seed pattern list.
    
    Args:
        pattern: List of seed names ["Omega", "Alpha", ...]
    """
    n_qubits = len(pattern)
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize each qubit with its seed
    for i, seed_name in enumerate(pattern):
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


def run_experiment_20():
    """Run EXPERIMENT 20: Adaptive Alpha Placement"""
    
    # Test patterns (12 qubits each)
    patterns = {
        "Pattern_A_Uniform_75pct": {
            "seeds": ["Omega", "Omega", "Omega", "Alpha", "Omega", "Omega", 
                     "Omega", "Alpha", "Omega", "Omega", "Omega", "Alpha"],
            "description": "Baseline 75% uniform (Ω Ω Ω α repeated)"
        },
        "Pattern_B_Sparse_Alpha": {
            "seeds": ["Omega", "Omega", "Omega", "Omega", "Alpha", "Omega", 
                     "Omega", "Omega", "Omega", "Alpha", "Omega", "Omega"],
            "description": "Sparse: 2 Alphas at positions 4, 9"
        },
        "Pattern_C_Dense_Alpha": {
            "seeds": ["Omega", "Omega", "Alpha", "Omega", "Omega", "Alpha", 
                     "Omega", "Omega", "Alpha", "Omega", "Omega", "Alpha"],
            "description": "Dense: 4 Alphas every 3 qubits"
        },
        "Pattern_D_Front_Heavy": {
            "seeds": ["Alpha", "Omega", "Omega", "Omega", "Omega", "Alpha", 
                     "Omega", "Omega", "Omega", "Omega", "Omega", "Omega"],
            "description": "Front-loaded: Alphas at 0, 5"
        },
        "Pattern_E_Back_Heavy": {
            "seeds": ["Omega", "Omega", "Omega", "Omega", "Omega", "Omega", 
                     "Omega", "Omega", "Alpha", "Omega", "Omega", "Alpha"],
            "description": "Back-loaded: Alphas at 8, 11"
        },
        "Pattern_F_Strategic_Cluster": {
            "seeds": ["Omega", "Omega", "Omega", "Omega", "Omega", "Alpha", 
                     "Alpha", "Omega", "Omega", "Omega", "Omega", "Alpha"],
            "description": "Strategic: Clustered Alphas at 5-6 (midpoint), 11"
        }
    }
    
    # Initialize IBM backend
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    sampler = SamplerV2(mode=backend)
    
    results = []
    all_jobs = []
    
    print("=" * 80)
    print("EXPERIMENT 20: ADAPTIVE ALPHA PLACEMENT")
    print("=" * 80)
    print()
    print("PHASE 1: SUBMITTING ALL 6 PATTERNS")
    print("-" * 80)
    
    # Phase 1: Submit all jobs
    for pattern_name, pattern_data in patterns.items():
        seeds = pattern_data['seeds']
        circuit = create_consciousness_circuit_from_pattern(seeds)
        transpiled = transpile(circuit, backend=backend, optimization_level=3)
        
        pattern_str = " ".join([s[0] for s in seeds])  # Abbreviated
        print(f"Submitting: {pattern_name:30s} | {pattern_str} | Depth: {transpiled.depth()}")
        
        job = sampler.run([transpiled], shots=512)
        
        all_jobs.append({
            "job_id": job.job_id(),
            "pattern_name": pattern_name,
            "pattern_description": pattern_data['description'],
            "seeds": seeds,
            "circuit_depth": transpiled.depth(),
            "job": job,
            "test_id": pattern_name
        })
    
    print()
    print(f"✓ Submitted {len(all_jobs)} patterns to queue")
    print()
    
    print("PHASE 2: COLLECTING RESULTS")
    print("-" * 80)
    
    # Phase 2: Collect results
    for idx, job_info in enumerate(all_jobs, 1):
        pattern_name = job_info['pattern_name']
        job = job_info['job']
        
        print(f"[{idx}/{len(all_jobs)}] Waiting for {pattern_name:30s} ... ", end="", flush=True)
        
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
            "pattern_name": pattern_name,
            "pattern_description": job_info['pattern_description'],
            "bridge_quality": float(bridge_quality),
            "entropy": float(entropy),
            "unique_states": len(counts),
            "circuit_depth": job_info['circuit_depth'],
            "job_id": job_info['job_id'],
            "alpha_count": sum(1 for s in job_info['seeds'] if s == "Alpha"),
            "alpha_ratio": sum(1 for s in job_info['seeds'] if s == "Alpha") / 12
        }
        
        results.append(result_data)
        
        print(f"✓ BQ={bridge_quality:.4f}")
    
    # Save results
    output = {
        "experiment": "Adaptive Alpha Placement (Exp 20)",
        "backend": "ibm_fez",
        "timestamp": datetime.now().isoformat(),
        "qubits": 12,
        "total_patterns": len(results),
        "hypothesis": "Alphas function as decoherence buffers; strategic placement beats uniform",
        "results": results
    }
    
    with open("experiment_20_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 20 COMPLETE")
    print("=" * 80)
    print(f"✓ Results saved: experiment_20_results.json")
    print(f"✓ Total patterns tested: {len(results)}")
    print()
    
    return results


if __name__ == "__main__":
    results = run_experiment_20()
    
    # Quick summary
    print("\nRESULTS SUMMARY")
    print("-" * 80)
    print(f"{'Pattern':<30} {'BQ':<10} {'α Count':<10} {'Depth':<8}")
    print("-" * 80)
    
    for r in sorted(results, key=lambda x: -x['bridge_quality']):
        print(f"{r['pattern_name']:<30} {r['bridge_quality']:<10.4f} {r['alpha_count']:<10} {r['circuit_depth']:<8}")
    
    print()
    
    # Find winner
    best = max(results, key=lambda x: x['bridge_quality'])
    print(f"WINNER: {best['pattern_name']}")
    print(f"  Bridge Quality: {best['bridge_quality']:.4f}")
    print(f"  Alpha Placement: {best['pattern_description']}")
    print()
    print(f"✓ Ready for analysis and next phase!")
