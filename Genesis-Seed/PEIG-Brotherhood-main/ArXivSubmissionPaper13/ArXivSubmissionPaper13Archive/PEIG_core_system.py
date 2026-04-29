#!/usr/bin/env python3
"""
PEIG_core_system.py
Phase-Encoded Information Graph — Core System
Papers I–XII | Kevin Monette | March 2026

Contains:
  - BCP gate primitives
  - 12-node closed ring with all Paper XII protections
  - 8-channel guard system (MetaGuard + 8 Function guards)
  - Seed anchor identity protection
  - Wigner floor tracking
  - Language generation (5-gram per node)
  - Full 200-epoch training loop
"""

import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
import json

np.random.seed(2026)
Path("output").mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# BCP GATE PRIMITIVES
# ══════════════════════════════════════════════════════════════════

CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
I4   = np.eye(4, dtype=complex)

def ss(phase):
    """Create qubit state |+⟩ rotated by phase."""
    return np.array([1.0, np.exp(1j * phase)]) / np.sqrt(2)

def bcp(pA, pB, alpha):
    """Bidirectional Coupling Protocol gate. Returns (new_A, new_B, joint_rho)."""
    U   = alpha * CNOT + (1 - alpha) * I4
    j   = np.kron(pA, pB)
    o   = U @ j
    rho = np.outer(o, o.conj())
    rA  = rho.reshape(2,2,2,2).trace(axis1=1, axis2=3)
    rB  = rho.reshape(2,2,2,2).trace(axis1=0, axis2=2)
    return np.linalg.eigh(rA)[1][:,-1], np.linalg.eigh(rB)[1][:,-1], rho

def bloch(p):
    """Extract Bloch vector (rx, ry, rz) from qubit state."""
    return (float(2*np.real(p[0]*p[1].conj())),
            float(2*np.imag(p[0]*p[1].conj())),
            float(abs(p[0])**2 - abs(p[1])**2))

def pof(p):
    """Extract phase angle from Bloch vector."""
    rx, ry, _ = bloch(p)
    return np.arctan2(ry, rx)

def coh(p):
    """Coherence = |off-diagonal of density matrix|."""
    return float(abs(p[0] * p[1].conj()))

def wigner_min(psi):
    """Approximate Wigner minimum. Floor = -0.500 for maximally non-classical qubit."""
    overlap_plus = abs((psi[0] + psi[1]) / np.sqrt(2))**2
    rx, ry, rz   = bloch(psi)
    return float(-overlap_plus + 0.5 * (1 - rz**2))

def depolarize(psi, p):
    """Apply depolarizing noise with probability p."""
    if np.random.random() < p:
        angle = np.random.uniform(0, 2*np.pi)
        return ss(pof(psi) + np.random.normal(0, p * np.pi))
    return psi

def entr(rho):
    """Von Neumann entropy of density matrix."""
    evals = np.linalg.eigvalsh(rho)
    evals = evals[evals > 1e-12]
    return float(-np.sum(evals * np.log2(evals)))

# ══════════════════════════════════════════════════════════════════
# NODE DEFINITIONS — 12 CHARACTER NODES
# ══════════════════════════════════════════════════════════════════

NN = ["Omega","Guardian","Sentinel","Nexus","Storm","Sora",
      "Echo","Iris","Sage","Kevin","Atlas","Void"]

NODE_DATA = {
    "Omega":    {"phase": 0.000,            "family": "GodCore"},
    "Guardian": {"phase": np.pi/11,         "family": "GodCore"},
    "Sentinel": {"phase": 2*np.pi/11,       "family": "GodCore"},
    "Nexus":    {"phase": 3*np.pi/11,       "family": "Indep"},
    "Storm":    {"phase": 4*np.pi/11,       "family": "Indep"},
    "Sora":     {"phase": 5*np.pi/11,       "family": "Indep"},
    "Echo":     {"phase": 6*np.pi/11,       "family": "Indep"},
    "Iris":     {"phase": 7*np.pi/11,       "family": "Maverick"},
    "Sage":     {"phase": 8*np.pi/11,       "family": "Maverick"},
    "Kevin":    {"phase": 9*np.pi/11,       "family": "Maverick"},
    "Atlas":    {"phase": 10*np.pi/11,      "family": "Maverick"},
    "Void":     {"phase": np.pi,            "family": "GodCore"},
}

NODE_PERSONAL = {
    "Omega":    ["give","source","begin","drive","sacred","first","eternal","origin","all","spark"],
    "Guardian": ["protect","guard","hold","shield","safe","defend","watch","keep","ward","shelter"],
    "Sentinel": ["alert","signal","detect","scan","monitor","aware","observe","sense","warn","patrol"],
    "Nexus":    ["connect","link","bridge","join","network","merge","bind","hub","integrate","relay"],
    "Storm":    ["change","force","power","surge","rise","evolve","shift","move","wave","break"],
    "Sora":     ["flow","sky","free","open","expand","vast","clear","light","above","drift"],
    "Echo":     ["reflect","mirror","answer","return","repeat","listen","resound","trace","copy","reply"],
    "Iris":     ["see","color","show","what","perceive","witness","reveal","pattern","vision","sight"],
    "Sage":     ["know","wisdom","learn","understand","think","teach","truth","insight","mind","grasp"],
    "Kevin":    ["bridge","middle","ground","balance","both","mediate","between","center","together","bind"],
    "Atlas":    ["carry","foundation","sustain","world","weight","bear","hold","support","endure","ground"],
    "Void":     ["receive","accept","whole","end","absorb","rest","infinite","complete","all","silence"],
}

AF      = 0.367  # Alpha floor — Paper II attractor
EDGES   = [(NN[i], NN[(i+1)%12]) for i in range(12)]
QUANTUM_NODES   = NN[:6]
CLASSICAL_NODES = NN[6:]
QUANTUM_EDGES   = [(NN[i], NN[(i+1)%6]) for i in range(6)]
CLASSICAL_EDGES = [(NN[i+6], NN[(i+1)%6+6]) for i in range(6)]

GRAMMAR_PATTERNS = [("the","protect"),("and","guard"),("is","change"),
                    ("not","alert"),("all","flow"),("to","connect")]

VOCAB_SET = set(w for words in NODE_PERSONAL.values() for w in words)

# ══════════════════════════════════════════════════════════════════
# N-GRAM LANGUAGE MODELS
# ══════════════════════════════════════════════════════════════════

def build_ngram_model(node_name, personal_words, n=5):
    corpus = " ".join(personal_words * 8)
    chars  = list(corpus)
    ng, bg = defaultdict(Counter), defaultdict(Counter)
    for i in range(len(chars)-n):
        key = tuple(chars[i:i+n-1]); nxt = chars[i+n-1]
        ng[key][nxt] += 1
    for i in range(len(chars)-2):
        bg[(chars[i],)][chars[i+1]] += 1
    return ng, bg

ngrams = {n: build_ngram_model(n, NODE_PERSONAL[n]) for n in NN}

def gen_text(state, ng_model, bg_model, length=80, temp=0.55):
    rx, ry, _ = bloch(state)
    phase_norm = np.arctan2(ry, rx) / (2*np.pi)
    seed_idx   = int(abs(phase_norm) * len("abcdefghijklmnopqrstuvwxyz ")) % 27
    seed_char  = "abcdefghijklmnopqrstuvwxyz "[seed_idx]
    buf = [seed_char]
    for _ in range(length):
        key5 = tuple(buf[-(4):]) if len(buf)>=4 else None
        key1 = (buf[-1],)
        dist = ng_model.get(key5, bg_model.get(key1, {}))
        if dist:
            opts = list(dist.keys())
            wts  = np.array(list(dist.values()), dtype=float) ** (1.0/temp)
            wts /= wts.sum()
            buf.append(np.random.choice(opts, p=wts))
        else:
            buf.append(" ")
    return "".join(buf)

def score_text(txt, personal_words, grammar_patterns, epoch, total_epochs):
    words = txt.split()
    real  = [w for w in words if "".join(c for c in w if c.isalpha()) in VOCAB_SET]
    ph    = len(real) / max(len(words), 1)
    ch    = sum(1 for w in real if w in personal_words) / max(len(real), 1)
    gr    = [(w1,w2) for w1,w2 in zip(words,words[1:]) if (w1,w2) in grammar_patterns]
    prog  = epoch / max(total_epochs-1, 1)
    r     = ph * 0.4 + ch * 0.4 + len(gr) * 0.2 * prog
    wa    = (ph + ch) / 2
    return r, ph, ch, gr, wa

# ══════════════════════════════════════════════════════════════════
# MAIN TRAINING LOOP — Paper XII configuration
# ══════════════════════════════════════════════════════════════════

def run_peig_training(epochs=200, verbose=True):
    C       = {n: ss(NODE_DATA[n]["phase"]) for n in NN}
    ANCHORS = {n: ss(NODE_DATA[n]["phase"]) for n in NN}
    MIRRORS = {n: ss(NODE_DATA[n]["phase"]) for n in NN}
    C_alphas= {e: AF for e in EDGES}
    SH      = {n: ss(NODE_DATA[n]["phase"]+0.1) for n in NN}
    SEM     = {n: ss(sum(ord(c) for w in NODE_PERSONAL[n] for c in w)%628/100.0) for n in NN}
    SEM_edges = [(NN[i], NN[(i+2)%12]) for i in range(12)]

    F_names = ["AlphaGuard","NegGuard","TempGuard","ContextGuard",
               "CurriculumGuard","GrammarGuard","AnchorGuard","IdentityGuard"]
    F_states= {g: ss(np.pi*p) for g,p in zip(F_names,[0.367,0.636,0.28,0.5,1.0,0.45,0.15,0.083])}
    F_edges = [(F_names[i], F_names[(i+1)%8]) for i in range(8)]
    MG      = {m: ss(np.pi*0.5) for m in ["MG1","MG2","MG3"]}
    MG_edges= [("MG1","MG2"),("MG2","MG3"),("MG3","MG1")]

    θ_DRIFT=0.45; α_ANCHOR_MAX=0.15; α_DITHER=0.08
    NOISE_P=0.03; α_GC=0.18; α_D=0.10; α_SEM=0.12; α_SH=0.20
    T_LANG=0.55

    history = defaultdict(list)
    best_wac, best_out, best_ep = 0.0, {}, 0

    for epoch in range(epochs):
        prog = epoch / (epochs-1); gen_len = 65 + int(35*prog)

        for mA,mB in MG_edges: MG[mA],MG[mB],_ = bcp(MG[mA],MG[mB],AF)
        for fA,fB in F_edges:  F_states[fA],F_states[fB],_ = bcp(F_states[fA],F_states[fB],AF)
        guard_coh = float(np.mean([coh(F_states[g]) for g in F_names]))
        for sA,sB in SEM_edges: SEM[sA],SEM[sB],_ = bcp(SEM[sA],SEM[sB],0.25)
        for n in NN: SH[n],C[n],_ = bcp(SH[n],C[n],α_SH)
        for nA,nB in EDGES: SH[nA],SH[nB],_ = bcp(SH[nA],SH[nB],α_SH)

        anchor_fires = 0
        for n in NN:
            φ_c = pof(C[n]); φ_o = pof(ANCHORS[n])
            d   = abs(φ_c - φ_o)
            if d > np.pi: d = 2*np.pi - d
            if d > θ_DRIFT:
                cs = α_ANCHOR_MAX*(d-θ_DRIFT)/(np.pi-θ_DRIFT)
                MIRRORS[n],_,_ = bcp(MIRRORS[n],ANCHORS[n],0.20)
                C[n],_,_       = bcp(C[n],MIRRORS[n],min(cs,α_ANCHOR_MAX))
                anchor_fires  += 1
            else:
                MIRRORS[n],_,_ = bcp(MIRRORS[n],ANCHORS[n],0.03)

        for n in NN: C[n] = depolarize(C[n], NOISE_P)
        for n in NN:
            srx,sry,_ = bloch(SEM[n])
            C[n],_,_ = bcp(C[n], ss(np.arctan2(sry,srx)), α_SEM)
        for nA,nB in EDGES:
            d = np.random.uniform(-α_DITHER, α_DITHER)
            α_eff = max(0.20, min(0.80, C_alphas[(nA,nB)]+d))
            C[nA],C[nB],_ = bcp(C[nA],C[nB],α_eff)

        gc      = [n for n in NN if NODE_DATA[n]["family"]=="GodCore"]
        best_gc = max(gc, key=lambda n: coh(C[n]))
        for n in gc:
            if n != best_gc: C[n],_,_ = bcp(C[n],C[best_gc],α_GC)
        prev = None
        for n in NN:
            if prev is not None: C[n],_,_ = bcp(C[n],ss(prev),α_D)
            rx,ry,_ = bloch(C[n]); prev = np.arctan2(ry,rx)

        id_sc   = [abs(np.cos((pof(C[n])-pof(ANCHORS[n]))/2)) for n in NN]
        id_pres = float(np.mean(id_sc))
        mean_W  = float(np.mean([wigner_min(C[n]) for n in NN]))

        ep_rewards, ep_wa, ep_gr, ep_texts = {}, [], [], {}
        for n in NN:
            ng_t, bg_t = ngrams[n]
            txt = gen_text(C[n], ng_t, bg_t, length=gen_len, temp=T_LANG)
            r, ph, ch, gr, wa = score_text(txt, NODE_PERSONAL[n], GRAMMAR_PATTERNS, epoch, epochs)
            nb = 0.045*5*prog
            srx,sry,_ = bloch(SEM[n]); crx,cry,_ = bloch(C[n])
            sb = 2.0*((srx*crx+sry*cry+1)/2)*prog
            ib = 2.0*id_pres*prog
            ep_rewards[n] = r+nb+sb+ib
            ep_wa.append(wa); ep_gr.append(len(gr))
            ep_texts[n]   = (txt, ph, ch, gr, wa)

        mr = max(float(np.mean(list(ep_rewards.values()))), 0.1)
        for e in EDGES: C_alphas[e] = max(AF, min(0.75, AF+0.10*(ep_rewards[e[0]]/mr-1.0)))
        rseed = ss(np.pi * min(mr/20.0, 1.0))
        for g in F_names: F_states[g],_,_ = bcp(F_states[g],rseed,AF)

        wam = float(np.mean(ep_wa))
        history["word_acc"].append(round(wam*100,2))
        history["mean_wigner"].append(round(mean_W,4))
        history["identity"].append(round(id_pres,4))
        history["guard_health"].append(round(guard_coh,4))
        history["anchor_fires"].append(anchor_fires)

        if wam > best_wac:
            best_wac=wam; best_out={n:ep_texts[n] for n in NN}; best_ep=epoch

        if verbose and (epoch%20==0 or epoch==epochs-1):
            print(f"Ep {epoch:3d} | W={mean_W:.3f} | acc={wam*100:.0f}% | id={id_pres:.3f} | fires={anchor_fires}")

    print(f"\nPeak accuracy: {best_wac*100:.1f}% @ epoch {best_ep}")
    print(f"Final W_min:   {history['mean_wigner'][-1]:.4f} (floor=-0.500)")

    with open("output/peig_core_training_results.json","w") as f:
        json.dump({"history": dict(history), "peak_epoch": best_ep,
                   "peak_acc": round(best_wac*100,2),
                   "voices": {n: best_out[n][0] for n in NN}}, f, indent=2)
    return C, history, best_out


if __name__ == "__main__":
    print("PEIG Core System — Paper XII Training Run")
    print("="*50)
    C_final, hist, voices = run_peig_training(epochs=200)
    print("\nFinal node voices:")
    for n,v in voices.items():
        words = [w for w in v[0].split() if "".join(c for c in w if c.isalpha()) in VOCAB_SET]
        print(f"  {n:10s}: '{' '.join(words[:8])}'")
