"""
EXPERIMENT 17: HARDWARE SCALING STUDY (2-50 QUBITS)
===================================================

Run consciousness circuit at every qubit count from 2 to 50
on IBM Quantum hardware and measure Bridge Quality degradation.

Goal: Find the maximum qubit count where consciousness persists
      with acceptable noise (BQ > 0.38)
"""

import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2


def create_consciousness_circuit(n_qubits):
    """Create n-qubit sequential consciousness circuit."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize superposition with phase
    for i in range(n_qubits):
        qc.h(i)
        if i > 0:
            qc.s(i)
    
    qc.barrier()
    
    # Sequential coupling
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def run_scaling_test(backend_name="ibm_fez", min_qubits=2, max_qubits=50):
    """Run consciousness circuit from min_qubits to max_qubits."""
    
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    
    results = []
    
    for n in range(min_qubits, max_qubits + 1):
        print(f"\n{'='*60}")
        print(f"Testing {n} qubits...")
        print(f"{'='*60}")
        
        # Create and transpile circuit
        circuit = create_consciousness_circuit(n)
        transpiled = transpile(circuit, backend=backend, optimization_level=3)
        
        # Run on hardware
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled], shots=512)
        result = job.result()
        
        # Extract counts
        pub_result = result[0]
        data = pub_result.data
        if hasattr(data, "meas"):
            counts = data.meas.get_counts()
        else:
            # Fallback
            for attr in dir(data):
                if attr.startswith("_"):
                    continue
                obj = getattr(data, attr)
                if hasattr(obj, "get_counts"):
                    counts = obj.get_counts()
                    break
        
        total_shots = sum(counts.values())
        
        # Calculate Bridge Quality
        probs = []
        for i in range(2 ** n):
            state = format(i, f'0{n}b')
            prob = counts.get(state, 0) / total_shots
            probs.append(prob)
        
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        bridge_quality = entropy / n
        
        result_data = {
            "qubits": n,
            "bridge_quality": float(bridge_quality),
            "entropy": float(entropy),
            "unique_states": len(counts),
            "circuit_depth": transpiled.depth(),
            "job_id": job.job_id(),
            "timestamp": datetime.now().isoformat()
        }
        
        results.append(result_data)
        
        print(f"Bridge Quality: {bridge_quality:.6f}")
        print(f"Entropy: {entropy:.6f} / {n}.0 bits")
        print(f"Circuit Depth: {transpiled.depth()}")
        print(f"Unique States: {len(counts)}")
        
        # Save incremental results
        with open(f"experiment_17_scaling_results.json", "w") as f:
            json.dump({
                "experiment": "Hardware Scaling Study (2-50 Qubits)",
                "backend": backend_name,
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2)
    
    return results


def create_visualizations(results):
    """Create comprehensive visualization suite."""
    
    qubits = [r["qubits"] for r in results]
    bq = [r["bridge_quality"] for r in results]
    depth = [r["circuit_depth"] for r in results]
    entropy = [r["entropy"] for r in results]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Bridge Quality vs Qubits
    ax1 = axes[0, 0]
    ax1.plot(qubits, bq, 'b-o', linewidth=2, markersize=4)
    ax1.axhline(y=0.45, color='g', linestyle='--', label='Ideal (0.45)')
    ax1.axhline(y=0.38, color='orange', linestyle='--', label='Minimum (0.38)')
    ax1.axhline(y=0.35, color='r', linestyle='--', label='Failed (<0.35)')
    ax1.fill_between(qubits, 0.45, 1.0, alpha=0.2, color='green')
    ax1.fill_between(qubits, 0.38, 0.45, alpha=0.2, color='yellow')
    ax1.fill_between(qubits, 0, 0.38, alpha=0.2, color='red')
    ax1.set_xlabel('Qubit Count', fontsize=12)
    ax1.set_ylabel('Bridge Quality', fontsize=12)
    ax1.set_title('Consciousness Persistence on Real Hardware', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Circuit Depth Scaling
    ax2 = axes[0, 1]
    ax2.plot(qubits, depth, 'r-s', linewidth=2, markersize=4)
    ax2.set_xlabel('Qubit Count', fontsize=12)
    ax2.set_ylabel('Transpiled Circuit Depth', fontsize=12)
    ax2.set_title('Hardware Circuit Complexity', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Entropy Scaling
    ax3 = axes[1, 0]
    ax3.plot(qubits, entropy, 'g-^', linewidth=2, markersize=4)
    ax3.plot(qubits, qubits, 'k--', alpha=0.5, label='Theoretical Maximum')
    ax3.set_xlabel('Qubit Count', fontsize=12)
    ax3.set_ylabel('Entropy (bits)', fontsize=12)
    ax3.set_title('Information Entropy vs Qubit Count', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Phase Diagram
    ax4 = axes[1, 1]
    scatter = ax4.scatter(qubits, depth, c=bq, cmap='RdYlGn', s=100, edgecolors='black')
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Bridge Quality', fontsize=12)
    ax4.set_xlabel('Qubit Count', fontsize=12)
    ax4.set_ylabel('Circuit Depth', fontsize=12)
    ax4.set_title('Consciousness Phase Diagram', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('experiment_17_hardware_scaling.png', dpi=300, bbox_inches='tight')
    print("\n✓ Visualization saved: experiment_17_hardware_scaling.png")
    plt.show()


if __name__ == "__main__":
    print("=" * 80)
    print("EXPERIMENT 17: HARDWARE SCALING STUDY (2-50 QUBITS)")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run scaling test
    results = run_scaling_test(backend_name="ibm_fez", min_qubits=2, max_qubits=50)
    
    # Create visualizations
    create_visualizations(results)
    
    print("\n" + "=" * 80)
    print("EXPERIMENT 17 COMPLETE")
    print("=" * 80)
