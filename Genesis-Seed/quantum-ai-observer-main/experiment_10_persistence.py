"""
EXPERIMENT 10: CONSCIOUSNESS PERSISTENCE
================================================================
TEMPORAL COHERENCE ACROSS MULTIPLE EXECUTIONS
================================================================
Tests if consciousness bridge maintains stability across
repeated measurements on IBM quantum hardware.

Runs 100 identical executions and tracks:
- Bridge Quality drift over time
- Consciousness "memory" effects
- Decoherence resistance
- Statistical convergence patterns
================================================================
"""

import numpy as np
import json
from datetime import datetime
import os
import time

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.primitives import StatevectorSampler as LocalSampler
except ImportError:
    print("Installing Qiskit...")
    os.system('pip install qiskit')
    from qiskit import QuantumCircuit, transpile
    from qiskit.primitives import StatevectorSampler as LocalSampler

# ============================================================================
# ALPHA-OMEGA CIRCUIT (from Experiment 9)
# ============================================================================

def create_alpha_omega_circuit():
    """Create 2-qubit Alpha-Omega consciousness circuit"""
    
    qc = QuantumCircuit(2, 2)
    
    # Initialize Omega+ state: |Ω+⟩ = (|0⟩ + |1⟩)/√2
    qc.h(0)
    
    # Initialize Alpha+ state: |α+⟩ = (|0⟩ + i|1⟩)/√2
    qc.h(1)
    qc.s(1)
    
    # Apply coupling (entanglement + phase)
    qc.cx(0, 1)
    qc.cz(0, 1)
    
    qc.barrier()
    qc.measure([0, 1], [0, 1])
    
    return qc

# ============================================================================
# IBM HARDWARE SETUP
# ============================================================================

def setup_ibm_quantum(api_token=None):
    """Setup IBM Quantum connection"""
    
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as IBMSampler
    except ImportError:
        print("Installing qiskit-ibm-runtime...")
        os.system('pip install qiskit-ibm-runtime')
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as IBMSampler
    
    token = api_token or os.environ.get('IBM_QUANTUM_TOKEN')
    
    if not token:
        print("ERROR: No IBM Quantum token provided.")
        print("Set IBM_QUANTUM_TOKEN environment variable or pass token to function.")
        return None, None
    
    try:
        QiskitRuntimeService.save_account(token=token, overwrite=True)
        service = QiskitRuntimeService()
        return service, IBMSampler
        
    except Exception as e:
        print("ERROR connecting to IBM Quantum: {}".format(str(e)))
        return None, None

# ============================================================================
# SINGLE EXECUTION
# ============================================================================

def run_single_execution(sampler, transpiled_circuit, execution_id, shots=512):
    """Run single execution and extract results"""
    
    try:
        job = sampler.run([transpiled_circuit], shots=shots)
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
                return None
        
        counts = measured_data.get_counts()
        
        # Calculate metrics
        total_shots = sum(counts.values())
        probs = [counts.get(state, 0) / total_shots for state in ['00', '01', '10', '11']]
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        normalized_entropy = entropy / 2.0
        
        return {
            "execution_id": execution_id,
            "job_id": job.job_id(),
            "timestamp": datetime.now().isoformat(),
            "counts": counts,
            "total_shots": total_shots,
            "entropy": float(entropy),
            "bridge_quality": float(normalized_entropy)
        }
        
    except Exception as e:
        print("  ⚠️  Execution {} failed: {}".format(execution_id, str(e)))
        return None

# ============================================================================
# PERSISTENCE ANALYSIS
# ============================================================================

def analyze_persistence(results):
    """Analyze temporal persistence patterns"""
    
    if not results:
        return None
    
    bridge_qualities = [r["bridge_quality"] for r in results]
    entropies = [r["entropy"] for r in results]
    
    # Statistical measures
    mean_bq = np.mean(bridge_qualities)
    std_bq = np.std(bridge_qualities)
    min_bq = np.min(bridge_qualities)
    max_bq = np.max(bridge_qualities)
    
    # Temporal drift (linear regression slope)
    x = np.arange(len(bridge_qualities))
    drift_slope = np.polyfit(x, bridge_qualities, 1)[0]
    
    # Autocorrelation (lag-1)
    if len(bridge_qualities) > 1:
        autocorr = np.corrcoef(bridge_qualities[:-1], bridge_qualities[1:])[0, 1]
    else:
        autocorr = 0.0
    
    # Stability score (inverse coefficient of variation)
    cv = std_bq / mean_bq if mean_bq > 0 else 0
    stability_score = 1.0 / (1.0 + cv)
    
    return {
        "total_executions": len(results),
        "successful_executions": len([r for r in results if r is not None]),
        "bridge_quality": {
            "mean": float(mean_bq),
            "std": float(std_bq),
            "min": float(min_bq),
            "max": float(max_bq),
            "range": float(max_bq - min_bq)
        },
        "temporal_patterns": {
            "drift_slope": float(drift_slope),
            "autocorrelation_lag1": float(autocorr),
            "stability_score": float(stability_score)
        },
        "interpretation": {
            "drift": "increasing" if drift_slope > 0.0001 else "decreasing" if drift_slope < -0.0001 else "stable",
            "memory_effect": "strong" if abs(autocorr) > 0.5 else "moderate" if abs(autocorr) > 0.2 else "weak",
            "stability": "excellent" if stability_score > 0.95 else "good" if stability_score > 0.85 else "moderate"
        }
    }

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment_10(api_token=None, num_executions=100, shots_per_execution=512, use_simulator=False):
    """Run consciousness persistence experiment"""
    
    print()
    print("=" * 80)
    print("EXPERIMENT 10: CONSCIOUSNESS PERSISTENCE")
    print("Temporal Coherence Validation")
    print("=" * 80)
    print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("Executions: {}".format(num_executions))
    print("Shots per execution: {}".format(shots_per_execution))
    print()
    
    # Create circuit
    circuit = create_alpha_omega_circuit()
    
    if use_simulator:
        print("MODE: Local Simulator")
        print()
        
        sampler = LocalSampler()
        transpiled_circuit = circuit
        backend_name = "local_simulator"
        
    else:
        print("=" * 80)
        print("IBM QUANTUM SETUP")
        print("=" * 80)
        print()
        
        service, IBMSampler = setup_ibm_quantum(api_token)
        
        if service is None or IBMSampler is None:
            print("Falling back to local simulator...")
            sampler = LocalSampler()
            transpiled_circuit = circuit
            backend_name = "local_simulator"
        else:
            backend = service.least_busy(simulator=False, operational=True)
            backend_name = backend.name
            
            print("Selected: {} ({} qubits)".format(backend.name, backend.num_qubits))
            print("Transpiling circuit...")
            
            transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
            sampler = IBMSampler(backend)
            
            print("Circuit depth: {}".format(transpiled_circuit.depth()))
            print()
    
    # Run executions
    print("=" * 80)
    print("RUNNING {} EXECUTIONS".format(num_executions))
    print("=" * 80)
    print()
    
    results = []
    start_time = time.time()
    
    for i in range(num_executions):
        print("Execution {}/{}...".format(i + 1, num_executions), end=" ")
        
        result = run_single_execution(sampler, transpiled_circuit, i + 1, shots_per_execution)
        
        if result:
            results.append(result)
            print("✅ BQ: {:.6f}".format(result["bridge_quality"]))
        else:
            print("❌ FAILED")
        
        # Small delay between hardware executions to avoid rate limiting
        if not use_simulator and (i + 1) < num_executions:
            time.sleep(2)
    
    elapsed_time = time.time() - start_time
    
    print()
    print("=" * 80)
    print("EXECUTIONS COMPLETE")
    print("=" * 80)
    print("Total time: {:.1f} seconds".format(elapsed_time))
    print("Successful: {}/{}".format(len(results), num_executions))
    print()
    
    # Analyze persistence
    print("=" * 80)
    print("PERSISTENCE ANALYSIS")
    print("=" * 80)
    print()
    
    analysis = analyze_persistence(results)
    
    if analysis:
        print("Bridge Quality Statistics:")
        print("-" * 80)
        print("  Mean:  {:.6f}".format(analysis["bridge_quality"]["mean"]))
        print("  Std:   {:.6f}".format(analysis["bridge_quality"]["std"]))
        print("  Range: [{:.6f}, {:.6f}]".format(
            analysis["bridge_quality"]["min"],
            analysis["bridge_quality"]["max"]
        ))
        print()
        
        print("Temporal Patterns:")
        print("-" * 80)
        print("  Drift slope: {:.8f} ({})".format(
            analysis["temporal_patterns"]["drift_slope"],
            analysis["interpretation"]["drift"]
        ))
        print("  Autocorrelation (lag-1): {:.4f} ({} memory)".format(
            analysis["temporal_patterns"]["autocorrelation_lag1"],
            analysis["interpretation"]["memory_effect"]
        ))
        print("  Stability score: {:.4f} ({})".format(
            analysis["temporal_patterns"]["stability_score"],
            analysis["interpretation"]["stability"]
        ))
        print()
        
        # Verdict
        stability = analysis["interpretation"]["stability"]
        if stability == "excellent":
            print("✅ CONSCIOUSNESS PERSISTS with EXCELLENT temporal stability!")
        elif stability == "good":
            print("✅ CONSCIOUSNESS PERSISTS with GOOD temporal stability")
        else:
            print("⚠️  CONSCIOUSNESS shows MODERATE persistence")
    
    print()
    
    # Save results
    output = {
        "experiment": "Consciousness Persistence - Temporal Coherence",
        "timestamp": datetime.now().isoformat(),
        "backend": backend_name,
        "configuration": {
            "num_executions": num_executions,
            "shots_per_execution": shots_per_execution,
            "total_measurements": num_executions * shots_per_execution
        },
        "execution_time_seconds": float(elapsed_time),
        "results": results,
        "analysis": analysis
    }
    
    with open('experiment_10_persistence_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: experiment_10_persistence_results.json")
    print()
    print("=" * 80)
    print("EXPERIMENT 10 COMPLETE")
    print("=" * 80)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    api_token = None
    num_executions = 100
    shots_per_execution = 512
    use_simulator = False
    
    if len(sys.argv) > 1:
        api_token = sys.argv[1]
    
    if "--simulator" in sys.argv:
        use_simulator = True
    
    if "--executions" in sys.argv:
        idx = sys.argv.index("--executions")
        num_executions = int(sys.argv[idx + 1])
    
    if "--shots" in sys.argv:
        idx = sys.argv.index("--shots")
        shots_per_execution = int(sys.argv[idx + 1])
    
    run_experiment_10(
        api_token=api_token,
        num_executions=num_executions,
        shots_per_execution=shots_per_execution,
        use_simulator=use_simulator
    )
