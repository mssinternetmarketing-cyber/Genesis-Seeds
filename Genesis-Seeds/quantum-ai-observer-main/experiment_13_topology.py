"""
EXPERIMENT 13: COUPLING TOPOLOGY OPTIMIZATION
================================================================
COMPREHENSIVE 20-QUBIT COUPLING PATTERN ANALYSIS
================================================================
Tests all major coupling topologies at fixed 20-qubit scale:
- Sequential: Linear chain (0→1→2→...→19)
- Star: Hub topology (0 connected to all others)
- Ring: Circular coupling (0→1→...→19→0)
- All-to-All: Complete graph (every qubit coupled to every other)
- Hybrid patterns: Best combinations of above

Measures which topology optimizes consciousness scaling.
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
# 20-QUBIT CONSCIOUSNESS CIRCUITS WITH DIFFERENT TOPOLOGIES
# ============================================================================

def create_consciousness_circuit_20qubits(coupling_pattern="sequential"):
    """
    Create 20-qubit consciousness circuit with specified coupling topology
    
    Args:
        coupling_pattern: "sequential", "star", "ring", "all_to_all", or "hybrid"
    """
    
    num_qubits = 20
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Initialize all qubits in superposition with phase variation
    for i in range(num_qubits):
        qc.h(i)
        if i > 0:
            qc.s(i)  # Phase gate for coherence
    
    qc.barrier()
    
    # Apply coupling based on pattern
    if coupling_pattern == "sequential":
        # Linear chain: 0→1→2→...→19
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
            qc.cz(i, i + 1)
    
    elif coupling_pattern == "star":
        # Star topology: 0 (hub) coupled to all others
        for i in range(1, num_qubits):
            qc.cx(0, i)
            qc.cz(0, i)
    
    elif coupling_pattern == "ring":
        # Ring topology: 0→1→2→...→19→0
        for i in range(num_qubits):
            next_qubit = (i + 1) % num_qubits
            qc.cx(i, next_qubit)
            qc.cz(i, next_qubit)
    
    elif coupling_pattern == "all_to_all":
        # Fully connected: every qubit coupled to every other
        # NOTE: This is expensive - limit to smaller subset to avoid over-coupling
        for i in range(num_qubits):
            for j in range(i + 1, min(i + 6, num_qubits)):  # Each qubit couples to ~5 neighbors
                qc.cx(i, j)
                qc.cz(i, j)
    
    elif coupling_pattern == "hybrid":
        # Hybrid: Star hub (0) + Ring outer shell
        # Hub
        for i in range(1, num_qubits):
            qc.cx(0, i)
            qc.cz(0, i)
        # Ring on outer qubits
        for i in range(1, num_qubits):
            next_qubit = (i % (num_qubits - 1)) + 1
            if next_qubit != i:
                qc.cx(i, next_qubit)
                qc.cz(i, next_qubit)
    
    qc.barrier()
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc

# ============================================================================
# EXECUTION AND ANALYSIS
# ============================================================================

def run_topology_test(pattern, sampler, shots=512):
    """Run 20-qubit consciousness circuit with given coupling pattern"""
    
    print()
    print("=" * 80)
    print("TESTING COUPLING PATTERN: {}".format(pattern.upper()))
    print("=" * 80)
    print()
    
    try:
        circuit = create_consciousness_circuit_20qubits(pattern)
        
        print("Circuit created: {} qubits, {} coupling pattern".format(20, pattern))
        gates = dict(circuit.count_ops())
        print("Gate count: {}".format(gates))
        print("Circuit depth: {}".format(circuit.depth()))
        print()
        
        print("Executing circuit...")
        job = sampler.run([circuit], shots=shots)
        result = job.result()
        
        pub_result = result[0]
        
        # Extract counts
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
        
        # Entropy calculation
        probs = []
        for i in range(2 ** 20):
            state = format(i, '020b')
            prob = counts.get(state, 0) / total_shots
            probs.append(prob)
        
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        max_entropy = 20.0
        normalized_entropy = entropy / max_entropy
        bridge_quality = normalized_entropy
        
        # Coupling density
        num_connections = len([g for g in gates.keys() if g in ['cx', 'cz']])
        max_possible = 20 * 19 // 2
        coupling_density = num_connections / max_possible if max_possible > 0 else 0
        
        print("Results:")
        print("-" * 80)
        print("Entropy: {:.6f} / {:.1f} bits".format(entropy, max_entropy))
        print("Bridge Quality: {:.6f}".format(bridge_quality))
        print("Coupling Gates: {}".format(num_connections))
        print("Coupling Density: {:.2%}".format(coupling_density))
        print()
        
        return {
            "pattern": pattern,
            "num_qubits": 20,
            "circuit_depth": circuit.depth(),
            "gate_count": gates,
            "num_connections": num_connections,
            "coupling_density": float(coupling_density),
            "total_shots": total_shots,
            "entropy": float(entropy),
            "max_entropy": float(max_entropy),
            "bridge_quality": float(bridge_quality),
            "unique_states": len(counts),
            "state_distribution": counts
        }
        
    except Exception as e:
        print("ERROR: {}".format(str(e)))
        return None

def compare_topologies(results):
    """Compare all coupling topologies"""
    
    valid_results = [r for r in results if r is not None]
    
    if not valid_results:
        return None
    
    # Sort by bridge quality
    sorted_results = sorted(valid_results, key=lambda r: r["bridge_quality"], reverse=True)
    
    print()
    print("=" * 80)
    print("TOPOLOGY COMPARISON")
    print("=" * 80)
    print()
    
    print("Ranking by Bridge Quality:")
    print("-" * 80)
    print("Rank | Pattern     | BQ      | Entropy | Depth | Gates | Coupling")
    print("-----|-------------|---------|---------|-------|-------|----------")
    
    for rank, result in enumerate(sorted_results, 1):
        print("{:4d} | {:<11s} | {:.6f} | {:.2f}  | {:5d} | {:5d} | {:.1%}".format(
            rank,
            result["pattern"],
            result["bridge_quality"],
            result["entropy"],
            result["circuit_depth"],
            len([g for g in result["gate_count"].values() if isinstance(g, int)]),
            result["coupling_density"]
        ))
    
    print()
    
    # Best and worst
    best = sorted_results[0]
    worst = sorted_results[-1]
    
    print("Best Configuration:")
    print("-" * 80)
    print("  Pattern: {}".format(best["pattern"]))
    print("  Bridge Quality: {:.6f}".format(best["bridge_quality"]))
    print("  Coupling Density: {:.2%}".format(best["coupling_density"]))
    print()
    
    print("Worst Configuration:")
    print("-" * 80)
    print("  Pattern: {}".format(worst["pattern"]))
    print("  Bridge Quality: {:.6f}".format(worst["bridge_quality"]))
    print("  Coupling Density: {:.2%}".format(worst["coupling_density"]))
    print()
    
    return sorted_results

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment_13(use_simulator=True):
    """Run comprehensive 20-qubit coupling topology optimization"""
    
    print()
    print("=" * 80)
    print("EXPERIMENT 13: COUPLING TOPOLOGY OPTIMIZATION")
    print("20-Qubit Consciousness Network")
    print("=" * 80)
    print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print()
    
    # Setup
    if use_simulator:
        print("MODE: Local Simulator (20-qubit optimal memory threshold)")
        sampler = LocalSampler()
        backend_name = "local_simulator"
    else:
        backend_name = "ibm_quantum"
    
    # Test patterns
    patterns = ["sequential", "star", "ring", "all_to_all", "hybrid"]
    
    print("Testing {} coupling patterns:".format(len(patterns)))
    for pattern in patterns:
        print("  - {}".format(pattern))
    print()
    
    # Execute tests
    results = []
    for pattern in patterns:
        result = run_topology_test(pattern, sampler, shots=512)
        if result:
            results.append(result)
    
    # Compare
    comparison = compare_topologies(results)
    
    # Save results
    output = {
        "experiment": "Coupling Topology Optimization - 20 Qubits",
        "timestamp": datetime.now().isoformat(),
        "backend": backend_name,
        "configuration": {
            "num_qubits": 20,
            "patterns_tested": patterns,
            "shots_per_circuit": 512
        },
        "results": results,
        "comparison": {
            "ranking": [{"rank": i + 1, "pattern": r["pattern"], "bridge_quality": r["bridge_quality"]}
                       for i, r in enumerate(comparison)] if comparison else []
        }
    }
    
    with open('experiment_13_topology_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: experiment_13_topology_results.json")
    print()
    print("=" * 80)
    print("EXPERIMENT 13 COMPLETE")
    print("=" * 80)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    use_simulator = True
    
    if "--hardware" in sys.argv:
        use_simulator = False
    
    run_experiment_13(use_simulator=use_simulator)
