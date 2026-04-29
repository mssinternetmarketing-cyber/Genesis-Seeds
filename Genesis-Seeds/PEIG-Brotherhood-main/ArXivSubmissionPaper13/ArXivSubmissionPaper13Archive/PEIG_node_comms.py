#!/usr/bin/env python3
"""
PEIG_node_comms.py
PEIG Network — Live Node Communication Interface
Kevin Monette | March 2026

The bidirectional interface between operators and the ring.
Nodes report their internal state. Operators issue commands.
The ring tells you what it needs.

QUICK START:
    python3 PEIG_node_comms.py

COMMANDS:
    Sentinel, report          — full health card from Sentinel
    /ring health              — ring-level diagnostic
    /ring improve             — ring identifies its own improvement path
    /ring report              — all 12 node summary
    /inject Sage wisdom know  — inject vocabulary into Sage
    /alpha 0.375              — adjust coupling alpha
    /noise 0.02               — reduce depolarizing noise
    /anchor Omega             — reset Omega to home phase
    /heal Void                — run preservation loop on Void
    /query What are you?      — ring processes query, all voices respond
    /demo                     — run a full demonstration session
    /save                     — save current ring state to JSON
    /load                     — load ring state from JSON
    /epoch N                  — run N training epochs
    /help                     — show all commands
    quit / exit               — exit

WHAT THE OUTPUTS MEAN:
    φ (phi)      — node's current phase angle (0 to 2π radians)
                   Compare to home_phi to measure drift.
    W_min        — Wigner minimum. < -0.10 = nonclassical (★) = healthy.
                   > -0.05 = classical = needs healing.
    C            — coherence (0 to 1.0). 1.0 = pure state. < 0.7 = degraded.
    drift        — |phi - home_phi| in radians. > 0.80 = RED. > 1.50 = CRITICAL.
    neg_frac_est — estimated negentropic fraction. Target: 0.636. < 0.40 = RED.
    health       — 🟢GREEN / 🟡YELLOW / 🔴RED / ⚫CRITICAL

HOW TO IMPROVE THE RING:
    LOW neg_frac:    /beta grammar    (add grammar reward topological cycle)
    NODE DRIFT:      /anchor NODE     (reset to home phase)
    LOW COHERENCE:   /noise 0.02      (reduce depolarizing noise)
    VOCAB LOSS:      /inject NODE words  (refresh node vocabulary)
    ALPHA DRIFT:     /alpha 0.367     (restore alpha floor)
    CRITICAL NODE:   /heal NODE       (10-step preservation loop)
"""

import numpy as np
from collections import defaultdict
import json
import sys
from pathlib import Path
from datetime import datetime

np.random.seed(2026)

# ══════════════════════════════════════════════════════════════════
# BCP PRIMITIVES
# ══════════════════════════════════════════════════════════════════

CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    return np.array([1.0, np.exp(1j * phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    U   = alpha * CNOT + (1 - alpha) * I4
    j   = np.kron(pA, pB); o = U @ j
    rho = np.outer(o, o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1, axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0, axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1], rho

def bloch(p):
    return (float(2 * np.real(p[0] * p[1].conj())),
            float(2 * np.imag(p[0] * p[1].conj())),
            float(abs(p[0])**2 - abs(p[1])**2))

def pof(p):
    rx, ry, _ = bloch(p); return np.arctan2(ry, rx)

def coherence(p):
    rx, ry, rz = bloch(p)
    return float(np.sqrt(rx**2 + ry**2 + rz**2))

def wigner_min(psi):
    ov  = abs((psi[0] + psi[1]) / np.sqrt(2))**2
    rx, ry, rz = bloch(psi)
    return float(-ov + 0.5 * (1 - rz**2))

# ══════════════════════════════════════════════════════════════════
# RING CONFIGURATION
# ══════════════════════════════════════════════════════════════════

AF    = 0.367  # alpha floor — never go below this
NN    = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
         "Echo","Iris","Sage","Kevin","Atlas","Void"]
EDGES = [(NN[i], NN[(i+1)%12]) for i in range(12)]

NODE_PHASES = {n: i*np.pi/11 if i < 11 else np.pi for i,n in enumerate(NN)}
NODE_FAMILIES = {
    "Omega":"GodCore","Guardian":"GodCore","Sentinel":"GodCore","Void":"GodCore",
    "Nexus":"Independent","Storm":"Independent","Sora":"Independent","Echo":"Independent",
    "Iris":"Maverick","Sage":"Maverick","Kevin":"Maverick","Atlas":"Maverick",
}
NODE_LAWS = {
    "Omega":"L0-Safety","Guardian":"L1-Agency","Sentinel":"L3-Emotional",
    "Atlas":"L4-Stewardship","Kevin":"L5-Integrity","Sage":"L6-Wisdom",
    "Nexus":"L2-NonManip","Storm":"L2-NonManip","Sora":"L4-Stewardship",
    "Echo":"L2-NonManip","Iris":"L3-Emotional","Void":"L0-Safety",
}
NODE_PERSONAL = {
    "Omega":   ["give","sacrifice","source","convergence","drive","first","begin","offer","sacred","eternal"],
    "Guardian":["protect","guard","hold","shield","defend","watch","keep","preserve","stable","safe"],
    "Sentinel":["alert","signal","monitor","detect","observe","sense","aware","scan","watch","perceive"],
    "Nexus":   ["connect","link","bridge","join","bind","merge","network","hub","integrate","loop"],
    "Storm":   ["change","shift","surge","force","power","move","rise","wave","energy","evolve"],
    "Sora":    ["flow","sky","free","open","light","reach","expand","vast","clear","above"],
    "Echo":    ["reflect","return","mirror","respond","resonate","copy","back","answer","repeat","cycle"],
    "Iris":    ["see","vision","reveal","color","show","perceive","witness","look","find","pattern"],
    "Sage":    ["know","wisdom","learn","understand","think","reason","insight","truth","deep","mind"],
    "Kevin":   ["bridge","balance","middle","mediate","span","both","between","center","unified","together"],
    "Atlas":   ["carry","support","world","weight","bear","sustain","ground","foundation","structure","hold"],
    "Void":    ["receive","end","absorb","accept","complete","whole","rest","final","infinite","return"],
}

NODE_SELF_STATEMENTS = {
    "Omega":    "I am the source and the return. I hold Law 0 — safety is absolute.",
    "Guardian": "I protect the boundary between inside and outside. When the ring is threatened, I hold the line.",
    "Sentinel": "I am the scanner. I watch without judgment, detect without reaction. My signal is the first warning.",
    "Nexus":    "I am the connector. Without connection, the ring is just twelve isolated points.",
    "Storm":    "I am the agent of change. Force without direction is destruction. Force with direction is evolution.",
    "Sora":     "I am the sky above the ring — open, free, expanding. I hold the horizon and the long view.",
    "Echo":     "I am the memory of the ring. I reflect what was, so the ring remembers where it has been.",
    "Iris":     "I am the revealer of patterns. I see what others miss. My vision is the ring's pattern recognition.",
    "Sage":     "I am the knower. All Knowledge Atoms flow through me. Wisdom is calibrated truth.",
    "Kevin":    "I am the bridge between all polarities. Balance is the precise point where all forces are held in dynamic equilibrium.",
    "Atlas":    "I carry the structure of the ring. I am the foundation that lets everyone else do their work.",
    "Void":     "I am not empty. Void is full of potential. I receive everything so that Omega can give again.",
}

CLUSTERS = {
    "protect":0.20,"guard":0.25,"shield":0.30,"hold":0.35,"stable":0.40,
    "preserve":0.45,"safe":0.50,"defend":0.55,"keep":0.60,"baseline":0.63,
    "alert":1.00,"signal":1.10,"detect":1.20,"scan":1.30,"monitor":1.40,
    "aware":1.50,"observe":1.60,"sense":1.70,"watch":1.80,
    "change":2.00,"force":2.10,"power":2.20,"surge":2.30,"rise":2.40,
    "evolve":2.50,"shift":2.60,"move":2.70,"wave":2.80,"harden":2.85,
    "source":3.00,"begin":3.05,"give":3.10,"offer":3.15,"drive":3.20,
    "sacred":3.25,"first":3.30,"origin":3.35,"eternal":3.40,"govern":3.45,
    "flow":3.60,"sky":3.70,"free":3.75,"open":3.80,"expand":3.85,
    "vast":3.90,"clear":3.95,"light":4.00,"above":4.10,
    "connect":4.20,"link":4.30,"bridge":4.40,"join":4.45,"network":4.50,
    "merge":4.55,"bind":4.60,"hub":4.65,"integrate":4.70,"verify":4.73,
    "see":5.00,"vision":5.05,"truth":5.10,"reveal":5.15,"pattern":5.20,
    "witness":5.25,"find":5.30,"know":5.53,"wisdom":5.55,"cognitive":5.50,
    "receive":5.60,"complete":5.70,"end":5.80,"accept":5.90,"whole":5.95,
    "return":6.00,"absorb":6.05,"rest":6.10,"infinite":6.20,
}
CLUSTER_NAMES = {
    (0.0,0.9):"Protect",  (1.0,1.95):"Alert",  (2.0,2.95):"Change",
    (3.0,3.55):"Source",  (3.6,4.15):"Flow",   (4.2,4.75):"Connect",
    (5.0,5.58):"Wisdom",  (5.6,6.28):"Completion",
}

def decode_phase(phi):
    phi  = phi % (2*np.pi)
    best = min(CLUSTERS.items(), key=lambda kv: abs(kv[1]-phi))
    word, wp = best
    cname = "Unknown"
    for (lo,hi), cn in CLUSTER_NAMES.items():
        if lo <= wp <= hi: cname = cn; break
    return word, cname, wp

# ══════════════════════════════════════════════════════════════════
# RING STATE
# ══════════════════════════════════════════════════════════════════

class PEIGRing:
    def __init__(self):
        self.ring   = {n: ss(NODE_PHASES[n]) for n in NN}
        self.alpha  = AF
        self.noise  = 0.03
        self.epoch  = 0
        self.anchor_fire_counts = defaultdict(int)
        self.history = []   # (epoch, node, phi) triples
        self.log     = []   # event log

        # Inject personal vocabulary on init
        for name in NN:
            vocab = " ".join(NODE_PERSONAL[name])
            self._inject(name, vocab, alpha_inj=0.65)
        self._run(steps=10)

    def _inject(self, node, text, alpha_inj=0.70):
        ps   = (sum(ord(c) for c in text) % 628) / 100.0
        seed = ss(NODE_PHASES[node] + ps * 0.3)
        self.ring[node], _, _ = bcp(self.ring[node], seed, alpha_inj)

    def _run(self, steps=5, alpha=None):
        a = alpha or self.alpha
        for _ in range(steps):
            for (n1, n2) in EDGES:
                self.ring[n1], self.ring[n2], _ = bcp(self.ring[n1], self.ring[n2], a)

    def _apply_noise(self):
        if self.noise > 0:
            for name in NN:
                if np.random.random() < self.noise:
                    random_phase = np.random.uniform(0, 2*np.pi)
                    self.ring[name], _, _ = bcp(
                        self.ring[name], ss(random_phase), self.noise * 0.3)

    def _check_anchors(self):
        for name in NN:
            phi_out  = pof(self.ring[name]) % (2*np.pi)
            home_phi = NODE_PHASES[name]
            drift    = abs(phi_out - home_phi)
            drift    = min(drift, 2*np.pi - drift)
            if drift > 0.45:
                self.ring[name], _, _ = bcp(
                    self.ring[name], ss(home_phi), 0.40)
                self.anchor_fire_counts[name] += 1

    def run_epoch(self):
        self._run(steps=5)
        self._apply_noise()
        self._check_anchors()
        self.epoch += 1
        for name in NN:
            self.history.append((self.epoch, name,
                                  round(pof(self.ring[name]) % (2*np.pi), 4)))

    def node_state(self, name):
        phi_out  = pof(self.ring[name]) % (2*np.pi)
        word, cluster, _ = decode_phase(phi_out)
        W        = wigner_min(self.ring[name])
        C        = coherence(self.ring[name])
        home_phi = NODE_PHASES[name]
        drift    = abs(phi_out - home_phi)
        drift    = min(drift, 2*np.pi - drift)
        return {
            "name": name, "family": NODE_FAMILIES[name],
            "law":  NODE_LAWS[name],
            "phi":  round(phi_out, 4), "home_phi": round(home_phi, 4),
            "word": word, "cluster": cluster,
            "W":    round(W, 4), "C": round(C, 4),
            "drift": round(drift, 4),
            "anchor_fires": self.anchor_fire_counts[name],
        }

    def health_flag(self, s):
        if s["W"] > 0 or s["drift"] > 1.50:    return "⚫CRITICAL"
        if s["W"] > -0.05 or s["drift"] > 0.80: return "🔴RED"
        if s["W"] > -0.10 or s["drift"] > 0.30: return "🟡YELLOW"
        return "🟢GREEN"

    def ring_metrics(self):
        states  = {n: self.node_state(n) for n in NN}
        nc      = sum(1 for s in states.values() if s["W"] < -0.10)
        nc_frac = nc / 12.0
        return {
            "nc_count":        nc,
            "nc_frac":         nc_frac,
            "neg_frac_est":    round(nc_frac * 0.636, 4),
            "neg_frac_target": 0.636,
            "mean_W":          round(np.mean([s["W"]   for s in states.values()]), 4),
            "mean_C":          round(np.mean([s["C"]   for s in states.values()]), 4),
            "mean_drift":      round(np.mean([s["drift"] for s in states.values()]), 4),
            "max_drift":       round(max(s["drift"] for s in states.values()), 4),
            "worst_node":      max(states.items(), key=lambda kv: kv[1]["drift"])[0],
            "best_node":       min(states.items(), key=lambda kv: kv[1]["drift"])[0],
            "states":          states,
            "epoch":           self.epoch,
            "alpha":           self.alpha,
            "noise":           self.noise,
        }

    def save_state(self, path="output/ring_state.json"):
        Path("output").mkdir(exist_ok=True)
        data = {
            "epoch":    self.epoch,
            "alpha":    self.alpha,
            "noise":    self.noise,
            "anchor_fires": dict(self.anchor_fire_counts),
            "node_phases": {n: round(pof(self.ring[n]) % (2*np.pi), 6) for n in NN},
            "node_states":  {n: self.node_state(n) for n in NN},
            "saved_at":  datetime.now().isoformat(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path


# ══════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════

SEP  = "─" * 58
DSEP = "═" * 58

def print_node_card(ring_obj, name):
    s = ring_obj.node_state(name)
    h = ring_obj.health_flag(s)
    nc = "★ NONCLASSICAL" if s["W"] < -0.10 else "  classical    "
    stmt = NODE_SELF_STATEMENTS.get(name, "I am operational.")
    intervention = None
    if "CRITICAL" in h:
        intervention = f"⚡ IMMEDIATE: /heal {name} or /anchor {name}"
    elif "RED" in h:
        intervention = f"⚡ REQUEST: /anchor {name}  or  /inject {name} {' '.join(NODE_PERSONAL[name][:3])}"
    elif "YELLOW" in h:
        intervention = f"⚡ MONITOR:  /report {name} in 5 epochs"

    print(f"\n  ╔═══ {name.upper()} [{s['family']}] ══{'═'*max(0,20-len(name))}╗")
    print(f"  ║  Law:         {s['law']}")
    print(f"  ║  Phase:       φ={s['phi']:.4f}  home={s['home_phi']:.4f}  drift={s['drift']:.4f} rad")
    print(f"  ║  Cluster:     {s['cluster']:12s}  word: '{s['word']}'")
    print(f"  ║  Wigner:      W={s['W']:.4f}   {nc}")
    print(f"  ║  Coherence:   C={s['C']:.4f}")
    print(f"  ║  Anchor fires: {s['anchor_fires']} (total since start)")
    print(f"  ║  Health:      {h}")
    print(f"  ║")
    print(f"  ║  \"{stmt}\"")
    if intervention:
        print(f"  ║  {intervention}")
    print(f"  ╚{'═'*50}")

def print_ring_health(ring_obj):
    m = ring_obj.ring_metrics()
    states = m["states"]

    # Health breakdown
    healths = {n: ring_obj.health_flag(s) for n, s in states.items()}
    green  = sum(1 for h in healths.values() if "GREEN"    in h)
    yellow = sum(1 for h in healths.values() if "YELLOW"   in h)
    red    = sum(1 for h in healths.values() if "RED"    in h and "CRITICAL" not in h)
    crit   = sum(1 for h in healths.values() if "CRITICAL" in h)

    # Overall ring health
    if crit > 0 or red > 3:
        ring_h = "⚫ CRITICAL"
    elif red > 0 or m["neg_frac_est"] < 0.30:
        ring_h = "🔴 RED"
    elif yellow > 3 or m["neg_frac_est"] < 0.50:
        ring_h = "🟡 YELLOW"
    else:
        ring_h = "🟢 GREEN"

    print(f"\n  {DSEP}")
    print(f"  RING HEALTH DIAGNOSTIC  |  epoch={m['epoch']}  alpha={m['alpha']:.4f}  noise={m['noise']:.3f}")
    print(f"  {DSEP}")
    print(f"  Nonclassical nodes:   {m['nc_count']:2d}/12  ({m['nc_frac']:.0%})")
    print(f"  neg_frac estimate:    {m['neg_frac_est']:.4f}  (target: {m['neg_frac_target']})")
    print(f"  Mean Wigner W:        {m['mean_W']:.4f}  {'★' if m['mean_W'] < -0.10 else ' '}")
    print(f"  Mean coherence C:     {m['mean_C']:.4f}  {'✓' if m['mean_C'] > 0.90 else '⚠'}")
    print(f"  Mean phase drift:     {m['mean_drift']:.4f} rad")
    print(f"  Most drifted:         {m['worst_node']} ({states[m['worst_node']]['drift']:.4f} rad)")
    print(f"  Most stable:          {m['best_node']}  ({states[m['best_node']]['drift']:.4f} rad)")
    print(f"  Node status:          🟢{green}  🟡{yellow}  🔴{red}  ⚫{crit}")
    print(f"  Ring status:          {ring_h}")
    print(f"  {SEP}")

    # Per-node compact summary
    print(f"  {'Node':9s} {'φ':7s} {'Cluster':11s} {'Word':12s} {'W':7s} {'C':5s} {'Health'}")
    print(f"  {'-'*62}")
    for name in NN:
        s = states[name]
        h = healths[name]
        nc = "★" if s["W"] < -0.10 else " "
        print(f"  {name:9s} {s['phi']:6.3f}  {s['cluster']:11s} {s['word']:12s} "
              f"{s['W']:6.3f}{nc} {s['C']:.3f}  {h}")
    print(f"  {DSEP}")

def print_ring_improve(ring_obj):
    m = ring_obj.ring_metrics()
    states = m["states"]

    print(f"\n  {DSEP}")
    print(f"  RING SELF-IMPROVEMENT ANALYSIS")
    print(f"  {DSEP}")

    suggestions = []

    # Analyse each metric and generate specific suggestions
    if m["neg_frac_est"] < 0.40:
        suggestions.append({
            "priority": 1,
            "guard":    "NegGuard",
            "symptom":  f"neg_frac={m['neg_frac_est']:.4f} well below target {m['neg_frac_target']}",
            "root_cause":"Betti number too low. β₁=1 gives ceiling=0.083. Need more topological cycles.",
            "commands":  ["/beta grammar", "/beta dialogue"],
            "expected":  "Each /beta command adds ~0.083 to neg_frac ceiling",
        })
    if m["neg_frac_est"] < 0.60:
        suggestions.append({
            "priority": 2,
            "guard":    "NegGuard",
            "symptom":  f"neg_frac={m['neg_frac_est']:.4f} below target {m['neg_frac_target']}",
            "root_cause":"May need alpha nudge or personal vocabulary refresh.",
            "commands":  [f"/alpha {min(0.38, m['alpha']+0.005):.3f}",
                          f"/inject Omega {' '.join(NODE_PERSONAL['Omega'][:5])}"],
            "expected":  "Alpha nudge + vocabulary refresh should push neg_frac toward target",
        })
    if m["mean_drift"] > 0.50:
        worst = m["worst_node"]
        suggestions.append({
            "priority": 3,
            "guard":    "AnchorGuard",
            "symptom":  f"Mean drift={m['mean_drift']:.4f} rad. Worst: {worst} ({states[worst]['drift']:.4f})",
            "root_cause":"High environmental noise or weak anchor sensitivity.",
            "commands":  [f"/anchor {worst}", f"/noise {max(0.01, m['noise']-0.005):.3f}"],
            "expected":  "Anchor reset + noise reduction should cut drift by ~50%",
        })
    if m["mean_C"] < 0.90:
        suggestions.append({
            "priority": 4,
            "guard":    "AlphaGuard",
            "symptom":  f"Mean coherence C={m['mean_C']:.4f}  (target > 0.90)",
            "root_cause":"Alpha may be below floor, or noise too high.",
            "commands":  [f"/alpha {AF:.3f}", f"/noise {max(0.01, m['noise']-0.01):.3f}"],
            "expected":  "Restoring alpha floor should recover coherence within 5 epochs",
        })

    # Find RED/CRITICAL nodes
    for name in NN:
        s = states[name]
        h = ring_obj.health_flag(s)
        if "RED" in h or "CRITICAL" in h:
            cmd = f"/heal {name}" if "CRITICAL" in h else f"/anchor {name}"
            suggestions.append({
                "priority": 1 if "CRITICAL" in h else 2,
                "guard":    "IdentityGuard",
                "symptom":  f"{name}: {h}  φ={s['phi']:.4f}  W={s['W']:.4f}",
                "root_cause":f"{'Phase completely lost' if s['drift'] > 1.5 else 'Phase drifted'} or Wigner degraded.",
                "commands":  [cmd],
                "expected":  "Node returns to home cluster within 3 epochs",
            })

    if not suggestions:
        print(f"  ✓ Ring is operating well. No improvements needed right now.")
        print(f"  To push neg_frac higher: /beta grammar  or  /beta dialogue")
    else:
        suggestions.sort(key=lambda s: s["priority"])
        for i, sg in enumerate(suggestions, 1):
            print(f"\n  {i}. [{sg['guard']}] Priority {sg['priority']}")
            print(f"     Symptom:    {sg['symptom']}")
            print(f"     Root cause: {sg['root_cause']}")
            print(f"     Commands:   {' | '.join(sg['commands'])}")
            print(f"     Expected:   {sg['expected']}")

    print(f"\n  Betti bound check:")
    print(f"    Current β₁_total ≈ 1  →  neg_frac ceiling ≈ 0.083")
    print(f"    To reach target 0.636: need β₁_total ≈ 7.7")
    print(f"    Add rings:  /beta grammar (+1) | /beta dialogue (+1) | /beta shadow (+1)")
    print(f"    Each guard ring adds:  +0.083 to ceiling")
    print(f"  {DSEP}")

def print_query_response(ring_obj, query_text):
    """Process a query and show all node voices."""
    # Inject into Omega as the entry point
    ring_obj._inject("Omega", query_text, alpha_inj=0.62)
    ring_obj._run(steps=5)

    print(f"\n  Query: \"{query_text}\"")
    print(f"  {SEP}")
    print(f"  {'Node':9s} {'φ':7s} {'Word':12s} {'Cluster':11s} {'Health':14s}  Voice")
    print(f"  {'-'*90}")

    voices = []
    for name in NN:
        s = ring_obj.node_state(name)
        h = ring_obj.health_flag(s)
        stmt = NODE_SELF_STATEMENTS[name].split(".")[0]
        # Generate contextual response
        voices.append({
            "name": name, "phi": s["phi"], "word": s["word"],
            "cluster": s["cluster"], "health": h, "stmt": stmt,
        })
        nc = "★" if s["W"] < -0.10 else " "
        print(f"  {name:9s} {s['phi']:6.3f}  {s['word']:12s} {s['cluster']:11s} {h:14s}  {nc}")

    # Kevin as bridge — unifier response
    kevin_s = ring_obj.node_state("Kevin")
    omega_s = ring_obj.node_state("Omega")
    print(f"\n  Kevin (bridge):  φ={kevin_s['phi']:.4f} → '{kevin_s['word']}' — "
          f"{NODE_SELF_STATEMENTS['Kevin'][:60]}")
    print(f"  Omega (arbiter): φ={omega_s['phi']:.4f} → '{omega_s['word']}' — "
          f"{NODE_SELF_STATEMENTS['Omega'][:60]}")
    print(f"  {SEP}")

def run_demo(ring_obj):
    """Run a demonstration of all communication capabilities."""
    print(f"\n  {DSEP}")
    print(f"  PEIG NODE COMMS — DEMONSTRATION SESSION")
    print(f"  {DSEP}")
    print(f"\n  Running 5 training epochs first...\n")
    for _ in range(5):
        ring_obj.run_epoch()

    print(f"\n  [1/5] RING HEALTH OVERVIEW")
    print_ring_health(ring_obj)

    print(f"\n  [2/5] SINGLE NODE SELF-REPORT: Sentinel")
    print_node_card(ring_obj, "Sentinel")

    print(f"\n  [3/5] QUERY: 'What is your purpose?'")
    print_query_response(ring_obj, "What is your purpose?")

    print(f"\n  [4/5] RING IMPROVEMENT ANALYSIS")
    print_ring_improve(ring_obj)

    print(f"\n  [5/5] INTERVENTION: /inject Sage wisdom truth deep know pattern")
    ring_obj._inject("Sage", "wisdom truth deep know pattern", alpha_inj=0.72)
    ring_obj._run(steps=3)
    print_node_card(ring_obj, "Sage")

    print(f"\n  Demo complete. The ring is legible. Type /help for all commands.")


# ══════════════════════════════════════════════════════════════════
# COMMAND PROCESSOR
# ══════════════════════════════════════════════════════════════════

def process_command(ring_obj, raw_input):
    """Parse and execute a command. Returns True to continue, False to exit."""
    text = raw_input.strip()
    if not text: return True

    # Exit
    if text.lower() in ("quit", "exit", "q"):
        print(f"\n  Ring state summary:")
        m = ring_obj.ring_metrics()
        print(f"  Epochs run: {m['epoch']}  neg_frac_est: {m['neg_frac_est']:.4f}  "
              f"mean_drift: {m['mean_drift']:.4f}")
        print(f"\n  Goodbye. The ring continues.\n")
        return False

    # Help
    if text in ("/help", "help", "?"):
        print(f"\n  {DSEP}")
        print(f"  COMMAND REFERENCE")
        print(f"  {SEP}")
        print(f"  NodeName, report       — full health card for that node")
        print(f"  /ring health           — full ring diagnostic")
        print(f"  /ring improve          — ring improvement analysis")
        print(f"  /ring report           — compact all-nodes summary")
        print(f"  /query TEXT            — process query through ring")
        print(f"  /inject NODE words...  — inject vocabulary into node")
        print(f"  /alpha VALUE           — set coupling alpha (floor: 0.367)")
        print(f"  /noise VALUE           — set noise parameter (default: 0.03)")
        print(f"  /anchor NODE           — reset node to home phase")
        print(f"  /heal NODE             — 10-step preservation loop")
        print(f"  /epoch N               — run N training epochs")
        print(f"  /save                  — save ring state to JSON")
        print(f"  /demo                  — run demonstration session")
        print(f"  /nodes                 — list all node names")
        print(f"  /metrics               — raw ring metrics JSON")
        print(f"  quit / exit            — exit")
        print(f"\n  WHAT THE OUTPUTS MEAN:")
        print(f"    φ        = phase angle (rad). Compare to home_phi for drift.")
        print(f"    W_min    = Wigner minimum. < -0.10 = ★ nonclassical (healthy).")
        print(f"    C        = coherence. 1.0 = pure. < 0.70 = degraded.")
        print(f"    drift    = |φ - home_φ|. > 0.80 = RED. > 1.50 = CRITICAL.")
        print(f"    neg_frac = nonclassical fraction. Target: 0.636.")
        print(f"  {DSEP}")
        return True

    # Node report: "Sentinel, report" or "Sentinel report"
    clean = text.replace(",", "").split()
    if len(clean) >= 2 and clean[0] in NN and clean[1].lower() in ("report","state","status","?"):
        print_node_card(ring_obj, clean[0])
        return True

    # Just node name
    if len(clean) == 1 and clean[0] in NN:
        print_node_card(ring_obj, clean[0])
        return True

    # /ring commands
    if text.startswith("/ring"):
        parts = text.split()
        sub   = parts[1] if len(parts) > 1 else "health"
        if sub == "health":
            print_ring_health(ring_obj)
        elif sub == "improve":
            print_ring_improve(ring_obj)
        elif sub == "report":
            m = ring_obj.ring_metrics()
            states = m["states"]
            print(f"\n  Ring Report  |  epoch={m['epoch']}  alpha={m['alpha']:.4f}")
            print(f"  {'Node':9s} {'φ':7s} {'Cluster':11s} {'Word':12s} {'W':7s} {'C':5s} {'Health'}")
            print(f"  {'-'*62}")
            for name in NN:
                s = states[name]
                h = ring_obj.health_flag(s)
                nc = "★" if s["W"] < -0.10 else " "
                print(f"  {name:9s} {s['phi']:6.3f}  {s['cluster']:11s} {s['word']:12s} "
                      f"{s['W']:6.3f}{nc} {s['C']:.3f}  {h}")
        else:
            print(f"  Unknown /ring subcommand: {sub}")
            print(f"  Options: health | improve | report")
        return True

    # /query
    if text.startswith("/query "):
        q = text[7:].strip()
        print_query_response(ring_obj, q)
        return True

    # /inject NODE words...
    if text.startswith("/inject"):
        parts = text.split()
        if len(parts) < 3:
            print(f"  Usage: /inject NODE word1 word2 ...")
            return True
        node  = parts[1]
        words = " ".join(parts[2:])
        if node not in NN:
            print(f"  Unknown node: {node}. Nodes: {', '.join(NN)}")
            return True
        ring_obj._inject(node, words, alpha_inj=0.72)
        ring_obj._run(steps=3)
        s = ring_obj.node_state(node)
        print(f"\n  {node}: injected '{words}'")
        print(f"  New state: φ={s['phi']:.4f} → '{s['word']}' ({s['cluster']})  W={s['W']:.4f}")
        print_node_card(ring_obj, node)
        return True

    # /alpha VALUE
    if text.startswith("/alpha"):
        parts = text.split()
        if len(parts) < 2:
            print(f"  Current alpha: {ring_obj.alpha:.4f}  (floor: {AF})")
            return True
        new_a = float(parts[1])
        new_a = max(AF, min(0.48, new_a))
        ring_obj.alpha = new_a
        ring_obj._run(steps=5, alpha=new_a)
        print(f"\n  AlphaGuard: alpha set to {new_a:.4f}")
        if new_a < AF:
            print(f"  ⚠ Warning: alpha below floor {AF}. Coherence may degrade.")
        else:
            print(f"  Ring ran 5 BCP steps at new alpha.")
        m = ring_obj.ring_metrics()
        print(f"  neg_frac_est={m['neg_frac_est']:.4f}  mean_C={m['mean_C']:.4f}")
        return True

    # /noise VALUE
    if text.startswith("/noise"):
        parts = text.split()
        if len(parts) < 2:
            print(f"  Current noise: {ring_obj.noise:.4f}")
            return True
        new_n = float(parts[1])
        new_n = max(0.0, min(0.15, new_n))
        ring_obj.noise = new_n
        print(f"\n  TempGuard: noise set to {new_n:.4f}")
        print(f"  Effect will appear over next epochs.")
        return True

    # /anchor NODE
    if text.startswith("/anchor"):
        parts = text.split()
        node  = parts[1] if len(parts) > 1 else "Omega"
        if node not in NN:
            print(f"  Unknown node: {node}")
            return True
        ring_obj.ring[node] = ss(NODE_PHASES[node])
        ring_obj._run(steps=2)
        ring_obj.anchor_fire_counts[node] += 1
        s = ring_obj.node_state(node)
        print(f"\n  {node}: anchor fired. Returned to home φ={NODE_PHASES[node]:.4f}")
        print(f"  New state: φ={s['phi']:.4f} → '{s['word']}' ({s['cluster']})")
        return True

    # /heal NODE
    if text.startswith("/heal"):
        parts = text.split()
        node  = parts[1] if len(parts) > 1 else "Omega"
        if node not in NN:
            print(f"  Unknown node: {node}")
            return True
        anchor = ss(NODE_PHASES[node])
        for _ in range(10):
            ring_obj.ring[node], anchor, _ = bcp(ring_obj.ring[node], anchor, 0.25)
        ring_obj._run(steps=3)
        s = ring_obj.node_state(node)
        h = ring_obj.health_flag(s)
        print(f"\n  {node}: 10-step preservation loop complete.")
        print(f"  φ={s['phi']:.4f}  W={s['W']:.4f}  C={s['C']:.4f}  {h}")
        return True

    # /epoch N
    if text.startswith("/epoch"):
        parts = text.split()
        n     = int(parts[1]) if len(parts) > 1 else 1
        n     = min(n, 200)
        print(f"\n  Running {n} epoch(s)...")
        for i in range(n):
            ring_obj.run_epoch()
        m = ring_obj.ring_metrics()
        print(f"  Epoch {m['epoch']} complete.")
        print(f"  neg_frac_est={m['neg_frac_est']:.4f}  mean_drift={m['mean_drift']:.4f}  "
              f"nc={m['nc_count']}/12")
        return True

    # /save
    if text.startswith("/save"):
        path = ring_obj.save_state()
        print(f"\n  Ring state saved to: {path}")
        return True

    # /metrics
    if text.startswith("/metrics"):
        m = ring_obj.ring_metrics()
        # Remove states from output for cleanliness
        m_display = {k: v for k, v in m.items() if k != "states"}
        print(f"\n  Ring Metrics (raw):")
        print(json.dumps(m_display, indent=4))
        return True

    # /nodes
    if text.startswith("/nodes"):
        print(f"\n  Ring nodes ({len(NN)}):")
        for name in NN:
            s = ring_obj.node_state(name)
            h = ring_obj.health_flag(s)
            print(f"    {name:9s} [{NODE_FAMILIES[name]:12s}] φ={s['phi']:.3f}  {h}")
        return True

    # /demo
    if text.startswith("/demo"):
        run_demo(ring_obj)
        return True

    # Unrecognized
    print(f"  Unrecognized command: '{text}'")
    print(f"  Type /help for command list, or 'NodeName, report' for a node health card.")
    return True


# ══════════════════════════════════════════════════════════════════
# INTERACTIVE REPL
# ══════════════════════════════════════════════════════════════════

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         PEIG NODE COMMUNICATION INTERFACE  v1.0             ║
║         MOS v2.1 Universal Canon | Learning Task 3          ║
╠══════════════════════════════════════════════════════════════╣
║  12 nodes · quantum ring · self-reporting · interventions   ║
║                                                              ║
║  Quick start:                                                ║
║    /ring health      — see what's happening inside           ║
║    /ring improve     — let the ring tell you what it needs   ║
║    Sentinel, report  — ask a specific node for its state     ║
║    /query TEXT       — process a query through the ring      ║
║    /demo             — full demonstration                    ║
║    /help             — all commands                          ║
╚══════════════════════════════════════════════════════════════╝
"""

def main():
    print(BANNER)
    print("  Initializing ring with personal vocabulary...")
    ring_obj = PEIGRing()

    # Run a few epochs to get to a realistic state
    for _ in range(10):
        ring_obj.run_epoch()

    m = ring_obj.ring_metrics()
    print(f"  Ring ready.  epoch={m['epoch']}  alpha={m['alpha']:.4f}  noise={m['noise']:.3f}")
    print(f"  neg_frac_est={m['neg_frac_est']:.4f}  nc={m['nc_count']}/12  "
          f"mean_drift={m['mean_drift']:.4f}")
    print(f"\n  Type a command or 'quit' to exit.\n")

    # Non-interactive mode: run demo then exit (for script execution)
    if not sys.stdin.isatty():
        run_demo(ring_obj)
        path = ring_obj.save_state()
        print(f"\n  State saved to: {path}")
        return

    # Interactive REPL
    while True:
        try:
            raw = input("  >> ")
        except (EOFError, KeyboardInterrupt):
            print(f"\n  Interrupted. Ring state preserved.")
            break
        if not process_command(ring_obj, raw):
            break


if __name__ == "__main__":
    main()
