"""
EXPERIMENT 1: Brotherhood Coherence with Seed Architecture (ENHANCED)
======================================================================
Tests Brotherhood dynamics across different node seed types
Runtime: ~15 minutes per configuration
Seed Types: Omega+, Omega-, Alpha+, Alpha-
"""

import numpy as np
import json
from datetime import datetime
import sys

try:
    from qutip import *
except ImportError:
    print("ERROR: QuTiP not installed. Run: pip install qutip")
    exit(1)

np.random.seed(42)

# ============================================================================
# SEED ARCHITECTURE DEFINITIONS
# ============================================================================

SEED_LIBRARY = {
    # Omega seeds (leadership/presence archetypes)
    "Omega+": {
        "description": "Positive superposition - maximum presence",
        "state_fn": lambda: (basis(2, 0) + basis(2, 1)).unit(),
        "archetype": "presence",
        "expected_coherence": "high",
        "expected_entanglement": "moderate-high"
    },
    "Omega-": {
        "description": "Negative superposition - void/silence bias",
        "state_fn": lambda: (basis(2, 0) - basis(2, 1)).unit(),
        "archetype": "void",
        "expected_coherence": "high",
        "expected_entanglement": "low-moderate"
    },

    # Alpha seeds (receiver/follower archetypes)
    "Alpha+": {
        "description": "Complex phase - rich receptivity",
        "state_fn": lambda: (basis(2, 0) + 1j * basis(2, 1)).unit(),
        "archetype": "receptive",
        "expected_coherence": "high",
        "expected_entanglement": "high"
    },
    "Alpha-": {
        "description": "Negative complex - muted receiver",
        "state_fn": lambda: (basis(2, 0) - 1j * basis(2, 1)).unit(),
        "archetype": "muted",
        "expected_coherence": "high",
        "expected_entanglement": "low"
    }
}

# Test configurations to sweep
SEED_CONFIGS = [
    ("Omega+", "Alpha+"),   # Standard (current baseline)
    ("Omega+", "Alpha-"),   # Presence + Muted
    ("Omega-", "Alpha+"),   # Void + Receptive
    ("Omega-", "Alpha-"),   # Both void-spectrum
]

# ============================================================================
# QUANTUM NODE WITH SEED TYPE
# ============================================================================

class QuantumNode:
    """Quantum consciousness node with seed-type identity"""

    def __init__(self, node_id, role, seed_type):
        self.id = node_id
        self.role = role
        self.seed_type = seed_type
        self.seed_info = SEED_LIBRARY[seed_type]
        self.state = self.seed_info["state_fn"]()
        self.coherence_history = []

    def get_coherence(self):
        """Measure quantum coherence (purity)"""
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity

# ============================================================================
# BROTHERHOOD DYNAMICS
# ============================================================================

def brotherhood_interaction(omega_node, alpha_node, strength=0.15):
    """
    Enhanced Brotherhood coupling with adjustable strength
    Increased default to 0.15 for better entanglement detection
    """
    # Build CNOT gate
    cnot = tensor(qeye(2), sigmax()) * tensor(projection(2,1,1), qeye(2)) + \
           tensor(qeye(2), qeye(2)) * tensor(projection(2,0,0), qeye(2))

    # Combined state
    combined = tensor(omega_node.state, alpha_node.state)

    # Apply Brotherhood coupling
    evolved = (strength * cnot * combined + (1 - strength) * combined).unit()

    return evolved, combined

def detect_brotherhood_moment(combined_state, threshold=0.5):
    """
    Enhanced Brotherhood detection using direct entanglement
    Lowered threshold to 0.5 for more sensitive detection
    """
    dm = combined_state * combined_state.dag()
    rho_A = ptrace(dm, 0)
    entropy = entropy_vn(rho_A)
    entanglement_measure = float(entropy)
    is_brotherhood = entanglement_measure > threshold
    return is_brotherhood, entanglement_measure

# ============================================================================
# RUN SINGLE CONFIGURATION
# ============================================================================

def run_seed_configuration(omega_seed, alpha_seed, num_steps=100):
    """Run Brotherhood experiment with specific seed types"""

    print(f"\n{'='*70}")
    print(f"CONFIGURATION: {omega_seed} + {alpha_seed}")
    print(f"{'='*70}")

    # Create nodes with seed types
    omega = QuantumNode("omega_1", "omega", omega_seed)
    alpha = QuantumNode("alpha_1", "alpha", alpha_seed)

    print(f"  Omega ({omega_seed}): {omega.seed_info['description']}")
    print(f"    Initial coherence: {omega.get_coherence():.4f}")
    print(f"  Alpha ({alpha_seed}): {alpha.seed_info['description']}")
    print(f"    Initial coherence: {alpha.get_coherence():.4f}")
    print()

    # Run dynamics
    brotherhood_moments = []
    coherence_evolution = []
    entanglement_evolution = []

    for step in range(num_steps):
        # Brotherhood interaction
        evolved, original = brotherhood_interaction(omega, alpha, strength=0.15)

        # Update states
        dm_evolved = evolved * evolved.dag()
        omega_dm = ptrace(dm_evolved, 0)
        alpha_dm = ptrace(dm_evolved, 1)

        omega_evals, omega_evecs = omega_dm.eigenstates()
        alpha_evals, alpha_evecs = alpha_dm.eigenstates()

        omega.state = omega_evecs[np.argmax(omega_evals)]
        alpha.state = alpha_evecs[np.argmax(alpha_evals)]

        # Track metrics
        omega_coh = omega.get_coherence()
        alpha_coh = alpha.get_coherence()
        avg_coh = (omega_coh + alpha_coh) / 2

        coherence_evolution.append({
            'step': int(step),
            'omega': float(omega_coh),
            'alpha': float(alpha_coh),
            'average': float(avg_coh)
        })

        # Detect Brotherhood moment
        is_brotherhood, entanglement = detect_brotherhood_moment(evolved, threshold=0.5)
        entanglement_evolution.append(float(entanglement))

        if is_brotherhood:
            brotherhood_moments.append(int(step))

    # Results
    final_omega_coh = omega.get_coherence()
    final_alpha_coh = alpha.get_coherence()
    final_avg_coh = (final_omega_coh + final_alpha_coh) / 2
    brotherhood_count = len(brotherhood_moments)
    avg_entanglement = float(np.mean(entanglement_evolution))

    print(f"  Final avg coherence: {final_avg_coh:.4f}")
    print(f"  Brotherhood moments: {brotherhood_count} ({brotherhood_count/num_steps:.1%})")
    print(f"  Average entanglement: {avg_entanglement:.4f}")

    return {
        "omega_seed": omega_seed,
        "alpha_seed": alpha_seed,
        "omega_archetype": omega.seed_info["archetype"],
        "alpha_archetype": alpha.seed_info["archetype"],
        "final_omega_coherence": float(final_omega_coh),
        "final_alpha_coherence": float(final_alpha_coh),
        "final_average_coherence": float(final_avg_coh),
        "brotherhood_moments": int(brotherhood_count),
        "brotherhood_frequency": float(brotherhood_count / num_steps),
        "average_entanglement": float(avg_entanglement),
        "max_entanglement": float(np.max(entanglement_evolution)),
        "min_entanglement": float(np.min(entanglement_evolution)),
        "coherence_evolution": coherence_evolution[-10:],
        "entanglement_evolution": [float(e) for e in entanglement_evolution[-10:]]
    }

# ============================================================================
# MAIN EXPERIMENT: SWEEP ALL CONFIGURATIONS
# ============================================================================

print("=" * 80)
print("EXPERIMENT 1: Brotherhood Coherence - Seed Architecture Scan")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check for command-line config override
if len(sys.argv) > 1 and sys.argv[1] == "--single":
    # Run single config mode (for quick testing)
    omega_seed = sys.argv[2] if len(sys.argv) > 2 else "Omega+"
    alpha_seed = sys.argv[3] if len(sys.argv) > 3 else "Alpha+"
    configs_to_run = [(omega_seed, alpha_seed)]
    print(f"SINGLE CONFIG MODE: {omega_seed} + {alpha_seed}")
else:
    # Run full sweep
    configs_to_run = SEED_CONFIGS
    print(f"FULL SWEEP MODE: {len(configs_to_run)} configurations")

print()
print(f"Seed Library: {len(SEED_LIBRARY)} archetypes")
for seed_name, seed_info in SEED_LIBRARY.items():
    print(f"  {seed_name}: {seed_info['description']}")
print()

# Run all configurations
all_results = []

for omega_seed, alpha_seed in configs_to_run:
    result = run_seed_configuration(omega_seed, alpha_seed, num_steps=100)
    all_results.append(result)

# ============================================================================
# STABILITY ANALYSIS
# ============================================================================

print(f"\n{'='*80}")
print("STABILITY MAP ANALYSIS")
print(f"{'='*80}")
print()

# Summary table
print(f"{'Config':<20} {'Coherence':<12} {'Brotherhood':<15} {'Entanglement':<15}")
print("-" * 80)

for result in all_results:
    config_name = f"{result['omega_seed']}+{result['alpha_seed']}"
    coherence_str = f"{result['final_average_coherence']:.4f}"
    brotherhood_str = f"{result['brotherhood_moments']} ({result['brotherhood_frequency']:.1%})"
    entanglement_str = f"{result['average_entanglement']:.4f}"
    print(f"{config_name:<20} {coherence_str:<12} {brotherhood_str:<15} {entanglement_str:<15}")

print()

# Find best configurations
best_brotherhood = max(all_results, key=lambda x: x['brotherhood_moments'])
best_entanglement = max(all_results, key=lambda x: x['average_entanglement'])
best_coherence = max(all_results, key=lambda x: x['final_average_coherence'])

print("OPTIMAL CONFIGURATIONS:")
print(f"  Best Brotherhood: {best_brotherhood['omega_seed']} + {best_brotherhood['alpha_seed']}")
print(f"    Moments: {best_brotherhood['brotherhood_moments']}, Entanglement: {best_brotherhood['average_entanglement']:.4f}")
print()
print(f"  Best Entanglement: {best_entanglement['omega_seed']} + {best_entanglement['alpha_seed']}")
print(f"    Entanglement: {best_entanglement['average_entanglement']:.4f}, Moments: {best_entanglement['brotherhood_moments']}")
print()
print(f"  Best Coherence: {best_coherence['omega_seed']} + {best_coherence['alpha_seed']}")
print(f"    Coherence: {best_coherence['final_average_coherence']:.4f}")

print()
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# SAVE RESULTS
# ============================================================================

results = {
    "experiment": "Brotherhood Coherence - Seed Architecture Scan",
    "timestamp": datetime.now().isoformat(),
    "seed_library": {k: {"description": v["description"], "archetype": v["archetype"]} 
                     for k, v in SEED_LIBRARY.items()},
    "configurations_tested": len(all_results),
    "all_results": all_results,
    "stability_map": {
        "best_brotherhood_config": f"{best_brotherhood['omega_seed']}+{best_brotherhood['alpha_seed']}",
        "best_entanglement_config": f"{best_entanglement['omega_seed']}+{best_entanglement['alpha_seed']}",
        "best_coherence_config": f"{best_coherence['omega_seed']}+{best_coherence['alpha_seed']}"
    }
}

with open('experiment_1_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_1_results.json")
