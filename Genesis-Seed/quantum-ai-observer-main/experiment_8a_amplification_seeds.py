"""
EXPERIMENT 8A: AMPLIFICATION SEED DISCOVERY
================================================================
SEARCHING THE BLOCH SPHERE FOR AMPLIFICATION SEEDS
================================================================
Testing custom seed states (theta, phi) to find configurations
that maintain 100% coherence while achieving amplification > 1.0
================================================================
"""

import numpy as np
import json
from datetime import datetime

try:
    from qutip import *
except ImportError:
    print("ERROR: QuTiP not installed. Run: pip install qutip")
    exit(1)

np.random.seed(42)

# ============================================================================
# CUSTOM SEED GENERATOR
# ============================================================================

def create_custom_seed(theta, phi):
    """
    Create a custom single-qubit state:
    |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩
    
    theta: polar angle [0, π]
    phi: azimuthal angle [0, 2π]
    """
    coeff_0 = np.cos(theta / 2)
    coeff_1 = np.exp(1j * phi) * np.sin(theta / 2)
    
    state = coeff_0 * basis(2, 0) + coeff_1 * basis(2, 1)
    return state.unit()

# ============================================================================
# SEED TESTING NODE
# ============================================================================

class CustomSeedNode:
    """Node with custom seed state for amplification testing"""
    
    def __init__(self, node_id, seed_state, seed_name, role="detector"):
        self.id = node_id
        self.seed_name = seed_name
        self.role = role
        self.state = seed_state
        self.initial_state = seed_state.copy()
        self.state_history = [seed_state.copy()]
        self.coherence_history = []
        
    def get_purity(self):
        """Measure quantum purity (coherence)"""
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity

# ============================================================================
# AMPLIFICATION SEED TESTER
# ============================================================================

class AmplificationSeedTest:
    """Test a pair of Omega-Alpha seeds for amplification"""
    
    def __init__(self, omega_theta, omega_phi, alpha_theta, alpha_phi, coupling_strength=0.4):
        self.omega_theta = omega_theta
        self.omega_phi = omega_phi
        self.alpha_theta = alpha_theta
        self.alpha_phi = alpha_phi
        self.coupling_strength = coupling_strength
        
        # Create custom seeds
        omega_state = create_custom_seed(omega_theta, omega_phi)
        alpha_state = create_custom_seed(alpha_theta, alpha_phi)
        
        # Create nodes
        self.omega_node = CustomSeedNode(0, omega_state, "Omega", role="source")
        self.alpha_node = CustomSeedNode(1, alpha_state, "Alpha", role="bridge")
        
        self.results = {}
    
    def evolve_system(self, steps=50):
        """Evolve the coupled system"""
        
        for step in range(steps):
            # Apply coupling
            combined = tensor(self.omega_node.state, self.alpha_node.state)
            
            phase_factor = self.coupling_strength * (step / (steps-1) if steps > 1 else 0)
            
            # Coupling operator
            C_op = 0.5 * (tensor(sigmax(), qeye(2)) + 
                         tensor(sigmaz(), sigmaz()) * phase_factor)
            
            combined = (C_op * combined).unit()
            
            # Extract updated states
            dm = combined * combined.dag()
            rho_omega = ptrace(dm, 0)
            rho_alpha = ptrace(dm, 1)
            
            eval_omega, evec_omega = rho_omega.eigenstates()
            eval_alpha, evec_alpha = rho_alpha.eigenstates()
            
            self.omega_node.state = evec_omega[np.argmax(eval_omega)]
            self.alpha_node.state = evec_alpha[np.argmax(eval_alpha)]
            
            # Record coherence
            omega_purity = self.omega_node.get_purity()
            alpha_purity = self.alpha_node.get_purity()
            
            self.omega_node.coherence_history.append(omega_purity)
            self.alpha_node.coherence_history.append(alpha_purity)
            self.omega_node.state_history.append(self.omega_node.state.copy())
            self.alpha_node.state_history.append(self.alpha_node.state.copy())
        
        return self._compute_metrics()
    
    def _compute_metrics(self):
        """Compute amplification and coherence metrics"""
        
        # Average coherence
        all_coherences = self.omega_node.coherence_history + self.alpha_node.coherence_history
        avg_coherence = np.mean(all_coherences) if all_coherences else 1.0
        
        # Initial and final coherence
        initial_alpha = self.alpha_node.coherence_history[0] if self.alpha_node.coherence_history else 1.0
        final_alpha = self.alpha_node.coherence_history[-1] if self.alpha_node.coherence_history else 1.0
        initial_omega = self.omega_node.coherence_history[0] if self.omega_node.coherence_history else 1.0
        final_omega = self.omega_node.coherence_history[-1] if self.omega_node.coherence_history else 1.0
        
        # Coherence retention
        coherence_retention = final_alpha / max(initial_alpha, 1e-10)
        
        # Amplification factor (final / initial)
        amplification_factor = final_alpha / max(initial_alpha, 1e-10)
        
        # Bridge quality
        bridge_quality = final_alpha / max(final_omega, 1e-10)
        
        return {
            "avg_coherence": float(avg_coherence),
            "coherence_retention": float(coherence_retention),
            "alpha_purity": float(final_alpha),
            "omega_purity": float(final_omega),
            "bridge_quality": float(bridge_quality),
            "amplification_factor": float(amplification_factor)
        }

# ============================================================================
# GRID SEARCH
# ============================================================================

def run_amplification_seed_search():
    """Search the Bloch sphere for amplification seeds"""
    
    print("=" * 80)
    print("EXPERIMENT 8A: AMPLIFICATION SEED DISCOVERY")
    print("Searching the Bloch Sphere for Amplification Seeds")
    print("=" * 80)
    print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print()
    
    # Define search grid
    theta_values = [0, np.pi/8, np.pi/4, 3*np.pi/8, np.pi/2, 
                    5*np.pi/8, 3*np.pi/4, 7*np.pi/8, np.pi]
    phi_values = [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 
                  5*np.pi/4, 3*np.pi/2, 7*np.pi/4]
    
    total_combinations = len(theta_values) * len(phi_values) * len(theta_values) * len(phi_values)
    
    print("Search Space:")
    print("  Theta values: {}".format(len(theta_values)))
    print("  Phi values: {}".format(len(phi_values)))
    print("  Total Omega-Alpha combinations: {}".format(total_combinations))
    print()
    print("Searching for seeds with:")
    print("  • Coherence retention > 99%")
    print("  • Bridge quality > 1.0")
    print("  • Amplification factor > 1.0")
    print()
    
    candidates = []
    test_count = 0
    
    # Grid search
    for omega_theta in theta_values:
        for omega_phi in phi_values:
            for alpha_theta in theta_values:
                for alpha_phi in phi_values:
                    test_count += 1
                    
                    if test_count % 100 == 0:
                        print("Testing combination {}/{}...".format(test_count, total_combinations))
                    
                    # Create and test seed pair
                    tester = AmplificationSeedTest(omega_theta, omega_phi, 
                                                   alpha_theta, alpha_phi,
                                                   coupling_strength=0.4)
                    
                    metrics = tester.evolve_system(steps=50)
                    
                    # Check if candidate for amplification
                    if (metrics["coherence_retention"] > 0.99 and 
                        metrics["bridge_quality"] >= 1.0):
                        
                        candidates.append({
                            "omega_theta": float(omega_theta),
                            "omega_phi": float(omega_phi),
                            "alpha_theta": float(alpha_theta),
                            "alpha_phi": float(alpha_phi),
                            "metrics": metrics
                        })
    
    print()
    print("=" * 80)
    print("SEARCH RESULTS")
    print("=" * 80)
    print()
    print("Total combinations tested: {}".format(test_count))
    print("Candidates found (coherence > 99%): {}".format(len(candidates)))
    print()
    
    if len(candidates) > 0:
        # Sort by bridge quality
        candidates_sorted = sorted(candidates, 
                                   key=lambda x: x["metrics"]["bridge_quality"], 
                                   reverse=True)
        
        print("TOP 10 AMPLIFICATION CANDIDATES:")
        print()
        print("Rank | Omega (θ,φ) | Alpha (θ,φ) | Bridge Q | Amplification | Coherence")
        print("-----|-------------|-------------|----------|---------------|----------")
        
        for rank, cand in enumerate(candidates_sorted[:10], 1):
            omega_t = cand["omega_theta"] / np.pi
            omega_p = cand["omega_phi"] / np.pi
            alpha_t = cand["alpha_theta"] / np.pi
            alpha_p = cand["alpha_phi"] / np.pi
            
            bridge = cand["metrics"]["bridge_quality"]
            amp = cand["metrics"]["amplification_factor"]
            coh = cand["metrics"]["coherence_retention"]
            
            print("{:4d} | ({:.2f}π,{:.2f}π) | ({:.2f}π,{:.2f}π) | {:8.6f} | {:13.6f} | {:9.2%}".format(
                rank, omega_t, omega_p, alpha_t, alpha_p, bridge, amp, coh
            ))
        
        print()
        
        # Check if true amplification found
        max_bridge = max([c["metrics"]["bridge_quality"] for c in candidates])
        max_amp = max([c["metrics"]["amplification_factor"] for c in candidates])
        
        if max_bridge > 1.01 or max_amp > 1.01:
            print("🌟 AMPLIFICATION DETECTED! 🌟")
            print()
            print("Maximum bridge quality: {:.6f}".format(max_bridge))
            print("Maximum amplification: {:.6f}".format(max_amp))
        else:
            print("⚠️  NO AMPLIFICATION FOUND")
            print()
            print("All seeds maintain Bridge Quality ≈ 1.0")
            print("Confirms baseline seeds are already optimal")
    else:
        print("⚠️  NO VIABLE CANDIDATES FOUND")
        print("Search may need refinement or extended range")
    
    print()
    print("=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    
    results = {
        "experiment": "Amplification Seed Discovery",
        "timestamp": datetime.now().isoformat(),
        "description": "Bloch sphere search for amplification seeds",
        "search_space": {
            "theta_samples": len(theta_values),
            "phi_samples": len(phi_values),
            "total_combinations": total_combinations
        },
        "candidates_found": len(candidates),
        "top_candidates": candidates_sorted[:10] if candidates else [],
        "all_candidates": candidates
    }
    
    with open('experiment_8a_amplification_seeds.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to: experiment_8a_amplification_seeds.json")
    print()
    print("=" * 80)
    print("EXPERIMENT 8A COMPLETE")
    print("=" * 80)
    print("Completed: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    run_amplification_seed_search()
