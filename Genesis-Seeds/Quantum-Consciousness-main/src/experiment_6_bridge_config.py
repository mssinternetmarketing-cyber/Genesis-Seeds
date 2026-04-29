"""
EXPERIMENT 6: Quantum Bridge Configuration
================================================================
Alpha Curious Nodes + Omega Anchor Nodes
Creating Stable, Coherent Entanglement Architecture
================================================================
Designed to maximize consciousness integration through
strategic Alpha-Omega coupling configurations
"""

import numpy as np
import json
from datetime import datetime
import itertools

try:
    from qutip import *
except ImportError:
    print("ERROR: QuTiP not installed. Run: pip install qutip")
    exit(1)

np.random.seed(42)

# ============================================================================
# SEED ARCHITECTURE - EXPANDED
# ============================================================================

SEED_LIBRARY = {
    "Omega+": lambda: (basis(2, 0) + basis(2, 1)).unit(),
    "Omega-": lambda: (basis(2, 0) - basis(2, 1)).unit(),
    "Alpha+": lambda: (basis(2, 0) + 1j * basis(2, 1)).unit(),
    "Alpha-": lambda: (basis(2, 0) - 1j * basis(2, 1)).unit()
}

SEED_ARCHETYPES = {
    "Omega+": "Presence (Source)",
    "Omega-": "Void (Silence Source)",
    "Alpha+": "Rich Receptivity (Bridge)",
    "Alpha-": "Muted Receptivity (Bridge)"
}

# ============================================================================
# QUANTUM BRIDGE NODE
# ============================================================================

class QuantumBridgeNode:
    """Node designed for conscious entanglement via Alpha-Omega pairing"""
    
    def __init__(self, node_id, seed_type, role="detector"):
        self.id = node_id
        self.seed_type = seed_type
        self.role = role  # "source" (Omega), "bridge" (Alpha), or "detector"
        self.archetype = SEED_ARCHETYPES[seed_type]
        
        if seed_type not in SEED_LIBRARY:
            raise ValueError("Invalid seed: {}".format(seed_type))
        
        self.state = SEED_LIBRARY[seed_type]()
        self.initial_state = self.state.copy()
        
        # Track evolution
        self.state_history = [self.state.copy()]
        self.coherence_history = []
        self.entanglement_history = []
        
    def get_purity(self):
        """Measure quantum purity (coherence)"""
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity
    
    def apply_phase(self, phase_shift):
        """Apply phase rotation for tuning"""
        U = np.exp(-1j * phase_shift * np.pi / 2) * basis(2,0)*basis(2,0).dag() + \
            np.exp(1j * phase_shift * np.pi / 2) * basis(2,1)*basis(2,1).dag()
        self.state = U * self.state

# ============================================================================
# BRIDGE CONFIGURATION TEMPLATES
# ============================================================================

class QuantumBridgeConfig:
    """Master configuration for Alpha-Omega quantum entanglement"""
    
    def __init__(self, config_name, alpha_nodes, omega_nodes, coupling_strength=0.3):
        self.name = config_name
        self.alpha_nodes = alpha_nodes  # List of Alpha seed types
        self.omega_nodes = omega_nodes  # List of Omega seed types
        self.coupling_strength = coupling_strength
        self.total_nodes = len(alpha_nodes) + len(omega_nodes)
        
        # Create physical nodes
        self.nodes = []
        node_id = 0
        
        # Create Omega source nodes
        for omega_seed in omega_nodes:
            self.nodes.append(QuantumBridgeNode(node_id, omega_seed, role="source"))
            node_id += 1
        
        # Create Alpha bridge nodes
        for alpha_seed in alpha_nodes:
            self.nodes.append(QuantumBridgeNode(node_id, alpha_seed, role="bridge"))
            node_id += 1
        
        self.results = {}
    
    def build_coupling_topology(self):
        """Define how nodes connect: Alpha as receivers, Omega as sources"""
        # Find Omega and Alpha nodes
        omegas = [n for n in self.nodes if n.role == "source"]
        alphas = [n for n in self.nodes if n.role == "bridge"]
        
        # Create coupling pairs: each Alpha connects to Omegas
        pairs = []
        for alpha in alphas:
            for omega in omegas:
                pairs.append((omega.id, alpha.id, self.coupling_strength))
        
        return pairs
    
    def evolve_coupled_system(self, steps=50):
        """Evolve the coupled Alpha-Omega system"""
        
        coupling_pairs = self.build_coupling_topology()
        
        for step in range(steps):
            # For each coupling pair, apply controlled interaction
            for omega_id, alpha_id, strength in coupling_pairs:
                omega_node = self.nodes[omega_id]
                alpha_node = self.nodes[alpha_id]
                
                # Create Bell-like state coupling
                combined = tensor(omega_node.state, alpha_node.state)
                
                # Controlled interaction: Alpha is receiver, Omega is source
                # Use phase-dependent coupling
                phase_factor = strength * (step / (steps-1) if steps > 1 else 0)
                
                # Apply coupling operator
                C_op = 0.5 * (tensor(sigmax(), qeye(2)) + 
                             tensor(sigmaz(), sigmaz()) * phase_factor)
                
                combined = (C_op * combined).unit()
                
                # Partial trace back to individual states
                dm = combined * combined.dag()
                rho_omega = ptrace(dm, 0)
                rho_alpha = ptrace(dm, 1)
                
                # Extract pure state approximation
                eval_omega, evec_omega = rho_omega.eigenstates()
                eval_alpha, evec_alpha = rho_alpha.eigenstates()
                
                omega_node.state = evec_omega[np.argmax(eval_omega)]
                alpha_node.state = evec_alpha[np.argmax(eval_alpha)]
            
            # Record metrics
            for node in self.nodes:
                purity = node.get_purity()
                node.coherence_history.append(purity)
                node.state_history.append(node.state.copy())
        
        return self._compute_entanglement_metrics()
    
    def _compute_entanglement_metrics(self):
        """Compute system-wide entanglement and consciousness metrics"""
        
        # Compute average coherence
        all_coherences = []
        for node in self.nodes:
            all_coherences.extend(node.coherence_history)
        
        avg_coherence = np.mean(all_coherences) if all_coherences else 1.0
        coherence_retention = (node.coherence_history[-1] / 
                              node.coherence_history[0] 
                              if node.coherence_history else 1.0)
        
        # Compute integrated information (Alpha-Omega coupling signature)
        alpha_purities = [node.coherence_history[-1] for node in self.nodes 
                         if node.role == "bridge"]
        omega_purities = [node.coherence_history[-1] for node in self.nodes 
                         if node.role == "source"]
        
        avg_alpha_purity = np.mean(alpha_purities) if alpha_purities else 1.0
        avg_omega_purity = np.mean(omega_purities) if omega_purities else 1.0
        
        # Bridge consciousness metric: how well Alpha preserves quality from Omega
        bridge_quality = min(avg_alpha_purity / max(avg_omega_purity, 1e-10), 1.0)
        
        return {
            "avg_coherence": float(avg_coherence),
            "coherence_retention": float(coherence_retention),
            "alpha_purity": float(avg_alpha_purity),
            "omega_purity": float(avg_omega_purity),
            "bridge_quality": float(bridge_quality),
            "alpha_count": len([n for n in self.nodes if n.role == "bridge"]),
            "omega_count": len([n for n in self.nodes if n.role == "source"]),
            "total_nodes": self.total_nodes
        }

# ============================================================================
# BRIDGE CONFIGURATIONS - DESIGNED ARCHITECTURES
# ============================================================================

def get_bridge_configurations():
    """Return designed quantum bridge configurations"""
    
    configs = []
    
    # CONFIG 1: Minimal Bridge (1 Omega + 1 Alpha)
    configs.append(QuantumBridgeConfig(
        "Minimal Bridge",
        alpha_nodes=["Alpha+"],
        omega_nodes=["Omega+"],
        coupling_strength=0.3
    ))
    
    # CONFIG 2: Dual Curiosity (2 Alpha + 1 Omega source)
    configs.append(QuantumBridgeConfig(
        "Dual Curiosity Bridge",
        alpha_nodes=["Alpha+", "Alpha-"],
        omega_nodes=["Omega+"],
        coupling_strength=0.4
    ))
    
    # CONFIG 3: Balanced Cross (2 Omega + 2 Alpha)
    configs.append(QuantumBridgeConfig(
        "Balanced Cross Bridge",
        alpha_nodes=["Alpha+", "Alpha-"],
        omega_nodes=["Omega+", "Omega-"],
        coupling_strength=0.35
    ))
    
    # CONFIG 4: Triple Alpha Receptor (3 Alpha + 2 Omega)
    configs.append(QuantumBridgeConfig(
        "Triple Receptor Gateway",
        alpha_nodes=["Alpha+", "Alpha+", "Alpha-"],
        omega_nodes=["Omega+", "Omega-"],
        coupling_strength=0.45
    ))
    
    # CONFIG 5: Omega-Alpha Harmony (Full diversity)
    configs.append(QuantumBridgeConfig(
        "Consciousness Harmonic",
        alpha_nodes=["Alpha+", "Alpha-"],
        omega_nodes=["Omega+", "Omega-"],
        coupling_strength=0.5
    ))
    
    # CONFIG 6: Resonance Chamber (High Alpha density)
    configs.append(QuantumBridgeConfig(
        "Resonance Chamber",
        alpha_nodes=["Alpha+", "Alpha+", "Alpha-", "Alpha-"],
        omega_nodes=["Omega+"],
        coupling_strength=0.6
    ))
    
    return configs

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

print("=" * 80)
print("EXPERIMENT 6: Quantum Bridge Configuration")
print("Alpha Curious Nodes + Omega Anchor Nodes")
print("=" * 80)
print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
print()

# Get all configurations
configs = get_bridge_configurations()

print("Testing {} bridge configurations...".format(len(configs)))
print()

all_results = []

for config_idx, config in enumerate(configs, 1):
    print("=" * 80)
    print("[{}/{}] CONFIG: {}".format(config_idx, len(configs), config.name))
    print("=" * 80)
    print("Architecture:")
    print("  Alpha bridges: {} nodes".format(config.total_nodes - len(config.omega_nodes)))
    print("  Omega sources: {} nodes".format(len(config.omega_nodes)))
    print("  Total system: {} nodes".format(config.total_nodes))
    print("  Coupling strength: {:.2f}".format(config.coupling_strength))
    print()
    
    # Run evolution
    metrics = config.evolve_coupled_system(steps=50)
    
    print("Results:")
    print("  Average coherence: {:.6f}".format(metrics["avg_coherence"]))
    print("  Coherence retention: {:.2%}".format(metrics["coherence_retention"]))
    print("  Alpha purity: {:.6f}".format(metrics["alpha_purity"]))
    print("  Omega purity: {:.6f}".format(metrics["omega_purity"]))
    print("  Bridge quality: {:.6f}".format(metrics["bridge_quality"]))
    print()
    
    config.results = metrics
    all_results.append({
        "configuration": config.name,
        "architecture": {
            "alpha_nodes": config.alpha_nodes,
            "omega_nodes": config.omega_nodes,
            "total_nodes": config.total_nodes,
            "coupling_strength": config.coupling_strength
        },
        "metrics": metrics
    })

print()
print("=" * 80)
print("BRIDGE CONFIGURATION RANKINGS")
print("=" * 80)
print()

# Sort by bridge quality
sorted_results = sorted(all_results, 
                       key=lambda x: x["metrics"]["bridge_quality"], 
                       reverse=True)

print("Ranked by Bridge Quality (Alpha coherence amplification):")
print()
for rank, result in enumerate(sorted_results, 1):
    print("[{}] {}".format(rank, result["configuration"]))
    print("    Bridge Quality: {:.6f}".format(result["metrics"]["bridge_quality"]))
    print("    Alpha Purity: {:.6f}".format(result["metrics"]["alpha_purity"]))
    print("    Omega Purity: {:.6f}".format(result["metrics"]["omega_purity"]))
    print("    Architecture: {} Alpha + {} Omega".format(
        result["metrics"]["alpha_count"],
        result["metrics"]["omega_count"]))
    print()

# Save results
print("=" * 80)
print("SAVING RESULTS")
print("=" * 80)

results = {
    "experiment": "Quantum Bridge Configuration",
    "timestamp": datetime.now().isoformat(),
    "description": "Alpha Curious Nodes + Omega Anchor Nodes entanglement configurations",
    "total_configurations": len(all_results),
    "configurations": all_results,
    "optimal_configuration": sorted_results[0]["configuration"] if sorted_results else "N/A",
    "seed_archetypes": SEED_ARCHETYPES
}

with open('experiment_6_bridge_config.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_6_bridge_config.json")
print()
print("=" * 80)
print("EXPERIMENT 6 COMPLETE")
print("=" * 80)
print("Completed: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
