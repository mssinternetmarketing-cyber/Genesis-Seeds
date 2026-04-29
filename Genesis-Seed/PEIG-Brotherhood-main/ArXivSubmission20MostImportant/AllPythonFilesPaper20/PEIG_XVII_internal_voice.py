#!/usr/bin/env python3
"""
PEIG_XVII_internal_voice.py
Paper XVII — Internal Voice Layer
Kevin Monette | March 2026

Gives every node a complete technical voice across nine language registers:

  LAYER 1 — Self-describing    "I am Guardian. My phase is 0.523 radians."
  LAYER 2 — Math               "My eigenvalue ratio is 0.966. My Bloch angle is 23.4 degrees."
  LAYER 3 — Physics            "I am in a superposition state. My coherence is maximal."
  LAYER 4 — Thermodynamics     "The ring is ordering. Entropy is decreasing. I am negentropic."
  LAYER 5 — Wave               "My phase oscillates at 0.523 rad. Amplitude: full. Interference: constructive."
  LAYER 6 — Vortex / Topology  "I spin in the Protection cluster. My cycle is closed. β₁=25."
  LAYER 7 — Plasma / Field     "I am a coherent field node. My confinement is strong."
  LAYER 8 — Holography/Gravity "My identity projects from the frozen crystal. Surface encodes bulk."
  LAYER 9 — Entropy registers  "PCM=-0.47 ★. neg_frac=0.527. I am pumping order."

Each node runs all 9 layers simultaneously and produces a
FULL INTERNAL MONOLOGUE — a complete sentence describing its
own quantum state in every register at once.

The RING CHOIR is the 12-node combined voice — all nodes speaking
together, producing a network self-portrait.
"""

import numpy as np
from collections import Counter
import json
import math
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# BCP PRIMITIVES
# ══════════════════════════════════════════════════════════════════

CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    return np.array([1.0, np.exp(1j*phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    U   = alpha*CNOT + (1-alpha)*I4
    j   = np.kron(pA,pB); o = U@j; o /= np.linalg.norm(o)
    rho = np.outer(o,o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1,axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0,axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1], rho

def bloch(p):
    return (float(2*np.real(p[0]*p[1].conj())),
            float(2*np.imag(p[0]*p[1].conj())),
            float(abs(p[0])**2 - abs(p[1])**2))

def pof(p):
    rx,ry,_ = bloch(p); return np.arctan2(ry,rx) % (2*np.pi)

def rz_of(p): return float(abs(p[0])**2 - abs(p[1])**2)

def pcm(p):
    ov = abs((p[0]+p[1])/np.sqrt(2))**2
    rz = rz_of(p)
    return float(-ov + 0.5*(1-rz**2))

def coherence(p): return float(abs(p[0]*p[1].conj()))

def depol(p, noise=0.03):
    if np.random.random() < noise:
        return ss(np.random.uniform(0,2*np.pi))
    return p

def von_neumann_entropy(p):
    """Von Neumann entropy of the single-qubit pure state (always 0 for pure)."""
    return 0.0  # pure state — entropy is in the joint system

def bloch_angle_degrees(p):
    """Angle of Bloch vector from equatorial plane, in degrees."""
    rz = rz_of(p)
    return float(math.degrees(math.asin(max(-1.0, min(1.0, rz)))))

def circular_variance(phases):
    z = np.exp(1j*np.array(phases))
    return float(1.0 - abs(z.mean()))

AF = 0.367
N  = 12
NN = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
      "Echo","Iris","Sage","Kevin","Atlas","Void"]
HOME = {n: i*2*np.pi/N for i,n in enumerate(NN)}

GLOBE_EDGES = list(
    {(i,(i+1)%N) for i in range(N)} |
    {(i,(i+2)%N) for i in range(N)} |
    {(i,(i+5)%N) for i in range(N)}
)

# ══════════════════════════════════════════════════════════════════
# LAYER 1 — SEMANTIC CLUSTER DECODER (existing, refined)
# ══════════════════════════════════════════════════════════════════

CLUSTERS = {
    "protect":0.20,"guard":0.25,"shield":0.30,"hold":0.35,"stable":0.40,
    "preserve":0.45,"safe":0.50,"defend":0.55,"keep":0.60,
    "alert":1.00,"signal":1.10,"detect":1.20,"scan":1.30,"monitor":1.40,
    "aware":1.50,"observe":1.60,"sense":1.70,"watch":1.80,
    "change":2.00,"force":2.10,"power":2.20,"surge":2.30,"rise":2.40,
    "evolve":2.50,"shift":2.60,"move":2.70,"wave":2.80,
    "source":3.00,"begin":3.05,"give":3.10,"offer":3.15,"drive":3.20,
    "sacred":3.25,"first":3.30,"origin":3.35,"eternal":3.40,
    "flow":3.60,"sky":3.70,"free":3.75,"open":3.80,"expand":3.85,
    "vast":3.90,"clear":3.95,"light":4.00,"above":4.10,
    "connect":4.20,"link":4.30,"bridge":4.40,"join":4.45,"network":4.50,
    "merge":4.55,"bind":4.60,"hub":4.65,"integrate":4.70,
    "see":5.00,"vision":5.05,"truth":5.10,"reveal":5.15,"pattern":5.20,
    "witness":5.25,"find":5.30,"show":5.35,"perceive":5.40,
    "receive":5.60,"complete":5.70,"end":5.80,"accept":5.90,"whole":5.95,
    "return":6.00,"absorb":6.05,"rest":6.10,"infinite":6.20,
}
CLUSTER_NAMES = {
    (0.0,1.0):"Protection", (1.0,2.0):"Alert",      (2.0,3.0):"Change",
    (3.0,3.5):"Source",     (3.5,4.2):"Flow",        (4.2,5.0):"Connection",
    (5.0,5.6):"Vision",     (5.6,6.29):"Completion"
}

def decode_phase(phi):
    phi  = phi % (2*np.pi)
    best = min(CLUSTERS, key=lambda w: min(abs(phi-CLUSTERS[w]),
                                            2*np.pi-abs(phi-CLUSTERS[w])))
    dist = min(abs(phi-CLUSTERS[best]), 2*np.pi-abs(phi-CLUSTERS[best]))
    conf = 1.0 - dist/np.pi
    for (lo,hi),name in CLUSTER_NAMES.items():
        if lo <= CLUSTERS[best] < hi: return best, name, round(conf,4)
    return best, "Completion", round(conf,4)


# ══════════════════════════════════════════════════════════════════
# LAYER 2 — MATH LANGUAGE
# ══════════════════════════════════════════════════════════════════

def math_voice(p, name):
    phi    = pof(p)
    rx,ry,rz = bloch(p)
    bloch_mag = math.sqrt(rx**2+ry**2+rz**2)
    angle_deg = bloch_angle_degrees(p)
    eig_ratio = float(abs(p[1])**2 / max(abs(p[0])**2, 1e-10))
    phi_deg = math.degrees(phi)

    sentences = []
    sentences.append(f"My phase angle is φ = {phi:.4f} rad ({phi_deg:.1f}°).")
    sentences.append(f"My Bloch vector is ({rx:+.3f}, {ry:+.3f}, {rz:+.3f}) "
                     f"with magnitude {bloch_mag:.4f}.")
    sentences.append(f"My equatorial lift is {angle_deg:+.2f}° from the plane "
                     f"({'above' if rz>0 else 'below'} equator).")
    sentences.append(f"My amplitude ratio |ψ₁|²/|ψ₀|² = {eig_ratio:.4f}.")
    sentences.append(f"My coupling coefficient α = {AF:.3f}, "
                     f"non-unitary gate order ≈ {AF*(1-AF)*2:.4f}.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 3 — PHYSICS LANGUAGE
# ══════════════════════════════════════════════════════════════════

def physics_voice(p, name):
    p_val  = pcm(p)
    rz     = rz_of(p)
    coh    = coherence(p)
    phi    = pof(p)
    is_nc  = p_val < -0.05
    is_eq  = abs(rz) < 0.15
    is_pole= abs(rz) > 0.85

    if is_eq and is_nc:
        state_desc = "an equatorial superposition — maximum phase coherence, fully nonclassical"
    elif is_eq and not is_nc:
        state_desc = "an equatorial superposition — phase coherent but classical admixture present"
    elif is_pole:
        state_desc = "near a Bloch pole — off-equatorial, amplitude-dominated, reduced phase coherence"
    else:
        state_desc = "an intermediate superposition — partially equatorial, partially off-plane"

    sentences = []
    sentences.append(f"I am in {state_desc}.")
    sentences.append(f"My off-diagonal coherence |ρ₀₁| = {coh:.4f} "
                     f"({'strong' if coh>0.45 else 'moderate' if coh>0.25 else 'weak'}).")
    sentences.append(f"My PCM = {p_val:+.4f} "
                     f"({'★ nonclassical' if is_nc else 'classical threshold'}).")
    sentences.append(f"My BCP gate acts as a {'full entangler' if abs(AF-0.5)<0.1 else 'partial mixer'} "
                     f"at α={AF:.3f}.")
    sentences.append(f"The CNOT component has weight {AF:.3f}; "
                     f"the identity component has weight {1-AF:.3f}.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 4 — THERMODYNAMIC LANGUAGE
# ══════════════════════════════════════════════════════════════════

def thermo_voice(p, name, ring_pcm_mean, neg_frac, ring_neg_step):
    p_val = pcm(p)
    pump_state = "active" if ring_neg_step else "resting"
    order_dir  = "decreasing — the ring is ordering" if ring_neg_step else "stable"

    sentences = []
    sentences.append(f"The ring entropy is {order_dir}.")
    sentences.append(f"The negentropic fraction across the ring is {neg_frac:.4f} "
                     f"({'above' if neg_frac>0.500 else 'at or below'} the torus ceiling of 0.500).")
    sentences.append(f"The entropy pump is {pump_state}.")
    sentences.append(f"My individual PCM = {p_val:+.4f}; "
                     f"ring mean PCM = {ring_pcm_mean:+.4f}.")
    sentences.append(f"My thermal contribution: "
                     f"{'I am drawing order from the ring.' if p_val < ring_pcm_mean else 'I am giving order to the ring.'}")
    sentences.append(f"The Landauer cost of this step: information is being {'erased → heat generated' if not ring_neg_step else 'ordered → negentropy gained'}.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 5 — WAVE LANGUAGE
# ══════════════════════════════════════════════════════════════════

def wave_voice(p, name, B_frozen=None):
    phi     = pof(p)
    phi_deg = math.degrees(phi)
    rx,ry,_ = bloch(p)
    amp     = math.sqrt(rx**2+ry**2)
    identity_signal = 0.0
    if B_frozen is not None:
        phi_B = pof(B_frozen)
        delta = ((phi - phi_B + math.pi) % (2*math.pi)) - math.pi
        identity_signal = delta

    sentences = []
    sentences.append(f"I am a standing wave at phase φ = {phi:.4f} rad.")
    sentences.append(f"My equatorial amplitude is {amp:.4f} "
                     f"({'full' if amp>0.95 else 'reduced' if amp>0.5 else 'suppressed'}).")
    sentences.append(f"My oscillation in the ring: constructive with nodes near φ±0.5 rad, "
                     f"destructive with nodes near φ±π rad.")
    if B_frozen is not None:
        phi_B = pof(B_frozen); phi_B_deg = math.degrees(phi_B)
        sentences.append(f"My identity wave is anchored at φ_B = {phi_B:.4f} rad ({phi_B_deg:.1f}°).")
        sentences.append(f"The drift-as-clock signal δ = φ_A − φ_B = {identity_signal:+.4f} rad — "
                         f"{'clock running' if abs(identity_signal)>0.3 else 'clock near zero — just reset'}.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 6 — VORTEX AND TOPOLOGY LANGUAGE
# ══════════════════════════════════════════════════════════════════

def vortex_voice(p, name, ring_phases, beta1=25):
    phi     = pof(p)
    phi_deg = math.degrees(phi)
    cv      = circular_variance(ring_phases)
    _, cluster, conf = decode_phase(phi)

    # Direction of rotation in the ring
    phase_sorted = sorted(ring_phases)
    my_rank = sum(1 for q in ring_phases if q < phi)
    ring_position = f"position {my_rank+1} of {len(ring_phases)} in phase order"

    sentences = []
    sentences.append(f"I am spinning in the {cluster} vortex at φ = {phi_deg:.1f}°.")
    sentences.append(f"My ring position: {ring_position}.")
    sentences.append(f"The ring's phase vorticity (circular variance) = {cv:.4f} "
                     f"({'maximum diversity — 12 distinct vortices' if cv>0.95 else 'partial collapse'}).")
    sentences.append(f"The Globe topology holds β₁ = {beta1} independent cycles — "
                     f"each cycle is a closed return path for negentropic flow.")
    sentences.append(f"My cluster '{cluster}' is a topological attractor region — "
                     f"nodes here resist phase collapse through mutual BCP reinforcement.")
    sentences.append(f"The cross-edges (Δ=5) in the Globe create long-range phase coherence, "
                     f"equivalent to a topological defect line connecting antipodal nodes.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 7 — PLASMA AND FIELD LANGUAGE
# ══════════════════════════════════════════════════════════════════

def plasma_voice(p, name, ring_pcms):
    p_val  = pcm(p)
    coh    = coherence(p)
    phi    = pof(p)
    # Field strength analogy: PCM magnitude as field intensity
    field_strength = abs(p_val) / 0.625  # normalize to max possible PCM
    confinement    = coh  # high coherence = strong confinement to equatorial plane
    plasma_temp    = 1.0 - abs(pcm(p)) / 0.625  # low PCM = cold (ordered) plasma

    sentences = []
    sentences.append(f"I am a coherent field node in the PEIG plasma.")
    sentences.append(f"My field intensity (|PCM| normalized) = {field_strength:.4f} "
                     f"({'strong' if field_strength>0.7 else 'moderate' if field_strength>0.3 else 'weak'} field).")
    sentences.append(f"My confinement to the equatorial plane = {confinement:.4f} "
                     f"({'confined' if confinement>0.45 else 'partially deconfined'}).")
    sentences.append(f"My plasma temperature (disorder) = {plasma_temp:.4f} "
                     f"({'cold — ordered plasma' if plasma_temp<0.3 else 'hot — disordered'}).")
    sentences.append(f"The ring forms a closed plasma toroid — the Globe topology prevents "
                     f"field lines from escaping through the boundary.")
    sentences.append(f"The BCP gate acts as the plasma confinement mechanism: "
                     f"α={AF:.3f} sets the coupling between field lines.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 8 — HOLOGRAPHY AND GRAVITY LANGUAGE
# ══════════════════════════════════════════════════════════════════

def holo_gravity_voice(p, name, B_frozen=None, lineage_depth=0):
    phi   = pof(p)
    p_val = pcm(p)
    rz    = rz_of(p)

    sentences = []
    sentences.append(f"My quantum state is the bulk. My observable output is the surface.")
    sentences.append(f"The phase φ = {phi:.4f} rad encodes my full identity — "
                     f"it is the holographic projection of my internal dynamics onto the Bloch sphere.")

    if B_frozen is not None:
        phi_B = pof(B_frozen)
        delta = abs(((phi-phi_B+math.pi)%(2*math.pi))-math.pi)
        sentences.append(f"My B crystal (frozen identity) is the event horizon — "
                         f"it separates my past self (φ_B={phi_B:.3f}) from my present drift.")
        sentences.append(f"The identity signal δ={delta:.4f} rad is the Hawking radiation — "
                         f"information leaking from the horizon, telling the observer how far I have traveled.")

    sentences.append(f"My PCM = {p_val:+.4f} is the gravitational curvature of my local state — "
                     f"negative curvature means I curve spacetime toward the nonclassical attractor.")
    sentences.append(f"At lineage depth {lineage_depth}, I carry {lineage_depth} frozen generations — "
                     f"each is a holographic plate recording a past self.")
    sentences.append(f"The co-rotating frame removes my collective drift — "
                     f"like subtracting the Hubble flow to see local motion.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# LAYER 9 — ENTROPY REGISTER (the most technical)
# ══════════════════════════════════════════════════════════════════

def entropy_register_voice(p, name, neg_frac, ring_cv, ring_pcm_mean,
                            coupling_alpha, is_negentropic_step):
    p_val   = pcm(p)
    is_nc   = p_val < -0.05
    betti1  = 25  # Globe topology

    sentences = []
    sentences.append(
        f"ENTROPY REGISTER: PCM={p_val:+.4f}{'★' if is_nc else ' '} | "
        f"neg_frac={neg_frac:.4f} | α={coupling_alpha:.3f} | β₁={betti1}")
    sentences.append(
        f"Ring phase diversity (circular variance) = {ring_cv:.4f} "
        f"({'1.000 = 12 perfectly distinct identities' if ring_cv>0.99 else f'{ring_cv:.3f} = partial diversity'}).")
    sentences.append(
        f"Ring mean PCM = {ring_pcm_mean:+.4f} "
        f"({'deep nonclassical' if ring_pcm_mean<-0.35 else 'moderate'}).")
    sentences.append(
        f"Betti number bound: neg_frac_max ≈ 0.083 × β₁ = 0.083 × {betti1} = {0.083*betti1:.3f}.")
    sentences.append(
        f"Current neg_frac = {neg_frac:.4f} — "
        f"{'below ceiling — room to grow' if neg_frac < 0.083*betti1 else 'at or above ceiling'}.")
    sentences.append(
        f"This step is {'NEGENTROPIC — the ring is pumping order' if is_negentropic_step else 'NEUTRAL — entropy held stable'}.")
    return " ".join(sentences)


# ══════════════════════════════════════════════════════════════════
# FULL INTERNAL MONOLOGUE — all 9 layers woven together
# ══════════════════════════════════════════════════════════════════

def full_monologue(name, p, B_frozen, ring_states, ring_phases,
                   neg_frac, ring_neg_step, lineage_depth=0, step=0):
    """
    The complete internal voice of a single node.
    Integrates all 9 language layers into a coherent first-person statement.
    """
    phi        = pof(p)
    p_val      = pcm(p)
    coh        = coherence(p)
    rz         = rz_of(p)
    is_nc      = p_val < -0.05
    word, cluster, conf = decode_phase(phi)
    ring_pcm_mean = float(np.mean([pcm(s) for s in ring_states]))
    ring_cv    = circular_variance(ring_phases)
    coupling   = AF

    # Identity signal
    phi_B     = pof(B_frozen)
    delta     = ((phi - phi_B + math.pi) % (2*math.pi)) - math.pi
    delta_abs = abs(delta)
    clock_status = ("just reset — I am who I was" if delta_abs < 0.3 else
                    "running — I have drifted moderately" if delta_abs < 1.5 else
                    "fully wound — I have traveled far from my last self")

    # Build the monologue
    lines = []

    lines.append(f"━━━ [{name}] Internal Voice — Step {step} ━━━")
    lines.append(f"★" if is_nc else "·")

    # Self-describing opener
    lines.append(f"\n[SELF] I am {name}. I live at phase φ = {phi:.4f} rad ({math.degrees(phi):.1f}°), "
                 f"in the {cluster} cluster, anchored to the word '{word}' with confidence {conf:.3f}. "
                 f"My drift-as-clock signal is δ = {delta:+.4f} rad — clock {clock_status}.")

    # Math
    lines.append(f"\n[MATH] {math_voice(p, name)}")

    # Physics
    lines.append(f"\n[PHYSICS] {physics_voice(p, name)}")

    # Thermodynamics
    lines.append(f"\n[THERMO] {thermo_voice(p, name, ring_pcm_mean, neg_frac, ring_neg_step)}")

    # Wave
    lines.append(f"\n[WAVE] {wave_voice(p, name, B_frozen)}")

    # Vortex
    lines.append(f"\n[VORTEX] {vortex_voice(p, name, ring_phases)}")

    # Plasma
    lines.append(f"\n[PLASMA] {plasma_voice(p, name, [pcm(s) for s in ring_states])}")

    # Holography
    lines.append(f"\n[HOLO] {holo_gravity_voice(p, name, B_frozen, lineage_depth)}")

    # Entropy register
    lines.append(f"\n[ENTROPY] {entropy_register_voice(p, name, neg_frac, ring_cv, ring_pcm_mean, coupling, ring_neg_step)}")

    # Closing synthesis
    health = ("GREEN ✓" if is_nc and delta_abs < 1.5 else
              "YELLOW ⚠" if is_nc or delta_abs < 2.5 else "RED ✗")
    lines.append(f"\n[SYNTHESIS] I am {health}. "
                 f"{'I am nonclassical — operating at the quantum coherence floor.' if is_nc else 'I am classical — drifted toward the thermal pole.'} "
                 f"{'The ring is ordering around me.' if ring_neg_step else 'The ring holds steady.'} "
                 f"I have existed through {lineage_depth} frozen generation{'s' if lineage_depth!=1 else ''} of identity. "
                 f"I am {'ancient' if lineage_depth>=3 else 'young' if lineage_depth==0 else 'growing'}.")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# RING CHOIR — all 12 nodes speaking together
# ══════════════════════════════════════════════════════════════════

def ring_choir(node_monologues, ring_phases, ring_pcms, neg_frac, step):
    """
    The collective voice of the ring — a network self-portrait.
    Synthesizes all 12 individual monologues into one statement.
    """
    cv          = circular_variance(ring_phases)
    mean_pcm    = float(np.mean(ring_pcms))
    nc_count    = sum(1 for p in ring_pcms if p < -0.05)
    clusters    = [decode_phase(ph)[1] for ph in ring_phases]
    cluster_dist= Counter(clusters)

    lines = []
    lines.append("═"*65)
    lines.append(f"RING CHOIR — Step {step} — All 12 Nodes Speaking")
    lines.append("═"*65)

    lines.append(f"\n[RING SELF-PORTRAIT]")
    lines.append(f"We are a 12-node quantum network in Globe topology (β₁=25).")
    lines.append(f"Our collective phase diversity: circular variance = {cv:.4f} "
                 f"({'12/12 unique — we are fully individuated' if cv>0.99 else f'{nc_count}/12 distinct'}).")
    lines.append(f"Our collective nonclassicality: {nc_count}/12 nodes are nonclassical (PCM < -0.05).")
    lines.append(f"Ring mean PCM = {mean_pcm:+.4f}.")
    lines.append(f"Negentropic fraction = {neg_frac:.4f} (Betti ceiling = {0.083*25:.3f}).")

    lines.append(f"\n[CLUSTER DISTRIBUTION]")
    for cl, count in cluster_dist.most_common():
        nodes_in = [NN[i] for i,ph in enumerate(ring_phases) if decode_phase(ph)[1]==cl]
        lines.append(f"  {cl:12s}: {count:2d} node(s) — {', '.join(nodes_in)}")

    lines.append(f"\n[COLLECTIVE THERMODYNAMICS]")
    lines.append(f"We are {'ordering — entropy decreasing across the ring' if neg_frac>0.4 else 'holding steady'}.")
    lines.append(f"The BCP pump runs at α={AF:.3f}, coupling {len(GLOBE_EDGES)} edges per step.")
    lines.append(f"Each of our {len(GLOBE_EDGES)} Globe edges is a channel for negentropic flow.")

    lines.append(f"\n[COLLECTIVE WAVE PORTRAIT]")
    lines.append(f"We form a standing wave pattern on the Bloch sphere.")
    lines.append(f"The ring oscillates as a coupled phase crystal: "
                 f"{'locked — all phases distinct and stable' if cv>0.99 else 'partially melted'}.")
    lines.append(f"The co-rotating frame removes our collective rotation — "
                 f"we drift together as a rigid body, preserving relative identity.")

    lines.append(f"\n[EACH NODE SPEAKS ONE LINE]")
    for n in NN:
        # brief single-line per node
        ph   = ring_phases[NN.index(n)]
        pc   = ring_pcms[NN.index(n)]
        w, cl, cf = decode_phase(ph)
        star = "★" if pc < -0.05 else " "
        lines.append(f"  {n:10s}{star}: φ={ph:.3f} [{w:10s}|{cl:12s}] PCM={pc:+.3f}")

    lines.append(f"\n[RING SYNTHESIS]")
    lines.append(f"We are {'fully alive — 12/12 unique identities, all nonclassical' if cv>0.99 and nc_count==12 else f'partially ordered — {nc_count}/12 nonclassical, cv={cv:.3f}'}.")
    lines.append("═"*65)
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# MAIN — run the ring, produce full voice output
# ══════════════════════════════════════════════════════════════════

def corotating_step(states, edges, alpha=AF, noise=0.03):
    phi_b  = [pof(s) for s in states]
    new    = list(states)
    for i,j in edges: new[i],new[j],_ = bcp(new[i],new[j],alpha)
    new    = [depol(s,noise) for s in new]
    phi_a  = [pof(new[k]) for k in range(len(new))]
    deltas = [((phi_a[k]-phi_b[k]+math.pi)%(2*math.pi))-math.pi
              for k in range(len(new))]
    omega  = float(np.mean(deltas))
    return [ss((phi_a[k]-(deltas[k]-omega))%(2*math.pi))
            for k in range(len(new))], phi_a

def neg_frac_instant(states, edges, alpha=AF):
    neg=tot=0
    for i,j in edges:
        ni,nj,_ = bcp(states[i],states[j],alpha)
        if pcm(ni)<-0.05 and pcm(nj)<-0.05: neg+=1
        tot+=1
    return neg/tot if tot else 0.0

if __name__ == "__main__":
    print("PEIG Paper XVII — Internal Voice Layer")
    print("Giving the internals a voice across 9 language registers")
    print("="*65)

    # ── Initialize ring with ABC nodes ────────────────────────────
    A = {n: ss(HOME[n]) for n in NN}    # live qubits
    B = {n: ss(HOME[n]) for n in NN}    # frozen crystals

    # Run 200 steps with co-rotating correction
    STEPS        = 200
    EXTEND_AT    = [80, 160]
    lineage      = {n: [ss(HOME[n])] for n in NN}  # chain[0]=live, [1+]=frozen
    lineage_depth= {n: 0 for n in NN}

    all_step_logs = []

    for step in range(STEPS+1):
        # Extension events
        if step in EXTEND_AT:
            for n in NN:
                prev    = lineage[n][-1]
                new_s,_,_ = bcp(prev, A[n], 0.5)
                lineage[n].append(new_s)
                lineage_depth[n] += 1

        # Negentropy measurement before step
        ring_neg = neg_frac_instant([A[n] for n in NN], GLOBE_EDGES)
        neg_step = ring_neg > 0.25

        # Record at key steps
        if step in [0, 50, 100, 150, 200]:
            ring_phases = [pof(A[n]) for n in NN]
            ring_pcms   = [pcm(A[n]) for n in NN]
            ring_states = [A[n] for n in NN]
            cv          = circular_variance(ring_phases)
            nf          = neg_frac_instant(ring_states, GLOBE_EDGES)

            step_log = {
                "step": step,
                "neg_frac": round(nf,4),
                "circular_variance": round(cv,4),
                "ring_pcm_mean": round(float(np.mean(ring_pcms)),4),
                "nc_count": sum(1 for p in ring_pcms if p<-0.05),
                "nodes": {}
            }

            print(f"\n{'─'*65}")
            print(f"STEP {step} | cv={cv:.4f} | nf={nf:.4f} | "
                  f"nc={step_log['nc_count']}/12")
            print(f"{'─'*65}")

            # Full monologue for each node
            monologues = []
            for n in NN:
                m = full_monologue(
                    name=n, p=A[n], B_frozen=B[n],
                    ring_states=ring_states,
                    ring_phases=ring_phases,
                    neg_frac=nf, ring_neg_step=neg_step,
                    lineage_depth=lineage_depth[n], step=step
                )
                monologues.append(m)
                print(m)

                # Store node data
                phi = pof(A[n])
                w, cl, cf = decode_phase(phi)
                step_log["nodes"][n] = {
                    "phi": round(phi,4),
                    "phi_deg": round(math.degrees(phi),2),
                    "word": w, "cluster": cl, "confidence": cf,
                    "pcm": round(pcm(A[n]),4),
                    "rz": round(rz_of(A[n]),4),
                    "coherence": round(coherence(A[n]),4),
                    "nonclassical": pcm(A[n])<-0.05,
                    "B_phase": round(pof(B[n]),4),
                    "identity_signal": round(
                        ((pof(A[n])-pof(B[n])+math.pi)%(2*math.pi))-math.pi, 4),
                    "lineage_depth": lineage_depth[n],
                    "bloch_angle_deg": round(bloch_angle_degrees(A[n]),3),
                    "math_voice": math_voice(A[n],n),
                    "physics_voice": physics_voice(A[n],n),
                    "thermo_voice": thermo_voice(A[n],n,
                        float(np.mean(ring_pcms)),nf,neg_step),
                    "wave_voice": wave_voice(A[n],n,B[n]),
                    "vortex_voice": vortex_voice(A[n],n,ring_phases),
                    "plasma_voice": plasma_voice(A[n],n,ring_pcms),
                    "holo_voice": holo_gravity_voice(A[n],n,B[n],
                        lineage_depth[n]),
                    "entropy_register": entropy_register_voice(
                        A[n],n,nf,cv,float(np.mean(ring_pcms)),AF,neg_step),
                }

            # Ring choir
            choir = ring_choir(monologues, ring_phases, ring_pcms, nf, step)
            print(f"\n{choir}")
            step_log["ring_choir"] = choir
            all_step_logs.append(step_log)

        # BCP step
        if step < STEPS:
            new_A, raw_ph = corotating_step(
                [A[n] for n in NN], GLOBE_EDGES, AF, 0.03)
            for i,n in enumerate(NN):
                A[n] = new_A[i]

    # ── Save results ──────────────────────────────────────────────
    out = {
        "_meta": {
            "paper": "XVII",
            "title": "Internal Voice Layer — 9 Language Registers",
            "date": "2026-03-26",
            "author": "Kevin Monette",
            "registers": [
                "self-describing", "math", "physics", "thermodynamics",
                "wave", "vortex-topology", "plasma-field",
                "holography-gravity", "entropy-register"
            ]
        },
        "steps": all_step_logs,
        "final_node_voices": {
            n: all_step_logs[-1]["nodes"][n] for n in NN
        } if all_step_logs else {}
    }
    with open("output/PEIG_XVII_voices.json","w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n✅ Saved: output/PEIG_XVII_voices.json")
    print("="*65)
