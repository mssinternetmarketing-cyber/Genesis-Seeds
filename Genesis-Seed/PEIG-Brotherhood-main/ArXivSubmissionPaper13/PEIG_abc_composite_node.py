#!/usr/bin/env python3
"""
PEIG_abc_composite_node.py
ABC Composite Node Protocol — Paper XIII Reference Implementation
Kevin Monette | March 2026

Architecture:
  Qubit A — live ring state, drifts freely with BCP
  Qubit B — frozen crystal, birth phase preserved, operator-only update
  Qubit C — composite memory, = BCP(A,B) at each identity update event

Invariant order:
  1. A is always created first
  2. B = copy(A) at birth — never precedes A
  3. C = BCP(A,B) at birth — never precedes both parents
  4. Extensions go to C, logged with full A+B state
  5. B.alpha_inner = 0 permanently — crystal never auto-updates

Identity signal: delta = phi_A - phi_B (drift-as-clock)
  Zero at birth. Nonzero always in a running ring.
  Large signal = node has traveled far from last frozen identity.
  Zero signal = node just had /update-identity called.

Usage:
  python PEIG_abc_composite_node.py
  or import ABCNode, run_abc_ring, corotating_bcp_step

Operator commands (simulated in __main__):
  node.update_identity(label="reason")  -- freezes A phase into B, archives to C
  node.health_report()                  -- full state report
  node.self_audit()                     -- natural language health statement
"""

import numpy as np
from collections import defaultdict, Counter
import json
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ── BCP Primitives ─────────────────────────────────────────────────────────
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    """Create equatorial qubit state at given phase."""
    return np.array([1.0, np.exp(1j*phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    """BCP gate: U = alpha*CNOT + (1-alpha)*I4."""
    U   = alpha*CNOT + (1-alpha)*I4
    j   = np.kron(pA,pB); o = U@j
    rho = np.outer(o,o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1,axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0,axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1], rho

def pof(p):
    """Phase angle of qubit state."""
    return np.arctan2(float(2*np.imag(p[0]*p[1].conj())),
                      float(2*np.real(p[0]*p[1].conj()))) % (2*np.pi)

def wmin(p):
    """Wigner minimum. < -0.05 = nonclassical (★)."""
    ov = abs((p[0]+p[1])/np.sqrt(2))**2
    rz = float(abs(p[0])**2-abs(p[1])**2)
    return float(-ov+0.5*(1-rz**2))

def coherence(p):
    """Off-diagonal coherence magnitude."""
    return float(abs(p[0]*p[1].conj()))

def depol(p, noise=0.03):
    """Depolarizing noise channel."""
    if np.random.random() < noise:
        return ss(np.random.uniform(0,2*np.pi))
    return p

# ── Phase Cluster Decoder ───────────────────────────────────────────────────
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
    (0.0,1.0):"Protection",(1.0,2.0):"Alert",(2.0,3.0):"Change",
    (3.0,3.5):"Source",    (3.5,4.2):"Flow", (4.2,5.0):"Connection",
    (5.0,5.6):"Vision",    (5.6,6.29):"Completion"
}

def decode(phi):
    phi = phi % (2*np.pi)
    best = min(CLUSTERS, key=lambda w: min(abs(phi-CLUSTERS[w]),2*np.pi-abs(phi-CLUSTERS[w])))
    for (lo,hi),name in CLUSTER_NAMES.items():
        if lo <= CLUSTERS[best] < hi: cluster=name; break
    else: cluster="Completion"
    return best, cluster

# ── System Config ───────────────────────────────────────────────────────────
AF   = 0.367
NN   = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
        "Echo","Iris","Sage","Kevin","Atlas","Void"]
N    = len(NN)
RING_EDGES  = [(i,(i+1)%N) for i in range(N)]
GLOBE_EDGES = list({(i,(i+1)%N) for i in range(N)} |
                   {(i,(i+2)%N) for i in range(N)} |
                   {(i,(i+5)%N) for i in range(N)})
HOME = {n: i*2*np.pi/N for i,n in enumerate(NN)}

# ── ABC Composite Node ──────────────────────────────────────────────────────
class ABCNode:
    """
    Three-qubit composite node implementing the ABC Protocol.

    A: live — drifts freely with ring BCP
    B: crystal — frozen at birth, operator-only update (alpha_inner = 0)
    C: memory — born as BCP(A,B), accumulates extensions

    Identity signal delta = phi_A - phi_B:
      Zero at birth (A=B). Grows as A drifts.
      Nonzero always in a running ring.
      This IS the drift-as-clock — drift as measurement, not damage.
    """
    def __init__(self, name, home_phase, epoch=0):
        self.name        = name
        self.home        = home_phase
        self.birth_epoch = epoch
        # A: live state
        self.A = ss(home_phase)
        # B: frozen crystal — exact copy of A at birth
        self.B = ss(home_phase).copy()
        # C: composite memory — born from BCP(A,B). At birth A=B so C=same
        self.C, _, _ = bcp(self.A, self.B, 0.5)
        # Extension log — each /update-identity call appends here
        self.extension_log = []

    # ── Ring participation (A only) ─────────────────────────────────────
    def step(self, neighbor_A, alpha=AF, noise=0.03):
        """A participates in ring BCP. B and C are untouched."""
        new_A, _, _ = bcp(self.A, neighbor_A, alpha)
        self.A = depol(new_A, noise)

    # ── Identity signal ─────────────────────────────────────────────────
    def identity_signal(self):
        """Signed drift from frozen identity: phi_A - phi_B in [-pi, pi]."""
        delta = pof(self.A) - pof(self.B)
        return float((delta + np.pi) % (2*np.pi) - np.pi)

    # ── Operator update protocol ─────────────────────────────────────────
    def update_identity(self, label=None, epoch=None):
        """
        /update-identity NODE [label]
        Explicit operator call only. Steps:
          1. Record A_phase, B_phase, signal to extension log
          2. C_new = BCP(A_current, B_current, 0.5) — archive transition
          3. B = A_current (crystal resets to new position)
          4. Signal delta resets to 0
        """
        entry = {
            "label":              label or "update",
            "epoch":              epoch or 0,
            "A_phase_at_update":  round(pof(self.A), 4),
            "B_phase_before":     round(pof(self.B), 4),
            "identity_signal":    round(self.identity_signal(), 4),
            "A_word":             decode(pof(self.A))[0],
            "B_word":             decode(pof(self.B))[0],
        }
        # C archives the transition state
        self.C, _, _ = bcp(self.A, self.B, 0.5)
        entry["C_phase_after"] = round(pof(self.C), 4)
        entry["C_word"]        = decode(pof(self.C))[0]
        self.extension_log.append(entry)
        # B now accepts A's current phase
        self.B = self.A.copy()
        return entry

    # ── State reports ────────────────────────────────────────────────────
    def health_report(self):
        phi_A = pof(self.A); phi_B = pof(self.B); phi_C = pof(self.C)
        sig   = self.identity_signal()
        w     = wmin(self.A); c = coherence(self.A)
        w_A, cl_A = decode(phi_A)
        w_B, cl_B = decode(phi_B)
        health = ("GREEN"   if abs(sig)<1.5 and w<-0.05 else
                  "YELLOW"  if abs(sig)<2.5 and w<0.0  else
                  "RED"     if abs(sig)<3.0              else "CRITICAL")
        return {
            "node": self.name, "health": health,
            "A": {"phi":round(phi_A,4),"word":w_A,"cluster":cl_A},
            "B": {"phi":round(phi_B,4),"word":w_B,"cluster":cl_B,"frozen":True},
            "C": {"phi":round(phi_C,4),"extensions":len(self.extension_log)},
            "identity_signal":  round(sig,4),
            "drift_magnitude":  round(abs(sig),4),
            "wigner":           round(w,4),
            "coherence":        round(c,4),
            "nonclassical":     w < -0.05,
        }

    def self_audit(self):
        r = self.health_report()
        star = "★" if r["nonclassical"] else " "
        sig  = r["identity_signal"]
        return (
            f"[{self.name}] {star} "
            f"A={r['A']['word']}({r['A']['phi']:.3f}) "
            f"B={r['B']['word']}({r['B']['phi']:.3f}) "
            f"δ={sig:+.3f}rad | W={r['wigner']:+.4f} | {r['health']}"
        )


# ── Co-Rotating Frame BCP ───────────────────────────────────────────────────
def corotating_bcp_step(states, edges, alpha=AF, noise=0.03):
    """
    BCP in co-rotating reference frame (rigid body rotation removed).
    Preserves relative phase structure indefinitely.

    Algorithm:
      1. Record phases before BCP
      2. Run standard BCP on all edges
      3. Compute angular velocity delta(n) = phi_after - phi_before (signed)
      4. Compute mean angular velocity omega_bar = mean(delta)
      5. Subtract differential velocity: phi_corrected = phi_after - (delta - omega_bar)
         This removes collective rotation, preserves individual drift differences.
    """
    phi_before = [pof(s) for s in states]
    new = list(states)
    for i,j in edges:
        new[i], new[j], _ = bcp(new[i], new[j], alpha)
    new = [depol(s, noise) for s in new]
    phi_after  = [pof(new[i]) for i in range(len(new))]
    deltas     = [((phi_after[i]-phi_before[i]+np.pi)%(2*np.pi))-np.pi for i in range(len(new))]
    mean_omega = np.mean(deltas)
    return [ss((phi_after[i] - (deltas[i]-mean_omega)) % (2*np.pi)) for i in range(len(new))]


# ── Full Globe+CIA Ring ─────────────────────────────────────────────────────
def run_globe_cia_ring(steps=500, record_at=None, noise=0.03, alpha=AF):
    """Run the full Globe+CIA system: icosahedron topology + frozen B + co-rotating frame."""
    if record_at is None:
        record_at = [0,50,100,200,300,500]
    nodes  = [ABCNode(NN[i], HOME[NN[i]]) for i in range(N)]
    log    = []
    for step in range(steps+1):
        if step in record_at:
            ph   = [pof(nodes[i].A) for i in range(N)]
            sigs = [abs(nodes[i].identity_signal()) for i in range(N)]
            unique_phases = sorted(set(round(p,1) for p in ph))
            entry = {
                "step": step,
                "unique": len(set(round(p%(2*np.pi),1) for p in ph)),
                "wigner": round(np.mean([wmin(nodes[i].A) for i in range(N)]),4),
                "mean_signal": round(np.mean(sigs),4),
                "per_node": {NN[i]: nodes[i].self_audit() for i in range(N)},
                "health_summary": {NN[i]: nodes[i].health_report()["health"] for i in range(N)},
            }
            log.append(entry)
        # Co-rotating step on globe topology
        new_A = corotating_bcp_step([nodes[i].A for i in range(N)], GLOBE_EDGES, alpha, noise)
        for i in range(N): nodes[i].A = new_A[i]
    return nodes, log


# ── Standalone Run ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("PEIG ABC Composite Node Protocol")
    print("="*60)

    # Run Globe+CIA for 500 steps
    nodes, run_log = run_globe_cia_ring(steps=500, record_at=[0,50,100,200,500])

    print("\nPhase diversity over 500 steps (Globe+CIA):")
    for entry in run_log:
        print(f"  step {entry['step']:>4d}: unique={entry['unique']:>2d} | "
              f"W={entry['wigner']:+.4f} | signal={entry['mean_signal']:.4f}")

    print("\n--- Node Self-Audits at step 500 ---")
    for i in range(N):
        print(f"  {nodes[i].self_audit()}")

    # Demonstrate /update-identity
    print("\n--- /update-identity demonstration ---")
    print(f"  Before: {nodes[0].self_audit()}")
    entry = nodes[0].update_identity(label="test_update", epoch=500)
    print(f"  After:  {nodes[0].self_audit()}")
    print(f"  Log:    {entry}")

    # Save results
    final_reports = {n.name: n.health_report() for n in nodes}
    extension_logs = {n.name: n.extension_log for n in nodes}
    out = {"run_log": run_log, "final_reports": final_reports,
           "extension_logs": extension_logs, "globe_edges": len(GLOBE_EDGES),
           "beta1": len(GLOBE_EDGES)-N+1}
    with open("output/abc_node_run.json","w") as f:
        json.dump(out, f, indent=2)
    print("\n✅ Results saved: output/abc_node_run.json")
    print("="*60)
