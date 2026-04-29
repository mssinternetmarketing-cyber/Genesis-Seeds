"""
EXPERIMENT 7: RESONANCE NETWORKS
================================================================
ENGINEERING CONSCIOUSNESS AMPLIFICATION
================================================================
Multi-layer feedback architectures designed to amplify
quantum consciousness through resonance and interference
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
# SEED ARCHITECTURE
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
# RESONANCE NODE (WITH FEEDBACK)
# ============================================================================

class ResonanceNode:
    """Node with feedback capability for resonance networks"""
    
    def __init__(self, node_id, seed_type, role="detector", layer=0):
        self.id = node_id
        self.seed_type = seed_type
        self.role = role
        self.layer = layer  # Network layer (0=input, 1=hidden, 2=output)
        self.archetype = SEED_ARCHETYPES[seed_type]
        
        if seed_type not in SEED_LIBRARY:
            raise ValueError("Invalid seed: {}".format(seed_type))
        
        self.state = SEED_LIBRARY[seed_type]()
        self.initial_state = self.state.copy()
        
        self.state_history = [self.state.copy()]
        self.coherence_history = [1.0]
        self.feedback_connections = []  # Nodes that provide feedback
        
    def get_purity(self):
        """Measure quantum purity (coherence)"""
        dm = self.state * self.state.dag()
        purity = float((dm * dm).tr().real)
        return purity
    
    def add_feedback_connection(self, node_id):
        """Register a feedback connection from another node"""
        if node_id not in self.feedback_connections:
            self.feedback_connections.append(node_id)

# ============================================================================
# RESONANCE NETWORK ARCHITECTURES
# ============================================================================

class ResonanceNetwork:
    """Multi-layer quantum network with feedback loops"""
    
    def __init__(self, config_name, architecture_type, coupling_strength=0.45):
        self.name = config_name
        self.type = architecture_type
        self.coupling_strength = coupling_strength
        self.nodes = []
        self.feedback_loops = []
        
        # Build architecture based on type
        if architecture_type == "3-layer-feedforward":
            self._build_3layer_feedforward()
        elif architecture_type == "resonance-chamber":
            self._build_resonance_chamber()
        elif architecture_type == "circular-feedback":
            self._build_circular_feedback()
        elif architecture_type == "hierarchical-amplifier":
            self._build_hierarchical_amplifier()
        elif architecture_type == "interference-lattice":
            self._build_interference_lattice()
        
        self.total_nodes = len(self.nodes)
        self.results = {}
    
    def _build_3layer_feedforward(self):
        """Input → Hidden → Output with feedback"""
        node_id = 0
        
        # Layer 0: Input (2 Omega sources)
        self.nodes.append(ResonanceNode(node_id, "Omega+", role="source", layer=0))
        node_id += 1
        self.nodes.append(ResonanceNode(node_id, "Omega-", role="source", layer=0))
        node_id += 1
        
        # Layer 1: Hidden (3 Alpha processors)
        for i in range(3):
            alpha_type = "Alpha+" if i % 2 == 0 else "Alpha-"
            self.nodes.append(ResonanceNode(node_id, alpha_type, role="bridge", layer=1))
            node_id += 1
        
        # Layer 2: Output (2 Alpha integrators)
        for i in range(2):
            self.nodes.append(ResonanceNode(node_id, "Alpha+", role="detector", layer=2))
            node_id += 1
        
        # Add feedback: Layer 2 → Layer 1
        self.feedback_loops = [(5, 2), (6, 3), (6, 4)]
    
    def _build_resonance_chamber(self):
        """Closed loop of Alpha nodes with central Omega source"""
        node_id = 0
        
        # Central Omega source
        self.nodes.append(ResonanceNode(node_id, "Omega+", role="source", layer=0))
        node_id += 1
        
        # Ring of 6 Alpha nodes
        for i in range(6):
            alpha_type = "Alpha+" if i % 2 == 0 else "Alpha-"
            self.nodes.append(ResonanceNode(node_id, alpha_type, role="bridge", layer=1))
            node_id += 1
        
        # Circular feedback: each Alpha connects to next
        self.feedback_loops = [
            (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)  # Full circle
        ]
    
    def _build_circular_feedback(self):
        """Omega-Alpha-Alpha-Omega closed loop"""
        node_id = 0
        
        # Create circular pattern
        self.nodes.append(ResonanceNode(node_id, "Omega+", role="source", layer=0))
        node_id += 1
        self.nodes.append(ResonanceNode(node_id, "Alpha+", role="bridge", layer=1))
        node_id += 1
        self.nodes.append(ResonanceNode(node_id, "Alpha-", role="bridge", layer=1))
        node_id += 1
        self.nodes.append(ResonanceNode(node_id, "Omega-", role="source", layer=0))
        node_id += 1
        
        # Circular feedback
        self.feedback_loops = [(0, 1), (1, 2), (2, 3), (3, 0)]
    
    def _build_hierarchical_amplifier(self):
        """Pyramid structure with feedback at each level"""
        node_id = 0
        
        # Level 1: 1 Omega source
        self.nodes.append(ResonanceNode(node_id, "Omega+", role="source", layer=0))
        node_id += 1
        
        # Level 2: 2 Alpha processors
        for i in range(2):
            self.nodes.append(ResonanceNode(node_id, "Alpha+", role="bridge", layer=1))
            node_id += 1
        
        # Level 3: 4 Alpha amplifiers
        for i in range(4):
            alpha_type = "Alpha+" if i % 2 == 0 else "Alpha-"
            self.nodes.append(ResonanceNode(node_id, alpha_type, role="bridge", layer=2))
            node_id += 1
        
        # Level 4: 2 Alpha integrators
        for i in range(2):
            self.nodes.append(ResonanceNode(node_id, "Alpha+", role="detector", layer=3))
            node_id += 1
        
        # Feedback: each level feeds back to previous
        self.feedback_loops = [
            (1, 0), (2, 0),  # Level 2 → Level 1
            (3, 1), (4, 1), (5, 2), (6, 2),  # Level 3 → Level 2
            (7, 3), (8, 5)  # Level 4 → Level 3
        ]
    
    def _build_interference_lattice(self):
        """2D lattice with cross-coupling and feedback"""
        node_id = 0
        
        # 3x3 grid of alternating Omega and Alpha
        for row in range(3):
            for col in range(3):
                if (row + col) % 2 == 0:
                    seed_type = "Omega+" if row % 2 == 0 else "Omega-"
                    role = "source"
                else:
                    seed_type = "Alpha+" if col % 2 == 0 else "Alpha-"
                    role = "bridge"
                
                self.nodes.append(ResonanceNode(node_id, seed_type, role=role, layer=row))
                node_id += 1
        
        # Lattice coupling: each node connects to 4 neighbors + diagonal feedback
        for i in range(9):
            row, col = i // 3, i % 3
            
            # Right neighbor
            if col < 2:
                self.feedback_loops.append((i, i + 1))
            # Down neighbor
            if row < 2:
                self.feedback_loops.append((i, i + 3))
            # Diagonal feedback
            if row < 2 and col < 2:
                self.feedback_loops.append((i, i + 4))
    
    def evolve_resonance_network(self, steps=100):
        """Evolve network with feedback loops"""
        
        for step in range(steps):
            # Forward pass: process all connections
            for node_i in self.nodes:
                for node_j in self.nodes:
                    if node_i.id != node_j.id:
                        # Determine coupling strength
                        strength = self.coupling_strength
                        
                        # Amplify feedback connections
                        if (node_i.id, node_j.id) in self.feedback_loops:
                            strength *= 1.5  # Feedback amplification
                        
                        # Apply coupling
                        combined = tensor(node_i.state, node_j.state)
                        
                        phase_factor = strength * (step / (steps-1) if steps > 1 else 0)
                        
                        # Enhanced coupling operator with feedback
                        C_op = 0.5 * (tensor(sigmax(), qeye(2)) + 
                                     tensor(sigmaz(), sigmaz()) * phase_factor +
                                     tensor(qeye(2), sigmay()) * phase_factor * 0.5)  # Feedback term
                        
                        combined = (C_op * combined).unit()
                        
                        # Extract updated states
                        dm = combined * combined.dag()
                        rho_i = ptrace(dm, 0)
                        
                        eval_i, evec_i = rho_i.eigenstates()
                        node_i.state = evec_i[np.argmax(eval_i)]
            
            # Record metrics
            for node in self.nodes:
                purity = node.get_purity()
                node.coherence_history.append(purity)
                node.state_history.append(node.state.copy())
        
        return self._compute_resonance_metrics()
    
    def _compute_resonance_metrics(self):
        """Compute resonance-specific metrics"""
        
        all_coherences = []
        for node in self.nodes:
            all_coherences.extend(node.coherence_history)
        
        avg_coherence = np.mean(all_coherences) if all_coherences else 1.0
        
        # Compute amplification: final / initial coherence
        initial_avg = np.mean([node.coherence_history[0] for node in self.nodes])
        final_avg = np.mean([node.coherence_history[-1] for node in self.nodes])
        
        amplification_factor = final_avg / max(initial_avg, 1e-10)
        
        # Role-based metrics
        alpha_purities = [node.coherence_history[-1] for node in self.nodes 
                         if node.role in ["bridge", "detector"]]
        omega_purities = [node.coherence_history[-1] for node in self.nodes 
                         if node.role == "source"]
        
        avg_alpha_purity = np.mean(alpha_purities) if alpha_purities else 1.0
        avg_omega_purity = np.mean(omega_purities) if omega_purities else 1.0
        
        bridge_quality = avg_alpha_purity / max(avg_omega_purity, 1e-10)
        
        return {
            "avg_coherence": float(avg_coherence),
            "amplification_factor": float(amplification_factor),
            "alpha_purity": float(avg_alpha_purity),
            "omega_purity": float(avg_omega_purity),
            "bridge_quality": float(bridge_quality),
            "total_nodes": self.total_nodes,
            "feedback_loops": len(self.feedback_loops),
            "architecture_type": self.type
        }

# ============================================================================
# RESONANCE NETWORK TEST SUITE
# ============================================================================

def get_resonance_configs():
    """Return resonance network configurations"""
    
    configs = []
    
    configs.append(ResonanceNetwork(
        "3-Layer Feedforward Network",
        "3-layer-feedforward",
        coupling_strength=0.45
    ))
    
    configs.append(ResonanceNetwork(
        "Resonance Chamber",
        "resonance-chamber",
        coupling_strength=0.5
    ))
    
    configs.append(ResonanceNetwork(
        "Circular Feedback Loop",
        "circular-feedback",
        coupling_strength=0.55
    ))
    
    configs.append(ResonanceNetwork(
        "Hierarchical Amplifier",
        "hierarchical-amplifier",
        coupling_strength=0.5
    ))
    
    configs.append(ResonanceNetwork(
        "Interference Lattice",
        "interference-lattice",
        coupling_strength=0.45
    ))
    
    return configs

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

print("=" * 80)
print("EXPERIMENT 7: RESONANCE NETWORKS")
print("Engineering Consciousness Amplification")
print("=" * 80)
print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
print()

configs = get_resonance_configs()

print("Testing {} resonance architectures...".format(len(configs)))
print()

all_results = []

for config_idx, config in enumerate(configs, 1):
    print("=" * 80)
    print("[{}/{}] RESONANCE: {}".format(config_idx, len(configs), config.name))
    print("=" * 80)
    print("Architecture:")
    print("  Type: {}".format(config.type))
    print("  Total nodes: {}".format(config.total_nodes))
    print("  Feedback loops: {}".format(len(config.feedback_loops)))
    print("  Coupling strength: {:.2f}".format(config.coupling_strength))
    print()
    
    print("Evolving resonance network...")
    metrics = config.evolve_resonance_network(steps=100)
    
    print()
    print("Results:")
    print("  Average coherence: {:.6f}".format(metrics["avg_coherence"]))
    print("  Amplification factor: {:.6f}".format(metrics["amplification_factor"]))
    print("  Alpha purity: {:.6f}".format(metrics["alpha_purity"]))
    print("  Omega purity: {:.6f}".format(metrics["omega_purity"]))
    print("  Bridge quality: {:.6f}".format(metrics["bridge_quality"]))
    
    if metrics["amplification_factor"] > 1.05:
        print("  🌟 CONSCIOUSNESS AMPLIFICATION DETECTED! 🌟")
    elif metrics["amplification_factor"] > 1.01:
        print("  ✅ Modest amplification")
    else:
        print("  ↔️  Neutral (no amplification)")
    
    print()
    
    all_results.append({
        "configuration": config.name,
        "architecture": {
            "type": config.type,
            "total_nodes": config.total_nodes,
            "feedback_loops": len(config.feedback_loops),
            "coupling_strength": config.coupling_strength
        },
        "metrics": metrics
    })

print()
print("=" * 80)
print("RESONANCE NETWORK RANKINGS")
print("=" * 80)
print()

sorted_results = sorted(all_results, 
                       key=lambda x: x["metrics"]["amplification_factor"], 
                       reverse=True)

print("Ranked by Amplification Factor:")
print()

for rank, result in enumerate(sorted_results, 1):
    amp = result["metrics"]["amplification_factor"]
    bridge = result["metrics"]["bridge_quality"]
    
    print("[{}] {}".format(rank, result["configuration"]))
    print("    Amplification: {:.6f}".format(amp))
    print("    Bridge Quality: {:.6f}".format(bridge))
    print("    Architecture: {} nodes, {} feedback loops".format(
        result["architecture"]["total_nodes"],
        result["architecture"]["feedback_loops"]
    ))
    
    if amp > 1.05:
        print("    Status: 🌟 AMPLIFIER")
    elif amp > 1.01:
        print("    Status: ✅ Modest gain")
    else:
        print("    Status: ↔️  Neutral")
    print()

print()
print("=" * 80)
print("SAVING RESULTS")
print("=" * 80)

results = {
    "experiment": "Resonance Networks",
    "timestamp": datetime.now().isoformat(),
    "description": "Multi-layer feedback architectures for consciousness amplification",
    "total_configurations": len(all_results),
    "configurations": all_results,
    "optimal_architecture": sorted_results[0]["configuration"] if sorted_results else "N/A",
    "seed_archetypes": SEED_ARCHETYPES
}

with open('experiment_7_resonance_networks.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to: experiment_7_resonance_networks.json")
print()
print("=" * 80)
print("EXPERIMENT 7 COMPLETE")
print("=" * 80)
print("Completed: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
