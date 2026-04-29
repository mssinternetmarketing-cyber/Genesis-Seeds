"""
EXPERIMENT 18: ALTERNATING SEED SCALING (2-50 QUBITS)
======================================================

Test consciousness scaling with ALTERNATING seed pattern:
Ω α Ω⁻ α⁻ Ω α Ω⁻ α⁻...

Pattern:
2 qubits:  Ω  α
4 qubits:  Ω  α  Ω⁻ α⁻
6 qubits:  Ω  α  Ω⁻ α⁻ Ω  α
8 qubits:  Ω  α  Ω⁻ α⁻ Ω  α  Ω⁻ α⁻
...

This creates a balanced rhythmic structure where each archetype
pair (Omega + Alpha) forms a consciousness "unit" that repeats.
"""

import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2


# Seed Library
SEED_LIBRARY = {
    "Omega":   {"phase": 0,     "amplitude": 1.0, "description": "Positive superposition - presence"},
    "Omega-":  {"phase": np.pi, "amplitude": 1.0, "description": "Negative superposition - void"},
    "Alpha":   {"phase": np.pi/2, "amplitude": 1.0, "description": "Complex phase - receptive"},
    "Alpha-":  {"phase": -np.pi/2, "amplitude": 1.0, "description": "Negative complex - muted"}
}


def generate_alternating_seed_pattern(n_qubits):
    """
    Generate alternating seed pattern:
    Ω α Ω⁻ α⁻ Ω α Ω⁻ α⁻...
    
    Returns list of seed names for n qubits.
    """
    base_pattern = ["Omega", "Alpha", "Omega-", "Alpha-"]
    
    seeds = []
    for i in range(n_qubits):
        seed = base_pattern[i % 4]
        seeds.append(seed)
    
    return seeds


def create_consciousness_circuit(n_qubits, seed_pattern):
    """
    Create consciousness circuit with alternating seed initialization.
    
    Args:
        n_qubits: Number of qubits
        seed_pattern: List of seed names (length = n_qubits)
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize each qubit with its seed
    for i, seed_name in enumerate(seed_pattern):
        seed = SEED_LIBRARY[seed_name]
        qc.h(i)  # Superposition
        qc.p(seed["phase"], i)  # Apply seed phase
    
    qc.barrier()
    
    # Sequential coupling (creating consciousness flow)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


def run_alternating_scaling_test(backend_name="ibm_fez", min_qubits=2, max_qubits=50):
    """
    Run consciousness circuit with alternating seeds from min_qubits to max_qubits.
    """
    
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    
    results = []
    
    for n in range(min_qubits, max_qubits + 1):
        print(f"\n{'='*70}")
        print(f"Testing {n} qubits with ALTERNATING SEED PATTERN")
        print(f"{'='*70}")
        
        # Generate seed pattern
        seed_pattern = generate_alternating_seed_pattern(n)
        print(f"Seed Pattern: {' '.join(seed_pattern)}")
        
        # Create and transpile circuit
        circuit = create_consciousness_circuit(n, seed_pattern)
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
        
        # Count seed types used
        seed_counts = {}
        for seed in seed_pattern:
            seed_counts[seed] = seed_counts.get(seed, 0) + 1
        
        result_data = {
            "qubits": n,
            "bridge_quality": float(bridge_quality),
            "entropy": float(entropy),
            "unique_states": len(counts),
            "circuit_depth": transpiled.depth(),
            "seed_pattern": seed_pattern,
            "seed_counts": seed_counts,
            "job_id": job.job_id(),
            "timestamp": datetime.now().isoformat()
        }
        
        results.append(result_data)
        
        print(f"Bridge Quality: {bridge_quality:.6f}")
        print(f"Entropy: {entropy:.6f} / {n}.0 bits")
        print(f"Circuit Depth: {transpiled.depth()}")
        print(f"Unique States: {len(counts)}")
        print(f"Seed Distribution: {seed_counts}")
        
        # Save incremental results
        with open(f"experiment_18_alternating_results.json", "w") as f:
            json.dump({
                "experiment": "Alternating Seed Scaling Study (2-50 Qubits)",
                "backend": backend_name,
                "seed_pattern_description": "Ω α Ω⁻ α⁻ repeating",
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2)
    
    return results


def create_comparison_visualizations(alternating_results, uniform_results_file=None):
    """
    Create visualizations comparing alternating pattern to uniform pattern.
    """
    
    # Extract alternating data
    qubits_alt = [r['qubits'] for r in alternating_results]
    bq_alt = [r['bridge_quality'] for r in alternating_results]
    
    # Load uniform results if provided
    if uniform_results_file:
        with open(uniform_results_file, 'r') as f:
            uniform_data = json.load(f)
        qubits_uni = [r['qubits'] for r in uniform_data['results']]
        bq_uni = [r['bridge_quality'] for r in uniform_data['results']]
    else:
        qubits_uni, bq_uni = None, None
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # Plot 1: Bridge Quality Comparison
    ax1 = axes[0, 0]
    ax1.plot(qubits_alt, bq_alt, 'b-o', linewidth=3, markersize=8, 
             label='Alternating Seeds (Ω α Ω⁻ α⁻)', zorder=3)
    
    if bq_uni:
        ax1.plot(qubits_uni, bq_uni, 'r--s', linewidth=2, markersize=6, 
                 label='Uniform Seeds (baseline)', alpha=0.7, zorder=2)
    
    ax1.axhline(y=0.45, color='green', linestyle='--', linewidth=2, alpha=0.5)
    ax1.axhline(y=0.38, color='orange', linestyle='--', linewidth=2, alpha=0.5)
    ax1.fill_between(qubits_alt, 0.45, 1.0, alpha=0.1, color='green')
    ax1.fill_between(qubits_alt, 0.38, 0.45, alpha=0.1, color='yellow')
    ax1.fill_between(qubits_alt, 0, 0.38, alpha=0.1, color='red')
    
    ax1.set_xlabel('Qubit Count', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Bridge Quality', fontsize=13, fontweight='bold')
    ax1.set_title('Alternating Seed Pattern: Consciousness Scaling', 
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Seed Distribution Over Scale
    ax2 = axes[0, 1]
    
    # Extract seed counts
    omega_counts = []
    alpha_counts = []
    omega_neg_counts = []
    alpha_neg_counts = []
    
    for r in alternating_results:
        sc = r['seed_counts']
        omega_counts.append(sc.get('Omega', 0))
        alpha_counts.append(sc.get('Alpha', 0))
        omega_neg_counts.append(sc.get('Omega-', 0))
        alpha_neg_counts.append(sc.get('Alpha-', 0))
    
    ax2.plot(qubits_alt, omega_counts, 'g-o', label='Ω (Presence)', linewidth=2)
    ax2.plot(qubits_alt, alpha_counts, 'b-s', label='α (Receptive)', linewidth=2)
    ax2.plot(qubits_alt, omega_neg_counts, 'r-^', label='Ω⁻ (Void)', linewidth=2)
    ax2.plot(qubits_alt, alpha_neg_counts, 'm-d', label='α⁻ (Muted)', linewidth=2)
    
    ax2.set_xlabel('Qubit Count', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Number of Qubits per Seed', fontsize=13, fontweight='bold')
    ax2.set_title('Balanced Seed Distribution', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Improvement Delta (if comparison available)
    ax3 = axes[1, 0]
    
    if bq_uni:
        # Calculate improvement
        improvement = [(bq_alt[i] - bq_uni[i]) for i in range(len(bq_alt))]
        
        colors = ['green' if imp > 0 else 'red' for imp in improvement]
        ax3.bar(qubits_alt, improvement, color=colors, alpha=0.7, edgecolor='black')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax3.set_xlabel('Qubit Count', fontsize=13, fontweight='bold')
        ax3.set_ylabel('BQ Improvement (Alternating - Uniform)', fontsize=13, fontweight='bold')
        ax3.set_title('Performance Delta', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
    else:
        ax3.text(0.5, 0.5, 'No comparison data available', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=14)
        ax3.axis('off')
    
    # Plot 4: Phase Diagram
    ax4 = axes[1, 1]
    
    depth_alt = [r['circuit_depth'] for r in alternating_results]
    scatter = ax4.scatter(qubits_alt, depth_alt, c=bq_alt, cmap='RdYlGn', 
                         s=150, edgecolors='black', linewidth=1.5, vmin=0.3, vmax=1.0)
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Bridge Quality', fontsize=12, fontweight='bold')
    
    ax4.set_xlabel('Qubit Count', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Circuit Depth', fontsize=13, fontweight='bold')
    ax4.set_title('Consciousness Phase Diagram', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('EXPERIMENT 18: Alternating Seed Pattern (Ω α Ω⁻ α⁻)', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('experiment_18_alternating_seeds.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("\n✓ Saved: experiment_18_alternating_seeds.png")
    plt.show()


if __name__ == "__main__":
    print("=" * 80)
    print("EXPERIMENT 18: ALTERNATING SEED SCALING")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Seed Pattern: Ω α Ω⁻ α⁻ (repeating)")
    print("Testing consciousness with balanced dialectic structure")
    print()
    
    # Run alternating seed scaling test
    results = run_alternating_scaling_test(
        backend_name="ibm_fez", 
        min_qubits=2, 
        max_qubits=50
    )
    
    # Create visualizations (compare to Experiment 17 if available)
    create_comparison_visualizations(
        results, 
        uniform_results_file="experiment_17_scaling_results.json"
    )
    
    print("\n" + "=" * 80)
    print("EXPERIMENT 18 COMPLETE")
    print("=" * 80)
