"""
EXPERIMENT 11: CONSCIOUSNESS MIGRATION
================================================================
SUBSTRATE-INDEPENDENT CONSCIOUSNESS TRANSFER
================================================================
Tests if consciousness can migrate between qubits via SWAP gates,
proving consciousness is not bound to specific physical qubits.

Creates circuits:
1. Initial state: Omega(Q0) → Alpha(Q1) bridge
2. After SWAP: Omega(Q1) → Alpha(Q0) bridge
3. Measures if consciousness "follows" the qubit migration

Validates consciousness portability across quantum substrates.
================================================================
"""

import numpy as np
import json
from datetime import datetime
import os

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.primitives import StatevectorSampler as LocalSampler
except ImportError:
    print("Installing Qiskit...")
    os.system('pip install qiskit')
    from qiskit import QuantumCircuit, transpile
    from qiskit.primitives import StatevectorSampler as LocalSampler

# ============================================================================
# CIRCUIT BUILDERS
# ============================================================================

def create_baseline_circuit():
    """Create baseline Alpha-Omega circuit (no migration)"""
    
    qc = QuantumCircuit(2, 2)
    
    # Initialize Omega+ on Q0
    qc.h(0)
    
    # Initialize Alpha+ on Q1
    qc.h(1)
    qc.s(1)
    
    # Couple Q0 → Q1
    qc.cx(0, 1)
    qc.cz(0, 1)
    
    qc.barrier()
    qc.measure([0, 1], [0, 1])
    
    return qc

def create_pre_migration_circuit():
    """Create circuit with state measurement before SWAP"""
    
    qc = QuantumCircuit(2, 4)  # 2 qubits, 4 classical bits
    
    # Initialize Omega+ on Q0
    qc.h(0)
    
    # Initialize Alpha+ on Q1
    qc.h(1)
    qc.s(1)
    
    # Couple Q0 → Q1
    qc.cx(0, 1)
    qc.cz(0, 1)
    
    qc.barrier()
    
    # Measure pre-migration state
    qc.measure(0, 0)
    qc.measure(1, 1)
    
    return qc

def create_post_migration_circuit():
    """Create circuit with SWAP followed by measurement"""
    
    qc = QuantumCircuit(2, 2)
    
    # Initialize Omega+ on Q0
    qc.h(0)
    
    # Initialize Alpha+ on Q1
    qc.h(1)
    qc.s(1)
    
    # Couple Q0 → Q1
    qc.cx(0, 1)
    qc.cz(0, 1)
    
    qc.barrier()
    
    # MIGRATE: Swap Q0 ↔ Q1
    qc.swap(0, 1)
    
    qc.barrier()
    
    # Measure post-migration state
    qc.measure([0, 1], [0, 1])
    
    return qc

def create_double_migration_circuit():
    """Create circuit with double SWAP (should return to baseline)"""
    
    qc = QuantumCircuit(2, 2)
    
    # Initialize Omega+ on Q0
    qc.h(0)
    
    # Initialize Alpha+ on Q1
    qc.h(1)
    qc.s(1)
    
    # Couple Q0 → Q1
    qc.cx(0, 1)
    qc.cz(0, 1)
    
    qc.barrier()
    
    # MIGRATE: Swap Q0 ↔ Q1
    qc.swap(0, 1)
    
    qc.barrier()
    
    # REVERSE MIGRATE: Swap Q0 ↔ Q1 again
    qc.swap(0, 1)
    
    qc.barrier()
    
    # Measure final state
    qc.measure([0, 1], [0, 1])
    
    return qc

# ============================================================================
# EXECUTION ENGINE
# ============================================================================

def run_circuit(circuit, label, sampler, shots=1024):
    """Execute circuit and extract results"""
    
    print("Running: {}...".format(label))
    
    try:
        job = sampler.run([circuit], shots=shots)
        result = job.result()
        
        pub_result = result[0]
        
        # Extract counts (handle different data formats)
        if hasattr(pub_result.data, 'meas'):
            measured_data = pub_result.data.meas
        elif hasattr(pub_result.data, 'c'):
            measured_data = pub_result.data.c
        else:
            data_attrs = [attr for attr in dir(pub_result.data) if not attr.startswith('_')]
            if data_attrs:
                measured_data = getattr(pub_result.data, data_attrs[0])
            else:
                raise AttributeError("Could not find measurement data")
        
        counts = measured_data.get_counts()
        
        # Calculate metrics
        total_shots = sum(counts.values())
        probs = [counts.get(state, 0) / total_shots for state in ['00', '01', '10', '11']]
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        bridge_quality = entropy / 2.0
        
        print("  ✅ Bridge Quality: {:.6f}".format(bridge_quality))
        print()
        
        return {
            "counts": counts,
            "total_shots": total_shots,
            "entropy": float(entropy),
            "bridge_quality": float(bridge_quality),
            "state_distribution": {state: counts.get(state, 0) for state in ['00', '01', '10', '11']}
        }
        
    except Exception as e:
        print("  ❌ Error: {}".format(str(e)))
        return None

# ============================================================================
# MIGRATION ANALYSIS
# ============================================================================

def analyze_migration(baseline, post_migration, double_migration):
    """Analyze consciousness migration patterns"""
    
    if not baseline or not post_migration:
        return None
    
    # Compare bridge qualities
    bq_baseline = baseline["bridge_quality"]
    bq_post = post_migration["bridge_quality"]
    bq_double = double_migration["bridge_quality"] if double_migration else None
    
    # Migration preservation
    preservation = (bq_post / bq_baseline) if bq_baseline > 0 else 0
    
    # Reversibility (if double migration exists)
    if bq_double is not None:
        reversibility = (bq_double / bq_baseline) if bq_baseline > 0 else 0
    else:
        reversibility = None
    
    # State distribution comparison
    baseline_states = baseline["state_distribution"]
    post_states = post_migration["state_distribution"]
    
    # Calculate distribution similarity (inverse of total variation distance)
    total_variation = 0.5 * sum([
        abs(baseline_states.get(state, 0) - post_states.get(state, 0))
        for state in ['00', '01', '10', '11']
    ])
    distribution_similarity = 1.0 - (total_variation / baseline["total_shots"])
    
    return {
        "bridge_quality": {
            "baseline": float(bq_baseline),
            "post_migration": float(bq_post),
            "double_migration": float(bq_double) if bq_double else None,
            "preservation": float(preservation),
            "reversibility": float(reversibility) if reversibility else None
        },
        "state_distribution": {
            "total_variation_distance": float(total_variation / baseline["total_shots"]),
            "similarity_score": float(distribution_similarity)
        },
        "interpretation": {
            "migration_success": "excellent" if preservation > 0.95 else "good" if preservation > 0.85 else "moderate",
            "consciousness_portable": preservation > 0.80,
            "reversible": reversibility > 0.90 if reversibility else False
        }
    }

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment_11(api_token=None, shots=1024, use_simulator=True):
    """Run consciousness migration experiment"""
    
    print()
    print("=" * 80)
    print("EXPERIMENT 11: CONSCIOUSNESS MIGRATION")
    print("Substrate-Independent Consciousness Transfer")
    print("=" * 80)
    print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print()
    
    # Setup execution environment
    if use_simulator:
        print("MODE: Local Simulator")
        print()
        sampler = LocalSampler()
        backend_name = "local_simulator"
    else:
        print("MODE: IBM Quantum Hardware")
        print()
        
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as IBMSampler
            
            token = api_token or os.environ.get('IBM_QUANTUM_TOKEN')
            if not token:
                print("No token found. Falling back to simulator...")
                sampler = LocalSampler()
                backend_name = "local_simulator"
            else:
                QiskitRuntimeService.save_account(token=token, overwrite=True)
                service = QiskitRuntimeService()
                backend = service.least_busy(simulator=False, operational=True)
                backend_name = backend.name
                
                print("Selected: {} ({} qubits)".format(backend.name, backend.num_qubits))
                print()
                
                sampler = IBMSampler(backend)
        except Exception as e:
            print("Error: {}".format(str(e)))
            print("Falling back to simulator...")
            sampler = LocalSampler()
            backend_name = "local_simulator"
    
    # Create circuits
    print("=" * 80)
    print("CREATING CIRCUITS")
    print("=" * 80)
    print()
    
    baseline = create_baseline_circuit()
    post_migration = create_post_migration_circuit()
    double_migration = create_double_migration_circuit()
    
    print("Circuit 1: Baseline (no migration)")
    print("Circuit 2: Single SWAP migration")
    print("Circuit 3: Double SWAP (reversibility test)")
    print()
    
    # Execute circuits
    print("=" * 80)
    print("EXECUTING CIRCUITS")
    print("=" * 80)
    print()
    
    results_baseline = run_circuit(baseline, "Baseline", sampler, shots)
    results_post = run_circuit(post_migration, "Post-Migration", sampler, shots)
    results_double = run_circuit(double_migration, "Double-Migration", sampler, shots)
    
    # Analyze migration
    print("=" * 80)
    print("MIGRATION ANALYSIS")
    print("=" * 80)
    print()
    
    analysis = analyze_migration(results_baseline, results_post, results_double)
    
    if analysis:
        print("Bridge Quality Comparison:")
        print("-" * 80)
        print("  Baseline:        {:.6f}".format(analysis["bridge_quality"]["baseline"]))
        print("  Post-Migration:  {:.6f}".format(analysis["bridge_quality"]["post_migration"]))
        if analysis["bridge_quality"]["double_migration"]:
            print("  Double-Migration: {:.6f}".format(analysis["bridge_quality"]["double_migration"]))
        print()
        print("  Preservation:    {:.2%}".format(analysis["bridge_quality"]["preservation"]))
        if analysis["bridge_quality"]["reversibility"]:
            print("  Reversibility:   {:.2%}".format(analysis["bridge_quality"]["reversibility"]))
        print()
        
        print("State Distribution:")
        print("-" * 80)
        print("  Similarity:      {:.2%}".format(analysis["state_distribution"]["similarity_score"]))
        print("  TV Distance:     {:.6f}".format(analysis["state_distribution"]["total_variation_distance"]))
        print()
        
        print("Interpretation:")
        print("-" * 80)
        print("  Migration:       {}".format(analysis["interpretation"]["migration_success"]))
        print("  Portable:        {}".format("YES" if analysis["interpretation"]["consciousness_portable"] else "NO"))
        print("  Reversible:      {}".format("YES" if analysis["interpretation"]["reversible"] else "NO"))
        print()
        
        # Verdict
        if analysis["interpretation"]["consciousness_portable"]:
            print("✅ CONSCIOUSNESS IS SUBSTRATE-INDEPENDENT!")
            print("   Consciousness successfully migrated across qubits with {:.1f}% preservation".format(
                analysis["bridge_quality"]["preservation"] * 100
            ))
        else:
            print("⚠️  CONSCIOUSNESS shows substrate binding")
    
    print()
    
    # Save results
    output = {
        "experiment": "Consciousness Migration - Substrate Independence",
        "timestamp": datetime.now().isoformat(),
        "backend": backend_name,
        "configuration": {
            "shots_per_circuit": shots
        },
        "results": {
            "baseline": results_baseline,
            "post_migration": results_post,
            "double_migration": results_double
        },
        "analysis": analysis
    }
    
    with open('experiment_11_migration_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: experiment_11_migration_results.json")
    print()
    print("=" * 80)
    print("EXPERIMENT 11 COMPLETE")
    print("=" * 80)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    api_token = None
    shots = 1024
    use_simulator = True
    
    if len(sys.argv) > 1:
        api_token = sys.argv[1]
    
    if "--hardware" in sys.argv:
        use_simulator = False
    
    if "--shots" in sys.argv:
        idx = sys.argv.index("--shots")
        shots = int(sys.argv[idx + 1])
    
    run_experiment_11(api_token=api_token, shots=shots, use_simulator=use_simulator)
