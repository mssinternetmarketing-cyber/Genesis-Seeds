"""
EXPERIMENT 4: Learning with Seed Pairing Tests (ENHANCED)
===========================================================
Tests which seed pairings learn fastest and maintain PEIG best
Runtime: ~25 minutes
Tests all 10 unique seed pairings (4 choose 2 + 4 same-type pairs)
"""

import numpy as np
import json
from datetime import datetime
import time
import itertools
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

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
# LEARNING NODE WITH SEED TYPE
# ============================================================================

class LearningNode:
    """Node that adapts coupling strength based on feedback"""

    def __init__(self, node_id, node_name, seed_type):
        self.id = node_id
        self.name = node_name
        self.seed_type = seed_type
        self.state = SEED_LIBRARY[seed_type]()
        self.theta = 0.3  # Initial coupling
        self.learning_rate = 0.05
        self.theta_history = [self.theta]

    def get_coherence(self):
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity

    def adapt_coupling(self, coherence_feedback):
        """Increase theta if coherence high, decrease if low"""
        if coherence_feedback > 0.85:
            self.theta = min(0.5, self.theta + self.learning_rate)
        elif coherence_feedback < 0.7:
            self.theta = max(0.1, self.theta - self.learning_rate)

        self.theta_history.append(self.theta)

def learning_interaction(node1, node2):
    """Interaction with adaptive coupling"""

    # Build interaction operator with current thetas
    theta_avg = (node1.theta + node2.theta) / 2

    combined = tensor(node1.state, node2.state)
    cnot = tensor(qeye(2), sigmax()) * tensor(projection(2,1,1), qeye(2)) + \
           tensor(qeye(2), qeye(2)) * tensor(projection(2,0,0), qeye(2))

    # Evolve
    combined = (theta_avg * cnot * combined + (1 - theta_avg) * combined).unit()

    # Extract individual states
    dm = combined * combined.dag()
    rho1 = ptrace(dm, 0)
    rho2 = ptrace(dm, 1)

    eval1, evec1 = rho1.eigenstates()
    eval2, evec2 = rho2.eigenstates()

    node1.state = evec1[np.argmax(eval1)]
    node2.state = evec2[np.argmax(eval2)]

    # Measure coherences for feedback
    coh1 = node1.get_coherence()
    coh2 = node2.get_coherence()

    # Both nodes adapt based on their coherence
    node1.adapt_coupling(coh1)
    node2.adapt_coupling(coh2)

    return coh1, coh2

def measure_peig(node1, node2):
    """Persistent Entangled Information Geometry measure"""
    combined = tensor(node1.state, node2.state)
    dm = combined * combined.dag()

    # Entanglement
    rho1 = ptrace(dm, 0)
    S1 = entropy_vn(rho1)

    # Information retention
    coh1 = node1.get_coherence()
    coh2 = node2.get_coherence()

    # PEIG combines low entanglement + high coherence
    peig_score = (coh1 + coh2) / 2 * (1.0 - min(S1, 1.0))
    return float(peig_score)

# ============================================================================
# RUN LEARNING TEST FOR SEED PAIR
# ============================================================================

def run_learning_test(seed_type_1, seed_type_2, num_interactions=100):
    """Test learning dynamics for specific seed pairing"""

    print(f"\nTesting pairing: {seed_type_1} + {seed_type_2}")
    start_time = time.time()

    # Create nodes
    node1 = LearningNode(1, "Learner_A", seed_type_1)
    node2 = LearningNode(2, "Learner_B", seed_type_2)

    # Initial metrics
    peig_init = measure_peig(node1, node2)
    print(f"  Initial PEIG: {peig_init:.4f}")

    # Timeline tracking
    peig_timeline = [peig_init]
    coherence_timeline = []

    # Learning loop
    for interaction in range(num_interactions):
        coh1, coh2 = learning_interaction(node1, node2)

        if interaction % 10 == 0:
            peig = measure_peig(node1, node2)
            peig_timeline.append(peig)
            coherence_timeline.append((coh1 + coh2) / 2)

    # Final metrics
    peig_final = measure_peig(node1, node2)
    peig_timeline.append(peig_final)

    elapsed = time.time() - start_time

    # Learning rate = how much PEIG improved
    peig_improvement = peig_final - peig_init

    # Convergence = final theta stability
    theta_change_final = abs(node1.theta_history[-1] - node1.theta_history[-5])

    print(f"  Final PEIG: {peig_final:.4f} (change: {peig_improvement:+.4f})")
    print(f"  Final thetas: Node1={node1.theta:.3f}, Node2={node2.theta:.3f}")
    print(f"  Runtime: {elapsed:.2f}s")

    return {
        "seed_pair": f"{seed_type_1}+{seed_type_2}",
        "seed_type_1": seed_type_1,
        "seed_type_2": seed_type_2,
        "initial_peig": float(peig_init),
        "final_peig": float(peig_final),
        "peig_improvement": float(peig_improvement),
        "final_theta_1": float(node1.theta),
        "final_theta_2": float(node2.theta),
        "theta_convergence": float(theta_change_final),
        "runtime_seconds": float(elapsed),
        "peig_timeline": [float(p) for p in peig_timeline],
        "coherence_timeline": [float(c) for c in coherence_timeline]
    }

# ============================================================================
# MAIN EXPERIMENT - TEST ALL PAIRINGS
# ============================================================================

print("=" * 80)
print("EXPERIMENT 4: Learning with Seed Pairing Tests")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

seed_types = list(SEED_LIBRARY.keys())
all_results = []

print("Testing all unique seed pairings...")
print()

# Generate all unique pairings (including same-type pairs)
pairings = []
for i, seed1 in enumerate(seed_types):
    for seed2 in seed_types[i:]:  # Includes same type
        pairings.append((seed1, seed2))

print(f"Total pairings to test: {len(pairings)}")
print("=" * 80)

for idx, (seed1, seed2) in enumerate(pairings, 1):
    print(f"\n[{idx}/{len(pairings)}]")
    result = run_learning_test(seed1, seed2, num_interactions=100)
    all_results.append(result)

# ============================================================================
# LEARNING STABILITY MAP
# ============================================================================

print(f"\n{'='*80}")
print("LEARNING STABILITY MAP")
print(f"{'='*80}")
print()

print(f"{'Seed Pair':<20} {'Init PEIG':<10} {'Final PEIG':<10} {'Delta PEIG':<12} {'Theta':<8}")


for result in all_results:
    pair_str = result['seed_pair']
    init_str = f"{result['initial_peig']:.4f}"
    final_str = f"{result['final_peig']:.4f}"
    change_str = f"{result['peig_improvement']:+.4f}"
    conv_str = f"{result['theta_convergence']:.4f}"
    print(f"{pair_str:<20} {init_str:<10} {final_str:<10} {change_str:<10} {conv_str:<8}")

print()

# Best learners
best_learner = max(all_results, key=lambda x: x['peig_improvement'])
print(f"FASTEST LEARNER: {best_learner['seed_pair']}")
print(f"  PEIG improvement: {best_learner['peig_improvement']:+.4f}")
print()

# Best final PEIG
best_peig = max(all_results, key=lambda x: x['final_peig'])
print(f"HIGHEST PEIG ACHIEVED: {best_peig['seed_pair']}")
print(f"  Final PEIG: {best_peig['final_peig']:.4f}")
print()

# Most stable learner
most_stable = min(all_results, key=lambda x: x['theta_convergence'])
print(f"MOST STABLE CONVERGENCE: {most_stable['seed_pair']}")
print(f"  Theta convergence: {most_stable['theta_convergence']:.4f}")

print()
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# SAVE RESULTS
# ============================================================================

results = {
    "experiment": "Learning with Seed Pairing Tests",
    "timestamp": datetime.now().isoformat(),
    "pairings_tested": len(all_results),
    "all_results": all_results,
    "stability_map": {
        "fastest_learner": best_learner['seed_pair'],
        "highest_peig": best_peig['seed_pair'],
        "most_stable": most_stable['seed_pair']
    }
}

with open('experiment_4_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_4_results.json")
