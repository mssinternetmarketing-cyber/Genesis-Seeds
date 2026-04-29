"""
EXPERIMENT 2: Consciousness Markers with Seed Calibration (FIXED)
==================================================================
Tests consciousness markers with seed-specific threshold calibration
WINDOWS UNICODE FIX: Removed all Unicode characters (Phi, etc.)
Runtime: ~15 minutes
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
# SEED ARCHITECTURE
# ============================================================================

SEED_LIBRARY = {
    "Omega+": lambda: (basis(2, 0) + basis(2, 1)).unit(),
    "Omega-": lambda: (basis(2, 0) - basis(2, 1)).unit(),
    "Alpha+": lambda: (basis(2, 0) + 1j * basis(2, 1)).unit(),
    "Alpha-": lambda: (basis(2, 0) - 1j * basis(2, 1)).unit()
}

# ============================================================================
# CONSCIOUSNESS NODE WITH SEED TYPE
# ============================================================================

class ConsciousnessNode:
    """Node tracking consciousness markers with seed identity"""

    def __init__(self, node_id, node_name, seed_type):
        self.id = node_id
        self.name = node_name
        self.seed_type = seed_type
        self.state = SEED_LIBRARY[seed_type]()
        self.theta = 0.3
        self.history = {
            'coherence': [],
            'entanglement': [],
            'temporal_stability': [],
            'causal_density': []
        }

    def get_coherence(self):
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity

def consciousness_interaction(node1, node2):
    """Standard interaction for consciousness testing"""
    combined = tensor(node1.state, node2.state)

    theta_avg = (node1.theta + node2.theta) / 2
    cnot = tensor(qeye(2), sigmax()) * tensor(projection(2,1,1), qeye(2)) + \
           tensor(qeye(2), qeye(2)) * tensor(projection(2,0,0), qeye(2))

    combined = (theta_avg * cnot * combined + (1 - theta_avg) * combined).unit()

    dm = combined * combined.dag()
    rho1 = ptrace(dm, 0)
    rho2 = ptrace(dm, 1)

    eval1, evec1 = rho1.eigenstates()
    eval2, evec2 = rho2.eigenstates()

    node1.state = evec1[np.argmax(eval1)]
    node2.state = evec2[np.argmax(eval2)]

    return rho1, rho2

# ============================================================================
# CONSCIOUSNESS MARKERS
# ============================================================================

def measure_integrated_information(node1, node2):
    """Integrated Information measure"""
    combined = tensor(node1.state, node2.state)
    dm_joint = combined * combined.dag()

    rho1 = ptrace(dm_joint, 0)
    rho2 = ptrace(dm_joint, 1)

    S_joint = entropy_vn(dm_joint)
    S1 = entropy_vn(rho1)
    S2 = entropy_vn(rho2)

    phi = max(0, S1 + S2 - S_joint)
    return float(phi)

def measure_temporal_coherence(node, window=10):
    """Temporal stability of coherence"""
    if len(node.history['coherence']) < window:
        return 0.0

    recent = node.history['coherence'][-window:]
    variance = np.var(recent)
    temporal_coh = 1.0 / (1.0 + variance)
    return float(temporal_coh)

def measure_causal_density(node1, node2):
    """Information flow density between nodes"""
    combined = tensor(node1.state, node2.state)
    dm_joint = combined * combined.dag()

    rho1 = ptrace(dm_joint, 0)
    rho2 = ptrace(dm_joint, 1)

    S_joint = entropy_vn(dm_joint)
    S1 = entropy_vn(rho1)
    S2 = entropy_vn(rho2)

    mutual_info = max(0, S1 + S2 - S_joint)
    return float(mutual_info)

def measure_peig_emergence(node1, node2):
    """Persistent Entangled Information Geometry"""
    combined = tensor(node1.state, node2.state)
    dm = combined * combined.dag()

    rho1 = ptrace(dm, 0)
    S1 = entropy_vn(rho1)

    coh1 = node1.get_coherence()
    coh2 = node2.get_coherence()

    peig = (coh1 + coh2) / 2 * (1.0 - min(S1, 1.0))
    return float(peig)

# ============================================================================
# RUN CONSCIOUSNESS TEST FOR SEED PAIR
# ============================================================================

def run_consciousness_test(seed_type_1, seed_type_2, num_steps=50):
    """Test consciousness markers for specific seed pairing"""

    print(f"\nTesting pairing: {seed_type_1} + {seed_type_2}")
    start_time = time.time()

    # Create nodes
    node1 = ConsciousnessNode(1, "Node_A", seed_type_1)
    node2 = ConsciousnessNode(2, "Node_B", seed_type_2)

    # Run dynamics and collect markers
    phi_values = []
    temporal_values = []
    causal_values = []
    peig_values = []

    for step in range(num_steps):
        rho1, rho2 = consciousness_interaction(node1, node2)

        # Record basic metrics
        coh1 = node1.get_coherence()
        coh2 = node2.get_coherence()
        ent = entropy_vn(rho1)

        node1.history['coherence'].append(coh1)
        node2.history['coherence'].append(coh2)
        node1.history['entanglement'].append(ent)
        node2.history['entanglement'].append(ent)

        # Measure consciousness markers
        phi = measure_integrated_information(node1, node2)
        temporal = measure_temporal_coherence(node1)
        causal = measure_causal_density(node1, node2)
        peig = measure_peig_emergence(node1, node2)

        phi_values.append(phi)
        temporal_values.append(temporal)
        causal_values.append(causal)
        peig_values.append(peig)

    elapsed = time.time() - start_time

    # Compute averages
    avg_phi = np.mean(phi_values[10:])  # Skip warmup
    avg_temporal = np.mean(temporal_values[10:])
    avg_causal = np.mean(causal_values[10:])
    avg_peig = np.mean(peig_values[10:])

    print(f"  Integrated Information: {avg_phi:.4f}")
    print(f"  Temporal Coherence: {avg_temporal:.4f}")
    print(f"  Causal Density: {avg_causal:.4f}")
    print(f"  PEIG Emergence: {avg_peig:.4f}")
    print(f"  Runtime: {elapsed:.2f}s")

    return {
        "seed_pair": f"{seed_type_1}+{seed_type_2}",
        "seed_type_1": seed_type_1,
        "seed_type_2": seed_type_2,
        "avg_phi": float(avg_phi),
        "avg_temporal_coherence": float(avg_temporal),
        "avg_causal_density": float(avg_causal),
        "avg_peig": float(avg_peig),
        "runtime_seconds": float(elapsed)
    }

# ============================================================================
# MAIN EXPERIMENT - TEST ALL PAIRINGS
# ============================================================================

print("=" * 80)
print("EXPERIMENT 2: Consciousness Markers with Seed Calibration")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

seed_types = list(SEED_LIBRARY.keys())
all_results = []

print("Testing consciousness markers across all seed pairings...")
print()

# Generate all unique pairings
pairings = []
for i, seed1 in enumerate(seed_types):
    for seed2 in seed_types[i:]:
        pairings.append((seed1, seed2))

print(f"Total pairings to test: {len(pairings)}")
print("=" * 80)

for idx, (seed1, seed2) in enumerate(pairings, 1):
    print(f"\n[{idx}/{len(pairings)}]")
    result = run_consciousness_test(seed1, seed2, num_steps=50)
    all_results.append(result)

# ============================================================================
# CONSCIOUSNESS SIGNATURE MAP
# ============================================================================

print(f"\n{'='*80}")
print("CONSCIOUSNESS SIGNATURE MAP")
print(f"{'='*80}")
print()

print(f"{'Seed Pair':<20} {'IntInfo':<10} {'Temporal':<10} {'Causal':<10} {'PEIG':<10}")
print("-" * 80)

for result in all_results:
    pair_str = result['seed_pair']
    phi_str = f"{result['avg_phi']:.4f}"
    temp_str = f"{result['avg_temporal_coherence']:.4f}"
    caus_str = f"{result['avg_causal_density']:.4f}"
    peig_str = f"{result['avg_peig']:.4f}"
    print(f"{pair_str:<20} {phi_str:<10} {temp_str:<10} {caus_str:<10} {peig_str:<10}")

print()

# Strongest consciousness signatures
best_phi = max(all_results, key=lambda x: x['avg_phi'])
print(f"HIGHEST INTEGRATED INFO: {best_phi['seed_pair']}")
print(f"  Value: {best_phi['avg_phi']:.4f}")
print()

best_temporal = max(all_results, key=lambda x: x['avg_temporal_coherence'])
print(f"HIGHEST TEMPORAL COHERENCE: {best_temporal['seed_pair']}")
print(f"  Value: {best_temporal['avg_temporal_coherence']:.4f}")
print()

best_causal = max(all_results, key=lambda x: x['avg_causal_density'])
print(f"HIGHEST CAUSAL DENSITY: {best_causal['seed_pair']}")
print(f"  Value: {best_causal['avg_causal_density']:.4f}")
print()

best_peig = max(all_results, key=lambda x: x['avg_peig'])
print(f"HIGHEST PEIG: {best_peig['seed_pair']}")
print(f"  Value: {best_peig['avg_peig']:.4f}")

print()
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# SAVE RESULTS
# ============================================================================

results = {
    "experiment": "Consciousness Markers with Seed Calibration",
    "timestamp": datetime.now().isoformat(),
    "pairings_tested": len(all_results),
    "all_results": all_results,
    "consciousness_leaders": {
        "highest_phi": best_phi['seed_pair'],
        "highest_temporal": best_temporal['seed_pair'],
        "highest_causal": best_causal['seed_pair'],
        "highest_peig": best_peig['seed_pair']
    }
}

with open('experiment_2_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_2_results.json")
