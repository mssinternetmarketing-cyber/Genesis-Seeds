"""
EXPERIMENT 1: Brotherhood Validation with Seed Pairing Tests (ENHANCED)
========================================================================
Tests Brotherhood dynamics across all seed pairings
Runtime: ~30 minutes
Tests all 10 unique seed pairings to identify which naturally form Brotherhood
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
# BROTHERHOOD NODE WITH SEED TYPE
# ============================================================================

class BrotherhoodNode:
    """Node tracking Brotherhood dynamics with seed identity"""

    def __init__(self, node_id, node_name, seed_type):
        self.id = node_id
        self.name = node_name
        self.seed_type = seed_type
        self.state = SEED_LIBRARY[seed_type]()
        self.theta = 0.3
        self.coherence_history = []
        self.entanglement_history = []

    def get_coherence(self):
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity

    def record_metrics(self, coherence, entanglement):
        self.coherence_history.append(coherence)
        self.entanglement_history.append(entanglement)

def brotherhood_interaction(node1, node2):
    """Standard Brotherhood interaction"""
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

    # Measure metrics
    coh1 = node1.get_coherence()
    coh2 = node2.get_coherence()
    ent = entropy_vn(rho1)

    node1.record_metrics(coh1, ent)
    node2.record_metrics(coh2, ent)

    return coh1, coh2, ent

def detect_brotherhood_event(node1, node2, window=10):
    """Detect if Brotherhood criteria met in recent history"""
    if len(node1.coherence_history) < window:
        return False

    recent_coh = node1.coherence_history[-window:]
    recent_ent = node1.entanglement_history[-window:]

    avg_coh = np.mean(recent_coh)
    avg_ent = np.mean(recent_ent)

    # Brotherhood: High coherence (>0.85) + Low entanglement (<0.3)
    return avg_coh > 0.85 and avg_ent < 0.3

# ============================================================================
# RUN BROTHERHOOD TEST FOR SEED PAIR
# ============================================================================

def run_brotherhood_test(seed_type_1, seed_type_2, num_steps=100):
    """Test Brotherhood dynamics for specific seed pairing"""

    print(f"\nTesting pairing: {seed_type_1} + {seed_type_2}")
    start_time = time.time()

    # Create nodes
    node1 = BrotherhoodNode(1, "Omega", seed_type_1)
    node2 = BrotherhoodNode(2, "Alpha", seed_type_2)

    # Run dynamics
    brotherhood_events = 0
    timeline = []

    for step in range(num_steps):
        coh1, coh2, ent = brotherhood_interaction(node1, node2)

        timeline.append({
            "step": step,
            "coherence_1": float(coh1),
            "coherence_2": float(coh2),
            "entanglement": float(ent)
        })

        # Check for Brotherhood
        if step >= 10 and detect_brotherhood_event(node1, node2):
            brotherhood_events += 1

    elapsed = time.time() - start_time

    # Final metrics
    final_coh = (node1.coherence_history[-1] + node2.coherence_history[-1]) / 2
    final_ent = node1.entanglement_history[-1]
    avg_coh = (np.mean(node1.coherence_history) + np.mean(node2.coherence_history)) / 2
    avg_ent = np.mean(node1.entanglement_history)

    brotherhood_ratio = brotherhood_events / (num_steps - 10)

    print(f"  Final coherence: {final_coh:.4f}")
    print(f"  Final entanglement: {final_ent:.4f}")
    print(f"  Brotherhood events: {brotherhood_events}/{num_steps-10} ({brotherhood_ratio:.1%})")
    print(f"  Runtime: {elapsed:.2f}s")

    return {
        "seed_pair": f"{seed_type_1}+{seed_type_2}",
        "seed_type_1": seed_type_1,
        "seed_type_2": seed_type_2,
        "final_coherence": float(final_coh),
        "final_entanglement": float(final_ent),
        "average_coherence": float(avg_coh),
        "average_entanglement": float(avg_ent),
        "brotherhood_events": int(brotherhood_events),
        "brotherhood_ratio": float(brotherhood_ratio),
        "runtime_seconds": float(elapsed),
        "timeline": timeline
    }

# ============================================================================
# MAIN EXPERIMENT - TEST ALL PAIRINGS
# ============================================================================

print("=" * 80)
print("EXPERIMENT 1: Brotherhood Validation with Seed Pairing Tests")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

seed_types = list(SEED_LIBRARY.keys())
all_results = []

print("Testing all unique seed pairings...")
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
    result = run_brotherhood_test(seed1, seed2, num_steps=100)
    all_results.append(result)

# ============================================================================
# BROTHERHOOD STABILITY MAP
# ============================================================================

print(f"\n{'='*80}")
print("BROTHERHOOD STABILITY MAP")
print(f"{'='*80}")
print()

print(f"{'Seed Pair':<20} {'Avg Coh':<10} {'Avg Ent':<10} {'B-Events':<10} {'B-Ratio':<8}")
print("-" * 80)

for result in all_results:
    pair_str = result['seed_pair']
    coh_str = f"{result['average_coherence']:.4f}"
    ent_str = f"{result['average_entanglement']:.4f}"
    events_str = f"{result['brotherhood_events']}"
    ratio_str = f"{result['brotherhood_ratio']:.1%}"
    print(f"{pair_str:<20} {coh_str:<10} {ent_str:<10} {events_str:<10} {ratio_str:<8}")

print()

# Best Brotherhood pair
best_brotherhood = max(all_results, key=lambda x: x['brotherhood_ratio'])
print(f"BEST BROTHERHOOD PAIR: {best_brotherhood['seed_pair']}")
print(f"  Brotherhood ratio: {best_brotherhood['brotherhood_ratio']:.1%}")
print(f"  Avg coherence: {best_brotherhood['average_coherence']:.4f}")
print(f"  Avg entanglement: {best_brotherhood['average_entanglement']:.4f}")
print()

# Most coherent pair
most_coherent = max(all_results, key=lambda x: x['average_coherence'])
print(f"MOST COHERENT PAIR: {most_coherent['seed_pair']}")
print(f"  Avg coherence: {most_coherent['average_coherence']:.4f}")
print()

# Lowest entanglement pair
least_entangled = min(all_results, key=lambda x: x['average_entanglement'])
print(f"LEAST ENTANGLED PAIR: {least_entangled['seed_pair']}")
print(f"  Avg entanglement: {least_entangled['average_entanglement']:.4f}")

print()
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# SAVE RESULTS
# ============================================================================

results = {
    "experiment": "Brotherhood Validation with Seed Pairing Tests",
    "timestamp": datetime.now().isoformat(),
    "pairings_tested": len(all_results),
    "all_results": all_results,
    "stability_map": {
        "best_brotherhood_pair": best_brotherhood['seed_pair'],
        "most_coherent_pair": most_coherent['seed_pair'],
        "least_entangled_pair": least_entangled['seed_pair']
    }
}

with open('experiment_1_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_1_results.json")
