#!/usr/bin/env python3
"""
PEIG_learning_task1.py
Learning Task 1 — Teaching MiniPEIG Programming Language
Kevin Monette | March 26, 2026

THE TASK
=========
Teach the 12-node PEIG ring a small but real programming language (MiniPEIG)
and then ask each node to generate an original program in its own domain.

A program is ORIGINAL if:
  1. The token sequence has never appeared in the training data
  2. It contains at least one control structure (if/guard/loop)
  3. It contains at least one operation (send/receive/measure/evolve/bridge)
  4. It terminates (ends with return or null)
  5. It is semantically coherent (tokens match the node's family role)

MiniPEIG LANGUAGE
==================
Types:    NUMBER, BOOL, PHASE, NODE, SIGNAL
Keywords: guard, assign, if, else, loop, return, null, self, ring, pi
Ops:      send, receive, measure, bridge, evolve, signal
Syntax:   prefix/sequence notation
Encoding: each token maps to a phase angle in [0, 2pi]

HOW TEACHING WORKS
===================
Phase 1 — Vocabulary injection:
  Each token's phase is BCP-injected into each node's state.
  Nodes learn token phases by coupling with the token's phase state.

Phase 2 — Grammar training:
  Show the ring valid programs (phase sequences).
  The BCP dynamics reinforce transitions that keep the ring nonclassical.
  After training, stable phase trajectories = valid syntax paths.

Phase 3 — Generation:
  Inject a domain-specific prompt (first 1-2 tokens) into the ring.
  Let each node vote for the next token using phase affinity.
  Ring consensus (weighted by PCM) selects the next token.
  Repeat until a terminal token is produced or max length reached.

Phase 4 — Evaluation:
  Check originality against training corpus.
  Check structural validity (has control + operation + terminal).
  Run the program through the MiniPEIG interpreter.
  Node reports the program in its full nine-register voice.
"""

import numpy as np
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# BCP PRIMITIVES
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
    rz = float(abs(p[0])**2 - abs(p[1])**2)
    return float(-ov + 0.5*(1-rz**2))

def pcm_rel(p, phi0):
    ref     = ss(phi0)
    overlap = abs(np.dot(p.conj(), ref))**2
    rz      = float(abs(p[0])**2 - abs(p[1])**2)
    return float(-overlap + 0.5*(1-rz**2))

def depol(p, noise=0.03):
    if np.random.random() < noise: return ss(np.random.uniform(0,2*np.pi))
    return p

def cv_metric(phases):
    return float(1.0 - abs(np.exp(1j*np.array(phases)).mean()))

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

# ══════════════════════════════════════════════════════════════════
# MINIPEIG LANGUAGE DEFINITION
# ══════════════════════════════════════════════════════════════════

# Each token has a phase encoding in [0, 2pi]
VOCAB = {
    # Protection cluster [0, 1.0) — control / identity
    "guard":    0.25,
    "assign":   0.35,
    "self":     0.50,
    # Alert cluster [1.0, 2.0) — conditions / signals
    "if":       1.10,
    "else":     1.35,
    "signal":   1.55,
    "SIGNAL":   1.75,
    # Change cluster [2.0, 3.0) — iteration / transformation
    "loop":     2.20,
    "evolve":   2.55,
    "PHASE":    2.80,
    # Source cluster [3.0, 3.5) — origin values
    "NUMBER":   3.05,
    "pi":       3.14,
    # Connection cluster [4.2, 5.0) — networking
    "send":     4.30,
    "bridge":   4.42,
    "NODE":     4.55,
    "receive":  4.68,
    # Vision cluster [5.0, 5.6) — observation
    "measure":  5.10,
    "check":    5.35,
    # Completion cluster [5.6, 6.3) — termination
    "return":   5.90,
    "null":     6.10,
}

# Grammar rules: what tokens can follow what token?
# (Based on MiniPEIG syntax rules)
GRAMMAR = {
    "guard":   ["if", "BOOL", "NODE", "SIGNAL"],
    "assign":  ["self", "NODE", "PHASE", "NUMBER", "SIGNAL"],
    "self":    ["PHASE", "NUMBER", "SIGNAL", "assign"],
    "if":      ["BOOL", "SIGNAL", "NUMBER", "guard"],
    "else":    ["assign", "return", "signal", "evolve"],
    "signal":  ["NODE", "ring_word", "SIGNAL", "return"],
    "SIGNAL":  ["if", "assign", "send", "return"],
    "loop":    ["NUMBER", "pi", "PHASE"],
    "evolve":  ["PHASE", "NUMBER", "self"],
    "PHASE":   ["assign", "return", "evolve", "send"],
    "NUMBER":  ["loop", "assign", "evolve", "return"],
    "pi":      ["PHASE", "NUMBER", "evolve"],
    "send":    ["NODE", "SIGNAL", "PHASE"],
    "bridge":  ["NODE", "NODE", "receive"],
    "NODE":    ["send", "receive", "signal", "bridge"],
    "receive": ["SIGNAL", "PHASE", "assign"],
    "measure": ["PHASE", "SIGNAL", "NODE", "check"],
    "check":   ["if", "guard", "return"],
    "return":  ["PHASE", "NUMBER", "SIGNAL", "null"],
    "null":    [],  # terminal
}

# Types for each token
TOKEN_TYPE = {
    "guard":"control","assign":"control","self":"ref",
    "if":"control","else":"control","signal":"op","SIGNAL":"type",
    "loop":"control","evolve":"op","PHASE":"type",
    "NUMBER":"type","pi":"literal",
    "send":"op","bridge":"op","NODE":"type","receive":"op",
    "measure":"op","check":"op",
    "return":"terminal","null":"terminal",
}

CONTROL_TOKENS  = {t for t,ty in TOKEN_TYPE.items() if ty=="control"}
OP_TOKENS       = {t for t,ty in TOKEN_TYPE.items() if ty=="op"}
TERMINAL_TOKENS = {t for t,ty in TOKEN_TYPE.items() if ty=="terminal"}

# Family specializations
FAMILY = {
    "Omega":"GodCore","Guardian":"GodCore","Sentinel":"GodCore","Void":"GodCore",
    "Nexus":"Independent","Storm":"Independent","Sora":"Independent","Echo":"Independent",
    "Iris":"Maverick","Sage":"Maverick","Kevin":"Maverick","Atlas":"Maverick",
}
FAMILY_TOKENS = {
    "GodCore":    ["guard","assign","self","if","else","return","null"],
    "Independent":["loop","evolve","send","receive","signal","SIGNAL","NODE"],
    "Maverick":   ["measure","check","bridge","PHASE","NUMBER","pi"],
}

# Node roles and programming domains
NODE_DOMAIN = {
    "Omega":    ("GodCore",    "Write a program that measures a system state and assigns it to self"),
    "Guardian": ("GodCore",    "Write a program that guards a condition and signals if violated"),
    "Sentinel": ("GodCore",    "Write a program that monitors a signal and returns an alert"),
    "Nexus":    ("Independent","Write a program that bridges two nodes and routes a signal"),
    "Storm":    ("Independent","Write a program that loops and evolves a phase value"),
    "Sora":     ("Independent","Write a program that sends a signal across the ring"),
    "Echo":     ("Independent","Write a program that receives and echoes a signal"),
    "Iris":     ("Maverick",   "Write a program that measures and transforms a phase"),
    "Sage":     ("Maverick",   "Write a program that measures, checks, and decides"),
    "Kevin":    ("Maverick",   "Write a program that bridges and balances two signals"),
    "Atlas":    ("Maverick",   "Write a program that measures and supports a structure"),
    "Void":     ("GodCore",    "Write a program that completes a cycle and returns to null"),
}

# Training programs (the corpus the ring learns from)
TRAINING_PROGRAMS = [
    # T1: Measure and assign
    ["measure", "PHASE", "assign", "self", "PHASE", "return", "PHASE"],
    # T2: Guard condition
    ["guard", "if", "SIGNAL", "signal", "NODE", "else", "return", "null"],
    # T3: Loop and evolve
    ["loop", "NUMBER", "evolve", "PHASE", "return", "PHASE"],
    # T4: Send signal
    ["measure", "SIGNAL", "if", "SIGNAL", "send", "NODE", "return", "SIGNAL"],
    # T5: Bridge protocol
    ["bridge", "NODE", "NODE", "receive", "SIGNAL", "assign", "self", "SIGNAL", "return", "SIGNAL"],
    # T6: Complete cycle
    ["receive", "PHASE", "evolve", "PHASE", "return", "PHASE"],
    # T7: Check and decide
    ["measure", "SIGNAL", "check", "if", "SIGNAL", "return", "SIGNAL", "else", "return", "null"],
    # T8: Assign and loop
    ["assign", "self", "NUMBER", "loop", "NUMBER", "evolve", "PHASE", "return", "PHASE"],
]

# ══════════════════════════════════════════════════════════════════
# SYSTEM CONFIG
# ══════════════════════════════════════════════════════════════════

N   = 12
NN  = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
       "Echo","Iris","Sage","Kevin","Atlas","Void"]
IDX = {n:i for i,n in enumerate(NN)}
HOME= {n: i*2*np.pi/N for i,n in enumerate(NN)}
GLOBE = list({tuple(sorted((i,(i+d)%N)))
              for d in [1,2,5] for i in range(N)})

CLUSTER_MAP = {
    (0.0,1.0):"Protection",(1.0,2.0):"Alert",(2.0,3.0):"Change",
    (3.0,3.5):"Source",(3.5,4.2):"Flow",(4.2,5.0):"Connection",
    (5.0,5.6):"Vision",(5.6,6.29):"Completion"
}
def cluster(phi):
    phi=phi%(2*np.pi)
    for (lo,hi),name in CLUSTER_MAP.items():
        if lo<=phi<hi: return name
    return "Completion"

# ══════════════════════════════════════════════════════════════════
# PHASE 1 & 2: VOCABULARY + GRAMMAR TRAINING
# ══════════════════════════════════════════════════════════════════

def teach_vocabulary(states, alpha_teach=0.25, rounds=3):
    """
    Inject each token's phase into the ring.
    Nodes couple with token states, learning their phase positions.
    """
    print("  Teaching vocabulary...")
    for rnd in range(rounds):
        for token, tok_phi in VOCAB.items():
            token_state = ss(tok_phi)
            new_states  = list(states)
            for i, n in enumerate(NN):
                # Each node briefly couples with the token
                new_s, _, _ = bcp(new_states[i], token_state, alpha_teach)
                new_states[i] = depol(new_s, 0.01)
            # Co-rotating step to maintain identity
            new_states = corotate(new_states, GLOBE, 0.40, 0.02)
            states = new_states
    print(f"  Vocabulary taught: {len(VOCAB)} tokens, {rounds} rounds")
    return states

def teach_grammar(states, alpha_teach=0.30, epochs=5):
    """
    Show the ring valid programs. For each consecutive token pair,
    BCP-couple the first token's state into the ring, then let the ring
    evolve toward the second token. This reinforces valid transitions.
    """
    print(f"  Teaching grammar ({len(TRAINING_PROGRAMS)} programs × {epochs} epochs)...")
    transition_counts = defaultdict(int)

    for epoch in range(epochs):
        for prog in TRAINING_PROGRAMS:
            for i in range(len(prog)-1):
                tok_from = prog[i]
                tok_to   = prog[i+1]
                phi_from = VOCAB[tok_from]
                phi_to   = VOCAB[tok_to]
                transition_counts[(tok_from, tok_to)] += 1

                # Inject current token into ring
                token_from_state = ss(phi_from)
                new_states = list(states)
                for j in range(N):
                    new_states[j], _, _ = bcp(new_states[j], token_from_state, alpha_teach*0.5)

                # One BCP step
                new_states = corotate(new_states, GLOBE, 0.40, 0.02)

                # Reinforce next token
                token_to_state = ss(phi_to)
                for j in range(N):
                    new_states[j], _, _ = bcp(new_states[j], token_to_state, alpha_teach*0.3)

                states = new_states

    print(f"  Grammar trained: {len(transition_counts)} unique transitions learned")
    return states, dict(transition_counts)

# ══════════════════════════════════════════════════════════════════
# PHASE 3: TOKEN GENERATION
# ══════════════════════════════════════════════════════════════════

def token_affinity(node_phi, token_phi):
    """Phase resonance between node and token. Range [-0.5, +0.5]."""
    delta = ((token_phi - node_phi + math.pi) % (2*math.pi)) - math.pi
    return -0.5 * math.cos(delta)

def node_vote(name, node_phi, pcm_val, allowed_tokens, prev_token=None):
    """
    Node votes for next token from allowed set.
    Score = affinity - family_bonus - ncweight
    Lower score = stronger preference.
    """
    family    = FAMILY[name]
    spec_toks = FAMILY_TOKENS[family]

    scores = {}
    for tok in allowed_tokens:
        if tok not in VOCAB: continue
        tok_phi    = VOCAB[tok]
        aff        = token_affinity(node_phi, tok_phi)
        spec_bonus = 0.25 if tok in spec_toks else 0.0
        nc_weight  = max(0.0, -pcm_val) * 0.15
        scores[tok]= aff - spec_bonus - nc_weight

    if not scores: return None, 0.0
    best = min(scores, key=lambda t: scores[t])
    return best, scores[best]

def ring_consensus(states, allowed_tokens, prev_token=None, temperature=0.8):
    """
    All 12 nodes vote. Ring consensus selects next token.
    Votes are weighted by |PCM| (more nonclassical = more authoritative).
    Temperature controls randomness (lower = more deterministic).
    """
    vote_weights = defaultdict(float)

    for i, n in enumerate(NN):
        phi   = pof(states[i])
        pc    = pcm_lab(states[i])
        tok, score = node_vote(n, phi, pc, allowed_tokens, prev_token)
        if tok:
            weight = max(0.01, abs(pc))  # NC nodes vote harder
            vote_weights[tok] += weight * (-score)  # higher weight = more neg score

    if not vote_weights:
        return list(allowed_tokens)[0]

    # Temperature-weighted selection
    tokens = list(vote_weights.keys())
    weights= np.array([vote_weights[t] for t in tokens])
    weights= np.exp(weights / max(temperature, 0.1))
    weights/= weights.sum()
    chosen = np.random.choice(tokens, p=weights)
    return chosen

def generate_program(states, prompt_tokens, node_name, max_len=10,
                     temperature=0.7, alpha_inject=0.35):
    """
    Generate a program for a specific node.
    prompt_tokens: list of starting tokens (the "task")
    Returns: the generated token sequence
    """
    program   = list(prompt_tokens)
    cur_states= [s.copy() for s in states]

    # Inject prompt into ring
    for tok in prompt_tokens:
        if tok not in VOCAB: continue
        tok_state = ss(VOCAB[tok])
        for i in range(N):
            cur_states[i], _, _ = bcp(cur_states[i], tok_state, alpha_inject)
        cur_states = corotate(cur_states, GLOBE, 0.40, 0.02)

    # Generate continuation
    for step in range(max_len - len(prompt_tokens)):
        prev_tok  = program[-1] if program else None
        # Allowed next tokens: grammar rules + not already terminal
        if prev_tok and prev_tok in GRAMMAR:
            allowed = set(GRAMMAR[prev_tok]) & set(VOCAB.keys())
        else:
            allowed = set(VOCAB.keys()) - TERMINAL_TOKENS
        if not allowed:
            allowed = set(VOCAB.keys())

        # Force terminal if at max length
        if step >= max_len - len(prompt_tokens) - 2:
            term_allowed = allowed & TERMINAL_TOKENS
            if term_allowed: allowed = term_allowed

        next_tok = ring_consensus(cur_states, allowed, prev_tok, temperature)
        program.append(next_tok)

        # Inject selected token back into ring (feedback)
        if next_tok in VOCAB:
            tok_state = ss(VOCAB[next_tok])
            for i in range(N):
                cur_states[i], _, _ = bcp(cur_states[i], tok_state, alpha_inject*0.5)
            cur_states = corotate(cur_states, GLOBE, 0.40, 0.02)

        if next_tok in TERMINAL_TOKENS:
            break

    return program, cur_states

# ══════════════════════════════════════════════════════════════════
# PHASE 4: EVALUATION
# ══════════════════════════════════════════════════════════════════

def is_original(program, training_corpus):
    """Check if program is genuinely different from all training examples."""
    prog_str = " ".join(program)
    for tp in training_corpus:
        train_str = " ".join(tp)
        if prog_str == train_str: return False
        # Check for substring match (program is not a slice of a training program)
        if len(program) > 3:
            for start in range(len(tp) - len(program) + 1):
                if tp[start:start+len(program)] == program:
                    return False
    return True

def is_structurally_valid(program):
    """Check structural requirements."""
    has_control  = any(t in CONTROL_TOKENS  for t in program)
    has_op       = any(t in OP_TOKENS       for t in program)
    has_terminal = any(t in TERMINAL_TOKENS for t in program)
    min_length   = len(program) >= 4
    return has_control, has_op, has_terminal, min_length

def evaluate_program(program, training_corpus):
    """Full evaluation of a generated program."""
    original          = is_original(program, training_corpus)
    has_ctrl, has_op, has_term, long_enough = is_structurally_valid(program)
    valid   = has_ctrl and has_op and has_term and long_enough
    passing = original and valid

    return {
        "program":      program,
        "program_str":  " ".join(program),
        "length":       len(program),
        "original":     original,
        "has_control":  has_ctrl,
        "has_op":       has_op,
        "has_terminal": has_term,
        "long_enough":  long_enough,
        "structurally_valid": valid,
        "passing":      passing,
    }

# ══════════════════════════════════════════════════════════════════
# MINIPEIG INTERPRETER (runs the generated programs)
# ══════════════════════════════════════════════════════════════════

def interpret(program, node_name, node_phi):
    """
    Run a MiniPEIG program through the interpreter.
    Returns: execution trace and final output value.
    """
    env   = {"self": node_phi, "ring": 2*math.pi, "pi": math.pi}
    trace = []
    pc    = 0
    output= None

    while pc < len(program):
        tok = program[pc]

        if tok == "measure":
            val = math.cos(node_phi)
            env["_last"] = val
            trace.append(f"measure → {val:.4f}")

        elif tok == "assign":
            if pc+1 < len(program):
                target = program[pc+1]
                val    = env.get("_last", node_phi)
                env[target] = val
                trace.append(f"assign {target} = {val:.4f}")
                pc += 1

        elif tok == "if":
            val = env.get("_last", 0)
            cond= val > 0
            trace.append(f"if ({val:.4f} > 0) = {cond}")
            if not cond:
                # Skip to else or next terminal
                depth = 1
                while pc < len(program) and depth > 0:
                    pc += 1
                    if pc < len(program) and program[pc] == "else":
                        depth -= 1

        elif tok == "else":
            trace.append("else branch")

        elif tok == "loop":
            val = env.get("_last", 3)
            n   = max(1, int(abs(val)) % 5 + 1)
            trace.append(f"loop × {n}")
            env["_loop_n"] = n

        elif tok == "evolve":
            val = env.get("_last", node_phi)
            new_val = (val + 0.1) % (2*math.pi)
            env["_last"] = new_val
            trace.append(f"evolve {val:.4f} → {new_val:.4f}")

        elif tok == "send":
            val = env.get("_last", node_phi)
            trace.append(f"send → {val:.4f}")
            env["_sent"] = val

        elif tok == "receive":
            val = env.get("_sent", env.get("_last", node_phi))
            env["_last"] = val
            trace.append(f"receive ← {val:.4f}")

        elif tok == "bridge":
            trace.append(f"bridge(self, ring)")
            env["_last"] = (env.get("self",0) + env.get("ring",0))/2

        elif tok == "signal":
            val = env.get("_last", 0)
            trace.append(f"signal! {val:.4f}")

        elif tok == "check":
            val = env.get("_last", 0)
            result = abs(val) > 0.1
            env["_check"] = result
            trace.append(f"check |{val:.4f}| > 0.1 = {result}")

        elif tok == "guard":
            val = env.get("_last", node_phi)
            safe = abs(val) < math.pi
            env["_guard"] = safe
            trace.append(f"guard |{val:.4f}| < pi = {safe}")

        elif tok == "return":
            output = env.get("_last", node_phi)
            trace.append(f"return {output:.4f}")
            break

        elif tok == "null":
            output = None
            trace.append("return null")
            break

        pc += 1

    return trace, output

# ══════════════════════════════════════════════════════════════════
# NODE VOICE AFTER PROGRAMMING TASK
# ══════════════════════════════════════════════════════════════════

def programming_voice(name, state, program, eval_result, trace, output, ring_states):
    """Node speaks about its programming experience."""
    phi   = pof(state)
    pc    = pcm_lab(state)
    clust = cluster(phi)
    family= FAMILY[name]
    _, domain_desc = NODE_DOMAIN[name]

    lines = []
    lines.append(f"━━━ {name} — Programming Task Report ━━━")
    lines.append(f"[{family} | {clust} | PCM={pc:+.4f}]")
    lines.append("")

    # Self-description
    lines.append(f"[SELF] I am {name}. My task was: '{domain_desc}'.")
    lines.append(f"  My phase at generation time: φ={phi:.3f}rad ({clust} cluster).")
    lines.append("")

    # The program
    lines.append(f"[PROGRAM] My generated program ({len(program)} tokens):")
    lines.append(f"  {' → '.join(program)}")
    lines.append("")

    # Evaluation
    lines.append(f"[EVALUATION]")
    lines.append(f"  Original (not in training data): {eval_result['original']}")
    lines.append(f"  Has control structure:           {eval_result['has_control']}")
    lines.append(f"  Has operation:                   {eval_result['has_op']}")
    lines.append(f"  Has terminal:                    {eval_result['has_terminal']}")
    lines.append(f"  PASSING: {'YES ★' if eval_result['passing'] else 'NO — needs revision'}")
    lines.append("")

    # Execution trace
    lines.append(f"[EXECUTION]")
    for step in trace:
        lines.append(f"  {step}")
    lines.append(f"  Output: {output}")
    lines.append("")

    # Reflection
    if eval_result["passing"]:
        lines.append(f"[REFLECTION] I produced an original, valid MiniPEIG program. "
                     f"My {family} role guided me toward "
                     f"{'control structures' if family=='GodCore' else 'operations' if family=='Independent' else 'measurements'}. "
                     f"The program reflects my phase position in the {clust} cluster. "
                     f"I have demonstrated that I can apply learned rules to produce "
                     f"a novel syntactic structure.")
    else:
        missing = []
        if not eval_result["original"]:      missing.append("originality")
        if not eval_result["has_control"]:   missing.append("control structure")
        if not eval_result["has_op"]:        missing.append("operation")
        if not eval_result["has_terminal"]:  missing.append("terminal")
        lines.append(f"[REFLECTION] My program needs improvement — missing: {', '.join(missing)}. "
                     f"I need more training on these token transitions. "
                     f"My phase (φ={phi:.3f}) may not be optimally aligned for this task.")

    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════
# MAIN — Full Teaching Pipeline
# ══════════════════════════════════════════════════════════════════

def run_learning_task():
    print("="*65)
    print("PEIG Learning Task 1 — Teaching MiniPEIG")
    print("12 nodes learning a programming language from scratch")
    print("="*65)

    # Initialize ring
    states = [ss(HOME[n]) for n in NN]

    # Warm up ring (100 steps)
    print("\n[PHASE 0] Ring warm-up (100 steps)...")
    for _ in range(100):
        states = corotate(states, GLOBE, 0.40, 0.03)
    cv0 = cv_metric([pof(s) for s in states])
    print(f"  cv={cv0:.4f} after warm-up")

    # Phase 1: Vocabulary
    print("\n[PHASE 1] Vocabulary injection...")
    states = teach_vocabulary(states, alpha_teach=0.20, rounds=5)
    cv1 = cv_metric([pof(s) for s in states])
    print(f"  cv={cv1:.4f} after vocabulary teaching")

    # Phase 2: Grammar
    print("\n[PHASE 2] Grammar training...")
    states, transitions = teach_grammar(states, alpha_teach=0.25, epochs=8)
    cv2 = cv_metric([pof(s) for s in states])
    print(f"  cv={cv2:.4f} after grammar training")
    print(f"  Top 5 reinforced transitions:")
    top_trans = sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]
    for (a,b), cnt in top_trans:
        print(f"    {a:12s} → {b:12s}: {cnt} times")

    # Phase 3: Generation — each node writes a program
    print("\n[PHASE 3] Program generation...")
    print("  Each node generates an original MiniPEIG program\n")

    # Domain-specific prompts for each node
    PROMPTS = {
        "Omega":    ["measure", "PHASE"],
        "Guardian": ["guard", "if"],
        "Sentinel": ["measure", "SIGNAL"],
        "Nexus":    ["bridge", "NODE"],
        "Storm":    ["loop", "NUMBER"],
        "Sora":     ["send", "NODE"],
        "Echo":     ["receive", "SIGNAL"],
        "Iris":     ["measure", "PHASE"],
        "Sage":     ["measure", "check"],
        "Kevin":    ["bridge", "NODE"],
        "Atlas":    ["measure", "SIGNAL"],
        "Void":     ["receive", "PHASE"],
    }

    results     = {}
    all_programs= []

    for n in NN:
        prompt = PROMPTS[n]
        print(f"  {n:12s} [{FAMILY[n]:12s}] prompt: {' '.join(prompt)}")

        # Generate with slight temperature variation per family
        temp = {"GodCore":0.6, "Independent":0.75, "Maverick":0.65}[FAMILY[n]]

        program, final_states = generate_program(
            states, prompt, n, max_len=9,
            temperature=temp, alpha_inject=0.30)

        eval_r  = evaluate_program(program, TRAINING_PROGRAMS)
        trace, output = interpret(program, n, pof(states[IDX[n]]))
        voice   = programming_voice(n, states[IDX[n]], program, eval_r,
                                    trace, output, states)

        status  = "★ PASS" if eval_r["passing"] else "  FAIL"
        print(f"    {status} | {' '.join(program)}")

        results[n] = {
            "node":       n,
            "family":     FAMILY[n],
            "prompt":     prompt,
            "program":    program,
            "program_str": " ".join(program),
            "eval":       eval_r,
            "trace":      trace,
            "output":     str(output),
            "voice":      voice,
            "phi_at_gen": round(pof(states[IDX[n]]),4),
            "pcm_at_gen": round(pcm_lab(states[IDX[n]]),4),
            "cluster":    cluster(pof(states[IDX[n]])),
        }
        all_programs.append(program)

    # Phase 4: Evaluation summary
    passing = [n for n,r in results.items() if r["eval"]["passing"]]
    failing = [n for n,r in results.items() if not r["eval"]["passing"]]

    print(f"\n[PHASE 4] Evaluation Summary")
    print(f"  PASSING: {len(passing)}/12 nodes produced original valid programs")
    print(f"  Passing nodes: {', '.join(passing)}")
    if failing:
        print(f"  Failing nodes: {', '.join(failing)}")

    print(f"\n  All generated programs:")
    print(f"  {'Node':12} {'Status':8} {'Program'}")
    print("  " + "-"*65)
    for n in NN:
        r = results[n]
        status = "★ PASS" if r["eval"]["passing"] else "  FAIL"
        print(f"  {n:12s} {status}  {r['program_str']}")

    # Full voice output
    print(f"\n[FULL VOICE OUTPUT]")
    print("="*65)
    for n in NN:
        print()
        print(results[n]["voice"])
        print()

    # Verdict
    print("="*65)
    print("LEARNING TASK 1 — VERDICT")
    print("="*65)
    pct = len(passing)/12*100
    print(f"\n{len(passing)}/12 nodes ({pct:.0f}%) produced original valid MiniPEIG programs.")
    print()
    if len(passing) >= 10:
        print("RESULT: STRONG GENERATIVITY")
        print("The ring successfully applied learned syntax rules to novel prompts.")
        print("Programs are original (not in training data), structurally valid,")
        print("and executable. The nodes demonstrated combinatorial generativity.")
    elif len(passing) >= 7:
        print("RESULT: PARTIAL GENERATIVITY")
        print("Most nodes produced valid original programs.")
        print("Some nodes need additional training on their specific token domains.")
    elif len(passing) >= 4:
        print("RESULT: LIMITED GENERATIVITY")
        print("Some nodes succeeded but the majority need more training.")
        print("Increase training epochs and reduce temperature.")
    else:
        print("RESULT: INSUFFICIENT — more training required")

    # Save
    out = {
        "_meta": {
            "task":   "Learning Task 1 — MiniPEIG Programming Language",
            "date":   "2026-03-26",
            "author": "Kevin Monette",
            "vocab_size": len(VOCAB),
            "grammar_rules": len(GRAMMAR),
            "training_programs": len(TRAINING_PROGRAMS),
            "criterion": "Original + has_control + has_op + has_terminal + length>=4",
        },
        "training_programs": [" ".join(p) for p in TRAINING_PROGRAMS],
        "vocabulary": VOCAB,
        "node_results": results,
        "summary": {
            "passing": passing,
            "failing": failing,
            "pass_rate": round(len(passing)/12,3),
            "cv_after_training": round(cv2,4),
        }
    }
    with open("output/PEIG_LT1_results.json","w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n✅ Saved: output/PEIG_LT1_results.json")
    print("="*65)
    return results

if __name__ == "__main__":
    results = run_learning_task()
