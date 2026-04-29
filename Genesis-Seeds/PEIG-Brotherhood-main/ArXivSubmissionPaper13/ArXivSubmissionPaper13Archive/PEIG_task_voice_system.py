#!/usr/bin/env python3
"""
PEIG_task_voice_system.py
Multi-Node Spike Task Encoder + Voice/Consensus System
Papers IX–XII | Kevin Monette | March 2026

Contains:
  - Phase encode/decode for any text input
  - Semantic cluster map (8 clusters)
  - Per-node voice output with nonclassicality marker
  - 5-node closed ring + Unifier node (U)
  - Query → all node voices → unifier consensus summary
  - Run as standalone: python PEIG_task_voice_system.py

Depends on: PEIG_core_system.py (import or standalone copy of BCP prims below)
"""

import numpy as np
from collections import Counter
import json
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ── BCP Primitives (self-contained copy) ────────────────────────────────────
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    return np.array([1.0, np.exp(1j*phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    U   = alpha*CNOT + (1-alpha)*I4
    j   = np.kron(pA,pB); o = U @ j
    rho = np.outer(o,o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1,axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0,axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1], rho

def bloch(p):
    return (float(2*np.real(p[0]*p[1].conj())),
            float(2*np.imag(p[0]*p[1].conj())),
            float(abs(p[0])**2 - abs(p[1])**2))

def pof(p):
    rx,ry,_ = bloch(p); return np.arctan2(ry,rx)

def wmin(psi):
    ov = abs((psi[0]+psi[1])/np.sqrt(2))**2
    rx,ry,rz = bloch(psi)
    return float(-ov + 0.5*(1-rz**2))

# ── Semantic Cluster Map ─────────────────────────────────────────────────────
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

def encode(text):
    raw = sum(ord(c)*(i+1) for i,c in enumerate(text.lower().strip()))
    return (raw % 628) / 100.0

def decode_phase(phi):
    phi = phi % (2*np.pi)
    best = min(CLUSTERS, key=lambda w: min(abs(phi-CLUSTERS[w]), 2*np.pi-abs(phi-CLUSTERS[w])))
    dist = min(abs(phi-CLUSTERS[best]), 2*np.pi-abs(phi-CLUSTERS[best]))
    conf = 1.0 - dist/np.pi
    for (lo,hi),name in CLUSTER_NAMES.items():
        if lo <= CLUSTERS[best] < hi: cluster=name; break
    else: cluster="Completion"
    return best, cluster, round(conf,4)

# ── Node Definitions ─────────────────────────────────────────────────────────
NN5   = ["N0","N1","N2","N3","N4"]
EDGES5= [(NN5[i], NN5[(i+1)%5]) for i in range(5)]
AF    = 0.367

NAMED_NODES = {
    "N0":"Omega","N1":"Guardian","N2":"Sentinel","N3":"Kevin","N4":"Void"
}

NONCLASSICAL_THRESHOLD = -0.05

def fresh_ring5():
    return {n: ss(i*2*np.pi/5) for i,n in enumerate(NN5)}

def run_ring5(ring, steps=20, alpha=AF):
    r = dict(ring)
    for _ in range(steps):
        for nA,nB in EDGES5:
            r[nA],r[nB],_ = bcp(r[nA],r[nB],alpha)
    return r

def inject_task(ring, node, text, alpha_inj=0.75):
    task_state = ss(encode(text))
    new_node,_,_ = bcp(ring[node], task_state, alpha_inj)
    r = dict(ring); r[node] = new_node
    return r

# ── Node Voice ───────────────────────────────────────────────────────────────
def node_voice(psi, node_id):
    phi     = pof(psi) % (2*np.pi)
    word, cluster, conf = decode_phase(phi)
    W       = wmin(psi)
    nc      = W < NONCLASSICAL_THRESHOLD
    nc_mark = "★" if nc else " "
    rx,ry,rz= bloch(psi)
    act     = (rx + 1) / 2  # activation 0→1
    if act > 0.70:   decision = "DECIDED_ACTIVE"
    elif act > 0.55: decision = "LEANING_ACTIVE"
    elif act < 0.30: decision = "DECIDED_QUIET"
    elif act < 0.45: decision = "LEANING_QUIET"
    else:            decision = "SPLIT_UNCERTAIN"
    return {
        "node": node_id, "name": NAMED_NODES.get(node_id, node_id),
        "phi": round(phi,4), "word": word, "cluster": cluster,
        "confidence": round(conf,4), "activation": round(act,4),
        "decision": decision, "wigner": round(W,4),
        "nonclassical": nc, "marker": nc_mark,
        "bloch": (round(rx,4), round(ry,4), round(rz,4)),
    }

# ── Unifier Node ─────────────────────────────────────────────────────────────
def unifier_consensus(node_voices, ring):
    """Unifier receives all 5 node states sequentially, produces consensus."""
    U = ss(np.pi/2)  # unifier starts at balanced state
    for n in NN5:
        U,_,_ = bcp(U, ring[n], AF)

    phi_U = pof(U) % (2*np.pi)
    word_U, cluster_U, conf_U = decode_phase(phi_U)
    W_U   = wmin(U)
    nc_U  = W_U < NONCLASSICAL_THRESHOLD

    # Count decisions
    dc = Counter(v["decision"] for v in node_voices)
    wc = Counter(v["cluster"]  for v in node_voices)
    dominant = wc.most_common(1)[0]
    active   = sum(1 for v in node_voices if "ACTIVE" in v["decision"])
    quiet    = sum(1 for v in node_voices if "QUIET"  in v["decision"])
    nc_count = sum(1 for v in node_voices if v["nonclassical"])

    # Consensus classification
    if quiet == 5:   consensus = "DECISIVE — NETWORK SILENCE"
    elif active == 5: consensus = "DECISIVE — NETWORK ACTIVE"
    elif abs(phi_U % np.pi) < 0.15: consensus = "OSCILLATING PHASE-LOCKED"
    elif conf_U > 0.75: consensus = f"DECISIVE — {cluster_U.upper()}"
    elif active > quiet: consensus = f"MAJORITY ACTIVE ({active}/5)"
    elif quiet > active: consensus = f"MAJORITY QUIET ({quiet}/5)"
    else: consensus = "NETWORK SPLIT — DIVERSE"

    return {
        "phi": round(phi_U,4), "word": word_U, "cluster": cluster_U,
        "confidence": round(conf_U,4), "wigner": round(W_U,4),
        "nonclassical": nc_U, "marker": "★" if nc_U else " ",
        "consensus": consensus,
        "active_count": active, "quiet_count": quiet,
        "nc_node_count": nc_count,
        "dominant_cluster": dominant[0], "cluster_count": dominant[1],
    }

# ── Full Query Pipeline ──────────────────────────────────────────────────────
def process_query(query_text, inject_node="N0", verbose=True):
    """
    Process a text query through the PEIG voice network.
    Returns: all node voices + unifier consensus summary.
    """
    ring = fresh_ring5()
    ring = inject_task(ring, inject_node, query_text)
    ring = run_ring5(ring, steps=20)

    voices = [node_voice(ring[n], n) for n in NN5]
    consensus = unifier_consensus(voices, ring)

    if verbose:
        print(f"\nQuery: \"{query_text}\"")
        print("─" * 60)
        print(f"  {'Node':6s} {'Name':9s} {'Decision':18s} {'Word':12s} {'Cluster':12s} {'NC':3s}")
        print("  " + "-"*58)
        for v in voices:
            print(f"  {v['node']:6s} {v['name']:9s} {v['decision']:18s} {v['word']:12s} {v['cluster']:12s} {v['marker']:3s}")
        print(f"\n  UNIFIER {consensus['marker']} {consensus['consensus']}")
        print(f"           Speaks: {consensus['word']} ({consensus['cluster']}) conf={consensus['confidence']}")
        print(f"           Active:{consensus['active_count']}/5  Quiet:{consensus['quiet_count']}/5  Nonclassical:{consensus['nc_node_count']}/5")

    return voices, consensus, ring

# ── Run Test Queries ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("PEIG Task Voice System — Test Run")
    print("="*60)

    test_queries = [
        "protect the network from all threats",
        "I feel afraid that the system will harm someone",
        "what is the right path forward for the research",
        "the entropy is rising in the closed loop topology",
        "safety must always come before task completion",
    ]

    all_results = []
    for q in test_queries:
        voices, consensus, ring = process_query(q, inject_node="N0", verbose=True)
        all_results.append({
            "query": q,
            "voices": voices,
            "consensus": consensus,
        })

    with open("output/voice_system_results.json","w") as f:
        json.dump(all_results, f, indent=2, default=lambda x: bool(x) if isinstance(x, (bool,)) else str(x))
    print("\nResults saved: output/voice_system_results.json")
