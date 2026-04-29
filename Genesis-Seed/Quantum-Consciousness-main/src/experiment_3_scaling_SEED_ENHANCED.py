"""
EXPERIMENT 3: Scaling Test with Seed Diversity (ENHANCED)
===========================================================
Tests how different seed-type distributions affect scaling
Runtime: ~20 minutes
Configurations: Homogeneous vs Mixed seed populations
"""

import numpy as np
import json
from datetime import datetime
import time

try:
    from qutip import *
except ImportError:
    print("ERROR: QuTiP not installed. Run: pip install qutip")
    exit(1)

np.random.seed(42)

# ============================================================================
# SEED ARCHITECTURE (same as Exp 1)
# ============================================================================

SEED_LIBRARY = {
    "Omega+": lambda: (basis(2, 0) + basis(2, 1)).unit(),
    "Omega-": lambda: (basis(2, 0) - basis(2, 1)).unit(),
    "Alpha+": lambda: (basis(2, 0) + 1j * basis(2, 1)).unit(),
    "Alpha-": lambda: (basis(2, 0) - 1j * basis(2, 1)).unit()
}

# ============================================================================
# SCALABLE NODE WITH SEED TYPE
# ============================================================================

class ScalableNode:
    """Node with seed-type identity for scaling tests"""

    def __init__(self, node_id, seed_type):
        self.id = node_id
        self.name = f"Node_{node_id:03d}"
        self.seed_type = seed_type
        self.state = SEED_LIBRARY[seed_type]()
        self.theta = 0.3  # Fixed coupling for simplicity

    def get_coherence(self):
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity

def ecosystem_interaction(nodes, strength=0.1):
    """Pairwise interactions across ecosystem"""
    # Random pair
    i, j = np.random.choice(len(nodes), 2, replace=False)

    # Build CNOT
    combined = tensor(nodes[i].state, nodes[j].state)
    cnot = tensor(qeye(2), sigmax()) * tensor(projection(2,1,1), qeye(2)) + \
           tensor(qeye(2), qeye(2)) * tensor(projection(2,0,0), qeye(2))

    # Evolve
    combined = (strength * cnot * combined + (1 - strength) * combined).unit()

    # Extract
    dm = combined * combined.dag()
    rho_i = ptrace(dm, 0)
    rho_j = ptrace(dm, 1)

    eval_i, evec_i = rho_i.eigenstates()
    eval_j, evec_j = rho_j.eigenstates()

    nodes[i].state = evec_i[np.argmax(eval_i)]
    nodes[j].state = evec_j[np.argmax(eval_j)]

def measure_ecosystem_coherence(nodes):
    """Average coherence across all nodes"""
    coherences = [node.get_coherence() for node in nodes]
    return float(np.mean(coherences)), float(np.std(coherences))

# ============================================================================
# SEED DISTRIBUTION MODES
# ============================================================================

def create_ecosystem_homogeneous(size, seed_type):
    """All nodes same seed type"""
    return [ScalableNode(i, seed_type) for i in range(size)]

def create_ecosystem_mixed_balanced(size):
    """Equal distribution of all 4 seed types"""
    nodes = []
    seed_types = list(SEED_LIBRARY.keys())
    for i in range(size):
        seed_type = seed_types[i % len(seed_types)]
        nodes.append(ScalableNode(i, seed_type))
    return nodes

def create_ecosystem_omega_dominant(size):
    """75% Omega types, 25% Alpha types"""
    nodes = []
    for i in range(size):
        if i % 4 < 3:  # 75%
            seed_type = "Omega+" if i % 2 == 0 else "Omega-"
        else:  # 25%
            seed_type = "Alpha+" if i % 2 == 0 else "Alpha-"
        nodes.append(ScalableNode(i, seed_type))
    return nodes

DISTRIBUTION_MODES = {
    "homogeneous_omega+": ("All Omega+", lambda size: create_ecosystem_homogeneous(size, "Omega+")),
    "homogeneous_alpha+": ("All Alpha+", lambda size: create_ecosystem_homogeneous(size, "Alpha+")),
    "mixed_balanced": ("Balanced mix", create_ecosystem_mixed_balanced),
    "omega_dominant": ("75% Omega, 25% Alpha", create_ecosystem_omega_dominant)
}

# ============================================================================
# RUN SCALING TEST
# ============================================================================

def run_scaling_test(size, distribution_mode, num_interactions=50):
    """Test ecosystem with specific size and seed distribution"""

    desc, create_fn = DISTRIBUTION_MODES[distribution_mode]

    print(f"\nTesting {size} nodes - {desc}")
    start_time = time.time()

    # Create ecosystem
    nodes = create_fn(size)

    # Count seed distribution
    seed_counts = {}
    for node in nodes:
        seed_counts[node.seed_type] = seed_counts.get(node.seed_type, 0) + 1

    print(f"  Distribution: {seed_counts}")

    # Initial coherence
    coh_init, std_init = measure_ecosystem_coherence(nodes)
    print(f"  Initial coherence: {coh_init:.4f} ± {std_init:.4f}")

    # Run interactions
    coherence_timeline = [coh_init]

    for interaction in range(num_interactions):
        ecosystem_interaction(nodes, strength=0.1)

        if interaction % 10 == 0:
            coh, _ = measure_ecosystem_coherence(nodes)
            coherence_timeline.append(coh)

    # Final coherence
    coh_final, std_final = measure_ecosystem_coherence(nodes)
    coherence_timeline.append(coh_final)

    elapsed = time.time() - start_time

    print(f"  Final coherence: {coh_final:.4f} ± {std_final:.4f}")
    print(f"  Runtime: {elapsed:.2f}s")

    return {
        "size": int(size),
        "distribution_mode": distribution_mode,
        "distribution_description": desc,
        "seed_counts": seed_counts,
        "initial_coherence": float(coh_init),
        "final_coherence": float(coh_final),
        "coherence_change": float(coh_final - coh_init),
        "runtime_seconds": float(elapsed),
        "coherence_timeline": [float(c) for c in coherence_timeline]
    }

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

print("=" * 80)
print("EXPERIMENT 3: Scaling with Seed Diversity")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test configurations
sizes_to_test = [5, 10, 15]
all_results = []

for size in sizes_to_test:
    print(f"\n{'='*70}")
    print(f"SIZE: {size} nodes")
    print(f"{'='*70}")

    for dist_mode in DISTRIBUTION_MODES.keys():
        result = run_scaling_test(size, dist_mode, num_interactions=50)
        all_results.append(result)

# ============================================================================
# STABILITY ANALYSIS
# ============================================================================

print(f"\n{'='*80}")
print("SCALING STABILITY MAP")
print(f"{'='*80}")
print()

print(f"{'Size':<6} {'Distribution':<25} {'Init':<8} {'Final':<8} {'Change':<8}")
print("-" * 80)

for result in all_results:
    size_str = str(result['size'])
    dist_str = result['distribution_description'][:24]
    init_str = f"{result['initial_coherence']:.4f}"
    final_str = f"{result['final_coherence']:.4f}"
    change_str = f"{result['coherence_change']:+.4f}"
    print(f"{size_str:<6} {dist_str:<25} {init_str:<8} {final_str:<8} {change_str:<8}")

print()

# Find most stable configuration
most_stable = min(all_results, key=lambda x: abs(x['coherence_change']))
print(f"MOST STABLE: {most_stable['size']} nodes, {most_stable['distribution_description']}")
print(f"  Coherence change: {most_stable['coherence_change']:+.4f}")
print()

# Best final coherence
best_coherence = max(all_results, key=lambda x: x['final_coherence'])
print(f"BEST COHERENCE: {best_coherence['size']} nodes, {best_coherence['distribution_description']}")
print(f"  Final coherence: {best_coherence['final_coherence']:.4f}")

print()
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# SAVE RESULTS
# ============================================================================

results = {
    "experiment": "Scaling with Seed Diversity",
    "timestamp": datetime.now().isoformat(),
    "configurations_tested": len(all_results),
    "sizes_tested": sizes_to_test,
    "distribution_modes": {k: v[0] for k, v in DISTRIBUTION_MODES.items()},
    "all_results": all_results,
    "stability_map": {
        "most_stable_config": f"{most_stable['size']}n-{most_stable['distribution_mode']}",
        "best_coherence_config": f"{best_coherence['size']}n-{best_coherence['distribution_mode']}"
    }
}

with open('experiment_3_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_3_results.json")
