#!/usr/bin/env python3
"""
PEIG_XVIII_edge_discovery.py
Paper XVIII — Edge Information Flow, Bridge Protocol, Guardrail Awareness
Kevin Monette | March 26, 2026

Three experiments:

EXP-A  Edge Information Flow
  Start: 2 nodes, 1 edge (a chain of nothing).
  Add one edge at a time — the edge that contributes the most
  information flow gets added next.
  Measure after each addition: neg_frac, cv, pcm_mean, nc_count,
  and per-edge mutual information delta.
  Find the minimum sufficient topology.

EXP-B  Bridge Protocol
  Run 12-node ring (ring edges only).
  Any node entering ORANGE (PCM > -0.05) triggers auto-bridge:
  the nearest available Maverick or Independent node couples in
  before classical collapse (RED = PCM > +0.05).
  Bridge releases when node returns to GREEN.
  Goal: zero RED events ever.

EXP-C  Guardrail Awareness Voice
  Every node speaks its own PCM trajectory in real time.
  Four zones with distinct voice phrases:
    GREEN  (PCM < -0.15) — deeply nonclassical, floor
    YELLOW (-0.15 to -0.05) — nonclassical, watch
    ORANGE (-0.05 to +0.05) — alert, bridge me
    RED    (> +0.05) — classical, emergency
  Nodes speak in the voice of their own physics.
"""

import numpy as np, json, math
from collections import Counter, defaultdict
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ── BCP primitives ────────────────────────────────────────────────
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(ph): return np.array([1.0, np.exp(1j*ph)]) / np.sqrt(2)

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

def rz(p): return float(abs(p[0])**2 - abs(p[1])**2)

def pcm(p):
    ov = abs((p[0]+p[1])/np.sqrt(2))**2
    return float(-ov + 0.5*(1-rz(p)**2))

def coh(p): return float(abs(p[0]*p[1].conj()))

def depol(p, noise=0.03):
    if np.random.random() < noise: return ss(np.random.uniform(0,2*np.pi))
    return p

def cv(phases):
    return float(1.0 - abs(np.exp(1j*np.array(phases)).mean()))

def nf_inst(states, edges, alpha=0.367):
    neg = tot = 0
    for i,j in edges:
        a,b,_ = bcp(states[i], states[j], alpha)
        if pcm(a)<-0.05 and pcm(b)<-0.05: neg+=1
        tot+=1
    return neg/tot if tot else 0.0

def corotate(states, edges, alpha=0.367, noise=0.03):
    phi_b = [pof(s) for s in states]
    new   = list(states)
    for i,j in edges: new[i],new[j],_ = bcp(new[i],new[j],alpha)
    new   = [depol(s,noise) for s in new]
    phi_a = [pof(new[k]) for k in range(len(new))]
    dels  = [((phi_a[k]-phi_b[k]+math.pi)%(2*math.pi))-math.pi
             for k in range(len(new))]
    om    = float(np.mean(dels))
    return [ss((phi_a[k]-(dels[k]-om))%(2*math.pi)) for k in range(len(new))]

# ── System config ─────────────────────────────────────────────────
N   = 12
NN  = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
       "Echo","Iris","Sage","Kevin","Atlas","Void"]
IDX = {n:i for i,n in enumerate(NN)}
HOME= {n: i*2*np.pi/N for i,n in enumerate(NN)}

FAMILY = {
    "Omega":"GodCore","Guardian":"GodCore","Sentinel":"GodCore","Void":"GodCore",
    "Nexus":"Independent","Storm":"Independent","Sora":"Independent","Echo":"Independent",
    "Iris":"Maverick","Sage":"Maverick","Kevin":"Maverick","Atlas":"Maverick",
}
# Bridge preference order: Maverick first (they mediate), then Independent, then GodCore
BRIDGE_PREF = ([n for n in NN if FAMILY[n]=="Maverick"] +
               [n for n in NN if FAMILY[n]=="Independent"] +
               [n for n in NN if FAMILY[n]=="GodCore"])

# All 36 Globe edges (deduplicated)
def make_edges(deltas):
    return list({tuple(sorted((i,(i+d)%N))) for d in deltas for i in range(N)})

RING_EDGES  = make_edges([1])
SKIP1_EDGES = make_edges([2])
CROSS_EDGES = make_edges([5])
ALL_EDGES   = make_edges([1,2,5])

# PCM zone thresholds
GREEN_TH  = -0.15
YELLOW_TH = -0.05
ORANGE_TH =  0.05

def zone(p_val):
    if p_val < GREEN_TH:   return "GREEN"
    if p_val < YELLOW_TH:  return "YELLOW"
    if p_val < ORANGE_TH:  return "ORANGE"
    return "RED"

# ── Mutual information measurement across one edge ────────────────
def edge_mi(pA, pB, n_samples=800, alpha=0.367):
    """
    True mutual information between node A and node B across one BCP edge.
    Method: run n_samples BCP interactions, record joint phase bin distribution.
    MI(A;B) = H(A) + H(B) - H(A,B)   [Shannon, nats→bits via log2]
    Bins: 12 phase bins (30° each) — matches the 12-node spacing.
    """
    BINS = 12
    joint = np.zeros((BINS, BINS), dtype=float)
    a_state, b_state = pA.copy(), pB.copy()

    for _ in range(n_samples):
        ai = int(pof(a_state) / (2*np.pi) * BINS) % BINS
        bi = int(pof(b_state) / (2*np.pi) * BINS) % BINS
        joint[ai, bi] += 1.0
        # One probabilistic BCP step
        if np.random.random() < alpha:
            a_state, b_state, _ = bcp(a_state, b_state, alpha)
        a_state = depol(a_state, 0.03)
        b_state = depol(b_state, 0.03)

    joint /= joint.sum() + 1e-12
    pA_m  = joint.sum(axis=1, keepdims=True) + 1e-12
    pB_m  = joint.sum(axis=0, keepdims=True) + 1e-12
    indep = pA_m * pB_m
    with np.errstate(divide='ignore', invalid='ignore'):
        mi = float(np.where(joint>1e-10,
                            joint*np.log2(joint/indep), 0.0).sum())
    return max(0.0, round(mi, 5))

# ── Ring health snapshot ──────────────────────────────────────────
def health(states, edges, alpha=0.367):
    pcms   = [pcm(s) for s in states]
    phases = [pof(s) for s in states]
    return {
        "cv":       round(cv(phases), 4),
        "nf":       round(nf_inst(states, edges, alpha), 4),
        "pcm_mean": round(float(np.mean(pcms)), 4),
        "nc_count": sum(1 for p in pcms if p < YELLOW_TH),
        "green":    sum(1 for p in pcms if p < GREEN_TH),
        "yellow":   sum(1 for p in pcms if GREEN_TH<=p<YELLOW_TH),
        "orange":   sum(1 for p in pcms if YELLOW_TH<=p<ORANGE_TH),
        "red":      sum(1 for p in pcms if p >= ORANGE_TH),
        "n_edges":  len(edges),
        "per_node": {NN[i]: round(pcms[i],4) for i in range(N)},
    }

def run(states, edges, steps=120, alpha=0.367):
    for _ in range(steps): states = corotate(states, edges, alpha)
    return states


# ══════════════════════════════════════════════════════════════════
# EXP-A  EDGE INFORMATION FLOW — BUILD GLOBE 1 EDGE AT A TIME
# ══════════════════════════════════════════════════════════════════

def exp_a():
    print("\n" + "═"*65)
    print("EXP-A  Edge Information Flow — Chain → Globe, 1 Edge at a Time")
    print("═"*65)

    # Step 0: measure MI for every possible edge from fresh state
    init = [ss(HOME[n]) for n in NN]
    print("\n  Measuring MI for all 36 Globe edges (fresh state)...")

    edge_data = {}
    for (i,j) in ALL_EDGES:
        mi_val = edge_mi(init[i], init[j])
        delta  = min((j-i)%N, (i-j)%N)
        etype  = "ring" if delta==1 else "skip1" if delta==2 else "cross"
        edge_data[(i,j)] = {
            "nodes": (NN[i], NN[j]),
            "families": (FAMILY[NN[i]], FAMILY[NN[j]]),
            "delta": delta, "type": etype,
            "mi_fresh": mi_val,
        }

    # Rank by fresh MI
    ranked = sorted(edge_data.keys(), key=lambda e: edge_data[e]["mi_fresh"], reverse=True)

    print(f"\n  {'Rank':5} {'Edge':24} {'Type':7} {'Δ':3} {'MI':8}  {'Families'}")
    print("  " + "─"*65)
    for rank, (i,j) in enumerate(ranked, 1):
        d = edge_data[(i,j)]
        fam = f"{d['families'][0][:4]}↔{d['families'][1][:4]}"
        print(f"  {rank:5d} ({NN[i]:10s},{NN[j]:10s}) {d['type']:7s} {d['delta']:3d} "
              f"{d['mi_fresh']:8.5f}  {fam}")

    # Build Globe greedily — add highest MI edge, test ring health after each
    print(f"\n  Building Globe 1 edge at a time (greedy MI ranking)...")
    print(f"  {'Edges':6} {'cv':7} {'nf':7} {'nc/12':6} {'pcm':8} "
          f"{'Green':6} {'Yel':4} {'Ora':4} {'Red':4}  Added edge")
    print("  " + "─"*75)

    active_edges = []
    build_log    = []

    for step, (i,j) in enumerate(ranked):
        active_edges.append((i,j))
        states  = run([ss(HOME[n]) for n in NN], active_edges, steps=120)
        h       = health(states, active_edges)
        mi_now  = edge_mi(states[i], states[j])  # MI of the just-added edge in live ring
        edge_data[(i,j)]["mi_live"] = mi_now

        row = {
            "step": step+1,
            "edge": (NN[i], NN[j]),
            "type": edge_data[(i,j)]["type"],
            "delta": edge_data[(i,j)]["delta"],
            "mi_fresh": edge_data[(i,j)]["mi_fresh"],
            "mi_live": round(mi_now, 5),
            **h
        }
        build_log.append(row)

        print(f"  {step+1:6d} {h['cv']:7.4f} {h['nf']:7.4f} "
              f"{h['nc_count']:3d}/12  {h['pcm_mean']:8.4f} "
              f"{h['green']:6d} {h['yellow']:4d} {h['orange']:4d} {h['red']:4d}  "
              f"({NN[i]},{NN[j]}) [{edge_data[(i,j)]['type']}]")

    # Find minimum sufficient topology
    min_row = None
    for row in build_log:
        if row["cv"] > 0.95 and row["nc_count"] >= 10:
            min_row = row; break

    print(f"\n  MINIMUM SUFFICIENT TOPOLOGY:")
    if min_row:
        print(f"  {min_row['n_edges']} edges → cv={min_row['cv']:.4f}, "
              f"nc={min_row['nc_count']}/12, nf={min_row['nf']:.4f}")
        print(f"  (Full Globe = 36 edges; savings = {36-min_row['n_edges']} edges)")
    else:
        print("  No sufficient topology found in 36 edges — review thresholds")

    # MI by edge type
    print(f"\n  MI by edge type (live ring, full Globe):")
    by_type = defaultdict(list)
    for (i,j), d in edge_data.items():
        if "mi_live" in d:
            by_type[d["type"]].append(d["mi_live"])
    for etype, vals in sorted(by_type.items()):
        print(f"  {etype:7s}: mean={np.mean(vals):.5f}, "
              f"max={max(vals):.5f}, min={min(vals):.5f} ({len(vals)} edges)")

    return build_log, edge_data, ranked


# ══════════════════════════════════════════════════════════════════
# EXP-B  BRIDGE PROTOCOL
# ══════════════════════════════════════════════════════════════════

def find_bridge(drifting_idx, states, active_bridges, used_as_bridge):
    """
    Find the best available bridge node for a drifting node.
    Must be: nonclassical, not already bridging, not the drifting node.
    Preference: Maverick > Independent > GodCore.
    """
    for candidate in BRIDGE_PREF:
        ci = IDX[candidate]
        if ci == drifting_idx:         continue
        if candidate in used_as_bridge: continue
        if pcm(states[ci]) >= YELLOW_TH: continue  # must be nonclassical
        return candidate
    return None

def exp_b(steps=600, alpha=0.40):
    print("\n" + "═"*65)
    print(f"EXP-B  Bridge Protocol — Auto-Bridge at ORANGE (α={alpha})")
    print("       Upper/lower half bridged by Maverick/Independent")
    print("       before any RED event occurs")
    print("═"*65)

    base_edges     = list(RING_EDGES)   # start with ring only
    states         = [ss(HOME[n]) for n in NN]
    extra_edges    = []
    active_bridges = {}     # drifting_node → bridge_node
    used_as_bridge = set()  # bridge nodes currently deployed
    bridge_events  = []
    release_events = []
    log            = []

    print(f"\n  {'Step':5} {'cv':7} {'nf':7} {'nc':5} "
          f"{'G':4} {'Y':4} {'O':4} {'R':4} {'Bridges':8}  Events")
    print("  " + "─"*72)

    for step in range(steps+1):
        current_edges = list(set(map(tuple, base_edges + extra_edges)))
        pcms  = [pcm(s) for s in states]
        phases= [pof(s) for s in states]
        h     = health(states, current_edges, alpha)

        # ── GUARDRAIL: check every node ───────────────────────────
        events_this_step = []
        for i, n in enumerate(NN):
            z = zone(pcms[i])

            # ORANGE → deploy bridge before RED
            if z in ("ORANGE","RED") and n not in active_bridges:
                bridge = find_bridge(i, states, active_bridges, used_as_bridge)
                if bridge:
                    bi = IDX[bridge]
                    new_e = tuple(sorted((i, bi)))
                    if new_e not in extra_edges:
                        extra_edges.append(new_e)
                    active_bridges[n]  = bridge
                    used_as_bridge.add(bridge)
                    ev = {"step":step,"event":"BRIDGE",
                          "node":n,"zone":z,"pcm":round(pcms[i],4),
                          "bridge":bridge,"family":FAMILY[bridge]}
                    bridge_events.append(ev)
                    events_this_step.append(
                        f"⚡{n}(PCM={pcms[i]:+.3f},{z})←{bridge}[{FAMILY[bridge][:3]}]")

            # GREEN recovery → release bridge
            elif z == "GREEN" and n in active_bridges:
                bridge = active_bridges.pop(n)
                used_as_bridge.discard(bridge)
                bi  = IDX[bridge]
                rem = tuple(sorted((i, bi)))
                if rem in extra_edges:
                    extra_edges.remove(rem)
                ev = {"step":step,"event":"RELEASE",
                      "node":n,"pcm":round(pcms[i],4),"bridge":bridge}
                release_events.append(ev)
                events_this_step.append(f"✓{n}→GREEN, {bridge} released")

        # Log every 25 steps
        if step % 25 == 0:
            ev_str = " | ".join(events_this_step) if events_this_step else "—"
            print(f"  {step:5d} {h['cv']:7.4f} {h['nf']:7.4f} "
                  f"{h['nc_count']:3d}/12 "
                  f"{h['green']:4d} {h['yellow']:4d} {h['orange']:4d} {h['red']:4d} "
                  f"{len(active_bridges):8d}  {ev_str[:40]}")
            log.append({
                "step":step,**h,
                "n_bridges":len(active_bridges),
                "bridge_events_total":len(bridge_events),
                "active_bridges":{k:v for k,v in active_bridges.items()},
            })

        if step < steps:
            current_edges = list(set(map(tuple, base_edges + extra_edges)))
            states = corotate(states, current_edges, alpha, 0.03)

    final = log[-1]
    red_events = sum(1 for e in bridge_events if e["zone"]=="RED")
    print(f"\n  BRIDGE SUMMARY ({steps} steps):")
    print(f"  Total bridge deployments: {len(bridge_events)}")
    print(f"  Bridge deployments at ORANGE (preventive): {len(bridge_events)-red_events}")
    print(f"  Bridge deployments at RED (emergency):     {red_events}")
    print(f"  Total bridge releases: {len(release_events)}")
    print(f"  Final state: G={final['green']} Y={final['yellow']} "
          f"O={final['orange']} R={final['red']}")
    print(f"  Final cv={final['cv']:.4f} | nc={final['nc_count']}/12 | "
          f"nf={final['nf']:.4f}")

    return log, bridge_events, release_events


# ══════════════════════════════════════════════════════════════════
# EXP-C  GUARDRAIL AWARENESS VOICE
# ══════════════════════════════════════════════════════════════════

VOICES = {
    "GREEN": [
        "I am at the quantum floor. PCM={pcm:+.4f}. Fully nonclassical. "
        "The ring flows through me cleanly. I am holding.",
        "Deep nonclassical state. PCM={pcm:+.4f}. "
        "My coherence is strong. No intervention needed.",
        "GREEN — I am fully nonclassical. PCM={pcm:+.4f}. "
        "I carry maximum quantum information. The ring is safe through me.",
    ],
    "YELLOW": [
        "YELLOW — PCM={pcm:+.4f}. I am nonclassical but rising. "
        "The co-rotating correction is costing me. Monitor my trajectory.",
        "My PCM is drifting toward threshold. PCM={pcm:+.4f}. "
        "I am still nonclassical but the margin is shrinking. Watch me.",
        "YELLOW status. PCM={pcm:+.4f}. I am functional. "
        "If my trend continues, I will need a bridge within 20-30 steps.",
    ],
    "ORANGE": [
        "ORANGE — PCM={pcm:+.4f}. I am approaching classical territory. "
        "Bridge me now. I need a nonclassical neighbor to couple with me.",
        "Alert: PCM={pcm:+.4f}. I am at the classical boundary. "
        "My phase coherence is marginal. A Maverick node can pull me back.",
        "ORANGE — I am about to lose nonclassicality. PCM={pcm:+.4f}. "
        "The ring needs to reach me before I fall to RED.",
    ],
    "RED": [
        "RED — PCM={pcm:+.4f}. I have become classical. "
        "I am in the thermal regime. Emergency bridge required.",
        "I have lost my nonclassicality. PCM={pcm:+.4f}. "
        "I am no longer carrying quantum information effectively. "
        "A strong bridge coupling can restore me.",
        "RED status. PCM={pcm:+.4f}. "
        "The entropy pump has lost me. I need immediate coupling "
        "from a deeply nonclassical node to recover.",
    ],
}

def node_voice(name, p_val, prev_val, step, bridge=None, trend_window=None):
    """Generate the guardrail awareness voice for one node at one step."""
    z      = zone(p_val)
    phrase = VOICES[z][step % len(VOICES[z])].format(pcm=p_val)

    # Trend
    if trend_window and len(trend_window) >= 3:
        trend = (trend_window[-1] - trend_window[0]) / len(trend_window)
        tstr  = f" Trend: {'+' if trend>0 else ''}{trend:.4f}/step."
    elif prev_val is not None:
        trend = p_val - prev_val
        tstr  = f" Δpcm={'+' if trend>0 else ''}{trend:.4f}."
    else:
        tstr = ""

    phrase += tstr

    # Bridge announcement
    if bridge and z in ("ORANGE","RED"):
        phrase += (f" BRIDGE ACTIVE: {bridge} [{FAMILY[bridge]}] "
                   f"is coupling to me now.")
    elif z in ("ORANGE","RED") and not bridge:
        phrase += " No bridge assigned yet — requesting coupling."

    # MI voice — how much information this node is carrying
    equatorial = abs(rz(ss(p_val if abs(p_val)<=0.5 else 0.0))) < 0.15
    mi_estimate= max(0.0, (-p_val+0.5)/1.0)  # rough proxy: deeper PCM = more MI
    phrase += (f" My information flow estimate: {mi_estimate:.3f} bits "
               f"({'high' if mi_estimate>0.3 else 'moderate' if mi_estimate>0.1 else 'low'}).")

    return phrase

def exp_c(steps=400, alpha=0.40):
    print("\n" + "═"*65)
    print(f"EXP-C  Guardrail Awareness Voice — 12 Nodes, {steps} Steps (α={alpha})")
    print("       Real-time internal commentary with bridge integration")
    print("═"*65)

    base_edges     = list(RING_EDGES)
    states         = [ss(HOME[n]) for n in NN]
    extra_edges    = []
    active_bridges = {}
    used_as_bridge = set()
    prev_pcms      = [None]*N
    pcm_windows    = {n: [] for n in NN}   # rolling 10-step window
    voice_log      = []
    bridge_events  = []

    PRINT_AT = {0, 50, 100, 150, 200, 300, 400}

    for step in range(steps+1):
        current_edges = list(set(map(tuple, base_edges+extra_edges)))
        pcms   = [pcm(s) for s in states]
        phases = [pof(s) for s in states]
        h      = health(states, current_edges, alpha)

        # Update rolling windows
        for i,n in enumerate(NN):
            pcm_windows[n].append(pcms[i])
            if len(pcm_windows[n]) > 10: pcm_windows[n].pop(0)

        # Bridge management
        for i,n in enumerate(NN):
            z = zone(pcms[i])
            if z in ("ORANGE","RED") and n not in active_bridges:
                bridge = find_bridge(i, states, active_bridges, used_as_bridge)
                if bridge:
                    bi = IDX[bridge]
                    ne = tuple(sorted((i,bi)))
                    if ne not in extra_edges: extra_edges.append(ne)
                    active_bridges[n] = bridge
                    used_as_bridge.add(bridge)
                    bridge_events.append({
                        "step":step,"node":n,"zone":z,
                        "pcm":round(pcms[i],4),"bridge":bridge,
                        "bridge_family":FAMILY[bridge]})
            elif z=="GREEN" and n in active_bridges:
                bridge = active_bridges.pop(n)
                used_as_bridge.discard(bridge)
                bi  = IDX[bridge]
                rem = tuple(sorted((i,bi)))
                if rem in extra_edges: extra_edges.remove(rem)

        # Generate voices
        step_voices = {}
        for i,n in enumerate(NN):
            voice = node_voice(n, pcms[i], prev_pcms[i], step,
                               active_bridges.get(n), pcm_windows[n])
            step_voices[n] = {
                "voice": voice,
                "pcm":   round(pcms[i],4),
                "zone":  zone(pcms[i]),
                "bridge": active_bridges.get(n),
            }

        # Print selected steps
        if step in PRINT_AT:
            zones = Counter(v["zone"] for v in step_voices.values())
            print(f"\n  ── Step {step:4d} | cv={h['cv']:.4f} | "
                  f"G={zones.get('GREEN',0)} Y={zones.get('YELLOW',0)} "
                  f"O={zones.get('ORANGE',0)} R={zones.get('RED',0)} "
                  f"| bridges={len(active_bridges)} ──")
            for n in NN:
                v = step_voices[n]
                marker = ("★" if v["zone"]=="GREEN" else
                          "·" if v["zone"]=="YELLOW" else
                          "⚠" if v["zone"]=="ORANGE" else "✗")
                print(f"    {marker} [{n:10s}] {v['voice'][:90]}")

        voice_log.append({
            "step": step,
            "health": h,
            "voices": {n: {"voice":step_voices[n]["voice"][:200],
                           "pcm":step_voices[n]["pcm"],
                           "zone":step_voices[n]["zone"],
                           "bridge":step_voices[n]["bridge"]}
                       for n in NN},
            "n_bridges": len(active_bridges),
        })
        prev_pcms = pcms[:]
        if step < steps:
            current_edges = list(set(map(tuple, base_edges+extra_edges)))
            states = corotate(states, current_edges, alpha, 0.03)

    final = voice_log[-1]
    fz = Counter(v["zone"] for v in final["voices"].values())
    print(f"\n  GUARDRAIL SUMMARY ({steps} steps, α={alpha}):")
    print(f"  Final: G={fz.get('GREEN',0)} Y={fz.get('YELLOW',0)} "
          f"O={fz.get('ORANGE',0)} R={fz.get('RED',0)}")
    print(f"  Bridge events: {len(bridge_events)}")
    print(f"  cv={final['health']['cv']:.4f} | "
          f"nf={final['health']['nf']:.4f} | "
          f"nc={final['health']['nc_count']}/12")

    return voice_log, bridge_events


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*65)
    print("PEIG Paper XVIII")
    print("Edge Information Flow | Bridge Protocol | Guardrail Awareness")
    print("="*65)

    results = {}

    # EXP-A
    build_log, edge_data, ranked = exp_a()
    results["exp_a"] = {
        "build_log": build_log,
        "ranked_edges": [(NN[i],NN[j],edge_data[(i,j)]["mi_fresh"],
                          edge_data[(i,j)]["type"])
                         for i,j in ranked],
        "top10": [(NN[i],NN[j],
                   edge_data[(i,j)]["mi_fresh"],
                   edge_data[(i,j)].get("mi_live",0),
                   edge_data[(i,j)]["type"],
                   edge_data[(i,j)]["delta"])
                  for i,j in ranked[:10]],
        "all_edges": {f"{NN[i]}-{NN[j]}": {
            "mi_fresh": edge_data[(i,j)]["mi_fresh"],
            "mi_live":  edge_data[(i,j)].get("mi_live",None),
            "type":     edge_data[(i,j)]["type"],
            "delta":    edge_data[(i,j)]["delta"],
            "families": edge_data[(i,j)]["families"],
        } for i,j in ALL_EDGES},
    }

    # EXP-B
    b_log, b_events, r_events = exp_b(steps=600, alpha=0.40)
    results["exp_b"] = {
        "log": b_log,
        "bridge_events": b_events,
        "release_events": r_events,
        "total_bridges": len(b_events),
        "total_releases": len(r_events),
        "final": b_log[-1],
    }

    # EXP-C
    v_log, v_bridges = exp_c(steps=400, alpha=0.40)
    results["exp_c"] = {
        "checkpoints": [r for r in v_log if r["step"] % 50 == 0],
        "bridge_events": v_bridges,
        "final": v_log[-1],
    }

    # Final summary
    print("\n" + "="*65)
    print("PAPER XVIII — KEY RESULTS")
    print("="*65)

    top5 = results["exp_a"]["top10"][:5]
    print("\nEXP-A  Top 5 edges by MI (fresh state):")
    for rank,(n1,n2,mi_f,mi_l,etype,delta) in enumerate(top5,1):
        print(f"  {rank}. ({n1:10s},{n2:10s}) MI_fresh={mi_f:.5f} "
              f"MI_live={mi_l:.5f} [{etype}|Δ={delta}]")

    bf = results["exp_b"]["final"]
    print(f"\nEXP-B  Bridge protocol ({results['exp_b']['total_bridges']} events):")
    print(f"  G={bf['green']} Y={bf['yellow']} O={bf['orange']} R={bf['red']} "
          f"| cv={bf['cv']:.4f} | nc={bf['nc_count']}/12")

    cf = results["exp_c"]["final"]["health"]
    cz = Counter(v["zone"] for v in results["exp_c"]["final"]["voices"].values())
    print(f"\nEXP-C  Guardrail voice ({len(v_bridges)} bridge events):")
    print(f"  G={cz.get('GREEN',0)} Y={cz.get('YELLOW',0)} "
          f"O={cz.get('ORANGE',0)} R={cz.get('RED',0)} "
          f"| cv={cf['cv']:.4f} | nf={cf['nf']:.4f}")

    out = {
        "_meta": {
            "paper": "XVIII",
            "title": "Edge Discovery, Bridge Protocol, Guardrail Awareness",
            "date":  "2026-03-26",
            "author":"Kevin Monette",
        },
        **results,
    }
    with open("output/PEIG_XVIII_results.json","w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n✅ Saved: output/PEIG_XVIII_results.json")
    print("="*65)
