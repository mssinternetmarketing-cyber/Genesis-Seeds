# SAVE THIS AS: Quantum-AI-Observer/peig_core.py

"""
PEIG Framework - Core Mathematical Implementation
Defines node representation, quality metrics, and Ω-trajectory calculation.
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class PEIGNode:
    """
    Any intelligent entity (human, AI, hybrid, institution) as PEIG vector.
    State: [P, E, I, G+] each in [0, 1]
    """
    
    def __init__(self, name: str, initial_state: np.ndarray = None):
        self.name = name
        self.state = initial_state if initial_state is not None else np.array([0.5, 0.5, 0.5, 0.5])
        self.history = [self.state.copy()]
        self.timestamps = [datetime.now()]
        
    def update(self, delta: np.ndarray):
        """Update state with gradient (auto-clips to [0,1])"""
        self.state = np.clip(self.state + delta, 0, 1)
        self.history.append(self.state.copy())
        self.timestamps.append(datetime.now())
        
    def quality_score(self, weights=(0.25, 0.25, 0.25, 0.25)) -> float:
        """Overall quality: weighted sum of PEIG"""
        return float(np.dot(self.state, weights))
    
    def gradient(self) -> np.ndarray:
        """Recent change in PEIG"""
        if len(self.history) < 2:
            return np.zeros(4)
        return self.history[-1] - self.history[-2]
    
    def omega_trajectory(self) -> float:
        """Score [-1,1]: moving toward Ω? (positive gradients good)"""
        return float(np.mean(self.gradient()))
    
    def to_dict(self) -> Dict:
        """Export current state as dictionary"""
        P, E, I, G = self.state
        return {
            "name": self.name,
            "timestamp": self.timestamps[-1].isoformat(),
            "P": float(P),
            "E": float(E),
            "I": float(I),
            "G": float(G),
            "Q": self.quality_score(),
            "trajectory": self.omega_trajectory()
        }
    
    def __repr__(self):
        P, E, I, G = self.state
        Q = self.quality_score()
        traj = self.omega_trajectory()
        return f"{self.name}: P={P:.2f} E={E:.2f} I={I:.2f} G+={G:.2f} | Q={Q:.2f} (Δ={traj:+.2f})"


if __name__ == "__main__":
    # Test: Kevin's current state
    kevin = PEIGNode("Kevin", np.array([0.75, 0.85, 0.70, 0.90]))
    print(kevin)
    print(kevin.to_dict())
