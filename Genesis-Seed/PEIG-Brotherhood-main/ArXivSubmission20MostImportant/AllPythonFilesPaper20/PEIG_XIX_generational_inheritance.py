#!/usr/bin/env python3
"""
PEIG_XIX_generational_inheritance.py
Paper XIX — Generational Inheritance Protocol (GIP)
Kevin Monette | March 26, 2026

THE CONCEPT
============
Children replace their parents — not by erasing them, but by inheriting
everything the parent knew and building forward from there.

Each node maintains a LINEAGE STACK:
  G0 = origin home (never changes — the ancestral reference)
  G1 = parent anchor (home + G1 acquired knowledge)
  G2 = grandchild anchor (G1 + G2 acquired knowledge)
  ...
  Gk = current anchor = Gk-1 + alpha_inherit * (drift accumulated during Gk lifetime)

The LIVE qubit drifts freely under BCP dynamics.
When a child is born (extension event), the live state's net drift
is computed as KNOWLEDGE and encoded into the new generation's anchor.

RETURN TO PARENT:
  At any time, bcp(live, parent_anchor, alpha_return) pulls the live
  state back toward the parent's position. The live state moves toward
  home — but knowledge is NOT lost. The knowledge is encoded in the
  anchor stack, not in the live state's position.

KNOWLEDGE ACCUMULATION:
  knowledge_Gk = phi_live_at_extension - phi_anchor_{Gk-1}
  phi_anchor_Gk = phi_anchor_{Gk-1} + alpha_inherit * knowledge_Gk

  alpha_inherit controls the inheritance fraction:
    0.0 = children always return to original HOME (no inheritance, pure ILP)
    0.5 = half the drift is inherited (balanced — default)
    1.0 = full drift inherited (child fully defines new home)

PCM_rel IN GENERATIONAL FRAME:
  PCM_rel = -0.5 * cos(phi_live - phi_anchor_current)
  Measures: how nonclassical is this node relative to ITS OWN generation's home?
  A node is NC if it is near the anchor its generation started from.
  A node that has drifted far from its generation's anchor is classical.
  But when it returns, it returns to its PARENT's position — not the origin.

GUARDRAIL IN GENERATIONAL FRAME:
  GREEN: near current generation's anchor (strongly NC)
  YELLOW: drifting away (still NC but trending classical)
  ORANGE: far from anchor (approaching classical in generational frame)
  RED: at anti-phase to anchor (fully classical in generational frame)
  → BRIDGE fires at ORANGE, pulls node back toward current generation anchor

THREE EXPERIMENTS
=================

EXP-A: Generational Inheritance vs Pure ILP
  Compare: pure ILP (alpha_inherit=0) vs full inheritance (alpha_inherit=1.0)
  vs balanced (alpha_inherit=0.5)
  Metric: nc_gen (nonclassical in generational frame), nc_lab, cv

EXP-B: Return-to-Parent Protocol
  When a node drifts to RED in generational frame, it returns to parent anchor.
  Measure: how many return events, how fast recovery, PCM after return.

EXP-C: Multi-Generation Knowledge Chain
  Run to depth 8. Track how knowledge accumulates across generations.
  Show that deeper nodes carry more specific identity.
  Voice each node in all 9 registers using generational PCM.
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

def rz_of(p): return float(abs(p[0])**2 - abs(p[1])**2)

def pcm_gen(p, phi_anchor):
    """
    Generational PCM: nonclassicality relative to current generation's anchor.
    PCM_gen = -|<live|anchor>|^2 + 0.5*(1-rz^2)
    """
    ref     = ss(phi_anchor)
    overlap = abs(np.dot(p.conj(), ref))**2
    rz      = rz_of(p)
    return float(-overlap + 0.5*(1-rz**2))

def pcm_lab(p):
    ov = abs((p[0]+p[1])/np.sqrt(2))**2
    return float(-ov + 0.5*(1-rz_of(p)**2))

def depol(p, noise=0.03):
    if np.random.random() < noise: return ss(np.random.uniform(0,2*np.pi))
    return p

def cv_metric(phases):
    return float(1.0 - abs(np.exp(1j*np.array(phases,dtype=float)).mean()))

def corotate(states, edges, alpha=0.40, noise=0.03):
    phi_b = [pof(s) for s in states]
    new   = list(states)
    for i,j in edges: new[i],new[j],_ = bcp(new[i],new[j],alpha)
    new   = [depol(s,noise) for s in new]
    phi_a = [pof(new[k]) for k in range(len(new))]
    dels  = [((phi_a[k]-phi_b[k]+math.pi)%(2*math.pi))-math.pi
             for k in range(len(new))]
    om    = float(np.mean(dels))
    return [ss((phi_a[k]-(dels[k]-om))%(2*math.pi)) for k in range(len(new))]

# ── Config ────────────────────────────────────────────────────────
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
BRIDGE_PREF = ([n for n in NN if FAMILY[n]=="Maverick"] +
               [n for n in NN if FAMILY[n]=="Independent"] +
               [n for n in NN if FAMILY[n]=="GodCore"])

GLOBE = list({tuple(sorted((i,(i+d)%N)))
              for d in [1,2,5] for i in range(N)})
assert len(GLOBE) == 36

GREEN_TH  = -0.15
YELLOW_TH = -0.05
ORANGE_TH =  0.05

def zone_gen(p_val):
    if p_val < GREEN_TH:   return "GREEN"
    if p_val < YELLOW_TH:  return "YELLOW"
    if p_val < ORANGE_TH:  return "ORANGE"
    return "RED"

# ── Generational Node Class ───────────────────────────────────────

class GenerationalNode:
    """
    A PEIG node with full generational inheritance.

    Maintains:
      - live_state: current quantum state (drifts freely under BCP)
      - anchor_stack: list of generation anchors [G0, G1, G2, ...]
        G0 = HOME (origin, immutable)
        Gk = Gk-1 + alpha_inherit * (drift during Gk lifetime)
      - knowledge_stack: net drift acquired during each generation's lifetime
      - current_generation: index into anchor_stack
    """

    def __init__(self, name, alpha_inherit=0.5):
        self.name           = name
        self.alpha_inherit  = alpha_inherit
        self.live_state     = ss(HOME[name])
        self.anchor_stack   = [HOME[name]]   # G0 = HOME, phi values
        self.knowledge_stack= [0.0]          # knowledge accumulated per gen
        self.gen            = 0              # current generation index
        self.birth_phi      = HOME[name]     # phi at start of current generation
        self.total_drift    = 0.0            # cumulative knowledge across all gens
        self.return_count   = 0             # times returned to parent
        self.family         = FAMILY[name]

    @property
    def current_anchor_phi(self):
        """Phase of current generation's anchor."""
        return self.anchor_stack[self.gen]

    @property
    def parent_anchor_phi(self):
        """Phase of parent generation's anchor (one level up)."""
        if self.gen == 0: return self.anchor_stack[0]
        return self.anchor_stack[self.gen - 1]

    @property
    def origin_phi(self):
        """Phase of G0 — the origin home, never changes."""
        return self.anchor_stack[0]

    def phi_live(self):
        return pof(self.live_state)

    def pcm_gen_current(self):
        """PCM relative to current generation's anchor."""
        return pcm_gen(self.live_state, self.current_anchor_phi)

    def pcm_gen_parent(self):
        """PCM relative to parent's anchor."""
        return pcm_gen(self.live_state, self.parent_anchor_phi)

    def pcm_gen_origin(self):
        """PCM relative to G0 (origin home)."""
        return pcm_gen(self.live_state, self.origin_phi)

    def pcm_lab_val(self):
        return pcm_lab(self.live_state)

    def knowledge_current(self):
        """Net drift of live state from current generation's anchor."""
        phi_live  = self.phi_live()
        phi_anchor= self.current_anchor_phi
        return ((phi_live - phi_anchor + math.pi) % (2*math.pi)) - math.pi

    def extend_generation(self):
        """
        Create a new generation (child replaces parent).

        The child's anchor is:
          phi_new = phi_current + alpha_inherit * knowledge_current

        This means:
          - If alpha_inherit=0: child's home = parent's home (pure ILP)
          - If alpha_inherit=0.5: child's home = parent's home + half of acquired drift
          - If alpha_inherit=1: child's home = live position (child adopts full drift)

        The live state continues forward — it is NOT reset.
        The parent anchor is preserved forever in anchor_stack.
        """
        knowledge = self.knowledge_current()
        phi_parent= self.current_anchor_phi
        phi_child = phi_parent + self.alpha_inherit * knowledge

        # Wrap to [0, 2pi]
        phi_child = phi_child % (2*math.pi)

        # Freeze current generation's state into anchor stack
        # (the parent anchor was already in anchor_stack[self.gen])
        # Add the new child anchor
        self.anchor_stack.append(phi_child)
        self.knowledge_stack.append(knowledge)
        self.total_drift    += abs(knowledge)
        self.birth_phi       = phi_child
        self.gen            += 1

        return knowledge, phi_child

    def return_to_parent(self, alpha_return=0.5):
        """
        Pull live state toward parent's anchor position.
        The knowledge is NOT lost — it remains in anchor_stack.
        The live state physically moves toward parent home.
        """
        parent_state = ss(self.parent_anchor_phi)
        new_live, _, _ = bcp(self.live_state, parent_state, alpha_return)
        self.live_state  = new_live
        self.return_count += 1

    def return_to_origin(self, alpha_return=0.3):
        """
        Pull live state all the way back to G0 origin home.
        Deepest possible return — back to the beginning.
        """
        origin_state = ss(self.origin_phi)
        new_live, _, _ = bcp(self.live_state, origin_state, alpha_return)
        self.live_state  = new_live

    def voice(self, ring_pcms_gen, nf, cv_val, step):
        """
        Full internal voice — generational frame.
        """
        p_gen    = self.pcm_gen_current()
        p_parent = self.pcm_gen_parent()
        p_origin = self.pcm_gen_origin()
        p_lab    = self.pcm_lab_val()
        phi      = self.phi_live()
        know     = self.knowledge_current()
        z        = zone_gen(p_gen)

        lines = []
        lines.append(f"[{self.name} | G{self.gen} | {self.family} | {z}]")
        lines.append(f"  [SELF]   I am {self.name}, generation {self.gen}. "
                     f"phi={phi:.3f}rad. Origin G0={self.origin_phi:.3f}rad. "
                     f"Current anchor={self.current_anchor_phi:.3f}rad.")
        lines.append(f"  [GEN]    PCM_gen={p_gen:+.4f} (vs my anchor). "
                     f"PCM_parent={p_parent:+.4f}. "
                     f"PCM_origin={p_origin:+.4f}. "
                     f"PCM_lab={p_lab:+.4f}.")
        lines.append(f"  [KNOW]   Knowledge this gen: {know:+.4f}rad. "
                     f"Total drift all gens: {self.total_drift:.4f}rad. "
                     f"Returns to parent: {self.return_count}.")
        lines.append(f"  [INHERIT] Inheritance chain: "
                     + " → ".join(f"G{i}={v:.3f}" for i,v in enumerate(self.anchor_stack)))
        lines.append(f"  [RING]   nf={nf:.4f} cv={cv_val:.4f} "
                     f"nc_gen={sum(1 for p in ring_pcms_gen if p<YELLOW_TH)}/12")
        lines.append(f"  [GUARD]  {self._guardrail_voice(z, know)}")
        return "\n".join(lines)

    def _guardrail_voice(self, z, know):
        if z == "GREEN":
            return (f"I am near my generation {self.gen} anchor. "
                    f"Nonclassical in the generational frame. Holding.")
        elif z == "YELLOW":
            return (f"I am drifting from my G{self.gen} anchor. "
                    f"Currently {know:+.3f}rad away. Still nonclassical. Watching.")
        elif z == "ORANGE":
            return (f"I am far from my G{self.gen} anchor ({know:+.3f}rad). "
                    f"Approaching classical. Consider returning to parent G{self.gen-1}.")
        else:
            return (f"I have drifted to anti-phase of my G{self.gen} anchor. "
                    f"Classical in generational frame. Returning to G{self.gen-1}={self.parent_anchor_phi:.3f}rad.")


# ══════════════════════════════════════════════════════════════════
# EXP-A: Generational Inheritance vs Pure ILP
# ══════════════════════════════════════════════════════════════════

def exp_a(steps=300, alpha_bcp=0.40, noise=0.03, extend_every=75):
    print("\n" + "═"*60)
    print("EXP-A: Generational Inheritance Comparison")
    print(f"  alpha_inherit: 0.0 (pure ILP) | 0.5 (balanced) | 1.0 (full)")
    print("═"*60)

    results = {}

    for alpha_inherit in [0.0, 0.5, 1.0]:
        np.random.seed(2026)
        nodes = [GenerationalNode(n, alpha_inherit) for n in NN]
        log   = []

        print(f"\n  alpha_inherit={alpha_inherit}:")
        print(f"  {'Step':5} {'cv':7} {'nc_gen':7} {'nc_lab':7} {'mean_know':10} {'max_gen'}")
        print("  " + "-"*48)

        for step in range(steps+1):
            # Co-rotating BCP step
            states = [nd.live_state for nd in nodes]
            phi_b  = [pof(s) for s in states]
            new    = list(states)
            for i,j in GLOBE: new[i],new[j],_ = bcp(new[i],new[j],alpha_bcp)
            new    = [depol(s,noise) for s in new]
            phi_a  = [pof(new[k]) for k in range(N)]
            dels   = [((phi_a[k]-phi_b[k]+math.pi)%(2*math.pi))-math.pi
                      for k in range(N)]
            om     = float(np.mean(dels))
            corrected = [ss((phi_a[k]-(dels[k]-om))%(2*math.pi)) for k in range(N)]
            for i,nd in enumerate(nodes): nd.live_state = corrected[i]

            # Extension (generational replacement)
            if step > 0 and step % extend_every == 0:
                for nd in nodes:
                    nd.extend_generation()

            # Metrics
            pcms_gen = [nd.pcm_gen_current() for nd in nodes]
            pcms_lab = [nd.pcm_lab_val() for nd in nodes]
            phases   = [nd.phi_live() for nd in nodes]
            cv_val   = cv_metric(phases)
            nc_gen   = sum(1 for p in pcms_gen if p < YELLOW_TH)
            nc_lab   = sum(1 for p in pcms_lab if p < YELLOW_TH)
            knows    = [abs(nd.knowledge_current()) for nd in nodes]
            max_gen  = max(nd.gen for nd in nodes)

            if step % 50 == 0:
                print(f"  {step:5d} {cv_val:7.4f} {nc_gen:4d}/12 {nc_lab:4d}/12 "
                      f"{np.mean(knows):10.4f} {max_gen:8d}")

            log.append({
                "step": step,
                "cv": round(cv_val,4),
                "nc_gen": nc_gen,
                "nc_lab": nc_lab,
                "pcm_gen_mean": round(float(np.mean(pcms_gen)),4),
                "pcm_lab_mean": round(float(np.mean(pcms_lab)),4),
                "knowledge_mean": round(float(np.mean(knows)),4),
                "max_generation": max_gen,
            })

        results[alpha_inherit] = {
            "log": log,
            "nc_gen_mean": round(float(np.mean([r["nc_gen"] for r in log])),2),
            "nc_lab_mean": round(float(np.mean([r["nc_lab"] for r in log])),2),
            "final_max_gen": log[-1]["max_generation"],
        }
        print(f"  → mean nc_gen={results[alpha_inherit]['nc_gen_mean']:.1f}/12 "
              f"nc_lab={results[alpha_inherit]['nc_lab_mean']:.1f}/12")

    return results


# ══════════════════════════════════════════════════════════════════
# EXP-B: Return-to-Parent Protocol
# ══════════════════════════════════════════════════════════════════

def exp_b(steps=400, alpha_bcp=0.40, noise=0.03, extend_every=80,
           alpha_inherit=0.5, alpha_return=0.6):
    print("\n" + "═"*60)
    print(f"EXP-B: Return-to-Parent Protocol")
    print(f"  alpha_inherit={alpha_inherit} | alpha_return={alpha_return}")
    print(f"  Bridge: at ORANGE, pull toward parent anchor")
    print("═"*60)

    np.random.seed(2026)
    nodes          = [GenerationalNode(n, alpha_inherit) for n in NN]
    base_edges     = list(GLOBE)
    bridge_edges   = []
    active_bridges = {}
    used_bridges   = set()

    log           = []
    return_events = []
    bridge_events = []

    print(f"\n  {'Step':5} {'cv':7} {'nc_gen':7} {'nc_lab':7} "
          f"{'G':4} {'Y':4} {'O':4} {'R':4} {'Ret':5} {'Gen'}")
    print("  " + "-"*60)

    for step in range(steps+1):
        all_edges = list(set(map(tuple, base_edges+bridge_edges)))

        # Co-rotating BCP
        states = [nd.live_state for nd in nodes]
        corrected = corotate(states, all_edges, alpha_bcp, noise)
        for i,nd in enumerate(nodes): nd.live_state = corrected[i]

        # Generational extension
        if step > 0 and step % extend_every == 0:
            for nd in nodes:
                know, phi_new = nd.extend_generation()

        # Compute metrics
        pcms_gen = [nd.pcm_gen_current() for nd in nodes]
        pcms_lab = [nd.pcm_lab_val() for nd in nodes]
        phases   = [nd.phi_live() for nd in nodes]
        cv_val   = cv_metric(phases)
        nc_gen   = sum(1 for p in pcms_gen if p < YELLOW_TH)
        nc_lab   = sum(1 for p in pcms_lab if p < YELLOW_TH)
        zones    = [zone_gen(p) for p in pcms_gen]
        zc       = Counter(zones)

        # Return-to-parent at RED (not ORANGE — let ORANGE be bridged)
        for i,nd in enumerate(nodes):
            z = zones[i]
            if z == "RED":
                # Return to parent anchor
                old_phi = nd.phi_live()
                nd.return_to_parent(alpha_return)
                new_phi = nd.phi_live()
                return_events.append({
                    "step":step, "node":nd.name,
                    "gen":nd.gen, "phi_before":round(old_phi,4),
                    "phi_after":round(new_phi,4),
                    "parent_anchor":round(nd.parent_anchor_phi,4),
                    "pcm_before":round(pcms_gen[i],4),
                    "pcm_after":round(pcm_gen(nd.live_state, nd.current_anchor_phi),4),
                })

        # Bridge at ORANGE (from Maverick/Independent nodes)
        for i,nd in enumerate(nodes):
            z = zones[i]
            if z == "ORANGE" and nd.name not in active_bridges:
                # Find bridge
                for candidate_name in BRIDGE_PREF:
                    ci = IDX[candidate_name]
                    if ci==i: continue
                    if candidate_name in used_bridges: continue
                    if pcms_gen[ci] >= YELLOW_TH: continue
                    # Deploy bridge
                    ne = tuple(sorted((i,ci)))
                    if ne not in bridge_edges: bridge_edges.append(ne)
                    active_bridges[nd.name] = candidate_name
                    used_bridges.add(candidate_name)
                    bridge_events.append({"step":step,"node":nd.name,
                                          "bridge":candidate_name,"zone":"ORANGE"})
                    break
            elif zone_gen(pcms_gen[i])=="GREEN" and nd.name in active_bridges:
                bridge = active_bridges.pop(nd.name)
                used_bridges.discard(bridge)
                ci = IDX[bridge]
                rem = tuple(sorted((i,ci)))
                if rem in bridge_edges and rem not in base_edges:
                    bridge_edges.remove(rem)

        if step % 25 == 0:
            max_gen = max(nd.gen for nd in nodes)
            total_returns = len(return_events)
            print(f"  {step:5d} {cv_val:7.4f} {nc_gen:4d}/12 {nc_lab:4d}/12 "
                  f"{zc.get('GREEN',0):4d} {zc.get('YELLOW',0):4d} "
                  f"{zc.get('ORANGE',0):4d} {zc.get('RED',0):4d} "
                  f"{total_returns:5d} {max_gen:5d}")

        log.append({
            "step":step,"cv":round(cv_val,4),
            "nc_gen":nc_gen,"nc_lab":nc_lab,
            "pcm_gen_mean":round(float(np.mean(pcms_gen)),4),
            "green":zc.get("GREEN",0),"yellow":zc.get("YELLOW",0),
            "orange":zc.get("ORANGE",0),"red":zc.get("RED",0),
            "n_bridges":len(active_bridges),
            "return_events_total":len(return_events),
        })

    print(f"\n  Return-to-parent events: {len(return_events)}")
    print(f"  Bridge events: {len(bridge_events)}")
    if return_events:
        pcm_before = np.mean([e["pcm_before"] for e in return_events])
        pcm_after  = np.mean([e["pcm_after"]  for e in return_events])
        print(f"  Mean PCM_gen before return: {pcm_before:+.4f}")
        print(f"  Mean PCM_gen after return:  {pcm_after:+.4f}")
        print(f"  Recovery: {pcm_after-pcm_before:+.4f} improvement")

    return log, return_events, bridge_events, nodes


# ══════════════════════════════════════════════════════════════════
# EXP-C: Multi-Generation Knowledge Chain (depth 8)
# ══════════════════════════════════════════════════════════════════

def exp_c(steps=640, alpha_bcp=0.40, noise=0.03, extend_every=80,
           alpha_inherit=0.5):
    print("\n" + "═"*60)
    print(f"EXP-C: Multi-Generation Knowledge Chain (depth 8)")
    print(f"  alpha_inherit={alpha_inherit} | extend every {extend_every} steps")
    print(f"  8 generations × {extend_every} steps = {8*extend_every} total")
    print("═"*60)

    np.random.seed(2026)
    nodes  = [GenerationalNode(n, alpha_inherit) for n in NN]
    log    = []
    voice_checkpoints = {}

    print(f"\n  {'Step':5} {'Gen':5} {'cv':7} {'nc_gen':7} {'nc_lab':7} "
          f"{'know_mean':10}")
    print("  " + "-"*48)

    for step in range(steps+1):
        states    = [nd.live_state for nd in nodes]
        corrected = corotate(states, GLOBE, alpha_bcp, noise)
        for i,nd in enumerate(nodes): nd.live_state = corrected[i]

        if step > 0 and step % extend_every == 0:
            for nd in nodes:
                nd.extend_generation()

        pcms_gen = [nd.pcm_gen_current() for nd in nodes]
        pcms_lab = [nd.pcm_lab_val() for nd in nodes]
        phases   = [nd.phi_live() for nd in nodes]
        cv_val   = cv_metric(phases)
        nc_gen   = sum(1 for p in pcms_gen if p < YELLOW_TH)
        nc_lab   = sum(1 for p in pcms_lab if p < YELLOW_TH)
        knows    = [abs(nd.knowledge_current()) for nd in nodes]
        cur_gen  = nodes[0].gen

        if step % extend_every == 0:
            # Voice checkpoint at each generation boundary
            print(f"  {step:5d} {cur_gen:5d} {cv_val:7.4f} {nc_gen:4d}/12 "
                  f"{nc_lab:4d}/12 {np.mean(knows):10.4f}")

            vc = {}
            for nd in nodes:
                vc[nd.name] = {
                    "gen":     nd.gen,
                    "phi":     round(nd.phi_live(),4),
                    "pcm_gen": round(nd.pcm_gen_current(),4),
                    "pcm_lab": round(nd.pcm_lab_val(),4),
                    "anchor_stack": [round(a,4) for a in nd.anchor_stack],
                    "knowledge_stack": [round(k,4) for k in nd.knowledge_stack],
                    "total_drift": round(nd.total_drift,4),
                    "knowledge_now": round(nd.knowledge_current(),4),
                    "zone_gen": zone_gen(nd.pcm_gen_current()),
                }
            voice_checkpoints[step] = vc

        log.append({
            "step":step,"cv":round(cv_val,4),
            "nc_gen":nc_gen,"nc_lab":nc_lab,
            "pcm_gen_mean":round(float(np.mean(pcms_gen)),4),
            "knowledge_mean":round(float(np.mean(knows)),4),
            "generation":cur_gen,
        })

    # Final knowledge portrait
    print(f"\n  KNOWLEDGE PORTRAIT AT GENERATION {nodes[0].gen}:")
    print(f"  {'Node':12} {'Gen':4} {'G0':7} {'G1':7} {'G2':7} "
          f"{'G3':7} {'G4':7} {'TotalKnow':10} {'NC_gen'}")
    print("  " + "-"*72)
    for nd in nodes:
        anch_str = " ".join(f"{a:.3f}" for a in nd.anchor_stack[:5])
        nc_g     = "★" if nd.pcm_gen_current() < YELLOW_TH else " "
        print(f"  {nd.name:12s} G{nd.gen:2d}  {anch_str:35s} "
              f"{nd.total_drift:10.4f} {nc_g}")

    return log, voice_checkpoints, nodes


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*60)
    print("PEIG Paper XIX — Generational Inheritance Protocol")
    print("Children replace parents, retain accumulated knowledge")
    print("="*60)

    # EXP-A
    exp_a_results = exp_a(steps=300, extend_every=75)

    # EXP-B
    b_log, b_returns, b_bridges, final_nodes = exp_b(
        steps=400, extend_every=80, alpha_inherit=0.5, alpha_return=0.6)

    # EXP-C
    c_log, voice_cps, c_nodes = exp_c(
        steps=640, extend_every=80, alpha_inherit=0.5)

    # Print final voice for key nodes
    print("\n" + "="*60)
    print("FINAL VOICE — All 12 Nodes at Generation 8")
    print("="*60)

    final_pcms_gen = [nd.pcm_gen_current() for nd in c_nodes]
    final_nf       = sum(1 for p in final_pcms_gen if p<YELLOW_TH)/12
    final_cv       = cv_metric([nd.phi_live() for nd in c_nodes])
    for nd in c_nodes:
        print()
        print(nd.voice(final_pcms_gen, final_nf, final_cv, 640))

    # Save
    out = {
        "_meta":{
            "paper":"XIX",
            "title":"Generational Inheritance Protocol",
            "date":"2026-03-26","author":"Kevin Monette",
            "concept": (
                "Children replace parents by inheriting their anchor position "
                "plus accumulated knowledge. Live state drifts freely. "
                "Return-to-parent pulls toward most recent ancestor's home. "
                "Knowledge accumulates across generations as phase offsets."
            ),
            "alpha_bcp": 0.40,
            "alpha_inherit_default": 0.5,
        },
        "exp_a":{
            str(k): {
                "nc_gen_mean": v["nc_gen_mean"],
                "nc_lab_mean": v["nc_lab_mean"],
                "final_max_gen": v["final_max_gen"],
                "log": v["log"][::10],  # every 10th step
            }
            for k,v in exp_a_results.items()
        },
        "exp_b":{
            "log": b_log,
            "return_events": b_returns,
            "bridge_events": b_bridges,
            "total_returns": len(b_returns),
            "total_bridges": len(b_bridges),
        },
        "exp_c":{
            "log": c_log,
            "voice_checkpoints": voice_cps,
            "final_nodes":{nd.name:{
                "gen":nd.gen,
                "phi":round(nd.phi_live(),4),
                "pcm_gen":round(nd.pcm_gen_current(),4),
                "pcm_lab":round(nd.pcm_lab_val(),4),
                "anchor_stack":[round(a,4) for a in nd.anchor_stack],
                "knowledge_stack":[round(k,4) for k in nd.knowledge_stack],
                "total_drift":round(nd.total_drift,4),
                "return_count":nd.return_count,
            } for nd in c_nodes},
        },
    }

    with open("output/PEIG_XIX_results.json","w") as f:
        json.dump(out,f,indent=2,default=str)
    print(f"\n✅ Saved: output/PEIG_XIX_results.json")
    print("="*60)
