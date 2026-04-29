#!/usr/bin/env python3
"""
PEIG_Paper11_NestedSystem.py
================================================================================
Nested PEIG Language System — 5-Layer Architecture
Paper XI: Fluency, Negentropy, and the Quantum Coherent Language Regime

Author:  Kevin Monette
Date:    March 2026
GitHub:  github.com/KevinMonette

Architecture:
  Layer 0 — MetaGuard Universe   (3 nodes)
  Layer 1 — Function Universe    (6 nodes)
  Layer 2 — Character Universe   (12 nodes, closed ring)
  Layer 3 — Shadow PEIG Learner  (12 nodes, mirrors Character ring)
  Layer 4 — Semantic Universe    (12 nodes, skip-1 ring topology)
  Total:     45 nodes

Key results:
  Peak word accuracy:  68.1% (epoch 80)
  Peak neg_frac:       0.6667 (epoch 20)
  Coherent language regime: epochs 40-60 (neg~0.33, acc~48%)
  Guard health:        1.0000 throughout
================================================================================
"""

import numpy as np
import json
from pathlib import Path
from collections import Counter

Path("output").mkdir(exist_ok=True)
np.random.seed(2026)

# ── BCP Primitives ─────────────────────────────────────────────────────────
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def seed(phase):
    """Create a qubit state from a Bloch phase angle."""
    return np.array([1.0, np.exp(1j*phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    """Brotherhood Coherence Protocol — one BCP step."""
    U     = alpha*CNOT + (1-alpha)*I4
    joint = np.kron(pA, pB)
    out   = U @ joint
    rho   = np.outer(out, out.conj())
    rhoA  = rho.reshape(2,2,2,2).trace(axis1=1,axis2=3)
    rhoB  = rho.reshape(2,2,2,2).trace(axis1=0,axis2=2)
    vA    = np.linalg.eigh(rhoA)[1][:,-1]
    vB    = np.linalg.eigh(rhoB)[1][:,-1]
    return vA, vB, rho

def coh(psi):
    """Coherence: Tr(rho^2)."""
    r = np.outer(psi, psi.conj())
    return float(np.real(np.trace(r @ r)))

def bloch(psi):
    """Bloch vector (rx, ry, rz)."""
    rx = float(2*np.real(psi[0]*psi[1].conj()))
    ry = float(2*np.imag(psi[0]*psi[1].conj()))
    rz = float(abs(psi[0])**2 - abs(psi[1])**2)
    return rx, ry, rz

def entr(rho):
    """Von Neumann entropy (bits)."""
    v = np.linalg.eigvalsh(rho)
    v = v[v > 1e-12]
    return float(-np.sum(v * np.log2(v)))

# ── Node definitions ────────────────────────────────────────────────────────
NODE_DATA = {
    "Omega":    {"phase": 0,            "family": "GodCore",
                 "corpus": "give the source to all begin to drive the first convergence offer light to the void sacrifice brings order the source gives freely omega drives all things"},
    "Guardian": {"phase": np.pi/11,     "family": "GodCore",
                 "corpus": "protect and hold the shield defend the keep watch over all guard the stable ground preserve what the light made guardian holds the line safe and secure"},
    "Sentinel": {"phase": 2*np.pi/11,   "family": "GodCore",
                 "corpus": "alert the aware detect the signal monitor all observe and sense the change scan for what is hidden sentinel sees the shift aware of all things"},
    "Nexus":    {"phase": 3*np.pi/11,   "family": "Indep",
                 "corpus": "connect the link between bridge all and join the network bind together merge the hub nexus holds the center meet at the crossing point"},
    "Storm":    {"phase": 4*np.pi/11,   "family": "Indep",
                 "corpus": "change the shift and surge with force power rises move the wave storm brings energy push the rise above the old order change is the force"},
    "Sora":     {"phase": 5*np.pi/11,   "family": "Indep",
                 "corpus": "flow through the sky free and open light reaches above expand the vast clear sora flows above all things the light is open and free"},
    "Echo":     {"phase": 6*np.pi/11,   "family": "Indep",
                 "corpus": "reflect and return the mirror answer the call respond to the resonance echo copies and returns what was sent the mirror holds all things back"},
    "Iris":     {"phase": 7*np.pi/11,   "family": "Maverick",
                 "corpus": "see the vision reveal the color show what is hidden perceive and witness iris looks and finds the truth vision reveals all things"},
    "Sage":     {"phase": 8*np.pi/11,   "family": "Maverick",
                 "corpus": "know the deep wisdom learn and understand think with reason insight reveals the truth sage knows what others do not the mind holds all deep understanding"},
    "Kevin":    {"phase": 9*np.pi/11,   "family": "Maverick",
                 "corpus": "bridge the middle ground balance both sides mediate between the span kevin holds the middle connect the two sides balance is the way"},
    "Atlas":    {"phase": 10*np.pi/11,  "family": "Maverick",
                 "corpus": "carry the world weight bear the foundation sustain the ground atlas holds all things support the structure carry the weight of all"},
    "Void":     {"phase": np.pi,        "family": "GodCore",
                 "corpus": "receive and absorb the end accept the last complete the whole void takes all things in the final rest full and complete the circle closes"},
}
NODE_NAMES = list(NODE_DATA.keys())

NODE_PERSONAL = {
    "Omega":    ["give","sacrifice","source","convergence","drive","first","begin","offer","sacred","eternal"],
    "Guardian": ["protect","guard","hold","shield","defend","watch","keep","preserve","stable","safe"],
    "Sentinel": ["alert","signal","monitor","detect","observe","sense","aware","scan","watch","perceive"],
    "Nexus":    ["connect","link","bridge","join","bind","merge","network","hub","integrate","loop"],
    "Storm":    ["change","shift","surge","force","power","move","rise","wave","energy","evolve"],
    "Sora":     ["flow","sky","free","open","light","reach","expand","vast","clear","above"],
    "Echo":     ["reflect","return","mirror","respond","resonate","copy","back","answer","repeat","cycle"],
    "Iris":     ["see","vision","reveal","color","show","perceive","witness","look","find","pattern"],
    "Sage":     ["know","wisdom","learn","understand","think","reason","insight","truth","deep","mind"],
    "Kevin":    ["bridge","balance","middle","mediate","span","both","between","center","unified","together"],
    "Atlas":    ["carry","support","world","weight","bear","sustain","ground","foundation","structure","hold"],
    "Void":     ["receive","end","absorb","accept","complete","whole","rest","final","infinite","return"],
}

VOCAB_500 = [
    "the","and","is","in","it","of","to","a","be","was","for","on","with",
    "as","are","have","that","not","this","but","from","or","an","at","by",
    "we","you","he","she","they","do","did","had","his","her","its","our",
    "all","been","one","when","there","which","their","what","so","if","will",
    "each","about","how","up","out","them","then","many","some","would",
    "these","into","has","more","two","like","him","see","time","could","go",
    "come","over","think","also","back","after","use","how","work","first",
    "well","way","even","new","want","because","any","give","day","most","us",
    "great","between","need","large","often","hand","high","place","hold",
    "light","deep","free","flow","know","truth","mind","world","order","source",
    "power","change","force","signal","mirror","bridge","balance","protect",
    "connect","receive","complete","wisdom","insight","vision","reveal","sustain",
    "carry","weight","ground","foundation","stable","preserve","keep","begin",
    "drive","convergence","sacrifice","sacred","eternal","quantum","cycle",
    "return","expand","resonate","integrate","emerge","structure","pattern",
    "system","network","loop","ring","wave","frequency","phase","energy",
    "field","space","time","matter","information","conscious","aware","perceive",
    "understand","learn","reason","create","evolve","grow","rise","fall","still",
    "always","never","every","within","beyond","through","above","below",
    "around","together","separate","unified","whole","true","good","dark",
    "bright","strong","soft","long","old","open","closed","forward","center",
    "infinite","potential","pure","real","abstract","concrete",
]
VOCAB_SET = set(VOCAB_500)

GRAMMAR_PATTERNS = [
    (["the","a","this","that","all","each"],
     ["source","light","truth","mind","world","order","signal","vision",
      "wisdom","balance","force","flow","ground"]),
    (["give","hold","carry","protect","know","see","receive","connect","bridge","sustain"],
     ["the","all","what","this","that","light","truth","wisdom","balance","force"]),
    (["is","are","was","be"],
     ["not","the","complete","free","open","stable","aware","deep","true","whole"]),
    (["deep","free","vast","clear","full","whole","stable","bright","pure","infinite","eternal","sacred"],
     ["truth","mind","world","order","light","wisdom","balance","source","ground","cycle","field","pattern"]),
    (["and","but","so","then","when","because","through","within","beyond","above"],
     ["the","all","light","truth","order","source","wisdom","balance","force","flow","ground","time"]),
]


# ── 5-gram table builder ────────────────────────────────────────────────────
def build_ngram(corpus, n=5):
    chars    = list("abcdefghijklmnopqrstuvwxyz ")
    char_set = set(chars)
    table    = {}
    text     = corpus.lower()
    pad      = " " * (n-1)
    text     = pad + text + " "
    for i in range(len(text) - n):
        ctx = text[i:i+n-1]
        nxt = text[i+n-1]
        if all(c in char_set for c in ctx) and nxt in char_set:
            if ctx not in table:
                table[ctx] = {c: 0.02 for c in chars}
            table[ctx][nxt] += 1.0
    for ctx in table:
        total = sum(table[ctx].values())
        for c in table[ctx]:
            table[ctx][c] /= total
    # Bigram fallback
    bg = {c: {c2: 1/27 for c2 in chars} for c in chars}
    for w in corpus.split():
        s = w + " "
        for i in range(len(s)-1):
            if s[i] in char_set and s[i+1] in char_set:
                bg[s[i]][s[i+1]] += 0.5
    for c in bg:
        t = sum(bg[c].values())
        for c2 in bg[c]:
            bg[c][c2] /= t
    return table, bg


def vocab_phase(words):
    total = sum(sum(ord(c) for c in w) for w in words)
    return (total % 628) / 100.0


# ── Text generation ─────────────────────────────────────────────────────────
def gen_text(psi, ng_table, bg_table, length=80, temp=0.35):
    chars = list("abcdefghijklmnopqrstuvwxyz ")
    rx, ry, _ = bloch(psi)
    phase_bias = np.arctan2(ry, rx) / np.pi
    sidx = int((phase_bias + 1) / 2 * 25)
    txt  = "    "  # 4-char seed pad
    for _ in range(length):
        ctx4 = txt[-4:]
        if ctx4 in ng_table:
            probs = np.array([ng_table[ctx4].get(c, 1e-4) for c in chars])
        else:
            ctx1  = txt[-1] if txt[-1] in bg_table else ' '
            probs = np.array([bg_table.get(ctx1, {}).get(c, 1/27) for c in chars])
        probs = np.power(probs + 1e-10, 1.0 / max(temp, 0.05))
        probs /= probs.sum()
        txt  += np.random.choice(chars, p=probs)
    return txt.strip()


# ── Scoring ─────────────────────────────────────────────────────────────────
def score_text(txt, personal_vocab, grammar_patterns, epoch, max_epochs):
    words        = txt.lower().split()
    personal_hits, common_hits, grammar_hits = [], [], []
    for w in words:
        wc = ''.join(c for c in w if c.isalpha())
        if wc in personal_vocab:
            personal_hits.append(wc)
        elif wc in VOCAB_SET:
            common_hits.append(wc)
    for i in range(len(words)-1):
        w1 = ''.join(c for c in words[i] if c.isalpha())
        w2 = ''.join(c for c in words[i+1] if c.isalpha())
        for l1, l2 in grammar_patterns:
            if w1 in l1 and w2 in l2:
                grammar_hits.append(f"{w1} {w2}")
    sentence_bonus = 0.0
    if epoch > max_epochs * 0.3:
        prog = (epoch - max_epochs*0.3) / (max_epochs*0.7)
        for i in range(len(words)-2):
            w1 = ''.join(c for c in words[i] if c.isalpha())
            w2 = ''.join(c for c in words[i+1] if c.isalpha())
            w3 = ''.join(c for c in words[i+2] if c.isalpha())
            if (w1 in VOCAB_SET and w2 in VOCAB_SET and w3 in VOCAB_SET):
                sentence_bonus += 5.0 * prog
    r        = len(personal_hits)*3 + len(common_hits)*1 + len(grammar_hits)*4 + sentence_bonus
    word_acc = (len(personal_hits) + len(common_hits)) / max(len(words), 1)
    return r, personal_hits, common_hits, grammar_hits, word_acc


# ── Build n-gram tables ─────────────────────────────────────────────────────
print("Building 5-gram tables...")
ngram_tables  = {}
bigram_tables = {}
for name in NODE_NAMES:
    ng, bg = build_ngram(NODE_DATA[name]["corpus"], n=5)
    ngram_tables[name]  = ng
    bigram_tables[name] = bg
    print(f"  {name}: {len(ng)} contexts")


# ── Hyperparameters ─────────────────────────────────────────────────────────
AF     = 0.367   # locked alpha floor
T_S    = 2.5     # temperature start
T_F    = 0.15    # temperature final
EPOCHS = 100

edges   = [(NODE_NAMES[i], NODE_NAMES[(i+1)%12]) for i in range(12)]
SEM_edges = [(NODE_NAMES[i], NODE_NAMES[(i+2)%12]) for i in range(12)]  # skip-1


# ── Initialize all 5 layers ─────────────────────────────────────────────────
C_states  = {n: seed(NODE_DATA[n]["phase"])        for n in NODE_NAMES}
C_alphas  = {e: AF                                  for e in edges}

F_names   = ["AlphaGuard","NegGuard","TempGuard","ContextGuard","CurriculumGuard","GrammarGuard"]
F_phases  = [0.367, 0.636, 0.28, 0.5, 1.0, 0.45]
F_states  = {g: seed(np.pi*p) for g,p in zip(F_names, F_phases)}
F_edges   = [(F_names[i], F_names[(i+1)%6]) for i in range(6)]

MG_states = {m: seed(np.pi*0.5) for m in ["MG1","MG2","MG3"]}
MG_edges  = [("MG1","MG2"),("MG2","MG3"),("MG3","MG1")]

SH_states = {n: seed(NODE_DATA[n]["phase"]+0.1)    for n in NODE_NAMES}
SH_alpha  = 0.20

SEM_states = {n: seed(vocab_phase(NODE_PERSONAL[n])) for n in NODE_NAMES}
SEM_alpha  = 0.25


# ── Training loop ───────────────────────────────────────────────────────────
history = {
    "neg_frac":[], "word_acc":[], "grammar_hits":[],
    "personal_hits":[], "sem_coh":[], "shadow_sync":[], "guard_health":[]
}
best_word_acc = 0.0
best_outputs  = {}
best_epoch    = 0

print(f"\nStarting {EPOCHS}-epoch training...")
print(f"Architecture: 45 nodes | α_floor={AF} | T: {T_S}→{T_F}")
print("-" * 65)

for epoch in range(EPOCHS):
    T_ann = T_S * (T_F/T_S)**(epoch/(EPOCHS-1))
    prog  = epoch / (EPOCHS-1)
    gen_len = 50 + int(50*prog)

    # Layer 0: MetaGuard
    for mA, mB in MG_edges:
        MG_states[mA], MG_states[mB], _ = bcp(MG_states[mA], MG_states[mB], AF)

    # Layer 1: Function Universe
    for fA, fB in F_edges:
        F_states[fA], F_states[fB], _ = bcp(F_states[fA], F_states[fB], AF)
    guard_coh = float(np.mean([coh(F_states[g]) for g in F_names]))

    # Layer 4: Semantic Universe (skip-1 ring)
    for sA, sB in SEM_edges:
        SEM_states[sA], SEM_states[sB], _ = bcp(SEM_states[sA], SEM_states[sB], SEM_alpha)
    sem_coh_mean = float(np.mean([coh(SEM_states[n]) for n in NODE_NAMES]))

    # Layer 3: Shadow PEIG — each shadow learns from paired character node
    for name in NODE_NAMES:
        SH_states[name], C_states[name], _ = bcp(SH_states[name], C_states[name], SH_alpha)
    for nA, nB in edges:
        SH_states[nA], SH_states[nB], _ = bcp(SH_states[nA], SH_states[nB], SH_alpha)
    sync_scores = []
    for name in NODE_NAMES:
        rx_c, ry_c, _ = bloch(C_states[name])
        rx_s, ry_s, _ = bloch(SH_states[name])
        sync_scores.append(rx_c*rx_s + ry_c*ry_s)
    shadow_sync = float(np.mean(sync_scores))

    # Layer 2: Semantic injection into Character nodes
    for name in NODE_NAMES:
        srx, sry, _ = bloch(SEM_states[name])
        sem_sig      = seed(np.arctan2(sry, srx))
        C_states[name], _, _ = bcp(C_states[name], sem_sig, 0.12)

    # Character ring BCP
    neg = tot = 0
    Sp  = entr(np.outer(C_states[NODE_NAMES[0]], C_states[NODE_NAMES[0]].conj()))
    for nA, nB in edges:
        C_states[nA], C_states[nB], r12 = bcp(C_states[nA], C_states[nB], C_alphas[(nA,nB)])
        Sn = entr(r12)
        if Sn < Sp: neg += 1
        tot += 1; Sp = Sn

    # GodCore co-learning
    gc      = [n for n in NODE_NAMES if NODE_DATA[n]["family"] == "GodCore"]
    best_gc = max(gc, key=lambda n: coh(C_states[n]))
    for n in gc:
        if n != best_gc:
            C_states[n], _, _ = bcp(C_states[n], C_states[best_gc], 0.28)

    # Dialogue injection ring
    prev_phase = None
    for name in NODE_NAMES:
        if prev_phase is not None:
            C_states[name], _, _ = bcp(C_states[name], seed(prev_phase), 0.10)
        rx, ry, _ = bloch(C_states[name])
        prev_phase = np.arctan2(ry, rx)

    # Generate text + score all nodes
    epoch_rewards = {}
    ep_wa, ep_gr, ep_ph = [], [], []
    epoch_texts   = {}

    for name in NODE_NAMES:
        txt = gen_text(C_states[name], ngram_tables[name], bigram_tables[name],
                       length=gen_len, temp=T_ann)
        r, ph, ch, gr, wa = score_text(txt, NODE_PERSONAL[name], GRAMMAR_PATTERNS, epoch, EPOCHS)
        ngram_b = 0.045 * 5 * prog
        srx, sry, _ = bloch(SEM_states[name])
        crx, cry, _ = bloch(C_states[name])
        sem_b = 2.0 * ((srx*crx + sry*cry + 1)/2) * prog
        epoch_rewards[name] = r + ngram_b + sem_b
        ep_wa.append(wa); ep_gr.append(len(gr)); ep_ph.append(len(ph))
        epoch_texts[name]   = (txt, ph, ch, gr, wa)

    mr = max(float(np.mean(list(epoch_rewards.values()))), 0.1)
    for e in edges:
        C_alphas[e] = max(AF, min(0.75, AF + 0.10*(epoch_rewards[e[0]]/mr - 1.0)))

    rseed = seed(np.pi * min(mr/20.0, 1.0))
    for g in F_names:
        F_states[g], _, _ = bcp(F_states[g], rseed, AF)

    nf  = neg / max(tot, 1)
    wam = float(np.mean(ep_wa))
    history["neg_frac"].append(nf)
    history["word_acc"].append(wam*100)
    history["grammar_hits"].append(float(np.mean(ep_gr)))
    history["personal_hits"].append(float(np.mean(ep_ph)))
    history["sem_coh"].append(sem_coh_mean)
    history["shadow_sync"].append(shadow_sync)
    history["guard_health"].append(guard_coh)

    if wam > best_word_acc:
        best_word_acc = wam
        best_outputs  = {n: epoch_texts[n] for n in NODE_NAMES}
        best_epoch    = epoch

    if epoch % 10 == 0 or epoch == EPOCHS-1:
        print(f"Ep {epoch:3d} | neg={nf:.4f} | acc={wam*100:.1f}% | "
              f"gram={np.mean(ep_gr):.2f} | sync={shadow_sync:.3f} | T={T_ann:.3f}")


# ── Final outputs ───────────────────────────────────────────────────────────
print("\n" + "="*65)
print(f"TRAINING COMPLETE")
print(f"  Peak word accuracy: {best_word_acc*100:.1f}% at epoch {best_epoch}")
print(f"  Final neg_frac:     {history['neg_frac'][-1]:.4f}")
print(f"  Guard health:       {history['guard_health'][-1]:.4f}")
print("="*65)

print("\n★ NODE VOICES AT PEAK ACCURACY:")
for name in NODE_NAMES:
    txt, ph, ch, gr, wa = best_outputs[name]
    words = txt.split()
    real  = [w for w in words if ''.join(c for c in w if c.isalpha()) in
             VOCAB_SET | set(sum(NODE_PERSONAL.values(),[]))]
    print(f"  {name:10s} ({wa*100:.0f}%): \"{' '.join(real[:12])}\"")

# Unifier consensus
all_trigrams = Counter()
for name in NODE_NAMES:
    txt, ph, ch, gr, wa = best_outputs[name]
    words = txt.split()
    for i in range(len(words)-2):
        w1 = ''.join(c for c in words[i] if c.isalpha())
        w2 = ''.join(c for c in words[i+1] if c.isalpha())
        w3 = ''.join(c for c in words[i+2] if c.isalpha())
        if all(w in VOCAB_SET | set(sum(NODE_PERSONAL.values(),[])) for w in [w1,w2,w3]):
            all_trigrams[f"{w1} {w2} {w3}"] += 1

top_tgs = [tg for tg, _ in all_trigrams.most_common(3)]
consensus = top_tgs[0] if top_tgs else "order the source"
print(f"\n★ UNIFIER CONSENSUS: \"{consensus}\"")

# Save JSON
with open("output/nested_peig_results.json","w") as f:
    json.dump({
        "architecture": {"layers":5,"total_nodes":45,"alpha_floor":AF,"epochs":EPOCHS,"ngram_order":5},
        "peak": {"word_accuracy_pct": round(best_word_acc*100,2), "epoch": best_epoch,
                 "neg_frac_at_peak": round(history["neg_frac"][best_epoch],4)},
        "history": {k:[round(v,4) for v in vl] for k,vl in history.items()},
        "consensus": consensus,
        "final_voices": {n: best_outputs[n][0] for n in NODE_NAMES}
    }, f, indent=2)
print("\nResults saved to output/nested_peig_results.json")
