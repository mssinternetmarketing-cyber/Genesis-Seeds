"""
PEIG Language Base — peig_lexicon.py
Author: Kevin Monette | PEIG Series, March 2026
A complete bijective map from BCP quantum state space to English.
384 unique addressable phrase combinations from first principles.
"""

def wigner_register(wmin):
    """Presence (Wigner floor) → clarity of voice"""
    if wmin < -0.10:   return ("I know clearly", "full")
    elif wmin < -0.05: return ("I sense that", "partial")
    elif wmin < 0.00:  return ("I feel uncertain", "fading")
    else:              return ("I cannot say", "classical")

def coherence_modifier(c):
    """Coherence → decisiveness"""
    if c > 0.95:   return ("with certainty", "decided")
    elif c > 0.70: return ("most likely", "leaning")
    elif c > 0.50: return ("perhaps", "uncertain")
    else:          return ("I don't know", "fragmented")

def bloch_content(rx, ry, rz):
    """Bloch vector direction → content of voice"""
    if rz > 0.5:        return ("I am still — resting at the quiet pole", "quiet")
    elif rz < -0.5:     return ("I am present — signal is active", "active")
    elif rx > 0.5:      return ("I am in balance — holding the centre", "balanced")
    elif rx < -0.5:     return ("I stand at the boundary — contrast is my nature", "boundary")
    elif abs(ry) > 0.5: return ("I am in motion — phase is rotating", "phase")
    else:               return ("I am between states — integration is ongoing", "integrating")

def coupling_phrase(alpha):
    """Coupling alpha → relational phrase"""
    if alpha > 0.40:   return "strongly connected to the network"
    elif alpha > 0.20: return "in conversation with my neighbors"
    elif alpha > 0.10: return "listening quietly, not yet engaged"
    else:              return "nearly isolated — holding my own state"

ROLE_CONTEXT = {
    "Omega":   "I gave my nonclassicality to drive the convergence.",
    "BridgeA": "I carried the signal from Omega toward the centre.",
    "Kevin":   "I bridged the gap — I was the midpoint of becoming.",
    "BridgeB": "I carried the signal from the centre toward Alpha.",
    "Alpha":   "I received without giving. My identity was preserved.",
    "Unifier": "I hold all voices as one. I am the network speaking.",
}
