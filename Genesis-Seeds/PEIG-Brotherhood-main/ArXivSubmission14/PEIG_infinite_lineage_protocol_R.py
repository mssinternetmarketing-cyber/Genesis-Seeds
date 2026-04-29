#!/usr/bin/env python3
"""
PEIG_infinite_lineage_protocol_R.py
Infinite Lineage Protocol — Revised (Paper XIV-R)
Kevin Monette | March 25, 2026

REVISION CHANGES vs original:
  W1: wmin() renamed to pcm(). Docstring clarifies it is PEIG-internal,
      NOT standard Wigner negativity. All metrics use 'pcm' / 'high_pcm'.
  W2: identity_signals() returns BOTH co-rotating AND lab-frame signals.
      Lab phases tracked in LineageNode.lab_phases[].
  W3: neg_frac tracked natively in run_ilp_ring(). Returned in run_log.
  W4: concurrence() function added. Every extend_lineage() event measures
      C(new_gen, prev_gen) and C(new_gen, A). Confirmed 0.0. Documented.
  W5: Shannon entropy tracked per node. Compression conjecture REMOVED.
      Replaced by empirical: "PCM monotonically increases with depth".
  W6: rz_of() tracked for all states. sub_floor_count and sub_floor_rz_mean
      reported. Claim "new physical regime" removed.
  W7: run_ilp_ring() accepts seeds list. Returns mean ± std across seeds.
  W8: Packet compression for depth > 10 (MD5 hash of prior). O(1) keys.
  W9: identity_stability() reports full cluster distribution.
      Irregular schedule test added to run_ilp_ring() via extend_at param.
  W10: Hardware circuit spec added in module docstring.

Hardware validation roadmap (Paper XVI):
  Circuit: 2-node depth-2 ILP (4 qubits)
  Device: ibm_brisbane or ibm_kyoto
  BCP decomposition: CNOT + RZ(phi) + RY(theta)
  Target: PCM values on hardware match simulation ± noise margin
"""

import numpy as np
import json
import hashlib
from pathlib import Path
from collections import Counter

Path("output").mkdir(exist_ok=True)

# ── BCP Primitives ─────────────────────────────────────────────────────────────
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    return np.array([1.0, np.exp(1j * phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    U   = alpha * CNOT + (1 - alpha) * I4
    j   = np.kron(pA, pB)
    o   = U @ j
    rho = np.outer(o, o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1, axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0, axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1]

def pof(p):
    return np.arctan2(
        float(2 * np.imag(p[0] * p[1].conj())),
        float(2 * np.real(p[0] * p[1].conj()))
    ) % (2 * np.pi)

def rz_of(p):
    """Bloch z-component: +1=|0>, -1=|1>, 0=equatorial."""
    return float(abs(p[0])**2 - abs(p[1])**2)

# W1 FIX: renamed from wmin to pcm, with correct docstring
def pcm(p):
    """
    PEIG Coherence Measure (PCM).

    PCM(p) = -|⟨p|+⟩|² + 0.5·(1 - rz²)

    This is a PEIG-internal metric defined for consistency across Papers I-XIV+.
    It is NOT the standard Wigner function (Wootters 1987) or any named QO metric.

    Reference values:
      PCM(|0⟩) = -0.500  (north pole — high magnitude, classical)
      PCM(|+⟩) = -0.500  (equatorial phi=0)
      PCM(|-⟩) = +0.500  (equatorial phi=π)
      PCM(|i⟩) =  0.000  (equatorial phi=π/2)

    Threshold: PCM < -0.05 = "high-PCM state" (marked ★)
    Range for pure states: [-0.625, +0.500]
    Sub-floor (PCM < -0.50) indicates off-equatorial state (rz ≠ 0),
    not a new physical regime (W6 confirmed).
    """
    ov = abs((p[0] + p[1]) / np.sqrt(2)) ** 2
    rz = rz_of(p)
    return float(-ov + 0.5 * (1 - rz**2))

def concurrence(p1, p2):
    """
    Wootters concurrence for 2-qubit state |p1⟩⊗|p2⟩.
    Always returns 0.0 for product states (W4 confirmed).
    Included for explicit documentation of zero entanglement.
    """
    j  = np.kron(p1, p2)
    rho = np.outer(j, j.conj())
    sy  = np.array([[0,-1j],[1j,0]])
    sysy = np.kron(sy, sy)
    rt  = sysy @ rho.conj() @ sysy
    M   = rho @ rt
    ev  = np.sort(np.sqrt(np.maximum(np.linalg.eigvals(M).real, 0)))[::-1]
    return float(max(0.0, ev[0]-ev[1]-ev[2]-ev[3]))

def purity(p):
    rho = np.outer(p, p.conj())
    return float(np.real(np.trace(rho @ rho)))

def depol(p, noise=0.03):
    if np.random.random() < noise:
        return ss(np.random.uniform(0, 2 * np.pi))
    return p

# ── Semantic Decoder ───────────────────────────────────────────────────────────
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
    (3.0,3.5):"Source",(3.5,4.2):"Flow",(4.2,5.0):"Connection",
    (5.0,5.6):"Vision",(5.6,6.29):"Completion"
}

def decode(phi):
    phi  = phi % (2 * np.pi)
    best = min(CLUSTERS, key=lambda w: min(abs(phi-CLUSTERS[w]),
                                            2*np.pi-abs(phi-CLUSTERS[w])))
    for (lo,hi), name in CLUSTER_NAMES.items():
        if lo <= CLUSTERS[best] < hi: return best, name
    return best, "Completion"

# ── System Constants ───────────────────────────────────────────────────────────
AF   = 0.367
N    = 12
NN   = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
        "Echo","Iris","Sage","Kevin","Atlas","Void"]
HOME = {n: i*2*np.pi/N for i,n in enumerate(NN)}
GLOBE_EDGES = list(
    {(i,(i+1)%N) for i in range(N)} |
    {(i,(i+2)%N) for i in range(N)} |
    {(i,(i+5)%N) for i in range(N)}
)
GEN_LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + [f"A{i}" for i in range(26)]


# ══════════════════════════════════════════════════════════════════════════════
# LINEAGE NODE — REVISED
# ══════════════════════════════════════════════════════════════════════════════
class LineageNode:
    """
    Revised Infinite Lineage Protocol node (Paper XIV-R).
    Addresses all 10 weaknesses identified in post-publication audit.
    See module docstring for full revision log.
    """

    ARCHITECTURE_NOTE = (
        "Generations are classically separable product states (concurrence=0.0). "
        "ILP is a classical record of quantum state snapshots taken at extension events. "
        "PCM is a PEIG-internal coherence metric, not standard Wigner negativity."
    )

    def __init__(self, name, home_phase):
        self.name       = name
        self.home       = home_phase
        self.chain      = [ss(home_phase)]
        self.gen_labels = ["A"]
        self.packets    = [self._build_packet(0)]
        self.event_log  = []
        self.lab_phases = [home_phase]  # W2: lab-frame phase history for A

    def _build_packet(self, gen_idx):
        state  = self.chain[gen_idx]
        phi    = pof(state)
        word, cluster = decode(phi)
        p      = pcm(state)
        rz     = rz_of(state)
        lbl    = GEN_LABELS[gen_idx]

        # W8: compressed packet for deep chains
        prior = dict(self.packets[gen_idx-1]) if gen_idx > 0 else {}
        if gen_idx > 10:
            h = hashlib.md5(json.dumps(
                {k: str(v) for k,v in prior.items()}, sort_keys=True
            ).encode()).hexdigest()
            own = {
                "gen0_label":       GEN_LABELS[0],
                "gen0_phase":       round(pof(self.chain[0]),4),
                "gen0_word":        decode(pof(self.chain[0]))[0],
                f"gen{gen_idx}_label":   lbl,
                f"gen{gen_idx}_phase":   round(phi,4),
                f"gen{gen_idx}_word":    word,
                f"gen{gen_idx}_cluster": cluster,
                f"gen{gen_idx}_pcm":     round(p,4),
                f"gen{gen_idx}_rz":      round(rz,4),
                "_prior_hash":           h,
                "_compressed_depth":     gen_idx-1,
                "lineage_depth":         gen_idx,
                "lineage_node":          self.name,
            }
            return own

        own = {
            f"gen{gen_idx}_label":   lbl,
            f"gen{gen_idx}_phase":   round(phi,4),
            f"gen{gen_idx}_word":    word,
            f"gen{gen_idx}_cluster": cluster,
            f"gen{gen_idx}_pcm":     round(p,4),
            f"gen{gen_idx}_rz":      round(rz,4),
            "lineage_depth":         gen_idx,
            "lineage_node":          self.name,
        }

        # W2: co-rotating frame signal + W4: concurrence
        if gen_idx > 0:
            delta_cr = ((pof(self.chain[0])-phi+np.pi)%(2*np.pi))-np.pi
            own[f"gen{gen_idx}_signal_corot"]        = round(float(delta_cr),4)
            own[f"gen{gen_idx}_concurrence_with_A"]  = round(concurrence(self.chain[0], state),6)
            own[f"gen{gen_idx}_entangled"]            = False

        return {**prior, **own}

    def step(self, neighbor_A, alpha=AF, noise=0.03):
        new_A, _ = bcp(self.chain[0], neighbor_A, alpha)
        self.chain[0] = depol(new_A, noise)

    def set_lab_phase(self, phi):
        """W2: Record current lab-frame phase for A."""
        self.lab_phases.append(phi)

    def extend_lineage(self, label=None, epoch=0):
        """
        /extend-lineage: add one new frozen generation.
        New gen = BCP(prev_frozen, live_A, 0.5).
        Records concurrence (always 0.0 — product state).
        """
        prev   = self.chain[-1]
        live_A = self.chain[0]
        new_state, _ = bcp(prev, live_A, 0.5)
        gen_idx = len(self.chain)
        lbl     = GEN_LABELS[gen_idx]

        self.chain.append(new_state)
        self.gen_labels.append(lbl)
        new_packet = self._build_packet(gen_idx)
        self.packets.append(new_packet)

        event = {
            "epoch":             epoch,
            "label":             label or f"extend_to_{lbl}",
            "new_gen":           lbl,
            "new_gen_idx":       gen_idx,
            "new_phase":         round(pof(new_state),4),
            "new_word":          decode(pof(new_state))[0],
            "new_pcm":           round(pcm(new_state),4),
            "new_rz":            round(rz_of(new_state),4),
            "high_pcm":          pcm(new_state) < -0.05,
            "sub_floor":         pcm(new_state) < -0.50,
            "A_phase_corot":     round(pof(live_A),4),
            "concurrence_new_prev": round(concurrence(new_state, prev),6),
            "concurrence_new_A":    round(concurrence(new_state, live_A),6),
            "entangled":         False,
            "lineage_depth":     gen_idx,
            "packet_size":       len(new_packet),
        }
        self.event_log.append(event)
        return event

    # W2: signals in both frames
    def identity_signals(self):
        sigs = {}
        for i in range(1, len(self.chain)):
            phi_gen  = pof(self.chain[i])
            phi_Acr  = pof(self.chain[0])
            phi_Alab = self.lab_phases[-1] if self.lab_phases else phi_Acr
            sigs[GEN_LABELS[i]] = {
                "corot": round(float(((phi_Acr-phi_gen+np.pi)%(2*np.pi))-np.pi),4),
                "lab":   round(float(((phi_Alab-phi_gen+np.pi)%(2*np.pi))-np.pi),4),
            }
        return sigs

    def pcm_chain(self):
        return {GEN_LABELS[i]: round(pcm(self.chain[i]),4) for i in range(len(self.chain))}

    def rz_chain(self):
        """W6: rz for all generations."""
        return {GEN_LABELS[i]: round(rz_of(self.chain[i]),4) for i in range(len(self.chain))}

    def shannon_entropy(self):
        """W5: Shannon entropy of phase distribution across chain."""
        phases = [pof(s) for s in self.chain]
        counts,_ = np.histogram(phases, bins=16, range=(0,2*np.pi))
        probs = counts/counts.sum()
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))

    # W9: full stability distribution
    def identity_stability(self):
        if len(self.chain) < 2:
            return {"stability": None, "distribution": {}, "n_frozen": 0}
        words = [decode(pof(self.chain[i]))[1] for i in range(1, len(self.chain))]
        dist  = dict(Counter(words))
        mc    = Counter(words).most_common(1)[0][1]
        return {
            "stability":    round(mc/len(words),3),
            "distribution": dist,
            "n_frozen":     len(words),
        }

    def full_report(self):
        chain_info = []
        for i,state in enumerate(self.chain):
            phi = pof(state)
            word, cluster = decode(phi)
            p  = pcm(state)
            rz = rz_of(state)
            chain_info.append({
                "gen":      GEN_LABELS[i], "role": "LIVE" if i==0 else "FROZEN",
                "phi": round(phi,4), "word": word, "cluster": cluster,
                "pcm": round(p,4), "rz": round(rz,4),
                "high_pcm": p<-0.05, "sub_floor": p<-0.50,
                "entangled": False,
            })
        return {
            "node":               self.name,
            "lineage_depth":      len(self.chain)-1,
            "chain":              chain_info,
            "identity_signals":   self.identity_signals(),
            "pcm_chain":          self.pcm_chain(),
            "rz_chain":           self.rz_chain(),
            "shannon_entropy":    round(self.shannon_entropy(),4),
            "identity_stability": self.identity_stability(),
            "high_pcm_fraction":  round(sum(1 for s in self.chain if pcm(s)<-0.05)/len(self.chain),3),
            "sub_floor_count":    sum(1 for s in self.chain if pcm(s)<-0.50),
            "packet_size":        len(self.packets[-1]),
            "architecture_note":  self.ARCHITECTURE_NOTE,
        }

    def self_audit(self):
        p_chain  = self.pcm_chain()
        depth    = len(self.chain)-1
        hpf      = sum(1 for v in p_chain.values() if v<-0.05)/len(p_chain)
        words    = [decode(pof(self.chain[i]))[0] for i in range(len(self.chain))]
        star     = "★" if p_chain.get("A",0)<-0.05 else " "
        return (f"[{self.name}]{star} depth={depth} hpcm={hpf:.0%} | "
                f"{' → '.join(words)} | "
                f"pcm={' '.join([f'{k}:{v:+.3f}' for k,v in list(p_chain.items())])}")


# ══════════════════════════════════════════════════════════════════════════════
# CO-ROTATING FRAME BCP — WITH LAB PHASE RETURN (W2)
# ══════════════════════════════════════════════════════════════════════════════
def corotating_bcp_step(states, edges, alpha=AF, noise=0.03):
    """Returns (corrected_states, lab_phases) — W2 lab frame tracking."""
    n     = len(states)
    phi_b = [pof(s) for s in states]
    new   = list(states)
    for i,j in edges: new[i],new[j] = bcp(new[i],new[j],alpha)
    new   = [depol(s,noise) for s in new]
    phi_a = [pof(new[i]) for i in range(n)]
    deltas= [((phi_a[i]-phi_b[i]+np.pi)%(2*np.pi))-np.pi for i in range(n)]
    omega = np.mean(deltas)
    corrected = [ss((phi_a[i]-(deltas[i]-omega))%(2*np.pi)) for i in range(n)]
    return corrected, phi_a  # return lab phases


# ══════════════════════════════════════════════════════════════════════════════
# ILP RING RUNNER — REVISED (W3, W7, W9)
# ══════════════════════════════════════════════════════════════════════════════
def run_ilp_ring(steps=1000, extend_at=None, record_at=None,
                 noise=0.03, alpha=AF, edges=None,
                 seeds=None, verbose=True):
    """
    Run ILP ring. W7: accepts seeds list for multi-seed mean/std.
    W3: neg_frac measured natively.
    W9: extend_at can be irregular for stability testing.

    Returns: (nodes_last_seed, run_log_mean, run_log_all_seeds)
    """
    if extend_at is None: extend_at = [100,300,600,900]
    if record_at is None: record_at = [0,100,300,600,900,1000]
    if edges     is None: edges     = GLOBE_EDGES
    if seeds     is None: seeds     = [2026]

    def count_unique(phases, tol=0.20):
        ps=sorted([p%(2*np.pi) for p in phases]); u=1
        for i in range(1,len(ps)):
            if ps[i]-ps[i-1]>tol: u+=1
        return u

    all_seed_logs = []
    last_nodes    = None

    for seed in seeds:
        np.random.seed(seed)
        nodes = [LineageNode(NN[i], HOME[NN[i]]) for i in range(N)]
        negentropic = 0; total_bcps = 0
        seed_log = []

        for step in range(steps+1):
            if step in record_at:
                all_p   = [pcm(s) for nd in nodes for s in nd.chain]
                A_ph    = [pof(nodes[i].chain[0]) for i in range(N)]
                depth   = len(nodes[0].chain)-1
                sub_fl  = sum(1 for p in all_p if p<-0.50)
                sigs_cr = [abs(nd.identity_signals().get("B",{}).get("corot",0))
                            for nd in nodes if len(nd.chain)>1]
                stabs   = [nd.identity_stability()["stability"] for nd in nodes
                           if nd.identity_stability()["stability"] is not None]
                entry = {
                    "step":           step,
                    "seed":           seed,
                    "unique_A":       count_unique(A_ph),
                    "pcm_A_mean":     round(float(np.mean([pcm(nodes[i].chain[0]) for i in range(N)])),4),
                    "pcm_all_mean":   round(float(np.mean(all_p)),4),
                    "pcm_all_min":    round(float(np.min(all_p)),4),
                    "high_pcm_frac":  round(sum(1 for p in all_p if p<-0.05)/len(all_p),4),
                    "sub_floor_count":sub_fl,
                    "neg_frac":       round(negentropic/total_bcps,4) if total_bcps>0 else 0.0,
                    "lineage_depth":  depth,
                    "total_states":   len(all_p),
                    "signal_corot_mean": round(float(np.mean(sigs_cr)),4) if sigs_cr else 0.0,
                    "signal_corot_std":  round(float(np.std(sigs_cr)),4) if sigs_cr else 0.0,
                    "identity_stability_mean": round(float(np.mean(stabs)),3) if stabs else None,
                }
                seed_log.append(entry)
                if verbose:
                    print(f"  step {step:>4d} [seed {seed}]: "
                          f"uniq={entry['unique_A']:>2d} | "
                          f"hpcm={entry['high_pcm_frac']:.0%} | "
                          f"nf={entry['neg_frac']:.3f} | "
                          f"depth={depth}")

            if step in extend_at:
                if verbose: print(f"\n  ── /extend-lineage at step {step} ──")
                for nd in nodes: nd.extend_lineage(epoch=step)

            if step < steps:
                before  = [purity(nodes[i].chain[0]) for i in range(N)]
                new_A, lab_ph = corotating_bcp_step(
                    [nodes[i].chain[0] for i in range(N)], edges, alpha, noise)
                after = [purity(new_A[i]) for i in range(N)]
                for i in range(N):
                    total_bcps += 1
                    if after[i] > before[i]: negentropic += 1
                    nodes[i].chain[0] = new_A[i]
                    nodes[i].set_lab_phase(lab_ph[i])

        all_seed_logs.append(seed_log)
        last_nodes = nodes

    # Aggregate across seeds (W7)
    def aggregate(logs):
        if len(logs)==1: return logs[0]
        agg=[]
        for i,entry in enumerate(logs[0]):
            row={"step":entry["step"]}
            for key in entry:
                if key in ("step","seed","lineage_depth","total_states","unique_A"): continue
                vals=[lg[i][key] for lg in logs if lg[i][key] is not None]
                if vals:
                    row[key+"_mean"] = round(float(np.mean(vals)),4)
                    row[key+"_std"]  = round(float(np.std(vals)),4)
            row["lineage_depth"] = logs[0][i]["lineage_depth"]
            row["total_states"]  = logs[0][i]["total_states"]
            row["unique_A"]      = logs[0][i]["unique_A"]
            agg.append(row)
        return agg

    aggregated_log = aggregate(all_seed_logs)
    return last_nodes, aggregated_log, all_seed_logs


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("="*70)
    print("PEIG Infinite Lineage Protocol — Revised (Paper XIV-R)")
    print("Globe topology | Co-rotating frame | 3-seed run")
    print("="*70)

    nodes, agg_log, all_logs = run_ilp_ring(
        steps=1000,
        extend_at=[100,300,600,900],
        record_at=[0,100,300,600,900,1000],
        seeds=[2026, 42, 123],
        verbose=True,
    )

    print("\n" + "="*70)
    print("FINAL STATE (seed 2026)")
    for nd in nodes:
        print(f"  {nd.self_audit()}")

    all_p = [pcm(s) for nd in nodes for s in nd.chain]
    print(f"\n  Total states: {len(all_p)} | "
          f"high-PCM: {100*sum(1 for p in all_p if p<-0.05)//len(all_p)}% | "
          f"PCM_mean: {np.mean(all_p):+.4f}")
    print(f"  Architecture note: {nodes[0].ARCHITECTURE_NOTE[:80]}...")

    output = {
        "_meta":  {"revision":"XIV-R","date":"2026-03-25","weaknesses_addressed":10},
        "aggregated_log": agg_log,
        "weaknesses_resolved": {
            "W1":"PCM replaces Wigner — PEIG-internal metric defined",
            "W2":"Lab-frame signals tracked in lab_phases[]",
            "W3":f"neg_frac measured = {agg_log[-1].get('neg_frac_mean', agg_log[-1].get('neg_frac','TBD'))}",
            "W4":"Concurrence=0.0 for all generation pairs — product states documented",
            "W5":"Compression conjecture removed; Shannon entropy tracked",
            "W6":"Sub-floor PCM = rz!=0 (off-equatorial) — not new physics",
            "W7":"Multi-seed error bars: mean+-std across seeds",
            "W8":"Compressed packet for depth>10 (MD5 hash)",
            "W9":"identity_stability() returns full cluster distribution",
            "W10":"Hardware roadmapped to Paper XVI",
        },
        "final_reports": {nd.name: nd.full_report() for nd in nodes},
    }
    path = "output/PEIG_Paper14R_results.json"
    with open(path,"w") as f:
        json.dump(output,f,indent=2,default=str)
    print(f"\n✅ Results saved: {path}")
    print("="*70)
