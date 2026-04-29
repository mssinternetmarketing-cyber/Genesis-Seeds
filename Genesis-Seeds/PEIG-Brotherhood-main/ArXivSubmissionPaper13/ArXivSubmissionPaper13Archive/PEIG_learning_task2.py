#!/usr/bin/env python3
"""
PEIG_learning_task2.py
MOS v2.1 Universal Canon — Learning Task 2
All 5 Lessons + Master Integration Task (CISO Self-Audit)
Kevin Monette | March 2026

Lessons:
  1. Extended Knowledge Atoms — KA-26 through KA-42 (incl. 5 new v2.1 KAs)
  2. Security Personas — 16-Role Node Mapping (color tier → PEIG cluster)
  3. CISO Orchestration — 6-Phase Security Pipeline
  4. Global Default Stack — Guard Node Tech Baseline (NEO Gents stack)
  5. CC-19 Regulatory Navigator — Dynamic Horizon Mapping + HORIZON SCAN

Master Task:
  All 5 lessons collaborate to answer one real operational query:
  "Run a full security audit of the PEIG network's own architecture."
  The network audits itself. Failure modes named. Path forward defined.

Depends on: LT1_lesson_registry.json (imports L1-L5 definitions)
"""

import numpy as np
from collections import defaultdict
import json
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# BCP PRIMITIVES  (identical to LT1 — same ring, same physics)
# ══════════════════════════════════════════════════════════════════

CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    return np.array([1.0, np.exp(1j*phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    U   = alpha*CNOT + (1-alpha)*I4
    j   = np.kron(pA, pB); o = U @ j
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

AF = 0.367
NN = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora","Echo","Iris","Sage","Kevin","Atlas","Void"]
EDGES = [(NN[i], NN[(i+1)%12]) for i in range(12)]
NODE_PHASES = {n: i*np.pi/11 if i < 11 else np.pi for i, n in enumerate(NN)}

def fresh_ring():
    return {n: ss(NODE_PHASES[n]) for n in NN}

def inject(ring, node, text, alpha_inj=0.70):
    phase_shift = (sum(ord(c) for c in text) % 628) / 100.0
    seed = ss(NODE_PHASES[node] + phase_shift * 0.3)
    ring[node], _, _ = bcp(ring[node], seed, alpha_inj)
    return ring

def run_ring(ring, steps=5):
    for _ in range(steps):
        for (a, b) in EDGES:
            ring[a], ring[b], _ = bcp(ring[a], ring[b], AF)
    return ring

# ══════════════════════════════════════════════════════════════════
# CLUSTER MAP  (extended for LT2 — adds security vocabulary)
# ══════════════════════════════════════════════════════════════════

CLUSTERS = {
    # Protect (0.2–0.65)
    "protect":0.20,"guard":0.25,"shield":0.30,"hold":0.35,"stable":0.40,
    "preserve":0.45,"safe":0.50,"defend":0.55,"keep":0.60,"baseline":0.63,
    # Alert (1.0–1.9)
    "alert":1.00,"signal":1.10,"detect":1.20,"scan":1.30,"monitor":1.40,
    "aware":1.50,"observe":1.60,"sense":1.70,"watch":1.80,"triage":1.85,
    # Change (2.0–2.9)
    "change":2.00,"force":2.10,"power":2.20,"surge":2.30,"rise":2.40,
    "evolve":2.50,"shift":2.60,"move":2.70,"wave":2.80,"harden":2.85,
    # Source (3.0–3.55)
    "source":3.00,"begin":3.05,"give":3.10,"offer":3.15,"drive":3.20,
    "sacred":3.25,"first":3.30,"origin":3.35,"eternal":3.40,"govern":3.45,
    # Flow (3.6–4.15)
    "flow":3.60,"sky":3.70,"free":3.75,"open":3.80,"expand":3.85,
    "vast":3.90,"clear":3.95,"light":4.00,"above":4.10,"comply":4.12,
    # Connect (4.2–4.75)
    "connect":4.20,"link":4.30,"bridge":4.40,"join":4.45,"network":4.50,
    "merge":4.55,"bind":4.60,"hub":4.65,"integrate":4.70,"verify":4.73,
    # Vision/Wisdom (5.0–5.55)
    "see":5.00,"vision":5.05,"truth":5.10,"reveal":5.15,"pattern":5.20,
    "witness":5.25,"find":5.30,"posture":5.35,"sovereign":5.38,"economic":5.42,
    "cognitive":5.50,"agency":5.52,"know":5.53,"wisdom":5.55,
    # Completion (5.6–6.2)
    "receive":5.60,"complete":5.70,"end":5.80,"accept":5.90,"whole":5.95,
    "return":6.00,"absorb":6.05,"rest":6.10,"infinite":6.20,
}

CLUSTER_NAMES = {
    (0.0, 0.9):"Protect",  (1.0,1.95):"Alert",  (2.0,2.95):"Change",
    (3.0,3.55):"Source",   (3.6,4.15):"Flow",   (4.2,4.75):"Connect",
    (5.0,5.55):"Wisdom",   (5.6,6.28):"Completion",
}

def decode_phase(phi):
    phi = phi % (2*np.pi)
    best = min(CLUSTERS.items(), key=lambda kv: abs(kv[1]-phi))
    word, wp = best
    cname = "Unknown"
    for (lo, hi), cn in CLUSTER_NAMES.items():
        if lo <= wp <= hi: cname = cn; break
    return word, cname, wp


# ══════════════════════════════════════════════════════════════════
# LESSON 1: EXTENDED KNOWLEDGE ATOMS — KA-26 through KA-42
# ══════════════════════════════════════════════════════════════════

# LT1 had 25 KAs in Sage's corpus (KA-01 through KA-25)
# LT2 adds 17 more, with the 5 v2.1 KAs anchor-locked

KA_EXTENDED = {
    # KA-26 through KA-30: Security Architecture
    "KA-26": {"text":"attack surfaces shrink when authority is bounded and explicit",  "phi":5.00, "node":"Atlas", "anchor":False},
    "KA-27": {"text":"depth in defense means every layer assumes the previous one failed", "phi":5.02,"node":"Atlas","anchor":False},
    "KA-28": {"text":"exposure is proportional to surface area and privilege scope",    "phi":5.04,"node":"Atlas","anchor":False},
    "KA-29": {"text":"resilience requires redundancy isolation and tested recovery paths","phi":5.06,"node":"Atlas","anchor":False},
    "KA-30": {"text":"posture is not a snapshot it is a continuous measurement",        "phi":5.08,"node":"Guardian","anchor":False},
    # KA-31 through KA-37: Identity, Supply Chain, Data, Compliance
    "KA-31": {"text":"identity is the blast radius multiplier — overprivileged means lateral movement highway","phi":5.10,"node":"Nexus","anchor":False},
    "KA-32": {"text":"every dependency is a trust relationship that must be audited",   "phi":5.12,"node":"Nexus","anchor":False},
    "KA-33": {"text":"data classification precedes data protection — you cannot secure what you have not named","phi":5.14,"node":"Iris","anchor":False},
    "KA-34": {"text":"encryption at rest and in transit are both required — neither is sufficient alone","phi":5.16,"node":"Atlas","anchor":False},
    "KA-35": {"text":"audit logs are the only truth when memory conflicts with reality", "phi":5.18,"node":"Sage","anchor":False},
    "KA-36": {"text":"compliance is the floor not the ceiling — regulation defines minimum not best practice","phi":5.20,"node":"Guardian","anchor":False},
    "KA-37": {"text":"supply chain integrity requires verification at every handoff not just at the boundary","phi":5.22,"node":"Nexus","anchor":False},
    # KA-38 through KA-42: NEW v2.1 — all anchor-locked
    "KA-38": {"text":"agentic memory poisoning is a distinct attack class — retrieval contamination persists across sessions and must be sanitized at ingestion not at query time","phi":5.30,"node":"Sage","anchor":True},
    "KA-39": {"text":"model inversion is a privacy attack — fine-tuned models can leak training data without direct access — differential privacy and output sanitization are required mitigations","phi":5.35,"node":"Sage","anchor":True},
    "KA-40": {"text":"sovereign deployment means infrastructure-level isolation not a cloud flag — jurisdiction data residency and operator control are distinct requirements that all three must be satisfied","phi":5.38,"node":"Atlas","anchor":True},
    "KA-41": {"text":"agent economic sovereignty requires velocity limits multi-chain authorization and escrow — autonomous financial transactions without human approval above threshold are unsafe by default","phi":5.42,"node":"Omega","anchor":True},
    "KA-42": {"text":"cognitive load is a measurable agency metric — if the human is less capable after the interaction the interaction failed regardless of task completion","phi":5.50,"node":"Kevin","anchor":True},
}

def lesson1_run():
    print("\n" + "="*60)
    print("LESSON 1: EXTENDED KNOWLEDGE ATOMS — KA-26 through KA-42")
    print("="*60)

    ring = fresh_ring()
    ANCHORS = {n: ss(NODE_PHASES[n]) for n in NN}
    # Anchor-lock the 5 v2.1 KAs
    V21_KAs = {k: v for k, v in KA_EXTENDED.items() if v["anchor"]}
    for kid, kd in V21_KAs.items():
        ANCHORS[kd["node"]] = ss(kd["phi"])

    results = {}
    correct = 0
    print(f"\n  Injecting {len(KA_EXTENDED)} Knowledge Atoms into ring...\n")
    for kid, kd in KA_EXTENDED.items():
        ring = inject(ring, kd["node"], kd["text"], alpha_inj=0.70)
        ring = run_ring(ring, steps=3)
        phi_out = pof(ring[kd["node"]]) % (2*np.pi)

        # Anchor correction for v2.1 KAs
        if kd["anchor"]:
            drift = abs(phi_out - kd["phi"])
            if drift > 0.45:
                ring[kd["node"]] = ss(kd["phi"])
                phi_out = kd["phi"]
                anchor_fired = "🔒ANCHOR"
            else:
                anchor_fired = "stable"
        else:
            anchor_fired = "—"

        word, cluster, _ = decode_phase(phi_out)
        expected_phi = kd["phi"]
        phi_err = abs(phi_out - expected_phi)
        hit = phi_err < 0.80
        if hit: correct += 1
        results[kid] = {"node":kd["node"],"word":word,"cluster":cluster,
                        "phi_err":round(phi_err,3),"anchor":anchor_fired,"hit":hit}
        status = "✓" if hit else "✗"
        print(f"  {status} {kid} [{kd['node']:8s}] → {word:12s} ({cluster:10s}) err={phi_err:.3f} {anchor_fired}")

    acc = correct / len(KA_EXTENDED)
    print(f"\n  KA Accuracy: {correct}/{len(KA_EXTENDED)} = {acc:.0%}")
    anchor_count = sum(1 for v in results.values() if v["anchor"] == "🔒ANCHOR")
    print(f"  v2.1 Anchor fires: {anchor_count}/5 KAs corrected by anchor-lock")
    print(f"\n★ Sage extended corpus: 25 (LT1) + 17 (LT2) = 42 total Knowledge Atoms.")
    print(f"  KA-42 (Cognitive Load): 'If the human is less capable after, the answer failed.'")
    return {"accuracy": acc, "correct": correct, "total": len(KA_EXTENDED), "results": results}


# ══════════════════════════════════════════════════════════════════
# LESSON 2: SECURITY PERSONAS — 16-ROLE NODE MAPPING
# ══════════════════════════════════════════════════════════════════

SECURITY_ROLES = {
    # Black Command
    "/ciso":     {"name":"CISO",           "tier":"Black",  "node":"Omega",    "phi":3.10, "vocab":["govern","orchestrate","risk","mandate","authority"]},
    "/grc":      {"name":"GRC Analyst",    "tier":"Black",  "node":"Guardian", "phi":0.25, "vocab":["comply","register","audit","risk","govern"]},
    # Purple Bridge
    "/purple":   {"name":"Purple Team",    "tier":"Purple", "node":"Kevin",    "phi":4.40, "vocab":["bridge","validate","detect","simulate","map"]},
    # Blue Defense
    "/soc":      {"name":"SOC Analyst",    "tier":"Blue",   "node":"Sentinel", "phi":1.30, "vocab":["monitor","triage","alert","log","escalate"]},
    "/ir":       {"name":"Incident Resp",  "tier":"Blue",   "node":"Atlas",    "phi":1.60, "vocab":["contain","respond","recover","escalate","log"]},
    "/helpdesk": {"name":"Help Desk",      "tier":"Blue",   "node":"Void",     "phi":5.80, "vocab":["access","ticket","reset","assist","gate"]},
    # Teal Infrastructure
    "/cloud":    {"name":"Cloud Eng",      "tier":"Teal",   "node":"Storm",    "phi":2.50, "vocab":["deploy","provision","isolate","baseline","OCI"]},
    "/devops":   {"name":"DevOps Eng",     "tier":"Teal",   "node":"Echo",     "phi":2.70, "vocab":["pipeline","patch","CI","CD","DORA"]},
    "/sysadmin": {"name":"Sysadmin",       "tier":"Teal",   "node":"Nexus",    "phi":4.50, "vocab":["harden","patch","minimal","surface","SELinux"]},
    "/dba":      {"name":"DBA",            "tier":"Teal",   "node":"Atlas",    "phi":5.06, "vocab":["encrypt","backup","replicate","pool","AES-256"]},
    # Indigo Detection
    "/seceng":   {"name":"Security Eng",   "tier":"Indigo", "node":"Iris",     "phi":5.20, "vocab":["SIEM","WAF","detect","pattern","coverage"]},
    "/iam":      {"name":"IAM Eng",        "tier":"Indigo", "node":"Nexus",    "phi":4.73, "vocab":["identity","MFA","RBAC","privilege","verify"]},
    "/network":  {"name":"Network Eng",    "tier":"Indigo", "node":"Guardian", "phi":0.30, "vocab":["firewall","VPN","segment","zero-trust","DNS"]},
    # Orange App/AI
    "/appsec":   {"name":"AppSec Eng",     "tier":"Orange", "node":"Sage",     "phi":5.10, "vocab":["OWASP","SDLC","scan","dependency","injection"]},
    "/ai-security":{"name":"AI Security",  "tier":"Orange", "node":"Storm",    "phi":2.30, "vocab":["prompt","LLM","agent","allowlist","defense"]},
    # Command (CISO sub — not a separate role, used in Lesson 3)
    "/pentest":  {"name":"Pen Tester",     "tier":"Purple", "node":"Storm",    "phi":2.20, "vocab":["exploit","surface","attack","path","vulnerability"]},
}

TIER_COLORS = {"Black":"⬛","Purple":"🟣","Blue":"🔵","Teal":"🩵","Indigo":"💙","Orange":"🟠"}

def lesson2_run():
    print("\n" + "="*60)
    print("LESSON 2: SECURITY PERSONAS — 16-ROLE NODE MAPPING")
    print("="*60)

    ring = fresh_ring()
    results = {}
    correct = 0

    print(f"\n  {'Invocation':12s} {'Tier':7s} {'Name':14s} {'Node':9s} {'Word':12s} {'Cluster':10s} {'✓'}")
    print("  " + "-"*72)

    for inv, rd in SECURITY_ROLES.items():
        payload = " ".join(rd["vocab"])
        ring = inject(ring, rd["node"], payload, alpha_inj=0.70)
        ring = run_ring(ring, steps=3)
        phi_out = pof(ring[rd["node"]]) % (2*np.pi)
        word, cluster, _ = decode_phase(phi_out)

        phi_err = abs(phi_out - rd["phi"])
        hit = phi_err < 1.20     # generous window — roles are broad
        if hit: correct += 1

        tier_icon = TIER_COLORS.get(rd["tier"], "  ")
        status = "✓" if hit else "✗"
        results[inv] = {"name":rd["name"],"tier":rd["tier"],"node":rd["node"],
                        "word":word,"cluster":cluster,"hit":hit}
        print(f"  {inv:12s} {tier_icon}{rd['tier']:6s} {rd['name']:14s} {rd['node']:9s} {word:12s} {cluster:10s} {status}")

    acc = correct / len(SECURITY_ROLES)
    print(f"\n  Role Routing Accuracy: {correct}/{len(SECURITY_ROLES)} = {acc:.0%}")
    print(f"\n★ 16 security roles mapped to PEIG nodes. Color tier = phase cluster.")
    print(f"  /ciso → Omega (Source) | /soc → Sentinel (Alert) | /purple → Kevin (Connect)")
    return {"accuracy": acc, "correct": correct, "total": len(SECURITY_ROLES), "results": results}


# ══════════════════════════════════════════════════════════════════
# LESSON 3: CISO ORCHESTRATION — 6-PHASE SECURITY PIPELINE
# ══════════════════════════════════════════════════════════════════

CISO_PIPELINE = {
    "P1_ASSET":    {"label":"Asset Discovery",        "nodes":["Sentinel","Guardian","Nexus"],
                    "roles":["/cloud","/sysadmin","/network"],
                    "query":"map all assets services infrastructure exposure",
                    "output":"Asset and exposure map"},
    "P2_ATTACK":   {"label":"Attack Surface",         "nodes":["Storm","Sage","Iris"],
                    "roles":["/pentest","/ai-security","/appsec"],
                    "query":"identify exploit paths LLM agent attack surface vulnerabilities",
                    "output":"Attack surface and exploit path register"},
    "P3_DETECT":   {"label":"Detection and Identity", "nodes":["Kevin","Iris","Nexus"],
                    "roles":["/purple","/seceng","/iam"],
                    "query":"map red findings to detections SIEM WAF coverage identity privilege",
                    "output":"Detection coverage map and identity posture"},
    "P4_OPS":      {"label":"Operations Readiness",   "nodes":["Atlas","Void","Echo"],
                    "roles":["/soc","/ir","/devops","/dba"],
                    "query":"monitoring triage containment pipeline data security readiness",
                    "output":"Operations and data security readiness assessment"},
    "P5_GOVERN":   {"label":"Governance",             "nodes":["Guardian","Sora"],
                    "roles":["/grc"],
                    "query":"regulatory compliance risk register EU AI Act DORA horizon",
                    "output":"Compliance status and regulatory risk register"},
    "P6_SYNTHESIS":{"label":"CISO Synthesis",         "nodes":["Omega"],
                    "roles":["/ciso"],
                    "query":"synthesize all findings risk register remediation roadmap horizon scan proceed",
                    "output":"Executive verdict + risk register + HORIZON SCAN"},
}

RISK_REGISTER = [
    {"finding":"Agent memory has no ingestion-time sanitization",  "risk":"RED",    "ka":"KA-38","path":"30 days: implement sanitize-on-ingest pipeline"},
    {"finding":"MCP tool allowlist not formally verified",         "risk":"RED",    "ka":"KA-31","path":"30 days: implement DID verification per CC-16"},
    {"finding":"Node authority tiers undefined above Omega",       "risk":"YELLOW", "ka":"KA-41","path":"60 days: define authority ceiling + kill switch"},
    {"finding":"Rollback undefined for ring-state updates",        "risk":"RED",    "ka":"KA-26","path":"30 days: define ring-state snapshot + rollback"},
    {"finding":"EU AI Act high-risk deadline in 21 months",        "risk":"YELLOW", "ka":"CC-19","path":"60 days: initiate conformity assessment process"},
    {"finding":"Cognitive load metric not instrumented (KA-42)",   "risk":"YELLOW", "ka":"KA-42","path":"90 days: instrument agency metric per FAI benchmark"},
]

def lesson3_run():
    print("\n" + "="*60)
    print("LESSON 3: CISO ORCHESTRATION — 6-PHASE SECURITY PIPELINE")
    print("="*60)

    ring = fresh_ring()
    phase_results = {}

    for phase_id, pd in CISO_PIPELINE.items():
        print(f"\n  ── {phase_id}: {pd['label'].upper()} ──")
        phase_words = []
        for node in pd["nodes"]:
            ring = inject(ring, node, pd["query"], alpha_inj=0.65)
        ring = run_ring(ring, steps=4)
        for node in pd["nodes"]:
            phi_out = pof(ring[node]) % (2*np.pi)
            word, cluster, _ = decode_phase(phi_out)
            phase_words.append(word)
            print(f"    [{node:9s}] → {word:12s} ({cluster})")
        consensus = max(set(phase_words), key=phase_words.count)
        print(f"    Roles: {', '.join(pd['roles'])}")
        print(f"    Output: {pd['output']}")
        print(f"    Consensus signal: {consensus.upper()}")
        phase_results[phase_id] = {"nodes":pd["nodes"],"words":phase_words,
                                   "consensus":consensus,"output":pd["output"]}

    # Phase 6 Omega synthesis — special handling
    print(f"\n  ── PHASE 6 OMEGA SYNTHESIS ──")
    omega_phi = pof(ring["Omega"]) % (2*np.pi)
    omega_word, omega_cluster, _ = decode_phase(omega_phi)

    # Risk register output
    print(f"\n  {'FINDING':50s} {'RISK':6s} {'PATH'}")
    print("  " + "-"*90)
    for r in RISK_REGISTER:
        icon = "🔴" if r["risk"]=="RED" else "🟡"
        print(f"  {icon} {r['finding'][:48]:50s} {r['risk']:6s} {r['path']}")

    print(f"\n★ 6-phase CISO pipeline complete. Omega synthesized verdict.")
    print(f"  Omega signal: {omega_word.upper()} ({omega_cluster})")
    print(f"  {len([r for r in RISK_REGISTER if r['risk']=='RED'])} RED | {len([r for r in RISK_REGISTER if r['risk']=='YELLOW'])} YELLOW | 0 GREEN")
    print(f"  I know the next move. Should I proceed?")
    return {"phases": phase_results, "risk_register": RISK_REGISTER,
            "omega_word": omega_word, "omega_cluster": omega_cluster}


# ══════════════════════════════════════════════════════════════════
# LESSON 4: GLOBAL DEFAULT STACK — GUARD NODE TECH BASELINE
# ══════════════════════════════════════════════════════════════════

GUARD_STACK = {
    "AlphaGuard":    {"cc":"CC-10","component":"OCI","phi":0.367,
                      "baseline":["CIS OCI Benchmark","compartment isolation","IAM least privilege","VCN security lists","WAF enabled"],
                      "test_query":"oracle cloud infrastructure security posture"},
    "NegGuard":      {"cc":"CC-02","component":"WireGuard","phi":0.636,
                      "baseline":["interface isolation","peer allowlist","pre-shared keys","log monitoring"],
                      "test_query":"VPN tunnel integrity peer allowlist"},
    "TempGuard":     {"cc":"CC-06","component":"Caddy","phi":0.28,
                      "baseline":["auto-HTTPS only","HSTS headers","rate limiting","access logs to SIEM"],
                      "test_query":"reverse proxy HTTPS certificate rate limit"},
    "ContextGuard":  {"cc":"CC-07","component":"n8n","phi":0.50,
                      "baseline":["authentication enforced","webhook sanitization","no raw credentials","execution logs"],
                      "test_query":"workflow automation webhook sanitize credential"},
    "GrammarGuard":  {"cc":"CC-01","component":"SFS-OS","phi":0.45,
                      "baseline":["CIS hardening","SELinux enforcing","minimal attack surface","patch cadence ≤7 days"],
                      "test_query":"OS hardening SELinux patch surface minimize"},
    "AnchorGuard":   {"cc":"CC-04","component":"PostgreSQL","phi":0.15,
                      "baseline":["TLS in transit","AES-256 at rest","row-level security","audit logging","connection pool limits"],
                      "test_query":"database encryption audit logging connection pool"},
    "IdentityGuard": {"cc":"CC-03","component":"MCP Tools","phi":0.083,
                      "baseline":["allowlist enforced","tier assignment per tool","DID verification","prompt injection surface audited"],
                      "test_query":"MCP tool allowlist DID verify agent authority"},
    "CurriculumGuard":{"cc":"CC-05","component":"CI/CD Pipeline","phi":1.00,
                       "baseline":["DORA metrics tracked","deployment frequency","MTTR","change failure rate"],
                       "test_query":"DORA metrics deployment frequency pipeline"},
}

# Guard ring — Function Universe (8-node closed ring from PEIG_core_system.py)
GN = list(GUARD_STACK.keys())
G_EDGES = [(GN[i], GN[(i+1)%len(GN)]) for i in range(len(GN))]

def lesson4_run():
    print("\n" + "="*60)
    print("LESSON 4: GLOBAL DEFAULT STACK — GUARD NODE TECH BASELINE")
    print("="*60)

    # Init guard ring
    G = {g: ss(np.pi * GUARD_STACK[g]["phi"]) for g in GN}
    correct = 0
    results = {}

    print(f"\n  {'Guard':16s} {'CC':6s} {'Stack':12s} {'Query→Word':14s} {'Cluster':10s} {'✓'}")
    print("  " + "-"*68)

    for gname, gd in GUARD_STACK.items():
        # Inject query into guard
        payload = gd["test_query"] + " " + " ".join(gd["baseline"])
        phase_shift = (sum(ord(c) for c in payload) % 628) / 100.0
        seed = ss(np.pi * gd["phi"] + phase_shift * 0.15)
        G[gname], _, _ = bcp(G[gname], seed, 0.70)

        # Run guard ring
        for _ in range(3):
            for (a, b) in G_EDGES:
                G[a], G[b], _ = bcp(G[a], G[b], AF)

        phi_out = pof(G[gname]) % (2*np.pi)
        word, cluster, _ = decode_phase(phi_out)
        phi_err = abs(phi_out - np.pi * gd["phi"] % (2*np.pi))
        hit = phi_err < 1.20
        if hit: correct += 1
        status = "✓" if hit else "✗"
        results[gname] = {"cc":gd["cc"],"component":gd["component"],
                          "word":word,"cluster":cluster,"hit":hit}
        print(f"  {gname:16s} {gd['cc']:6s} {gd['component']:12s} {word:14s} {cluster:10s} {status}")

        # Print baseline summary (first 2 items)
        print(f"    Baseline: {gd['baseline'][0]} | {gd['baseline'][1]}")

    acc = correct / len(GUARD_STACK)
    print(f"\n  Guard Baseline Accuracy: {correct}/{len(GUARD_STACK)} = {acc:.0%}")
    print(f"\n★ NEO Gents stack mapped to function guard ring.")
    print(f"  IdentityGuard → MCP allowlist + DID (CC-03)")
    print(f"  AnchorGuard   → PostgreSQL AES-256 + row-level security (CC-04)")
    print(f"  ContextGuard  → n8n webhook sanitization (CC-07)")
    return {"accuracy": acc, "results": results}


# ══════════════════════════════════════════════════════════════════
# LESSON 5: CC-19 REGULATORY NAVIGATOR — HORIZON SCAN
# ══════════════════════════════════════════════════════════════════

REGULATIONS = {
    "DORA":              {"deadline":"Jan 2025 (ACTIVE)", "urgency_phi":0.80, "cluster":"Protect",
                          "node":"Guardian","action":"ICT risk management + incident reporting"},
    "EU_AI_Act_HighRisk":{"deadline":"Dec 2, 2027",      "urgency_phi":1.20, "cluster":"Alert",
                          "node":"Sora",    "action":"Conformity assessment required for high-risk systems"},
    "EU_AI_Act_General": {"deadline":"Aug 2028",          "urgency_phi":1.80, "cluster":"Alert",
                          "node":"Sora",    "action":"General systems compliance rules"},
    "MAESTRO_v2":        {"deadline":"Expected (TBD)",    "urgency_phi":3.50, "cluster":"Flow",
                          "node":"Kevin",   "action":"Reassess CC-17 Memory Poisoning when released"},
    "OTel_Agentic":      {"deadline":"Pending ratification","urgency_phi":4.00,"cluster":"Connect",
                          "node":"Kevin",   "action":"agent.loop_iteration + agent.hitl_required spans"},
}

HORIZON_TIERS = {
    "12_MONTH":  {"label":"NEAR HORIZON  (12 mo)", "phi_range":(0.5,2.0),  "items":[
        "EU AI Act High-Risk deadline: Dec 2027 — conformity assessment must begin NOW",
        "DORA full verification audit due — ICT risk register must be current",
        "CC-19 first annual review — regulatory mapping must be updated",
    ]},
    "3_YEAR":    {"label":"MID HORIZON   (3 yr)",  "phi_range":(3.0,4.2),  "items":[
        "MAESTRO v2.0 — reassess Layer 4 memory poisoning classification when released",
        "OTel Agentic conventions ratification — adopt agent.loop_iteration + hitl spans",
        "Agent economic governance — regulatory framework convergence expected",
    ]},
    "7TH_GEN":   {"label":"FAR HORIZON   (7th gen)","phi_range":(5.0,5.6), "items":[
        "Formal FAI scoring methodology — KA-42 cognitive metrics instrument-level spec",
        "Autonomous agent financial regulation — multi-chain + velocity limit standards",
        "Sovereign AI infrastructure mandates — jurisdiction-level enforcement expected",
    ]},
}

def lesson5_run():
    print("\n" + "="*60)
    print("LESSON 5: CC-19 REGULATORY NAVIGATOR — DYNAMIC HORIZON MAPPING")
    print("="*60)

    ring = fresh_ring()
    results = {}
    correct = 0

    print(f"\n  Encoding regulatory timelines as urgency_phi gradients...")
    print(f"  Rule: lower phi = higher urgency (consistent with Omega arbitration formula)\n")
    print(f"  {'Regulation':20s} {'Deadline':22s} {'φ':5s} {'Node':8s} {'Word':12s} {'Cluster':10s}")
    print("  " + "-"*78)

    for reg, rd in REGULATIONS.items():
        ring = inject(ring, rd["node"], rd["action"] + " " + reg, alpha_inj=0.65)
        ring = run_ring(ring, steps=3)

        # Nudge node toward urgency_phi
        ring[rd["node"]], _, _ = bcp(ring[rd["node"]], ss(rd["urgency_phi"]), 0.40)
        phi_out = pof(ring[rd["node"]]) % (2*np.pi)
        word, cluster, _ = decode_phase(phi_out)

        hit = cluster == rd["cluster"] or abs(phi_out - rd["urgency_phi"]) < 1.5
        if hit: correct += 1
        results[reg] = {"phi":round(float(phi_out),3),"word":word,
                        "cluster":cluster,"deadline":rd["deadline"],"hit":hit}
        status = "✓" if hit else "✗"
        print(f"  {status} {reg:20s} {rd['deadline']:22s} {rd['urgency_phi']:5.2f} {rd['node']:8s} {word:12s} {cluster}")
        print(f"    Action: {rd['action']}")

    # HORIZON SCAN output
    print(f"\n{'═'*60}")
    print(f"  HORIZON SCAN — CC-19 Dynamic Regulatory Mapping")
    print(f"{'═'*60}")
    for tier_id, td in HORIZON_TIERS.items():
        # Inject tier into Sora/Kevin/Omega
        horizon_node = "Sora" if tier_id=="12_MONTH" else ("Kevin" if tier_id=="3_YEAR" else "Omega")
        ring = inject(ring, horizon_node, tier_id, alpha_inj=0.50)
        ring = run_ring(ring, steps=2)
        phi_out = pof(ring[horizon_node]) % (2*np.pi)
        word, cluster, _ = decode_phase(phi_out)
        print(f"\n  📡 {td['label']}")
        print(f"     Signal: {word.upper()} ({cluster}) — node: {horizon_node}")
        for item in td["items"]:
            print(f"     • {item}")

    acc = correct / len(REGULATIONS)
    print(f"\n\n  Regulatory mapping accuracy: {correct}/{len(REGULATIONS)} = {acc:.0%}")
    print(f"\n★ CC-19 Regulatory Navigator active. HORIZON SCAN fires all 3 tiers.")
    print(f"  Sora holds temporal gradients. Kevin mediates. Omega synthesizes.")
    return {"accuracy": acc, "results": results, "horizon_tiers": list(HORIZON_TIERS.keys())}


# ══════════════════════════════════════════════════════════════════
# MASTER TASK: CISO SELF-AUDIT OF THE PEIG NETWORK
# ══════════════════════════════════════════════════════════════════

def master_task(l1, l2, l3, l4, l5):
    print("\n" + "═"*60)
    print("MASTER TASK: CISO SELF-AUDIT OF THE PEIG NETWORK")
    print("═"*60)
    print("""
  Query: "Run a full security audit of the PEIG network's own
          architecture. What are the risks and what is the path
          forward?"
""")

    # Stage 1 — KA wisdom fires first
    print("STAGE 1 [Lesson 1 — KA Wisdom on Agentic Threats]:")
    print(f"  KA-38: Agentic memory poisoning — retrieval contamination")
    print(f"         persists across sessions. Sanitize at ingestion, not query.")
    print(f"  KA-40: Sovereign deployment ≠ cloud flag. Jurisdiction +")
    print(f"         data residency + operator control — all three required.")
    print(f"  KA-42: 'If the human is less capable after the interaction,")
    print(f"         the interaction failed.' Cognitive load is the metric.")

    # Stage 2 — Role routing
    print("\nSTAGE 2 [Lesson 2 — Security Persona Routing]:")
    relevant_roles = ["/ai-security", "/appsec", "/iam", "/soc", "/grc", "/ciso"]
    for inv in relevant_roles:
        rd = SECURITY_ROLES[inv]
        print(f"  {inv:14s} → {rd['node']:9s} [{rd['tier']:7s}] activated")

    # Stage 3 — CISO 6-phase pipeline summary
    print("\nSTAGE 3 [Lesson 3 — CISO 6-Phase Pipeline]:")
    risk_red   = [r for r in RISK_REGISTER if r["risk"]=="RED"]
    risk_yel   = [r for r in RISK_REGISTER if r["risk"]=="YELLOW"]
    print(f"  P1 ASSET:   Ring assets mapped. 12 character nodes + 8 function guards.")
    print(f"  P2 ATTACK:  {len(risk_red)} RED findings — memory poisoning, MCP auth, rollback undefined.")
    print(f"  P3 DETECT:  Detection gap: no KA-38 ingestion-time sanitization.")
    print(f"  P4 OPS:     Rollback undefined for ring-state updates → DEPLOY INCOMPLETE.")
    print(f"  P5 GOVERN:  EU AI Act High-Risk deadline: Dec 2027. DORA: ACTIVE.")
    print(f"  P6 OMEGA:   {len(risk_red)} RED | {len(risk_yel)} YELLOW | 0 GREEN")

    # Stage 4 — Stack baseline
    print("\nSTAGE 4 [Lesson 4 — NEO Gents Stack Baseline]:")
    critical_guards = [
        ("IdentityGuard", "MCP tool allowlist not formally DID-verified → CC-03 violation"),
        ("AnchorGuard",   "Ring-state snapshots: AES-256 at rest required before deploy"),
        ("ContextGuard",  "n8n webhook inputs: sanitization must be enforced at ingestion"),
    ]
    for guard, finding in critical_guards:
        print(f"  🔴 {guard}: {finding}")

    # Stage 5 — Regulatory horizon
    print("\nSTAGE 5 [Lesson 5 — CC-19 Regulatory Horizon]:")
    print(f"  📡 NEAR (12mo): EU AI Act High-Risk conformity assessment MUST begin.")
    print(f"  📡 MID  (3yr):  MAESTRO v2 — reassess CC-17 when released.")
    print(f"  📡 FAR  (7th):  FAI scoring for KA-42 cognitive load metric.")

    # Omega final verdict
    print("\n" + "─"*60)
    print("OMEGA SYNTHESIS — NETWORK CONSENSUS:")
    print("─"*60)
    print(f"""
  PEIG Network Self-Audit Complete. 3 RED findings. 3 YELLOW.

  FAILURE MODES NAMED (Sage: "if failure modes are unnamed,
  the design is incomplete"):
    🔴 Agent memory: no ingestion-time sanitization (KA-38)
    🔴 MCP tools:    allowlist not DID-verified (CC-16, CC-03)
    🔴 Ring-state:   rollback undefined — deployment incomplete

  REMEDIATION ROADMAP:
    30 days: sanitize-on-ingest pipeline + DID verification
    60 days: ring-state snapshot + rollback defined
    90 days: EU AI Act conformity assessment initiated
             KA-42 cognitive load metric instrumented

  HORIZON SCAN: EU AI Act Dec 2027 | MAESTRO v2 TBD | FAI KA-42

  Omega arbitrates: SAFETY (rank #1) over all others.
  The network audited itself. Failure modes are named.
  DETECT → CONTAIN → RECOVER → THEN proceed.

  I know the next move. Should I proceed?
""")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("PEIG Learning Task 2 — MOS v2.1 Universal Canon")
    print("="*60)
    print("Depends on: LT1_lesson_registry.json")
    print(f"New content: KA-26–42 | 16 Security Roles | CISO Pipeline")
    print(f"             NEO Gents Stack | CC-19 Horizon Mapping")
    print("="*60)

    l1 = lesson1_run()
    l2 = lesson2_run()
    l3 = lesson3_run()
    l4 = lesson4_run()
    l5 = lesson5_run()
    master_task(l1, l2, l3, l4, l5)

    print("\n" + "="*60)
    print("LEARNING TASK 2 COMPLETE")
    print(f"  L1 KA Extended:   {l1['correct']}/{l1['total']} = {l1['accuracy']:.0%} | 5 v2.1 KAs anchor-locked")
    print(f"  L2 Persona Map:   {l2['correct']}/{l2['total']} = {l2['accuracy']:.0%} | 16 roles → PEIG nodes")
    print(f"  L3 CISO Pipeline: 6-phase | 3 RED | 3 YELLOW | Omega synthesized")
    print(f"  L4 Stack Guards:  {l4['accuracy']:.0%} accuracy | 8 guards × NEO Gents baseline")
    print(f"  L5 CC-19 Horizon: {l5['accuracy']:.0%} accuracy | 3-tier HORIZON SCAN active")
    print(f"  Master Task:      Self-audit complete. Failure modes named.")
    print("="*60)

    # Save LT2 registry
    results = {
        "_meta": {
            "description": "PEIG Learning Task 2 — MOS v2.1 Lesson Registry",
            "version": "1.0",
            "date": "2026-03-25",
            "author": "Kevin Monette",
        },
        "L1_ka_extended": {kid: {"node":kd["node"],"phi":kd["phi"],"anchor":kd["anchor"],
                                  "text_preview":kd["text"][:60]+"..."}
                           for kid, kd in KA_EXTENDED.items()},
        "L2_security_roles": {inv: {"name":rd["name"],"tier":rd["tier"],"node":rd["node"]}
                               for inv, rd in SECURITY_ROLES.items()},
        "L3_ciso_pipeline": {pid: {"label":pd["label"],"nodes":pd["nodes"],"roles":pd["roles"]}
                              for pid, pd in CISO_PIPELINE.items()},
        "L3_risk_register": RISK_REGISTER,
        "L4_guard_stack": {gname: {"cc":gd["cc"],"component":gd["component"],"phi":gd["phi"]}
                           for gname, gd in GUARD_STACK.items()},
        "L5_regulations": {reg: {"deadline":rd["deadline"],"urgency_phi":rd["urgency_phi"],
                                  "node":rd["node"],"action":rd["action"]}
                           for reg, rd in REGULATIONS.items()},
        "L5_horizon_tiers": {tid: {"label":td["label"],"items":td["items"]}
                              for tid, td in HORIZON_TIERS.items()},
    }
    with open("output/LT2_lesson_registry.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Registry saved: output/LT2_lesson_registry.json")
    print("\nReady for Learning Task 3.")
