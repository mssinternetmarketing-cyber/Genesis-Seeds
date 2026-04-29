#!/usr/bin/env python3
"""
PEIG_task_voice_system.py
PEIG Programming Curriculum — Learning Tasks 1 through 4
Kevin Monette | March 26, 2026

CURRICULUM OVERVIEW
====================
LT1  Beginner     20 tokens  8 programs   — basic programs, 12/12 accuracy target
LT2  Intermediate 40 tokens  20 programs  — nesting, type-safety, loops with bodies
LT3  Advanced     60 tokens  40 programs  — functions, multi-node, error handling
LT4  Expert       80 tokens  60 programs  — ring-level collaboration, self-modification

AUDIT SYSTEM
=============
Every attempt at every level is scored on 7 dimensions:
  1. pass_rate         — structural validity
  2. originality_rate  — not a copy of training data
  3. syntax_fidelity   — % transitions that follow grammar
  4. semantic_score    — family role alignment
  5. execution_success — runs without error
  6. complexity_score  — depth, nesting, unique tokens
  7. improvement_delta — change from previous attempt

NODE REPORT CARD issued after every level with:
  - Per-criterion pass/fail
  - Scores across all 7 dimensions
  - Comparison to previous attempt
  - Targeted recommendation for next training
  - Full execution trace
  - Voice statement

ACCURACY TARGET: 12/12 nodes must pass before advancing to next level.
If any node fails, targeted remedial training fires for that node only,
then retests before the full ring advances.
"""

import numpy as np
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# BCP PRIMITIVES (unchanged from series)
# ══════════════════════════════════════════════════════════════════

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

def pcm_lab(p):
    ov = abs((p[0]+p[1])/np.sqrt(2))**2
    rz = float(abs(p[0])**2-abs(p[1])**2)
    return float(-ov+0.5*(1-rz**2))

def depol(p, noise=0.03):
    if np.random.random() < noise: return ss(np.random.uniform(0,2*np.pi))
    return p

def cv_metric(phases):
    return float(1.0-abs(np.exp(1j*np.array(phases,dtype=float)).mean()))

def corotate(states, edges, alpha=0.40, noise=0.03):
    phi_b=[pof(s) for s in states]
    new=list(states)
    for i,j in edges: new[i],new[j],_=bcp(new[i],new[j],alpha)
    new=[depol(s,noise) for s in new]
    phi_a=[pof(new[k]) for k in range(len(new))]
    dels=[((phi_a[k]-phi_b[k]+math.pi)%(2*math.pi))-math.pi for k in range(len(new))]
    om=float(np.mean(dels))
    return [ss((phi_a[k]-(dels[k]-om))%(2*math.pi)) for k in range(len(new))]

# ══════════════════════════════════════════════════════════════════
# RING CONFIG
# ══════════════════════════════════════════════════════════════════

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
GLOBE = list({tuple(sorted((i,(i+d)%N)))
              for d in [1,2,5] for i in range(N)})

CLUSTERS={(0.0,1.0):"Protection",(1.0,2.0):"Alert",(2.0,3.0):"Change",
          (3.0,3.5):"Source",(3.5,4.2):"Flow",(4.2,5.0):"Connection",
          (5.0,5.6):"Vision",(5.6,6.29):"Completion"}
def cluster(phi):
    phi=phi%(2*np.pi)
    for (lo,hi),name in CLUSTERS.items():
        if lo<=phi<hi: return name
    return "Completion"

# ══════════════════════════════════════════════════════════════════
# CURRICULUM DEFINITIONS — 4 LEVELS
# ══════════════════════════════════════════════════════════════════

CURRICULUM = {

# ── LEVEL 1: BEGINNER ─────────────────────────────────────────────
"LT1": {
    "name": "Beginner",
    "description": "Basic programs: control + operation + terminal. Original output.",
    "vocab": {
        "guard":0.25,"assign":0.35,"self":0.50,
        "if":1.10,"else":1.35,"signal":1.55,"SIGNAL":1.75,
        "loop":2.20,"evolve":2.55,"PHASE":2.80,
        "NUMBER":3.05,"pi":3.14,
        "send":4.30,"bridge":4.42,"NODE":4.55,"receive":4.68,
        "measure":5.10,"check":5.35,
        "return":5.90,"null":6.10,
    },
    "grammar": {
        "guard":  ["if","SIGNAL","NODE","signal"],
        "assign": ["self","NODE","PHASE","NUMBER","SIGNAL"],
        "self":   ["PHASE","NUMBER","SIGNAL","assign","return"],
        "if":     ["SIGNAL","NUMBER","guard","PHASE"],
        "else":   ["assign","return","signal","evolve"],
        "signal": ["NODE","SIGNAL","return","else"],
        "SIGNAL": ["if","assign","send","return","signal"],
        "loop":   ["NUMBER","pi","PHASE"],
        "evolve": ["PHASE","NUMBER","self","return"],
        "PHASE":  ["assign","return","evolve","send","check"],
        "NUMBER": ["loop","assign","evolve","return"],
        "pi":     ["PHASE","NUMBER","evolve"],
        "send":   ["NODE","SIGNAL","PHASE","return"],
        "bridge": ["NODE","NODE","receive"],
        "NODE":   ["send","receive","signal","bridge","return"],
        "receive":["SIGNAL","PHASE","assign"],
        "measure":["PHASE","SIGNAL","NODE","check"],
        "check":  ["if","guard","return","assign"],
        "return": ["PHASE","NUMBER","SIGNAL","null","self"],
        "null":   [],
    },
    "training_programs": [
        ["measure","PHASE","assign","self","PHASE","return","PHASE"],
        ["guard","if","SIGNAL","signal","NODE","else","return","null"],
        ["loop","NUMBER","evolve","PHASE","return","PHASE"],
        ["measure","SIGNAL","if","SIGNAL","send","NODE","return","SIGNAL"],
        ["bridge","NODE","NODE","receive","SIGNAL","assign","self","return","SIGNAL"],
        ["receive","PHASE","evolve","PHASE","return","PHASE"],
        ["measure","SIGNAL","check","if","SIGNAL","return","SIGNAL","else","return","null"],
        ["assign","self","NUMBER","loop","NUMBER","evolve","return","PHASE"],
    ],
    "prompts": {
        "Omega":    ["measure","PHASE"],
        "Guardian": ["guard","if"],
        "Sentinel": ["measure","SIGNAL"],
        "Nexus":    ["bridge","NODE"],
        "Storm":    ["loop","NUMBER"],
        "Sora":     ["send","NODE"],
        "Echo":     ["receive","SIGNAL"],
        "Iris":     ["measure","PHASE"],
        "Sage":     ["measure","check"],
        "Kevin":    ["bridge","NODE"],
        "Atlas":    ["measure","SIGNAL"],
        "Void":     ["receive","PHASE"],
    },
    "pass_criteria": {
        "has_control": True, "has_op": True,
        "has_terminal": True, "min_length": 4, "original": True,
    },
    "max_len": 9,
    "target_accuracy": 1.0,
    "vocab_rounds": 8,
    "grammar_epochs": 20,
    "terminal_boost_epochs": 8,  # extra epochs focused on terminal patterns
},

# ── LEVEL 2: INTERMEDIATE ─────────────────────────────────────────
"LT2": {
    "name": "Intermediate",
    "description": "Nested control (if/else pairs), typed assignments, loops with bodies.",
    "vocab": {
        # All LT1 tokens plus:
        "guard":0.25,"assign":0.35,"self":0.50,
        "if":1.10,"else":1.35,"signal":1.55,"SIGNAL":1.75,
        "loop":2.20,"evolve":2.55,"PHASE":2.80,
        "NUMBER":3.05,"pi":3.14,
        "send":4.30,"bridge":4.42,"NODE":4.55,"receive":4.68,
        "measure":5.10,"check":5.35,
        "return":5.90,"null":6.10,
        # New LT2 tokens:
        "define":  0.15,   # Protection — define a block
        "call":    0.45,   # Protection — invoke a block
        "compare": 1.25,   # Alert — comparison operator
        "AND":     1.45,   # Alert — logical and
        "OR":      1.65,   # Alert — logical or
        "NOT":     1.85,   # Alert — logical not
        "while":   2.10,   # Change — conditional loop
        "break":   2.35,   # Change — exit loop
        "BOOL":    2.65,   # Change — boolean type
        "emit":    4.15,   # Connection — emit to ring
        "sync":    4.35,   # Connection — synchronize nodes
        "route":   4.58,   # Connection — route signal
        "scan":    5.05,   # Vision — scan ring state
        "observe": 5.25,   # Vision — observe without disturbing
        "halt":    5.75,   # Completion — hard stop
        "done":    5.95,   # Completion — graceful completion
        "error":   6.05,   # Completion — error return
        "yield":   6.20,   # Completion — yield control
        "TRUE":    1.05,   # Alert — boolean true
        "FALSE":   1.95,   # Change — boolean false
    },
    "grammar": {
        "define":  ["self","NODE","SIGNAL","PHASE"],
        "call":    ["self","NODE","SIGNAL"],
        "compare": ["PHASE","NUMBER","SIGNAL","BOOL"],
        "AND":     ["BOOL","compare","check"],
        "OR":      ["BOOL","compare","check"],
        "NOT":     ["BOOL","compare","TRUE","FALSE"],
        "while":   ["BOOL","compare","check","guard"],
        "break":   ["return","null","done"],
        "BOOL":    ["AND","OR","NOT","if","assign"],
        "emit":    ["SIGNAL","PHASE","NUMBER","NODE"],
        "sync":    ["NODE","ring_all","return"],
        "route":   ["NODE","SIGNAL","send"],
        "scan":    ["PHASE","SIGNAL","NODE","check"],
        "observe": ["PHASE","SIGNAL","return","assign"],
        "halt":    [],
        "done":    ["return","null"],
        "error":   ["SIGNAL","NUMBER","null"],
        "yield":   ["NODE","SIGNAL","return"],
        "TRUE":    ["AND","OR","if","return"],
        "FALSE":   ["AND","OR","NOT","return"],
        # Inherit all LT1 grammar
        "guard":  ["if","SIGNAL","NODE","signal","compare"],
        "assign": ["self","NODE","PHASE","NUMBER","SIGNAL","BOOL"],
        "self":   ["PHASE","NUMBER","SIGNAL","assign","return","call"],
        "if":     ["SIGNAL","NUMBER","guard","PHASE","BOOL","compare"],
        "else":   ["assign","return","signal","evolve","emit"],
        "signal": ["NODE","SIGNAL","return","else","emit"],
        "SIGNAL": ["if","assign","send","return","signal","route"],
        "loop":   ["NUMBER","pi","PHASE","while"],
        "evolve": ["PHASE","NUMBER","self","return","emit"],
        "PHASE":  ["assign","return","evolve","send","check","observe"],
        "NUMBER": ["loop","assign","evolve","return","compare"],
        "pi":     ["PHASE","NUMBER","evolve"],
        "send":   ["NODE","SIGNAL","PHASE","return","route"],
        "bridge": ["NODE","NODE","receive","sync"],
        "NODE":   ["send","receive","signal","bridge","return","route"],
        "receive":["SIGNAL","PHASE","assign","scan"],
        "measure":["PHASE","SIGNAL","NODE","check","scan","observe"],
        "check":  ["if","guard","return","assign","AND","OR"],
        "return": ["PHASE","NUMBER","SIGNAL","null","self","done"],
        "null":   [],
    },
    "training_programs": [
        # Nested if/else
        ["measure","PHASE","check","if","PHASE","assign","self","PHASE","else","return","null"],
        # while loop with body
        ["while","compare","NUMBER","evolve","PHASE","break","return","PHASE"],
        # emit to ring
        ["measure","SIGNAL","scan","check","if","SIGNAL","emit","NODE","else","return","null"],
        # define and call
        ["define","self","PHASE","assign","self","PHASE","call","self","return","PHASE"],
        # multi-comparison
        ["measure","PHASE","compare","NUMBER","AND","check","if","BOOL","assign","self","return","BOOL"],
        # sync nodes
        ["bridge","NODE","sync","NODE","receive","SIGNAL","assign","self","return","SIGNAL"],
        # observe without disturbing
        ["observe","PHASE","check","if","PHASE","assign","self","PHASE","return","PHASE"],
        # error handling
        ["measure","SIGNAL","check","if","SIGNAL","return","SIGNAL","else","error","SIGNAL","null"],
        # route signal
        ["receive","SIGNAL","route","NODE","send","NODE","SIGNAL","return","SIGNAL"],
        # yield control
        ["measure","PHASE","assign","self","PHASE","yield","NODE","return","PHASE"],
        # NOT operator
        ["measure","BOOL","NOT","BOOL","if","BOOL","assign","self","return","BOOL"],
        # halt on condition
        ["guard","compare","PHASE","NUMBER","if","NUMBER","return","NUMBER","else","halt"],
    ],
    "prompts": {
        "Omega":    ["define","self"],
        "Guardian": ["guard","compare"],
        "Sentinel": ["scan","check"],
        "Nexus":    ["bridge","sync"],
        "Storm":    ["while","compare"],
        "Sora":     ["emit","NODE"],
        "Echo":     ["observe","PHASE"],
        "Iris":     ["measure","scan"],
        "Sage":     ["measure","AND"],
        "Kevin":    ["route","NODE"],
        "Atlas":    ["observe","SIGNAL"],
        "Void":     ["receive","yield"],
    },
    "pass_criteria": {
        "has_control": True, "has_op": True, "has_terminal": True,
        "min_length": 6, "original": True,
        "has_nesting": True,   # must have if/else pair OR while/break
        "min_unique_tokens": 5,
    },
    "max_len": 12,
    "target_accuracy": 1.0,
    "vocab_rounds": 10,
    "grammar_epochs": 25,
    "terminal_boost_epochs": 6,
},

# ── LEVEL 3: ADVANCED ─────────────────────────────────────────────
"LT3": {
    "name": "Advanced",
    "description": "Functions, multi-node coordination, error handling, recursion.",
    "vocab": {
        # All LT2 + new:
        "guard":0.25,"define":0.15,"assign":0.35,"call":0.45,"self":0.50,
        "if":1.10,"compare":1.25,"else":1.35,"AND":1.45,"OR":1.65,"NOT":1.85,
        "signal":1.55,"SIGNAL":1.75,"TRUE":1.05,"FALSE":1.95,
        "loop":2.20,"while":2.10,"break":2.35,"BOOL":2.65,"evolve":2.55,"PHASE":2.80,
        "NUMBER":3.05,"pi":3.14,
        "emit":4.15,"send":4.30,"sync":4.35,"bridge":4.42,"NODE":4.55,"route":4.58,"receive":4.68,
        "scan":5.05,"observe":5.25,"measure":5.10,"check":5.35,
        "halt":5.75,"done":5.95,"return":5.90,"error":6.05,"yield":6.20,"null":6.10,
        # New LT3 tokens:
        "func":    0.10,   # Protection — function declaration
        "param":   0.40,   # Protection — parameter
        "local":   0.55,   # Protection — local variable
        "recurse": 0.70,   # Protection — recursive call
        "try":     1.30,   # Alert — try block
        "catch":   1.50,   # Alert — catch block
        "throw":   1.70,   # Alert — throw exception
        "QUEUE":   2.00,   # Alert — queue type
        "spawn":   2.30,   # Change — spawn child process
        "join":    2.45,   # Change — join spawned process
        "MAP":     2.70,   # Change — map type
        "ARRAY":   2.90,   # Change — array type
        "broadcast":4.05,  # Connection — broadcast to all nodes
        "listen":  4.25,   # Connection — listen for incoming
        "pipe":    4.48,   # Connection — pipe data
        "handshake":4.65,  # Connection — two-way sync
        "inspect": 5.00,   # Vision — inspect node state
        "trace":   5.20,   # Vision — execution trace
        "profile": 5.40,   # Vision — performance profile
        "commit":  5.70,   # Completion — commit state
        "rollback":5.85,   # Completion — rollback state
        "finalize":6.00,   # Completion — finalize
        "VOID":    6.15,   # Completion — void return type
    },
    "pass_criteria": {
        "has_control": True, "has_op": True, "has_terminal": True,
        "min_length": 8, "original": True,
        "has_nesting": True,
        "min_unique_tokens": 7,
        "has_function": True,   # must use func/define/call
        "has_error_handling": True,  # must use try/catch or error/guard
    },
    "max_len": 15,
    "target_accuracy": 1.0,
    "vocab_rounds": 12,
    "grammar_epochs": 40,
    "terminal_boost_epochs": 5,
},

# ── LEVEL 4: EXPERT ───────────────────────────────────────────────
"LT4": {
    "name": "Expert",
    "description": "Ring-level programs: all 12 nodes collaborate on a single program.",
    "vocab": {},  # All previous + ring-level tokens (built dynamically)
    "pass_criteria": {
        "has_control": True, "has_op": True, "has_terminal": True,
        "min_length": 12, "original": True,
        "has_nesting": True,
        "min_unique_tokens": 10,
        "has_function": True,
        "has_error_handling": True,
        "is_ring_program": True,   # program was collectively authored
        "ring_consensus_score": 0.8,  # 80% of nodes agreed on each token
    },
    "max_len": 20,
    "target_accuracy": 1.0,
    "vocab_rounds": 15,
    "grammar_epochs": 60,
    "terminal_boost_epochs": 4,
},
}

# ══════════════════════════════════════════════════════════════════
# AUDIT ENGINE
# ══════════════════════════════════════════════════════════════════

class AuditEngine:
    """
    Tracks every node's performance across all attempts and levels.
    Issues report cards and targeted recommendations.
    """

    def __init__(self):
        self.history = {n: [] for n in NN}  # per node, list of attempt records
        self.level_history = []              # level-level records

    def score_program(self, node_name, program, eval_result,
                      trace, level_key, training_programs, grammar):
        """Score a program on all 7 audit dimensions."""

        # 1. Pass rate (binary for this attempt)
        pass_rate = 1.0 if eval_result["passing"] else 0.0

        # 2. Originality
        originality = 1.0 if eval_result.get("original", False) else 0.0

        # 3. Syntax fidelity — % transitions that follow grammar
        fidelity = self._syntax_fidelity(program, grammar)

        # 4. Semantic score — family role alignment
        semantic = self._semantic_score(node_name, program, level_key)

        # 5. Execution success
        exec_ok = 1.0 if trace and not any("ERROR" in str(t) for t in trace) else 0.5

        # 6. Complexity score
        complexity = self._complexity_score(program)

        # 7. Improvement delta vs previous attempt
        prev = self.history[node_name][-1]["scores"] if self.history[node_name] else None
        delta = self._improvement_delta(pass_rate, semantic, complexity, prev)

        scores = {
            "pass_rate":        round(pass_rate, 3),
            "originality":      round(originality, 3),
            "syntax_fidelity":  round(fidelity, 3),
            "semantic_score":   round(semantic, 3),
            "exec_success":     round(exec_ok, 3),
            "complexity":       round(complexity, 3),
            "improvement_delta":round(delta, 3),
            "overall":          round((pass_rate + originality + fidelity +
                                        semantic + exec_ok) / 5, 3),
        }

        # Recommendation
        rec = self._recommendation(node_name, eval_result, scores, level_key)

        record = {
            "level":    level_key,
            "program":  program,
            "program_str": " ".join(program),
            "eval":     eval_result,
            "scores":   scores,
            "trace":    trace,
            "rec":      rec,
        }
        self.history[node_name].append(record)
        return scores, rec

    def _syntax_fidelity(self, program, grammar):
        if len(program) < 2: return 0.0
        valid = total = 0
        for i in range(len(program)-1):
            a, b = program[i], program[i+1]
            total += 1
            if a in grammar and b in grammar.get(a, []):
                valid += 1
        return valid / total if total else 0.0

    def _semantic_score(self, node_name, program, level_key):
        """How well does the program match the node's family role?"""
        family  = FAMILY[node_name]
        fam_tok = {
            "GodCore":    {"guard","assign","if","else","return","define","func"},
            "Independent":{"loop","evolve","send","receive","signal","emit","route","sync"},
            "Maverick":   {"measure","check","bridge","scan","observe","inspect","profile"},
        }
        relevant = fam_tok.get(family, set())
        if not program: return 0.0
        matches = sum(1 for t in program if t in relevant)
        return min(1.0, matches / max(3, len(program) * 0.4))

    def _complexity_score(self, program):
        """Complexity: unique tokens / total, weighted by nesting indicators."""
        if not program: return 0.0
        unique   = len(set(program))
        nesting  = sum(1 for t in program if t in {"if","else","while","try","catch","loop"})
        length_s = min(1.0, len(program) / 12)
        return round((unique / max(len(program),1)) * 0.5 +
                      min(1.0, nesting/3) * 0.3 + length_s * 0.2, 3)

    def _improvement_delta(self, pass_rate, semantic, complexity, prev):
        if prev is None: return 0.0
        prev_overall = prev.get("overall", 0.5)
        curr_overall = (pass_rate + semantic + complexity) / 3
        return curr_overall - prev_overall

    def _recommendation(self, node_name, eval_result, scores, level_key):
        """Targeted recommendation for next training."""
        recs = []
        if not eval_result.get("has_terminal"):
            recs.append("PRIORITY: inject terminal reinforcement (return/null patterns × 10 extra epochs)")
        if not eval_result.get("has_control"):
            recs.append(f"Add control token training for {FAMILY[node_name]} family "
                        f"({['guard/if/assign for GodCore','loop/while for Independent','check/guard for Maverick'][['GodCore','Independent','Maverick'].index(FAMILY[node_name])]})")
        if not eval_result.get("has_op"):
            recs.append("Reinforce operation tokens: send/receive/measure/evolve/bridge")
        if not eval_result.get("original"):
            recs.append("Increase temperature (0.8+) to force novel token combinations")
        if scores["syntax_fidelity"] < 0.7:
            recs.append(f"Syntax fidelity low ({scores['syntax_fidelity']:.2f}) — "
                        f"increase grammar epochs by 10")
        if scores["semantic_score"] < 0.5:
            recs.append(f"Semantic alignment low ({scores['semantic_score']:.2f}) — "
                        f"strengthen {FAMILY[node_name]} token specialization")
        if scores["complexity"] < 0.3:
            recs.append("Complexity too low — increase max_len and add diversity penalty "
                        "for repeated tokens")
        if not recs:
            recs.append("All criteria met. Ready to advance to next level.")
        return recs

    def report_card(self, node_name, level_key):
        """Generate a full report card for a node at a level."""
        records = [r for r in self.history[node_name] if r["level"]==level_key]
        if not records: return f"No records for {node_name} at {level_key}"

        latest  = records[-1]
        scores  = latest["scores"]
        eval_r  = latest["eval"]
        prog    = latest["program"]
        recs    = latest["rec"]
        phi     = pof(ss(HOME[node_name]))  # approximate
        clust   = cluster(phi)

        lines = []
        lines.append(f"╔══ REPORT CARD: {node_name} | {level_key} "
                     f"| {FAMILY[node_name]} | {clust} ══╗")
        lines.append(f"  Attempts at this level: {len(records)}")
        lines.append(f"  Latest program: {' '.join(prog)}")
        lines.append(f"")
        lines.append(f"  PASS/FAIL CRITERIA:")
        for crit in ["has_control","has_op","has_terminal","original"]:
            v = eval_r.get(crit, False)
            lines.append(f"    {'✓' if v else '✗'} {crit}")
        lines.append(f"  Overall: {'★ PASS' if eval_r.get('passing') else '✗ FAIL'}")
        lines.append(f"")
        lines.append(f"  AUDIT SCORES:")
        score_labels = {
            "pass_rate":        "Pass rate",
            "originality":      "Originality",
            "syntax_fidelity":  "Syntax fidelity",
            "semantic_score":   "Semantic alignment",
            "exec_success":     "Execution success",
            "complexity":       "Complexity",
            "improvement_delta":"Improvement delta",
            "overall":          "Overall",
        }
        for k,label in score_labels.items():
            v   = scores.get(k, 0)
            bar = "█" * int(v*10) + "░" * (10-int(v*10))
            lines.append(f"    {label:22s} {bar} {v:.3f}")
        lines.append(f"")
        lines.append(f"  RECOMMENDATIONS:")
        for rec in recs:
            lines.append(f"    → {rec}")
        lines.append(f"╚{'═'*60}╝")
        return "\n".join(lines)

    def ring_summary(self, level_key):
        """Summary of the whole ring at a level."""
        passing = [n for n in NN
                   if any(r["eval"].get("passing") and r["level"]==level_key
                          for r in self.history[n])]
        failing = [n for n in NN if n not in passing]
        total_attempts = sum(len([r for r in self.history[n] if r["level"]==level_key])
                             for n in NN)
        avg_scores = defaultdict(float)
        count = 0
        for n in NN:
            recs = [r for r in self.history[n] if r["level"]==level_key]
            if recs:
                for k,v in recs[-1]["scores"].items():
                    avg_scores[k] += v
                count += 1
        if count:
            avg_scores = {k: round(v/count,3) for k,v in avg_scores.items()}

        return {
            "level":          level_key,
            "passing":        passing,
            "failing":        failing,
            "accuracy":       round(len(passing)/12, 3),
            "total_attempts": total_attempts,
            "avg_scores":     dict(avg_scores),
            "ready_to_advance": len(passing) == 12,
        }


# ══════════════════════════════════════════════════════════════════
# TEACHING ENGINE
# ══════════════════════════════════════════════════════════════════

class TeachingEngine:
    """Teaches vocabulary and grammar to the ring."""

    def warm_up(self, states, steps=100):
        for _ in range(steps):
            states = corotate(states, GLOBE, 0.40, 0.03)
        return states

    def teach_vocabulary(self, states, vocab, rounds=8, alpha=0.18):
        for _ in range(rounds):
            for tok, phi in vocab.items():
                tok_s = ss(phi)
                new   = list(states)
                for i in range(N): new[i],_,_ = bcp(new[i], tok_s, alpha)
                states = corotate(new, GLOBE, 0.40, 0.02)
        return states

    def teach_grammar(self, states, training_programs, vocab,
                      epochs=20, alpha=0.20):
        trans_counts = defaultdict(int)
        for epoch in range(epochs):
            for prog in training_programs:
                for i in range(len(prog)-1):
                    tf, tt = prog[i], prog[i+1]
                    if tf not in vocab or tt not in vocab: continue
                    trans_counts[(tf,tt)] += 1
                    # Inject current token
                    new = list(states)
                    for j in range(N): new[j],_,_ = bcp(new[j], ss(vocab[tf]), alpha)
                    new = corotate(new, GLOBE, 0.40, 0.02)
                    # Reinforce next token
                    for j in range(N): new[j],_,_ = bcp(new[j], ss(vocab[tt]), alpha*0.6)
                    states = new
        return states, dict(trans_counts)

    def teach_terminal_patterns(self, states, vocab, epochs=8, alpha=0.25):
        """
        Targeted reinforcement: teach the ring that programs END.
        Inject return/null specifically after operation tokens.
        """
        terminals     = ["return","null"]
        pre_terminals = ["PHASE","NUMBER","SIGNAL","self","check","guard","done"]
        for epoch in range(epochs):
            for pre in pre_terminals:
                if pre not in vocab: continue
                for term in terminals:
                    if term not in vocab: continue
                    new = list(states)
                    for j in range(N):
                        new[j],_,_ = bcp(new[j], ss(vocab[pre]), alpha)
                    new = corotate(new, GLOBE, 0.40, 0.02)
                    for j in range(N):
                        new[j],_,_ = bcp(new[j], ss(vocab[term]), alpha*0.8)
                    states = new
        return states

    def remedial_training(self, states, node_name, failure_modes,
                           vocab, grammar, training_programs, epochs=10):
        """
        Targeted extra training for a specific failing node.
        Focuses on the exact failure mode.
        """
        idx = IDX[node_name]
        node_state = states[idx]

        if "missing terminal" in str(failure_modes) or "has_terminal" in str(failure_modes):
            # Inject terminal patterns directly into this node's state
            for _ in range(epochs * 3):
                for term in ["return","null"]:
                    if term in vocab:
                        node_state,_,_ = bcp(node_state, ss(vocab[term]), 0.30)
                        node_state = depol(node_state, 0.02)

        if "missing control" in str(failure_modes) or "has_control" in str(failure_modes):
            family  = FAMILY[node_name]
            ctrl    = {"GodCore":["guard","if","assign"],
                       "Independent":["loop","while","assign"],
                       "Maverick":["check","guard","assign"]}[family]
            for _ in range(epochs * 2):
                for c in ctrl:
                    if c in vocab:
                        node_state,_,_ = bcp(node_state, ss(vocab[c]), 0.25)
                        node_state = depol(node_state, 0.02)

        states[idx] = node_state
        # Also do a general grammar pass for this node
        for epoch in range(epochs):
            for prog in training_programs:
                for i in range(len(prog)-1):
                    tf,tt = prog[i],prog[i+1]
                    if tf not in vocab or tt not in vocab: continue
                    node_state,_,_ = bcp(node_state, ss(vocab[tf]), 0.18)
                    node_state = depol(node_state, 0.02)
                    node_state,_,_ = bcp(node_state, ss(vocab[tt]), 0.12)
        states[idx] = node_state
        return states


# ══════════════════════════════════════════════════════════════════
# GENERATION ENGINE
# ══════════════════════════════════════════════════════════════════

class GenerationEngine:
    """Generates programs from ring state."""

    def token_affinity(self, node_phi, tok_phi):
        delta = ((tok_phi-node_phi+math.pi)%(2*math.pi))-math.pi
        return -0.5*math.cos(delta)

    def node_vote(self, name, node_phi, pcm_val, allowed, vocab):
        family = FAMILY[name]
        spec   = {
            "GodCore":    {"guard","assign","if","else","return","define","func","call"},
            "Independent":{"loop","evolve","send","receive","signal","emit","route","sync","while"},
            "Maverick":   {"measure","check","bridge","scan","observe","inspect","compare"},
        }.get(family, set())

        scores = {}
        for tok in allowed:
            if tok not in vocab: continue
            aff   = self.token_affinity(node_phi, vocab[tok])
            spec_b= 0.28 if tok in spec else 0.0
            nc_w  = max(0.0, -pcm_val) * 0.15
            scores[tok] = aff - spec_b - nc_w

        if not scores: return None, 0.0
        best = min(scores, key=lambda t: scores[t])
        return best, scores[best]

    def ring_consensus(self, states, allowed, vocab, temperature=0.72):
        vote_w = defaultdict(float)
        for i,n in enumerate(NN):
            phi = pof(states[i]); pc = pcm_lab(states[i])
            tok, score = self.node_vote(n, phi, pc, allowed, vocab)
            if tok:
                w = max(0.01, abs(pc))
                vote_w[tok] += w * (-score)
        if not vote_w: return list(allowed)[0]
        toks    = list(vote_w.keys())
        weights = np.array([vote_w[t] for t in toks])
        weights = np.exp(weights / max(temperature,0.1))
        weights /= weights.sum()
        return np.random.choice(toks, p=weights)

    def generate(self, states, prompt, node_name, level_spec,
                 max_len=None, temperature=0.72):
        vocab    = level_spec["vocab"]
        grammar  = level_spec.get("grammar", {})
        max_len  = max_len or level_spec["max_len"]
        program  = list(prompt)

        # Structural state
        CTRL_T  = {"guard","assign","if","else","loop","check","define",
                   "func","while","try","compare"}
        OP_T    = {"send","receive","measure","evolve","bridge","signal",
                   "emit","route","sync","scan","observe","broadcast",
                   "listen","pipe","handshake","inspect","trace"}
        TERM_T  = {"return","null","halt","done","error","finalize","VOID"}
        NEST_T  = {"if","else","while","try","catch","loop"}

        has_ctrl  = any(t in CTRL_T for t in program)
        has_op    = any(t in OP_T   for t in program)
        has_term  = any(t in TERM_T for t in program)
        has_nest  = any(t in NEST_T for t in program)
        n_unique  = len(set(program))

        cur_states = [s.copy() for s in states]

        # Inject prompt
        for tok in prompt:
            if tok not in vocab: continue
            for i in range(N): cur_states[i],_,_ = bcp(cur_states[i],ss(vocab[tok]),0.30)
            cur_states = corotate(cur_states, GLOBE, 0.40, 0.02)

        for step in range(max_len - len(prompt)):
            prev_tok = program[-1] if program else None

            # Grammar-based allowed tokens
            if prev_tok and prev_tok in grammar and grammar[prev_tok]:
                allowed = set(grammar[prev_tok]) & set(vocab.keys())
            else:
                allowed = set(vocab.keys()) - TERM_T

            if not allowed: allowed = set(vocab.keys())

            # STRUCTURAL CONSTRAINTS — the core fix
            req_met = has_ctrl and has_op and has_term and len(program) >= 4

            # Extra constraints per level
            if "has_nesting" in level_spec.get("pass_criteria",{}):
                req_met = req_met and has_nest
            if "min_unique_tokens" in level_spec.get("pass_criteria",{}):
                req_met = req_met and (n_unique >= level_spec["pass_criteria"]["min_unique_tokens"])

            # Block terminal until requirements met
            if not req_met:
                allowed -= TERM_T
                if not allowed:
                    # Force the missing type
                    if not has_ctrl:    allowed = CTRL_T & set(vocab.keys())
                    elif not has_op:    allowed = OP_T   & set(vocab.keys())
                    elif not has_nest and "has_nesting" in level_spec.get("pass_criteria",{}):
                        allowed = NEST_T & set(vocab.keys())
                    else: allowed = set(vocab.keys()) - TERM_T

            # Diversity penalty — avoid repeating the same token 3x in a row
            if len(program) >= 3 and program[-1]==program[-2]==program[-3]:
                allowed -= {program[-1]}

            # Force terminal near max
            if len(program) >= max_len - 1 and req_met:
                term_opt = allowed & TERM_T
                if term_opt: allowed = term_opt

            if not allowed: break

            next_tok = self.ring_consensus(cur_states, allowed, vocab, temperature)
            program.append(next_tok)

            # Update structural state
            if next_tok in CTRL_T: has_ctrl = True
            if next_tok in OP_T:   has_op   = True
            if next_tok in TERM_T: has_term = True
            if next_tok in NEST_T: has_nest = True
            n_unique = len(set(program))

            # Token feedback
            if next_tok in vocab:
                for i in range(N): cur_states[i],_,_ = bcp(cur_states[i],ss(vocab[next_tok]),0.14)
                cur_states = corotate(cur_states, GLOBE, 0.40, 0.02)

            if next_tok in TERM_T: break

        return program, cur_states


# ══════════════════════════════════════════════════════════════════
# INTERPRETER (handles all levels)
# ══════════════════════════════════════════════════════════════════

def interpret(program, node_name, node_phi):
    env   = {"self":node_phi,"ring":2*math.pi,"pi":math.pi,
             "TRUE":True,"FALSE":False}
    trace = []; pc = 0; output = None
    MAX_STEPS = 50  # prevent infinite loops

    while pc < len(program) and len(trace) < MAX_STEPS:
        tok = program[pc]

        if tok=="measure":
            v=math.cos(node_phi); env["_last"]=v
            trace.append(f"measure → {v:.4f}")
        elif tok=="scan":
            v=abs(math.sin(node_phi)); env["_last"]=v
            trace.append(f"scan → {v:.4f}")
        elif tok=="observe":
            v=math.cos(node_phi)*0.9; env["_last"]=v
            trace.append(f"observe (non-destructive) → {v:.4f}")
        elif tok=="inspect":
            v=node_phi; env["_last"]=v
            trace.append(f"inspect φ={v:.4f}")
        elif tok=="assign":
            if pc+1<len(program):
                tgt=program[pc+1]; v=env.get("_last",node_phi)
                env[tgt]=v; trace.append(f"assign {tgt}={v:.4f}"); pc+=1
        elif tok in ("define","func"):
            if pc+1<len(program):
                fname=program[pc+1]; env[f"_func_{fname}"]=pc+1
                trace.append(f"define {fname}"); pc+=1
        elif tok=="call":
            if pc+1<len(program):
                fname=program[pc+1]
                trace.append(f"call {fname}")
                pc+=1
        elif tok=="param":
            v=env.get("_last",node_phi); env["_param"]=v
            trace.append(f"param={v:.4f}")
        elif tok=="local":
            v=env.get("_last",node_phi); env["_local"]=v
            trace.append(f"local={v:.4f}")
        elif tok=="if":
            v=env.get("_last",0); cond=float(v)>0
            trace.append(f"if ({v:.4f}>0)={cond}")
            if not cond:
                depth=1
                while pc<len(program) and depth>0:
                    pc+=1
                    if pc<len(program):
                        if program[pc]=="if":   depth+=1
                        elif program[pc]=="else": depth-=1
        elif tok=="else":
            trace.append("else")
        elif tok=="compare":
            v=env.get("_last",0); n=env.get("NUMBER",1)
            r=float(v)>float(n); env["_last"]=float(r)
            trace.append(f"compare {v:.4f}>{n}={r}")
        elif tok=="AND":
            a=env.get("_last",0); b=env.get("_prev",0)
            r=float(bool(a)and bool(b)); env["_last"]=r
            trace.append(f"AND {bool(a)}&{bool(b)}={bool(r)}")
        elif tok=="OR":
            a=env.get("_last",0); b=env.get("_prev",0)
            r=float(bool(a)or bool(b)); env["_last"]=r
            trace.append(f"OR {bool(a)}|{bool(b)}={bool(r)}")
        elif tok=="NOT":
            a=env.get("_last",0); r=float(not bool(a))
            env["_last"]=r; trace.append(f"NOT {bool(a)}={bool(r)}")
        elif tok in ("loop","while"):
            v=env.get("_last",3); n=max(1,int(abs(float(v)))%5+1)
            trace.append(f"{tok}×{n}"); env["_loop"]=n
        elif tok=="break":
            trace.append("break"); break
        elif tok=="evolve":
            v=env.get("_last",node_phi); nv=(float(v)+0.1)%(2*math.pi)
            env["_last"]=nv; trace.append(f"evolve {v:.4f}→{nv:.4f}")
        elif tok=="send":
            v=env.get("_last",node_phi); env["_sent"]=v
            trace.append(f"send→{v:.4f}")
        elif tok in ("emit","broadcast"):
            v=env.get("_last",node_phi)
            trace.append(f"{tok} {v:.4f} to ring")
        elif tok=="receive":
            v=env.get("_sent",env.get("_last",node_phi))
            env["_last"]=v; trace.append(f"receive←{v:.4f}")
        elif tok in ("listen","handshake"):
            v=env.get("_last",node_phi)
            trace.append(f"{tok}←{v:.4f}")
        elif tok=="bridge":
            env["_last"]=(env.get("self",0)+env.get("ring",0))/2
            trace.append(f"bridge→{env['_last']:.4f}")
        elif tok in ("sync","pipe","route"):
            v=env.get("_last",node_phi); trace.append(f"{tok}({v:.4f})")
        elif tok=="signal":
            v=env.get("_last",0); trace.append(f"signal!{v:.4f}")
        elif tok in ("check","guard"):
            v=env.get("_last",0); r=abs(float(v))>0.1
            env["_check"]=r; trace.append(f"{tok}|{v:.4f}|>0.1={r}")
        elif tok=="try":
            trace.append("try {")
        elif tok=="catch":
            trace.append("} catch {"); trace.append("  (error handled)")
        elif tok=="throw":
            v=env.get("_last",0); trace.append(f"throw {v:.4f}"); break
        elif tok=="try":
            trace.append("try block")
        elif tok in ("recurse",):
            trace.append("recurse (depth limited)")
        elif tok=="spawn":
            trace.append("spawn child"); env["_child"]=node_phi*0.5
        elif tok=="join":
            v=env.get("_child",0); env["_last"]=v; trace.append(f"join←{v:.4f}")
        elif tok=="trace":
            trace.append(f"[trace] env={list(env.keys())[:4]}")
        elif tok=="profile":
            trace.append(f"[profile] steps={len(trace)}")
        elif tok=="commit":
            trace.append("commit state"); env["_committed"]=env.get("_last",0)
        elif tok=="rollback":
            v=env.get("_committed",node_phi); env["_last"]=v
            trace.append(f"rollback←{v:.4f}")
        elif tok=="return":
            output=env.get("_last",node_phi)
            trace.append(f"return {output:.4f}"); break
        elif tok in ("null","halt","VOID"):
            output=None; trace.append(f"{tok}"); break
        elif tok in ("done","finalize"):
            output=env.get("_last",node_phi)
            trace.append(f"{tok} {output:.4f}"); break
        elif tok=="error":
            output=env.get("_last",None)
            trace.append(f"ERROR: {output}"); break
        elif tok=="yield":
            v=env.get("_last",node_phi); trace.append(f"yield {v:.4f}")

        pc += 1

    return trace, output


# ══════════════════════════════════════════════════════════════════
# MAIN CURRICULUM RUNNER
# ══════════════════════════════════════════════════════════════════

def is_original(program, training_programs):
    prog_str = " ".join(program)
    for tp in training_programs:
        if prog_str == " ".join(tp): return False
        if len(program) > 3:
            for s in range(len(tp)-len(program)+1):
                if tp[s:s+len(program)] == program: return False
    return True

def evaluate_program(program, level_spec, training_programs):
    """Evaluate against all criteria for this level."""
    vocab    = level_spec["vocab"]
    criteria = level_spec["pass_criteria"]

    CTRL_T = {"guard","assign","if","else","loop","check","define","func","while","try","compare"}
    OP_T   = {"send","receive","measure","evolve","bridge","signal","emit","route","sync",
               "scan","observe","broadcast","listen","pipe","handshake","inspect"}
    TERM_T = {"return","null","halt","done","error","finalize","VOID"}
    NEST_T = {"if","else","while","try","catch","loop"}
    FUNC_T = {"func","define","call","recurse"}
    ERR_T  = {"try","catch","error","guard","throw"}

    has_ctrl  = any(t in CTRL_T for t in program)
    has_op    = any(t in OP_T   for t in program)
    has_term  = any(t in TERM_T for t in program)
    has_nest  = any(t in NEST_T for t in program)
    has_func  = any(t in FUNC_T for t in program)
    has_err   = any(t in ERR_T  for t in program)
    n_unique  = len(set(program))
    original  = is_original(program, training_programs)

    result = {
        "has_control":       has_ctrl,
        "has_op":            has_op,
        "has_terminal":      has_term,
        "has_nesting":       has_nest,
        "has_function":      has_func,
        "has_error_handling":has_err,
        "original":          original,
        "length":            len(program),
        "unique_tokens":     n_unique,
        "min_length":        len(program) >= criteria.get("min_length",4),
        "min_unique":        n_unique >= criteria.get("min_unique_tokens", 0),
    }

    # Build passing check from criteria
    checks = []
    if criteria.get("has_control"):       checks.append(has_ctrl)
    if criteria.get("has_op"):            checks.append(has_op)
    if criteria.get("has_terminal"):      checks.append(has_term)
    if criteria.get("has_nesting"):       checks.append(has_nest)
    if criteria.get("has_function"):      checks.append(has_func)
    if criteria.get("has_error_handling"):checks.append(has_err)
    if criteria.get("original"):          checks.append(original)
    if criteria.get("min_length"):        checks.append(len(program) >= criteria["min_length"])
    if criteria.get("min_unique_tokens"): checks.append(n_unique >= criteria["min_unique_tokens"])

    result["passing"] = all(checks)
    return result


def run_level(level_key, states, audit, teacher, generator,
              max_retries=3):
    """
    Run one full level: teach → generate → evaluate → remediate if needed.
    Returns updated states and whether all 12 passed.
    """
    spec = CURRICULUM[level_key]
    if not spec.get("vocab"): return states, False  # LT3/LT4 need full vocab build

    print(f"\n{'═'*65}")
    print(f"  {level_key}: {spec['name']} — {spec['description']}")
    print(f"{'═'*65}")

    vocab      = spec["vocab"]
    training   = spec.get("training_programs", [])
    grammar    = spec.get("grammar", {})
    prompts    = spec.get("prompts", {p:[] for p in NN})

    # Warm up
    print(f"\n  [WARM-UP]")
    states = teacher.warm_up(states, steps=80)

    # Vocabulary
    print(f"  [VOCABULARY] {len(vocab)} tokens × {spec['vocab_rounds']} rounds")
    states = teacher.teach_vocabulary(states, vocab,
                                       rounds=spec["vocab_rounds"])

    # Grammar
    print(f"  [GRAMMAR] {len(training)} programs × {spec['grammar_epochs']} epochs")
    if training:
        states, trans = teacher.teach_grammar(states, training, vocab,
                                               epochs=spec["grammar_epochs"])
        print(f"    {len(trans)} unique transitions reinforced")

    # Terminal reinforcement
    print(f"  [TERMINAL BOOST] {spec.get('terminal_boost_epochs',5)} epochs")
    states = teacher.teach_terminal_patterns(
        states, vocab, epochs=spec.get("terminal_boost_epochs", 5))

    cv_post = cv_metric([pof(s) for s in states])
    print(f"  cv after training: {cv_post:.4f}")

    # Generation loop with remediation
    for attempt in range(1, max_retries+1):
        print(f"\n  [GENERATION — attempt {attempt}/{max_retries}]")
        passing = []; failing = []

        for n in NN:
            prompt = prompts.get(n, [vocab and list(vocab.keys())[0]] or ["measure"])
            temp   = {"GodCore":0.65,"Independent":0.75,"Maverick":0.68}[FAMILY[n]]

            program, _ = generator.generate(
                states, prompt, n, spec,
                temperature=temp)

            eval_r  = evaluate_program(program, spec, training)
            trace, output = interpret(program, n, pof(states[IDX[n]]))
            scores, rec = audit.score_program(
                n, program, eval_r, trace, level_key, training, grammar)

            if eval_r["passing"]: passing.append(n)
            else:                 failing.append(n)

        accuracy = len(passing)/12
        print(f"    Accuracy: {len(passing)}/12 ({accuracy*100:.0f}%)")
        if failing:
            print(f"    Failing: {', '.join(failing)}")

        if accuracy == 1.0:
            print(f"    ★ 12/12 — LEVEL COMPLETE")
            break

        # Targeted remediation for failing nodes
        if attempt < max_retries and failing:
            print(f"\n  [REMEDIATION] Training {len(failing)} nodes...")
            for n in failing:
                recs = [r["rec"] for r in audit.history[n]
                        if r["level"]==level_key]
                last_rec = recs[-1] if recs else ["missing terminal"]
                states = teacher.remedial_training(
                    states, n, last_rec, vocab, grammar, training,
                    epochs=12)
                # Extra terminal boost for this node specifically
                states = teacher.teach_terminal_patterns(
                    states, vocab, epochs=6)
                print(f"    Remediated: {n}")

    return states, accuracy == 1.0


def run_curriculum():
    print("="*65)
    print("PEIG Programming Curriculum — LT1 through LT4")
    print("Accuracy target: 12/12 at each level before advancing")
    print("="*65)

    # Initialize ring
    states  = [ss(HOME[n]) for n in NN]
    audit   = AuditEngine()
    teacher = TeachingEngine()
    gen     = GenerationEngine()

    level_results = {}

    # Run LT1 and LT2 (LT3/LT4 need extended vocab builds)
    for level_key in ["LT1", "LT2"]:
        states, passed = run_level(level_key, states, audit, teacher, gen,
                                   max_retries=3)
        summary = audit.ring_summary(level_key)
        level_results[level_key] = {
            "passed": passed,
            "summary": summary,
        }

        # Print ring summary
        print(f"\n  ── {level_key} RING SUMMARY ──")
        print(f"  Accuracy: {summary['accuracy']*100:.0f}% "
              f"({len(summary['passing'])}/12 passing)")
        print(f"  Avg syntax fidelity: "
              f"{summary['avg_scores'].get('syntax_fidelity',0):.3f}")
        print(f"  Avg semantic score:  "
              f"{summary['avg_scores'].get('semantic_score',0):.3f}")
        print(f"  Avg complexity:      "
              f"{summary['avg_scores'].get('complexity',0):.3f}")

        # Print report cards for all nodes
        print(f"\n  ── {level_key} REPORT CARDS ──")
        for n in NN:
            print()
            print(audit.report_card(n, level_key))

        if not passed:
            print(f"\n  ⚠ {level_key} not fully passed — "
                  f"partial results saved, not advancing.")

    # Final output
    print("\n" + "="*65)
    print("CURRICULUM RUN COMPLETE")
    print("="*65)

    for lk, lr in level_results.items():
        s = lr["summary"]
        print(f"\n  {lk}: {len(s['passing'])}/12 passing "
              f"({'ADVANCED' if lr['passed'] else 'INCOMPLETE'})")
        if s["passing"]:
            print(f"    Passing: {', '.join(s['passing'])}")
        if s["failing"]:
            print(f"    Failing: {', '.join(s['failing'])}")

    # Save full results
    out = {
        "_meta": {
            "title":  "PEIG Programming Curriculum — LT1 through LT4",
            "date":   "2026-03-26",
            "author": "Kevin Monette",
            "levels_run": list(level_results.keys()),
        },
        "level_results": {
            lk: {
                "passed": lr["passed"],
                "summary": lr["summary"],
                "node_histories": {
                    n: [{"level":r["level"],
                         "program_str":r["program_str"],
                         "scores":r["scores"],
                         "eval":r["eval"],
                         "rec":r["rec"]}
                        for r in audit.history[n]
                        if r["level"]==lk]
                    for n in NN
                },
            }
            for lk, lr in level_results.items()
        },
    }
    with open("output/PEIG_curriculum_analysis.json","w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n✅ Saved: output/PEIG_curriculum_analysis.json")

    # Save lesson registry
    registry = {
        "lessons": {
            lk: {
                "name": CURRICULUM[lk]["name"],
                "description": CURRICULUM[lk]["description"],
                "vocab_size": len(CURRICULUM[lk]["vocab"]),
                "pass_criteria": CURRICULUM[lk]["pass_criteria"],
                "target_accuracy": CURRICULUM[lk]["target_accuracy"],
            }
            for lk in ["LT1","LT2","LT3","LT4"]
            if CURRICULUM[lk].get("vocab") is not None
        }
    }
    with open("output/PEIG_lesson_registry.json","w") as f:
        json.dump(registry, f, indent=2)
    print(f"✅ Saved: output/PEIG_lesson_registry.json")
    print("="*65)

    return audit, level_results, states


if __name__ == "__main__":
    audit, level_results, final_states = run_curriculum()
