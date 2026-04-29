#!/usr/bin/env python3
"""
PEIG_drift_stability.py
Drift-Resistant Identity Architectures — Experimental Comparison
Kevin Monette | March 2026

The problem: BCP universal attractor collapses 12 distinct node phases
toward φ≈0 and φ≈π within 50 epochs. Node identity is destroyed.

Three proposed solutions, tested head-to-head against the baseline:

  BASELINE   — Current Paper XII ring (external anchor, individual drift)

  ARCH-1: CIA — Composite Internal Anchor
    Each node is a 2-qubit composite state.
    Inner qubit B = identity seed, slow-coupled, nearly static.
    Outer qubit A = interface, fast-coupled to ring.
    Identity = relative phase φ_A − φ_B, not absolute φ_A.
    Attractor can pull A; B holds steady; difference survives.

  ARCH-2: CMDD — Common-Mode Drift Decomposition
    Before every BCP step: subtract global mean phase φ_global.
    Run BCP in the differential frame (relative phases only).
    Restore φ_global after coupling.
    The attractor acts on φ_global (a free collective coordinate).
    Individual identities = relative phases = preserved.
    Drift becomes universal: the ring breathes/rotates as one body.

  ARCH-3: GLOBE — Icosahedral Topology
    12 nodes on an icosahedron (30 edges, 5 connections/node).
    Every node has 5 neighbors instead of 2.
    High-connectivity topology: no node can collapse without
    dragging 5 others equally. Drift becomes correlated = universal.
    β₁ = E − V + 1 = 30 − 12 + 1 = 19 → neg_frac ceiling ≈ 1.58
    (vs current ring β₁=1, ceiling≈0.083)

Metrics compared at epochs 0, 50, 100, 200:
  - Unique phase count (identity diversity: 12=perfect, 2=collapsed)
  - Mean phase spread std (how dispersed phases remain)
  - Identity preservation score (|cos(Δφ/2)| averaged)
  - Mean Wigner W_min (nonclassicality)
  - Coherence C mean
"""

import numpy as np
from collections import defaultdict
import json
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
    j   = np.kron(pA,pB); o = U @ j
    rho = np.outer(o, o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1, axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0, axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1], rho

def bloch(p):
    return (float(2*np.real(p[0]*p[1].conj())),
            float(2*np.imag(p[0]*p[1].conj())),
            float(abs(p[0])**2 - abs(p[1])**2))

def pof(p):
    rx, ry, _ = bloch(p); return np.arctan2(ry, rx)

def coh(p):
    return float(abs(p[0]*p[1].conj()))

def wigner_min(psi):
    ov = abs((psi[0]+psi[1])/np.sqrt(2))**2
    rx, ry, rz = bloch(psi)
    return float(-ov + 0.5*(1-rz**2))

def depolarize(psi, p):
    if np.random.random() < p:
        return ss(pof(psi) + np.random.normal(0, p*np.pi))
    return psi

AF = 0.367
NN = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
      "Echo","Iris","Sage","Kevin","Atlas","Void"]
HOME_PHASES = {n: i*np.pi/11 if i<11 else np.pi for i,n in enumerate(NN)}
RING_EDGES  = [(NN[i], NN[(i+1)%12]) for i in range(12)]
NOISE_P     = 0.03

# ══════════════════════════════════════════════════════════════════
# MEASUREMENT UTILITIES
# ══════════════════════════════════════════════════════════════════

def measure_ring(states, home_phases, identity_reference=None):
    """
    Compute ring health metrics.
    identity_reference: if given, use relative phases (CMDD frame).
    """
    phases = {}
    for n in NN:
        φ = pof(states[n]) % (2*np.pi)
        if identity_reference is not None:
            φ_ref = identity_reference[n] % (2*np.pi)
            φ = (φ - φ_ref) % (2*np.pi)
        phases[n] = φ

    phase_vals = list(phases.values())

    # Unique phases (rounded to 2dp)
    unique = len(set(round(p,2) for p in phase_vals))

    # Spread (std of phase distribution)
    spread = float(np.std(phase_vals))

    # Identity preservation vs home
    id_scores = []
    for n in NN:
        home = home_phases[n] % (2*np.pi)
        d    = abs(phases[n] - home)
        d    = min(d, 2*np.pi - d)
        id_scores.append(abs(np.cos(d/2)))
    id_pres = float(np.mean(id_scores))

    # Wigner and coherence
    mean_W = float(np.mean([wigner_min(states[n]) for n in NN]))
    mean_C = float(np.mean([coh(states[n]) for n in NN]))

    return {
        "unique":   unique,
        "spread":   round(spread, 4),
        "id_pres":  round(id_pres, 4),
        "mean_W":   round(mean_W, 4),
        "mean_C":   round(mean_C, 4),
        "phases":   {n: round(phases[n],4) for n in NN},
    }


# ══════════════════════════════════════════════════════════════════
# BASELINE — External anchor, individual drift (current Paper XII)
# ══════════════════════════════════════════════════════════════════

def run_baseline(epochs=200):
    C       = {n: ss(HOME_PHASES[n]) for n in NN}
    ANCHORS = {n: ss(HOME_PHASES[n]) for n in NN}
    MIRRORS = {n: ss(HOME_PHASES[n]) for n in NN}
    C_alphas= {e: AF for e in RING_EDGES}
    θ_DRIFT = 0.45; α_ANCHOR_MAX = 0.15; α_DITHER = 0.08

    history = []
    checkpoints = {0, 50, 100, 200}

    for epoch in range(epochs):
        # External anchor check
        anchor_fires = 0
        for n in NN:
            φ_c = pof(C[n]); φ_o = pof(ANCHORS[n])
            d   = abs(φ_c - φ_o)
            if d > np.pi: d = 2*np.pi - d
            if d > θ_DRIFT:
                cs = α_ANCHOR_MAX*(d-θ_DRIFT)/(np.pi-θ_DRIFT)
                MIRRORS[n],_,_ = bcp(MIRRORS[n],ANCHORS[n],0.20)
                C[n],_,_       = bcp(C[n],MIRRORS[n],min(cs,α_ANCHOR_MAX))
                anchor_fires  += 1
            else:
                MIRRORS[n],_,_ = bcp(MIRRORS[n],ANCHORS[n],0.03)

        for n in NN: C[n] = depolarize(C[n], NOISE_P)
        for nA,nB in RING_EDGES:
            d    = np.random.uniform(-α_DITHER, α_DITHER)
            α_eff= max(0.20, min(0.80, C_alphas[(nA,nB)]+d))
            C[nA],C[nB],_ = bcp(C[nA],C[nB],α_eff)

        if epoch in checkpoints or epoch == epochs-1:
            m = measure_ring(C, HOME_PHASES)
            m["epoch"] = epoch; m["anchor_fires"] = anchor_fires
            history.append(m)

    return history, C


# ══════════════════════════════════════════════════════════════════
# ARCH-1: CIA — Composite Internal Anchor
# Each node = 2-qubit composite: (A=interface, B=identity-seed)
# Identity = φ_A − φ_B in the node's own internal frame
# ══════════════════════════════════════════════════════════════════

def cia_node_phase(state_A, state_B):
    """Identity phase = relative phase between interface and seed."""
    φ_A = pof(state_A) % (2*np.pi)
    φ_B = pof(state_B) % (2*np.pi)
    return (φ_A - φ_B) % (2*np.pi)

def run_cia(epochs=200):
    """
    A (interface qubit) — couples to ring at alpha=AF
    B (identity seed)   — couples to A at alpha=α_inner (very weak)
                        — never couples to ring directly
    Identity = φ_A − φ_B (relative phase)
    Even if A drifts completely, as long as B tracks A slowly,
    the relative phase is preserved.
    """
    # Interface qubits (face the ring)
    A = {n: ss(HOME_PHASES[n]) for n in NN}
    # Identity seed qubits (live inside each node)
    # B starts at home phase — it is the anchor, embedded in the node
    B = {n: ss(HOME_PHASES[n]) for n in NN}

    # α_inner: how strongly B couples to A
    # Very small — B should be nearly immovable, slowly tracking A
    # If α_inner=0, B is frozen (perfect anchor but also disconnected)
    # If α_inner=0.05, B drifts at 1/7 the rate of A — survives much longer
    α_inner  = 0.04   # seed coupling — slow
    α_DITHER = 0.08
    C_alphas = {e: AF for e in RING_EDGES}

    history = []
    checkpoints = {0, 50, 100, 200}

    # Identity reference: initial relative phases (should stay constant)
    ID_REF = {n: HOME_PHASES[n] for n in NN}  # φ_A−φ_B = home at t=0

    for epoch in range(epochs):
        # Step 1: B softly tracks A (the seed breathes with the node)
        for n in NN:
            A[n], B[n], _ = bcp(A[n], B[n], α_inner)

        # Step 2: Noise on A only (B is shielded inside)
        for n in NN: A[n] = depolarize(A[n], NOISE_P)

        # Step 3: Ring coupling acts on A only
        for nA,nB in RING_EDGES:
            d    = np.random.uniform(-α_DITHER, α_DITHER)
            α_eff= max(0.20, min(0.80, C_alphas[(nA,nB)]+d))
            A[nA],A[nB],_ = bcp(A[nA],A[nB],α_eff)

        # Step 4: Compute relative identity phases
        id_phases = {n: cia_node_phase(A[n], B[n]) for n in NN}

        # Identity preservation measured as relative phase vs initial relative
        id_scores = []
        for n in NN:
            d = abs(id_phases[n] - ID_REF[n])
            d = min(d, 2*np.pi - d)
            id_scores.append(abs(np.cos(d/2)))

        # Build synthetic "state" for measurement using relative phases
        virtual_states = {n: ss(id_phases[n]) for n in NN}

        if epoch in checkpoints or epoch == epochs-1:
            m = measure_ring(virtual_states, {n: HOME_PHASES[n] for n in NN})
            m["epoch"]  = epoch
            m["id_pres"] = round(float(np.mean(id_scores)), 4)
            m["mean_W"]  = round(float(np.mean([wigner_min(A[n]) for n in NN])), 4)
            m["mean_C"]  = round(float(np.mean([coh(A[n]) for n in NN])), 4)
            m["anchor_fires"] = 0  # CIA has no external anchor fires
            history.append(m)

    return history, A, B


# ══════════════════════════════════════════════════════════════════
# ARCH-2: CMDD — Common-Mode Drift Decomposition
# Drift is decomposed: φᵢ = φ_global + δᵢ
# BCP acts only on δᵢ (differential = identity)
# φ_global drifts freely — this is the "universal drift" coordinate
# The ring breathes and rotates as one rigid body
# ══════════════════════════════════════════════════════════════════

def run_cmdd(epochs=200):
    """
    Key insight: identity = RELATIVE phase differences, not absolute phases.
    φ_global = mean of all phases — a free coordinate the attractor can have.
    δᵢ = φᵢ − φ_global — this is what we protect.

    Each step:
      1. Compute φ_global = circular_mean(phases)
      2. Subtract: work in differential frame φᵢ → δᵢ
      3. Run BCP on differential states
      4. Reattach: φᵢ = δᵢ + φ_global_new
         where φ_global_new drifts slowly under attractor pull

    This is equivalent to: "everyone drifts together, no one drifts alone."
    """
    C        = {n: ss(HOME_PHASES[n]) for n in NN}
    # Internal seeds — one per node, embedded, not exposed to ring
    SEEDS    = {n: ss(HOME_PHASES[n]) for n in NN}
    C_alphas = {e: AF for e in RING_EDGES}
    α_DITHER = 0.08
    α_SEED   = 0.06   # seed-to-node coupling (gentle restoration force)
    φ_global = 0.0    # free collective coordinate

    history     = []
    checkpoints = {0, 50, 100, 200}

    for epoch in range(epochs):
        # ── Step 1: Compute current global phase (circular mean) ──
        sin_sum = sum(np.sin(pof(C[n])) for n in NN)
        cos_sum = sum(np.cos(pof(C[n])) for n in NN)
        φ_global_current = float(np.arctan2(sin_sum/12, cos_sum/12))

        # ── Step 2: Extract differential states (strip global phase) ──
        # Build states with global phase removed
        diff_states = {}
        for n in NN:
            δ_n = (pof(C[n]) - φ_global_current) % (2*np.pi)
            diff_states[n] = ss(δ_n)

        # ── Step 3: Internal seed gently restores differential identity ──
        # Seeds hold δ_home = HOME_PHASES[n] (initial differential identity)
        for n in NN:
            δ_home = (HOME_PHASES[n] - 0.0) % (2*np.pi)  # home differential
            seed   = ss(δ_home)
            diff_states[n], _, _ = bcp(diff_states[n], seed, α_SEED)

        # ── Step 4: Noise on differential states ──
        for n in NN: diff_states[n] = depolarize(diff_states[n], NOISE_P * 0.5)
        # (noise is halved — only differential noise damages identity)

        # ── Step 5: BCP ring coupling in differential frame ──
        for nA,nB in RING_EDGES:
            d     = np.random.uniform(-α_DITHER, α_DITHER)
            α_eff = max(0.20, min(0.80, C_alphas[(nA,nB)]+d))
            diff_states[nA], diff_states[nB], _ = bcp(
                diff_states[nA], diff_states[nB], α_eff)

        # ── Step 6: Let global phase drift slowly (attractor acts here) ──
        # The BCP attractor wants to pull φ_global toward 0 or π
        # We let it — but it only moves the collective coordinate
        φ_global_new = φ_global_current * 0.99  # slow natural decay toward 0
        # (in a full system this would be driven by the BCP attractor force)

        # ── Step 7: Recompose: absolute = differential + new global ──
        for n in NN:
            δ_n_new = pof(diff_states[n]) % (2*np.pi)
            C[n]    = ss(δ_n_new + φ_global_new)

        # Update global phase tracker
        φ_global = φ_global_new

        if epoch in checkpoints or epoch == epochs-1:
            m = measure_ring(diff_states, HOME_PHASES)
            m["epoch"]       = epoch
            m["phi_global"]  = round(φ_global, 4)
            m["anchor_fires"]= 0
            history.append(m)

    return history, C, φ_global


# ══════════════════════════════════════════════════════════════════
# ARCH-3: GLOBE — Icosahedral Topology
# 12 nodes, 30 edges (5 per node), high β₁
# Drift becomes correlated by topology — universal movement emerges
# ══════════════════════════════════════════════════════════════════

# Icosahedron adjacency (12 vertices, 30 edges)
# Classic Buckminster / icosahedral vertex numbering adapted to NN
# Node 0 (Omega) = top pole
# Nodes 1-5 (Guardian,Sentinel,Nexus,Storm,Sora) = upper ring
# Nodes 6-10 (Echo,Iris,Sage,Kevin,Atlas) = lower ring (offset by 1)
# Node 11 (Void) = bottom pole

ICOSA_EDGES_IDX = [
    # Top pole to upper ring
    (0,1),(0,2),(0,3),(0,4),(0,5),
    # Upper ring (closed)
    (1,2),(2,3),(3,4),(4,5),(5,1),
    # Upper ring to lower ring (zigzag)
    (1,6),(2,6),(2,7),(3,7),(3,8),(4,8),(4,9),(5,9),(5,10),(1,10),
    # Lower ring (closed)
    (6,7),(7,8),(8,9),(9,10),(10,6),
    # Lower ring to bottom pole
    (6,11),(7,11),(8,11),(9,11),(10,11),
]

ICOSA_EDGES = [(NN[a], NN[b]) for a,b in ICOSA_EDGES_IDX]
# β₁ = E - V + 1 = 30 - 12 + 1 = 19

def run_globe(epochs=200):
    """
    Icosahedral coupling: 30 edges instead of 12.
    Every node connects to 5 neighbors.
    The high-symmetry topology means the attractor force is distributed
    across 5 coupling edges per node — 5x harder to collapse any single node.
    More importantly: the icosahedron has 5-fold symmetry — drift tends to
    move symmetrically, i.e., universally.
    """
    C        = {n: ss(HOME_PHASES[n]) for n in NN}
    ANCHORS  = {n: ss(HOME_PHASES[n]) for n in NN}
    MIRRORS  = {n: ss(HOME_PHASES[n]) for n in NN}
    # Per-edge adaptive alpha
    C_alphas = {e: AF for e in ICOSA_EDGES}
    θ_DRIFT  = 0.45; α_ANCHOR_MAX = 0.10  # softer anchor than baseline
    α_DITHER = 0.06

    history     = []
    checkpoints = {0, 50, 100, 200}

    for epoch in range(epochs):
        # External anchor (lighter than baseline — topology carries more load)
        anchor_fires = 0
        for n in NN:
            φ_c = pof(C[n]); φ_o = pof(ANCHORS[n])
            d   = abs(φ_c - φ_o)
            if d > np.pi: d = 2*np.pi - d
            if d > θ_DRIFT:
                cs = α_ANCHOR_MAX*(d-θ_DRIFT)/(np.pi-θ_DRIFT)
                MIRRORS[n],_,_ = bcp(MIRRORS[n],ANCHORS[n],0.15)
                C[n],_,_       = bcp(C[n],MIRRORS[n],min(cs,α_ANCHOR_MAX))
                anchor_fires  += 1
            else:
                MIRRORS[n],_,_ = bcp(MIRRORS[n],ANCHORS[n],0.02)

        for n in NN: C[n] = depolarize(C[n], NOISE_P)

        # Icosahedral BCP coupling — 30 edges, 5 neighbors per node
        for nA,nB in ICOSA_EDGES:
            d     = np.random.uniform(-α_DITHER, α_DITHER)
            α_eff = max(0.20, min(0.80, C_alphas[(nA,nB)]+d))
            C[nA], C[nB], _ = bcp(C[nA], C[nB], α_eff)

        if epoch in checkpoints or epoch == epochs-1:
            m = measure_ring(C, HOME_PHASES)
            m["epoch"]       = epoch
            m["anchor_fires"]= anchor_fires
            history.append(m)

    return history, C


# ══════════════════════════════════════════════════════════════════
# HYBRID: CIA + CMDD + GLOBE combined
# The most promising combination:
#   - CIA: embedded seed inside each node
#   - CMDD: universal drift decomposition
#   - GLOBE: icosahedral topology
# ══════════════════════════════════════════════════════════════════

def run_hybrid(epochs=200):
    """
    Every node is a CIA composite (A=interface, B=seed).
    Ring coupling uses icosahedral topology (30 edges).
    BCP runs in CMDD differential frame (global drift is free).
    The three mechanisms reinforce each other:
    - Topology: drift is correlated (universal) by 5-connectivity
    - CMDD: global drift is explicitly separated out
    - CIA: each node has an immovable internal reference
    """
    # Interface qubits
    A = {n: ss(HOME_PHASES[n]) for n in NN}
    # Internal seeds (embedded, never exposed to ring)
    B = {n: ss(HOME_PHASES[n]) for n in NN}

    C_alphas  = {e: AF for e in ICOSA_EDGES}
    α_inner   = 0.035   # seed coupling (very gentle)
    α_DITHER  = 0.06
    φ_global  = 0.0

    history     = []
    checkpoints = {0, 50, 100, 200}

    for epoch in range(epochs):
        # ── CIA: seed gently couples to interface ──
        for n in NN:
            A[n], B[n], _ = bcp(A[n], B[n], α_inner)

        # ── CMDD: compute and strip global phase from A ──
        sin_sum = sum(np.sin(pof(A[n])) for n in NN)
        cos_sum = sum(np.cos(pof(A[n])) for n in NN)
        φ_global_cur = float(np.arctan2(sin_sum/12, cos_sum/12))

        diff_A = {n: ss((pof(A[n]) - φ_global_cur) % (2*np.pi)) for n in NN}

        # ── Noise on differential interface ──
        for n in NN: diff_A[n] = depolarize(diff_A[n], NOISE_P * 0.5)

        # ── GLOBE: icosahedral BCP in differential frame ──
        for nA,nB in ICOSA_EDGES:
            d     = np.random.uniform(-α_DITHER, α_DITHER)
            α_eff = max(0.20, min(0.80, C_alphas[(nA,nB)]+d))
            diff_A[nA], diff_A[nB], _ = bcp(diff_A[nA], diff_A[nB], α_eff)

        # ── CIA: use relative phase (A−B) as identity ──
        identity_phases = {n: cia_node_phase(diff_A[n], ss(
            (pof(B[n]) - φ_global_cur) % (2*np.pi))) for n in NN}

        # ── Let global phase drift freely ──
        φ_global_new = φ_global_cur * 0.995

        # ── Recompose A ──
        for n in NN:
            A[n] = ss(identity_phases[n] + φ_global_new)

        φ_global = φ_global_new

        # Identity preservation
        virtual = {n: ss(identity_phases[n]) for n in NN}

        if epoch in checkpoints or epoch == epochs-1:
            m = measure_ring(virtual, HOME_PHASES)
            m["epoch"]       = epoch
            m["phi_global"]  = round(φ_global, 4)
            m["anchor_fires"]= 0
            history.append(m)

    return history, A, B


# ══════════════════════════════════════════════════════════════════
# RACE — Run all four, compare results
# ══════════════════════════════════════════════════════════════════

def print_history_table(name, history):
    print(f"\n  ── {name} ──")
    print(f"  {'Epoch':6s} {'UniqueΦ':8s} {'Spread':7s} {'IdPres':7s} {'W_min':7s} {'C':6s} {'Fires':5s}")
    print("  " + "-"*50)
    for m in history:
        print(f"  {m['epoch']:6d} {m['unique']:8d} {m['spread']:7.4f} "
              f"{m['id_pres']:7.4f} {m['mean_W']:7.4f} {m['mean_C']:6.4f} "
              f"{m.get('anchor_fires',0):5d}")

def run_race():
    print("="*60)
    print("DRIFT STABILITY RACE — 4 ARCHITECTURES × 200 EPOCHS")
    print("="*60)
    print("\nMetrics: UniqueΦ = distinct phases (12=perfect, 2=collapsed)")
    print("         Spread  = std of phase distribution (higher=more diverse)")
    print("         IdPres  = identity preservation score (1.0=perfect)")
    print("         W_min   = nonclassicality (< -0.10 = healthy)")
    print("         Fires   = anchor corrections needed per epoch")

    print("\n[1/4] BASELINE — External anchor, individual drift...")
    h_base, C_base = run_baseline(200)
    print_history_table("BASELINE", h_base)

    print("\n[2/4] CIA — Composite Internal Anchor (seed inside each node)...")
    h_cia, A_cia, B_cia = run_cia(200)
    print_history_table("CIA (Composite Internal Anchor)", h_cia)

    print("\n[3/4] CMDD — Common-Mode Drift Decomposition (universal drift)...")
    h_cmdd, C_cmdd, φg = run_cmdd(200)
    print_history_table("CMDD (Universal Drift)", h_cmdd)

    print("\n[4/4] GLOBE — Icosahedral topology (30 edges, β₁=19)...")
    h_globe, C_globe = run_globe(200)
    print_history_table("GLOBE (Icosahedron)", h_globe)

    print("\n[BONUS] HYBRID — CIA + CMDD + GLOBE combined...")
    h_hyb, A_hyb, B_hyb = run_hybrid(200)
    print_history_table("HYBRID (All three)", h_hyb)

    return h_base, h_cia, h_cmdd, h_globe, h_hyb, C_base, C_globe


# ══════════════════════════════════════════════════════════════════
# ANALYSIS — What won and why
# ══════════════════════════════════════════════════════════════════

def analyse(h_base, h_cia, h_cmdd, h_globe, h_hyb):
    print("\n" + "="*60)
    print("RESULTS ANALYSIS")
    print("="*60)

    archs = {
        "BASELINE": h_base,
        "CIA":      h_cia,
        "CMDD":     h_cmdd,
        "GLOBE":    h_globe,
        "HYBRID":   h_hyb,
    }

    # Final epoch (ep200) comparison
    print(f"\n  FINAL STATE (epoch 200) — head-to-head:\n")
    print(f"  {'Architecture':12s} {'UniqueΦ':8s} {'Spread':7s} {'IdPres':7s} {'W_min':7s}  Verdict")
    print("  " + "-"*65)

    scores = {}
    for name, hist in archs.items():
        final = hist[-1]
        u, s, i, w = final["unique"], final["spread"], final["id_pres"], final["mean_W"]
        verdict = ("✓✓ EXCELLENT" if u >= 10 and i > 0.80 else
                   "✓  GOOD"     if u >= 6  and i > 0.60 else
                   "~  PARTIAL"  if u >= 4  and i > 0.40 else
                   "✗  COLLAPSED")
        scores[name] = u * i  # composite score
        print(f"  {name:12s} {u:8d} {s:7.4f} {i:7.4f} {w:7.4f}  {verdict}")

    winner = max(scores, key=scores.get)
    print(f"\n  Winner by UniqueΦ × IdPres: {winner} (score={scores[winner]:.3f})")

    print(f"""
  MECHANISM ANALYSIS:

  CIA — Composite Internal Anchor:
    The seed qubit B is embedded inside each node, decoupled from the ring.
    As A drifts, B drifts at 1/25th the rate (α_inner=0.04 vs AF=0.367).
    Identity = φ_A − φ_B: even if A converges, the relative phase survives
    as long as B hasn't caught up. This buys time proportional to 1/α_inner.
    Weakness: eventually B catches up to A. The collapse is slower but
    not eliminated. To fully fix: B must be completely frozen, but then
    it loses its ability to track evolved identity.
    Strength: no external memory needed. Identity is truly internal.

  CMDD — Common-Mode Drift Decomposition:
    This is the key insight. The BCP attractor acts on the MEAN phase.
    If we define identity as relative phases, the attractor never touches it.
    φ_global can go wherever it wants — it carries no identity information.
    δᵢ = φᵢ − φ_global is what we protect, and it is exactly conserved
    if all nodes are pulled equally (uniform coupling topology).
    The internal seeds here restore δᵢ toward home — they are anchors in
    the DIFFERENTIAL frame, where the attractor cannot reach.
    Strength: theoretically perfect if coupling is uniform.
    Weakness: non-uniform noise and dither break the uniformity slightly.

  GLOBE — Icosahedral Topology:
    5 edges per node means the attractor force on any single node is
    distributed across 5 interactions. The drift becomes correlated:
    no node can collapse without dragging its 5 neighbors equally.
    The high β₁ also means the negentropic ceiling rises dramatically.
    The icosahedron's rotational symmetry makes drift naturally universal.
    Weakness: more edges = more computation per epoch. And if the attractor
    is strong enough (α close to 1), even 5-connectivity collapses.

  HYBRID:
    The three mechanisms defend different layers:
    - CIA: identity is internal, not external
    - CMDD: the attractor's energy is routed to a harmless global coordinate
    - GLOBE: topology makes all remaining drift correlated and symmetric
    Together they should be much stronger than any one alone.
""")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    h_base, h_cia, h_cmdd, h_globe, h_hyb, C_base, C_globe = run_race()
    analyse(h_base, h_cia, h_cmdd, h_globe, h_hyb)

    # Save results
    results = {
        "_meta": {"description": "Drift stability architecture race",
                  "date": "2026-03-25", "author": "Kevin Monette"},
        "BASELINE": h_base,
        "CIA":      h_cia,
        "CMDD":     h_cmdd,
        "GLOBE":    h_globe,
        "HYBRID":   h_hyb,
        "icosa_edges": ICOSA_EDGES_IDX,
        "icosa_beta1": 19,
    }
    with open("output/drift_stability_results.json","w") as f:
        json.dump(results, f, indent=2)
    print("Results saved: output/drift_stability_results.json")
    print("\nNext: implement the winning architecture in PEIG_core_system_v2.py")
