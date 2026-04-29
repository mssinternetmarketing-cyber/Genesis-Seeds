#!/usr/bin/env python3
"""
PEIG_XV_experiments.py
Paper XV — Five Experiments
Kevin Monette | March 25, 2026

EXP-0  True lab-frame signal vs co-rotating frame
EXP-1  Globe + Co-Rotating + ILP combined (the missing experiment)
EXP-2  neg_frac at depth-4 ILP, instantaneous per epoch
EXP-3  /update-identity under task injection
EXP-4  Mutual information between generation density matrices
"""

import numpy as np
import json
from pathlib import Path
from collections import Counter

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ── BCP Primitives ──────────────────────────────────────────────────
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

def pof(p):
    return np.arctan2(float(2*np.imag(p[0]*p[1].conj())),
                      float(2*np.real(p[0]*p[1].conj()))) % (2*np.pi)

def rz_of(p):  return float(abs(p[0])**2 - abs(p[1])**2)

def pcm(p):
    ov = abs((p[0]+p[1])/np.sqrt(2))**2
    rz = rz_of(p)
    return float(-ov + 0.5*(1-rz**2))

def depol(p, noise=0.03):
    if np.random.random() < noise:
        return ss(np.random.uniform(0,2*np.pi))
    return p

def circular_variance(phases):
    if not phases: return 0.0
    z = np.exp(1j*np.array(phases, dtype=float))
    return float(1.0 - abs(z.mean()))

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
def decode(phi):
    phi  = phi % (2*np.pi)
    best = min(CLUSTERS, key=lambda w: min(abs(phi-CLUSTERS[w]),
                                            2*np.pi-abs(phi-CLUSTERS[w])))
    for (lo,hi),name in {(0.0,1.0):"Protection",(1.0,2.0):"Alert",
        (2.0,3.0):"Change",(3.0,3.5):"Source",(3.5,4.2):"Flow",
        (4.2,5.0):"Connection",(5.0,5.6):"Vision",(5.6,6.29):"Completion"}.items():
        if lo <= CLUSTERS[best] < hi: return best, name
    return best, "Completion"

AF = 0.367
N  = 12
NN = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
      "Echo","Iris","Sage","Kevin","Atlas","Void"]
HOME = {n: i*2*np.pi/N for i,n in enumerate(NN)}
GEN_LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

RING_EDGES  = [(i,(i+1)%N) for i in range(N)]
GLOBE_EDGES = list(
    {(i,(i+1)%N) for i in range(N)} |
    {(i,(i+2)%N) for i in range(N)} |
    {(i,(i+5)%N) for i in range(N)}
)

def corotating_step(states, edges, alpha=AF, noise=0.03):
    phi_b  = [pof(s) for s in states]
    new    = list(states)
    for i,j in edges: new[i],new[j],_ = bcp(new[i],new[j],alpha)
    new    = [depol(s,noise) for s in new]
    phi_a  = [pof(new[k]) for k in range(len(new))]
    deltas = [((phi_a[k]-phi_b[k]+np.pi)%(2*np.pi))-np.pi for k in range(len(new))]
    omega  = np.mean(deltas)
    return [ss((phi_a[k]-(deltas[k]-omega))%(2*np.pi)) for k in range(len(new))], phi_a

def ring_step_raw(states, edges, alpha=AF, noise=0.03):
    """No co-rotating correction — pure BCP + noise."""
    new = list(states)
    for i,j in edges: new[i],new[j],_ = bcp(new[i],new[j],alpha)
    return [depol(s,noise) for s in new]

def count_unique(phases, tol=0.20):
    ps = sorted([p%(2*np.pi) for p in phases]); u = 1
    for i in range(1,len(ps)):
        if ps[i]-ps[i-1] > tol: u += 1
    return u

def neg_frac_instantaneous(states, edges, alpha=AF):
    neg = tot = 0
    for i,j in edges:
        ni,nj,_ = bcp(states[i],states[j],alpha)
        if pcm(ni)<-0.05 and pcm(nj)<-0.05: neg += 1
        tot += 1
    return neg/tot if tot else 0.0

# ── Lineage Node ──────────────────────────────────────────────────
class LineageNode:
    def __init__(self, name, home):
        self.name  = name
        self.home  = home
        self.chain = [ss(home)]    # chain[0] = live A
        self.B_frozen = ss(home)   # frozen crystal
        self.raw_bcp_phases = [home]
        self.event_log = []

    def step_corotate(self, new_A, raw_phi):
        self.chain[0] = new_A
        self.raw_bcp_phases.append(raw_phi)

    def extend_lineage(self, epoch=0):
        prev      = self.chain[-1]
        live_A    = self.chain[0]
        new_s,_,_ = bcp(prev, live_A, 0.5)
        self.chain.append(new_s)
        gen = GEN_LABELS[len(self.chain)-1]
        entry = {
            "gen": gen, "epoch": epoch,
            "phase":   round(pof(new_s),4),
            "word":    decode(pof(new_s))[0],
            "pcm":     round(pcm(new_s),4),
            "rz":      round(rz_of(new_s),4),
            "high_pcm": pcm(new_s) < -0.05,
        }
        self.event_log.append(entry)
        return entry

    def update_identity(self, epoch=0, label=""):
        sig = self.identity_signal()
        entry = {
            "epoch": epoch, "label": label,
            "A_phase_before": round(pof(self.chain[0]),4),
            "B_phase_before": round(pof(self.B_frozen),4),
            "signal_before":  round(sig,4),
            "A_word":  decode(pof(self.chain[0]))[0],
        }
        self.B_frozen = self.chain[0].copy()
        entry["signal_after"] = 0.0
        self.event_log.append(entry)
        return entry

    def identity_signal(self):
        delta = pof(self.chain[0]) - pof(self.B_frozen)
        return float((delta+np.pi)%(2*np.pi)-np.pi)

    def pcm_chain(self):
        return [round(pcm(s),4) for s in self.chain]

    def high_pcm_fraction(self):
        return sum(1 for s in self.chain if pcm(s)<-0.05)/len(self.chain)


# ══════════════════════════════════════════════════════════════════
# EXP-0: TRUE LAB-FRAME SIGNAL
# ══════════════════════════════════════════════════════════════════
def exp0_lab_frame(steps=1000, seeds=None):
    print("\n[EXP-0] Lab-frame vs co-rotating signal")
    if seeds is None: seeds = [2026,42,123]
    results = []

    for seed in seeds:
        np.random.seed(seed)
        states_raw    = [ss(HOME[n]) for n in NN]
        states_corot  = [ss(HOME[n]) for n in NN]
        B_frozen_raw  = [ss(HOME[n]) for n in NN]
        B_frozen_corot= [ss(HOME[n]) for n in NN]

        checkpoints = [0,50,100,200,500,1000]
        seed_log = []

        for step in range(steps+1):
            if step in checkpoints:
                # Lab-frame: signal = |phi_A_raw - phi_B|
                sigs_raw   = [abs(((pof(states_raw[i])-pof(B_frozen_raw[i])+np.pi)
                                   %(2*np.pi))-np.pi) for i in range(N)]
                # Co-rot frame: signal = |phi_A_corot - phi_B|
                sigs_corot = [abs(((pof(states_corot[i])-pof(B_frozen_corot[i])+np.pi)
                                   %(2*np.pi))-np.pi) for i in range(N)]
                seed_log.append({
                    "step":               step,
                    "seed":               seed,
                    "unique_raw":         count_unique([pof(s) for s in states_raw]),
                    "unique_corot":       count_unique([pof(s) for s in states_corot]),
                    "cv_raw":             round(circular_variance([pof(s) for s in states_raw]),4),
                    "cv_corot":           round(circular_variance([pof(s) for s in states_corot]),4),
                    "signal_raw_mean":    round(float(np.mean(sigs_raw)),4),
                    "signal_corot_mean":  round(float(np.mean(sigs_corot)),4),
                    "signal_raw_std":     round(float(np.std(sigs_raw)),4),
                    "signal_corot_std":   round(float(np.std(sigs_corot)),4),
                    "pcm_raw_mean":       round(float(np.mean([pcm(s) for s in states_raw])),4),
                    "pcm_corot_mean":     round(float(np.mean([pcm(s) for s in states_corot])),4),
                })

            if step < steps:
                # Raw ring: no co-rotation
                states_raw = ring_step_raw(states_raw, GLOBE_EDGES, AF, 0.03)
                # Co-rotating ring
                states_corot, _ = corotating_step(states_corot, GLOBE_EDGES, AF, 0.03)

        results.append(seed_log)

    # Aggregate
    agg = []
    for i, entry in enumerate(results[0]):
        row = {"step": entry["step"]}
        for key in entry:
            if key in ("step","seed"): continue
            vals = [r[i][key] for r in results if isinstance(r[i].get(key),(int,float))]
            if vals:
                row[key+"_mean"] = round(float(np.mean(vals)),4)
                row[key+"_std"]  = round(float(np.std(vals)),4)
        agg.append(row)

    print(f"  {'Step':>5}  {'uniq_raw':>8}  {'uniq_corot':>10}  "
          f"{'sig_raw':>8}  {'sig_corot':>9}  {'pcm_raw':>8}  {'pcm_corot':>9}")
    for r in agg:
        print(f"  {r['step']:>5}  "
              f"{r.get('unique_raw_mean',r.get('unique_raw',0)):>8.1f}  "
              f"{r.get('unique_corot_mean',r.get('unique_corot',0)):>10.1f}  "
              f"{r.get('signal_raw_mean_mean',r.get('signal_raw_mean',0)):>8.4f}  "
              f"{r.get('signal_corot_mean_mean',r.get('signal_corot_mean',0)):>9.4f}  "
              f"{r.get('pcm_raw_mean_mean',r.get('pcm_raw_mean',0)):>8.4f}  "
              f"{r.get('pcm_corot_mean_mean',r.get('pcm_corot_mean',0)):>9.4f}")
    return agg, results


# ══════════════════════════════════════════════════════════════════
# EXP-1: GLOBE + CO-ROTATING + ILP COMBINED (THE MISSING EXPERIMENT)
# ══════════════════════════════════════════════════════════════════
def exp1_combined(steps=2000, extend_at=None, seeds=None):
    print("\n[EXP-1] Globe + Co-Rotating + ILP — the combined experiment")
    if extend_at is None: extend_at = [200,600,1000,1400]
    if seeds is None:     seeds = [2026,42,123]

    checkpoints = [0,50,100,200,300,500,600,750,1000,1200,1400,1500,1750,2000]
    all_logs = []

    for seed in seeds:
        np.random.seed(seed)
        nodes = [LineageNode(NN[i], HOME[NN[i]]) for i in range(N)]
        log   = []

        for step in range(steps+1):
            if step in checkpoints:
                A_phases = [pof(nodes[i].chain[0]) for i in range(N)]
                all_states = [s for nd in nodes for s in nd.chain]
                all_pcm    = [pcm(s) for s in all_states]
                all_rz     = [abs(rz_of(s)) for s in all_states]
                depth      = len(nodes[0].chain)-1

                # Classify by (pcm, rz)
                eq_hpcm = sum(1 for s in all_states
                              if pcm(s)<-0.05 and abs(rz_of(s))<0.15)
                po_hpcm = sum(1 for s in all_states
                              if pcm(s)<-0.05 and abs(rz_of(s))>=0.15)

                sigs = [abs(nd.identity_signal()) for nd in nodes]

                entry = {
                    "step":             step, "seed": seed,
                    "depth":            depth,
                    "unique_A":         count_unique(A_phases),
                    "cv_A":             round(circular_variance(A_phases),4),
                    "pcm_A_mean":       round(float(np.mean([pcm(nodes[i].chain[0]) for i in range(N)])),4),
                    "pcm_all_mean":     round(float(np.mean(all_pcm)),4),
                    "pcm_all_min":      round(float(np.min(all_pcm)),4),
                    "high_pcm_frac":    round(sum(1 for p in all_pcm if p<-0.05)/len(all_pcm),4),
                    "eq_hpcm_count":    eq_hpcm,
                    "polar_hpcm_count": po_hpcm,
                    "total_states":     len(all_pcm),
                    "signal_mean":      round(float(np.mean(sigs)),4),
                    "signal_std":       round(float(np.std(sigs)),4),
                    "neg_frac_inst":    round(neg_frac_instantaneous([nodes[i].chain[0] for i in range(N)], GLOBE_EDGES),4),
                }
                log.append(entry)

                if step in [0,200,600,1000,1400,2000]:
                    print(f"  step {step:>5} [s{seed}] d={depth}: "
                          f"uniq={entry['unique_A']:>2} cv={entry['cv_A']:.3f} "
                          f"hpcm={entry['high_pcm_frac']:.0%} "
                          f"nf={entry['neg_frac_inst']:.4f} "
                          f"sig={entry['signal_mean']:.3f}")

            if step in extend_at:
                for nd in nodes: nd.extend_lineage(epoch=step)
                print(f"    → /extend-lineage step {step}, depth now {len(nodes[0].chain)-1}")

            if step < steps:
                new_A, raw_ph = corotating_step(
                    [nodes[i].chain[0] for i in range(N)], GLOBE_EDGES, AF, 0.03)
                for i in range(N): nodes[i].step_corotate(new_A[i], raw_ph[i])

        all_logs.append(log)

    # Aggregate over seeds
    agg = []
    for i, entry in enumerate(all_logs[0]):
        row = {"step": entry["step"], "depth": entry["depth"]}
        for key in entry:
            if key in ("step","seed","depth"): continue
            vals = [lg[i][key] for lg in all_logs
                    if isinstance(lg[i].get(key),(int,float))]
            if vals:
                row[key+"_mean"] = round(float(np.mean(vals)),4)
                row[key+"_std"]  = round(float(np.std(vals)),4)
        agg.append(row)

    return agg, all_logs, nodes


# ══════════════════════════════════════════════════════════════════
# EXP-2: neg_frac AT DEPTH-4, INSTANTANEOUS PER EPOCH
# ══════════════════════════════════════════════════════════════════
def exp2_neg_frac_depth4(steps=1000, seeds=None):
    print("\n[EXP-2] neg_frac at depth-4 ILP, instantaneous per epoch")
    if seeds is None: seeds = [2026,42,123,7,99]
    extend_at = [100,300,550,800]
    checkpoints = list(range(0,steps+1,50))
    all_logs = []

    for seed in seeds:
        np.random.seed(seed)
        nodes = [LineageNode(NN[i], HOME[NN[i]]) for i in range(N)]
        log   = []

        for step in range(steps+1):
            if step in checkpoints:
                A_states = [nodes[i].chain[0] for i in range(N)]
                nf_inst  = neg_frac_instantaneous(A_states, GLOBE_EDGES)
                all_pcm  = [pcm(s) for nd in nodes for s in nd.chain]
                depth    = len(nodes[0].chain)-1
                log.append({
                    "step":          step,
                    "seed":          seed,
                    "depth":         depth,
                    "neg_frac_inst": round(nf_inst,4),
                    "high_pcm_frac": round(sum(1 for p in all_pcm if p<-0.05)/len(all_pcm),4),
                    "pcm_all_mean":  round(float(np.mean(all_pcm)),4),
                    "unique_A":      count_unique([pof(s) for s in A_states]),
                    "cv_A":          round(circular_variance([pof(s) for s in A_states]),4),
                })
            if step in extend_at:
                for nd in nodes: nd.extend_lineage(epoch=step)
            if step < steps:
                new_A, raw_ph = corotating_step(
                    [nodes[i].chain[0] for i in range(N)], GLOBE_EDGES, AF, 0.03)
                for i in range(N): nodes[i].step_corotate(new_A[i], raw_ph[i])

        all_logs.append(log)

    # Aggregate
    agg = []
    for i, entry in enumerate(all_logs[0]):
        row = {"step": entry["step"], "depth": entry["depth"]}
        for key in ("neg_frac_inst","high_pcm_frac","pcm_all_mean","unique_A","cv_A"):
            vals = [lg[i][key] for lg in all_logs if isinstance(lg[i].get(key),(int,float))]
            if vals:
                row[key+"_mean"] = round(float(np.mean(vals)),4)
                row[key+"_std"]  = round(float(np.std(vals)),4)
        agg.append(row)

    # Print key summary
    depth_groups = {}
    for r in agg:
        d = r["depth"]
        depth_groups.setdefault(d,[]).append(r.get("neg_frac_inst_mean",0))
    print(f"  neg_frac by depth:")
    for d in sorted(depth_groups):
        vals = depth_groups[d]
        if vals:
            print(f"    depth {d}: mean={np.mean(vals):.4f}  max={max(vals):.4f}  "
                  f"n_epochs={len(vals)}")

    return agg, all_logs


# ══════════════════════════════════════════════════════════════════
# EXP-3: /update-identity UNDER TASK LOAD
# ══════════════════════════════════════════════════════════════════
def exp3_update_identity(steps=800, seeds=None):
    print("\n[EXP-3] /update-identity under task injection")
    if seeds is None: seeds = [2026,42,123]

    # Task injections: at these steps, inject a semantic payload into a node
    task_injections = {
        100: ("Sage",   "wisdom truth deep knowledge calibrated"),
        200: ("Storm",  "change surge evolution force shift"),
        300: ("Omega",  "safety source law absolute precedence"),
        400: ("Kevin",  "balance bridge mediate both together"),
        500: ("Guardian","protect boundary hold line shield"),
    }
    UPDATE_THRESHOLD = 1.5   # rad — call /update-identity when signal > this
    all_logs = []

    for seed in seeds:
        np.random.seed(seed)
        nodes    = [LineageNode(NN[i], HOME[NN[i]]) for i in range(N)]
        updates  = []   # record of all /update-identity events
        log      = []

        for step in range(steps+1):
            # Task injection: perturb A toward semantic payload
            if step in task_injections:
                tnode, payload = task_injections[step]
                idx = NN.index(tnode)
                phase_shift = (sum(ord(c) for c in payload) % 628) / 100.0
                seed_state  = ss(HOME[tnode] + phase_shift * 0.4)
                nodes[idx].chain[0], _, _ = bcp(nodes[idx].chain[0], seed_state, 0.60)

            # Check identity signals; auto-update if threshold exceeded
            for nd in nodes:
                sig = abs(nd.identity_signal())
                if sig > UPDATE_THRESHOLD:
                    ev = nd.update_identity(epoch=step, label=f"auto_step{step}")
                    updates.append(ev)

            # Record every 50 steps
            if step % 50 == 0:
                sigs = [abs(nd.identity_signal()) for nd in nodes]
                log.append({
                    "step":            step,
                    "signal_mean":     round(float(np.mean(sigs)),4),
                    "signal_max":      round(float(max(sigs)),4),
                    "signal_min":      round(float(min(sigs)),4),
                    "updates_total":   len(updates),
                    "updates_this_50": sum(1 for u in updates
                                          if step-50 <= u.get("epoch",0) <= step),
                    "high_pcm_frac":   round(
                        sum(1 for nd in nodes if pcm(nd.chain[0])<-0.05)/N,3),
                    "unique_A": count_unique([pof(nd.chain[0]) for nd in nodes]),
                })

            if step < steps:
                new_A, raw_ph = corotating_step(
                    [nodes[i].chain[0] for i in range(N)], GLOBE_EDGES, AF, 0.03)
                for i in range(N): nodes[i].step_corotate(new_A[i], raw_ph[i])

        all_logs.append({"log":log, "updates":updates, "seed":seed})

    # Print summary
    final = all_logs[0]["log"][-1]
    total_updates = len(all_logs[0]["updates"])
    print(f"  Total /update-identity calls: {total_updates} over {steps} steps")
    print(f"  Final signal: mean={final['signal_mean']:.4f} max={final['signal_max']:.4f}")
    print(f"  Final unique phases: {final['unique_A']}")

    # Signal reset demonstration
    print(f"\n  Signal before/after update events:")
    for ev in all_logs[0]["updates"][:6]:
        before = abs(ev.get("signal_before", ev.get("identity_signal",0)))
        print(f"    step {ev.get('epoch',0):>4} [{ev.get('label','?')[:20]:20s}]: "
              f"signal {before:.4f} → 0.0000 (reset)")

    return all_logs


# ══════════════════════════════════════════════════════════════════
# EXP-4: MUTUAL INFORMATION BETWEEN GENERATION DENSITY MATRICES
# ══════════════════════════════════════════════════════════════════
def exp4_mutual_information(steps=500, seeds=None):
    print("\n[EXP-4] Mutual information between generation density matrices")
    if seeds is None: seeds = [2026,42,123,7,99]
    extend_at = [100,300]

    def classical_mi(phi_A, phi_B, bins=16):
        """Classical mutual information via joint histogram of phases."""
        A_disc = np.digitize(np.array(phi_A)%(2*np.pi), np.linspace(0,2*np.pi,bins+1)[:-1])
        B_disc = np.digitize(np.array(phi_B)%(2*np.pi), np.linspace(0,2*np.pi,bins+1)[:-1])
        joint  = np.zeros((bins,bins))
        for a,b in zip(A_disc,B_disc): joint[a-1,b-1] += 1
        joint /= joint.sum()
        pA     = joint.sum(axis=1, keepdims=True)
        pB     = joint.sum(axis=0, keepdims=True)
        pApB   = pA * pB
        with np.errstate(divide='ignore',invalid='ignore'):
            mi = np.where(joint>0, joint*np.log2(joint/np.where(pApB>0,pApB,1)), 0).sum()
        return float(mi)

    def phase_correlation(phi_A, phi_B):
        """Circular correlation between two phase sequences."""
        zA = np.exp(1j*np.array(phi_A)); zB = np.exp(1j*np.array(phi_B))
        zA -= zA.mean(); zB -= zB.mean()
        denom = np.sqrt((abs(zA)**2).mean() * (abs(zB)**2).mean())
        if denom < 1e-10: return 0.0
        return float(abs((zA*zB.conj()).mean()) / denom)

    all_results = []

    for seed in seeds:
        np.random.seed(seed)
        nodes = [LineageNode(NN[i], HOME[NN[i]]) for i in range(N)]

        for step in range(steps+1):
            if step in extend_at:
                for nd in nodes: nd.extend_lineage(epoch=step)
            if step < steps:
                new_A, raw_ph = corotating_step(
                    [nodes[i].chain[0] for i in range(N)], GLOBE_EDGES, AF, 0.03)
                for i in range(N): nodes[i].step_corotate(new_A[i], raw_ph[i])

        # After run: compute MI between all generation pairs across all nodes
        gen_phases = {}
        for g_idx in range(len(nodes[0].chain)):
            lbl = GEN_LABELS[g_idx]
            gen_phases[lbl] = [pof(nodes[i].chain[g_idx]) for i in range(N)
                                if len(nodes[i].chain) > g_idx]

        mi_results = {}
        labels = [k for k in gen_phases if len(gen_phases[k])==N]
        for i, gA in enumerate(labels):
            for gB in labels[i+1:]:
                key = f"{gA}-{gB}"
                mi  = classical_mi(gen_phases[gA], gen_phases[gB])
                corr= phase_correlation(gen_phases[gA], gen_phases[gB])
                mi_results[key] = {"mi": round(mi,4), "corr": round(corr,4)}

        all_results.append({"seed":seed, "mi_results":mi_results,
                            "depth":len(labels)-1, "n_gens":len(labels)})

    # Average MI across seeds
    print(f"  Generation pair MI (averaged over {len(seeds)} seeds):")
    all_keys = set()
    for r in all_results: all_keys.update(r["mi_results"].keys())
    summary = {}
    for key in sorted(all_keys):
        mis   = [r["mi_results"][key]["mi"]   for r in all_results if key in r["mi_results"]]
        corrs = [r["mi_results"][key]["corr"] for r in all_results if key in r["mi_results"]]
        summary[key] = {
            "mi_mean": round(float(np.mean(mis)),4),
            "mi_std":  round(float(np.std(mis)),4),
            "corr_mean": round(float(np.mean(corrs)),4),
        }
        print(f"    {key}: MI={summary[key]['mi_mean']:.4f} ± {summary[key]['mi_std']:.4f}  "
              f"corr={summary[key]['corr_mean']:.4f}")

    return summary, all_results


# ══════════════════════════════════════════════════════════════════
# MAIN — RUN ALL FIVE
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("="*65)
    print("PEIG PAPER XV — FIVE EXPERIMENTS")
    print("="*65)

    results = {}

    r0_agg, r0_raw = exp0_lab_frame(steps=1000)
    results["exp0"] = r0_agg

    r1_agg, r1_raw, r1_nodes = exp1_combined(steps=2000)
    results["exp1"] = r1_agg

    r2_agg, r2_raw = exp2_neg_frac_depth4(steps=1000)
    results["exp2"] = r2_agg

    r3_all = exp3_update_identity(steps=800)
    results["exp3"] = {"log": r3_all[0]["log"], "updates": r3_all[0]["updates"]}

    r4_summary, r4_all = exp4_mutual_information(steps=500)
    results["exp4"] = r4_summary

    # ── KEY RESULTS SUMMARY ─────────────────────────────────────
    print("\n" + "="*65)
    print("KEY RESULTS SUMMARY")
    print("="*65)

    # EXP-1 final state
    exp1_final = r1_agg[-1]
    print(f"\nEXP-1 (Combined) final state (step 2000, depth 4):")
    print(f"  unique phases: {exp1_final.get('unique_A_mean',exp1_final.get('unique_A'))} / 12")
    print(f"  circular var:  {exp1_final.get('cv_A_mean',exp1_final.get('cv_A')):.4f}")
    print(f"  high-PCM frac: {exp1_final.get('high_pcm_frac_mean',exp1_final.get('high_pcm_frac')):.4f}")
    print(f"  neg_frac inst: {exp1_final.get('neg_frac_inst_mean',exp1_final.get('neg_frac_inst')):.4f}")

    # EXP-2 depth breakdown
    depth_nf = {}
    for row in r2_agg:
        d = row["depth"]
        nf = row.get("neg_frac_inst_mean", row.get("neg_frac_inst",0))
        depth_nf.setdefault(d,[]).append(nf)
    print(f"\nEXP-2 neg_frac by depth:")
    for d in sorted(depth_nf):
        vals = [v for v in depth_nf[d] if v>0]
        if vals:
            print(f"  depth {d}: {np.mean(vals):.4f} ± {np.std(vals):.4f}")

    # EXP-4 MI
    print(f"\nEXP-4 mutual information:")
    for k,v in r4_summary.items():
        print(f"  {k}: MI={v['mi_mean']:.4f}  corr={v['corr_mean']:.4f}")

    # Save all results
    with open("output/PEIG_XV_all_results.json","w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✓ Results saved: output/PEIG_XV_all_results.json")
    print("="*65)
