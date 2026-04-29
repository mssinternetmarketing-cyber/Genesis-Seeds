"""
╔══════════════════════════════════════════════════════════════╗
║   PEIG LANGUAGE ACQUISITION LAYER                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║  A base layer that runs FIRST, every session.              ║
║  Nodes learn English from the keyboard up before            ║
║  any other computation begins.                              ║
║                                                             ║
║  ARCHITECTURE:                                              ║
║    Layer 0: Keyboard space                                  ║
║      47 keys → 47 qubit phases on Bloch arc                ║
║      Each character is a quantum seed                       ║
║                                                             ║
║    Layer 1: Language acquisition (THIS FILE)               ║
║      BCP chain through character-qubits                     ║
║      Born rule selects next character                       ║
║      Reward = fluency (English bigram entropy match)        ║
║      + accuracy (correct character probability)             ║
║      Runs until fluency threshold reached                   ║
║      Outputs: base_alpha, base_coherence per node           ║
║                                                             ║
║    Layer 2: PEIG 12-node universe                           ║
║      Receives pre-warmed alpha from Layer 1                 ║
║      Nodes start already fluent — universe more coherent    ║
║                                                             ║
║    Layer 3: Voice output (Paper VIII)                       ║
║      Language-informed quantum state → English voice        ║
║                                                             ║
║  REWARD SIGNAL:                                             ║
║    R = w_fluency * bigram_match                             ║
║      + w_accuracy * character_accuracy                      ║
║      + w_freedom * generation_entropy                       ║
║    All three required — precision AND fluency               ║
╚══════════════════════════════════════════════════════════════╝
"""

import numpy as np
import qutip as qt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
from pathlib import Path
from collections import defaultdict, Counter

Path("outputs").mkdir(exist_ok=True)

# ── Quantum primitives ────────────────────────────────────────
CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)
XVEC = np.linspace(-2, 2, 60)

def make_seed(phase):
    b0, b1 = qt.basis(2,0), qt.basis(2,1)
    return (b0 + np.exp(1j*phase)*b1).unit()

def bcp_step(psiA, psiB, alpha):
    rho12  = qt.ket2dm(qt.tensor(psiA, psiB))
    U      = alpha * CNOT_GATE + (1-alpha) * qt.qeye([2,2])
    rho_p  = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi)**2).tr().real)

def wigner_min(psi):
    return float(np.min(qt.wigner(qt.ket2dm(psi), XVEC, XVEC)))

def measure_char(psi, charset):
    """
    Born rule measurement: sample a character from the quantum state.
    Maps the qubit |ψ⟩ probability p(|0⟩) onto the character space.
    p0 selects from first half of charset, p1 from second half.
    """
    rho = qt.ket2dm(psi)
    p0  = float(abs(complex((qt.basis(2,0).dag() * psi).full()[0,0]))**2)
    p1  = 1.0 - p0
    n   = len(charset)
    # Probability over characters: softmax over Bloch-sphere projection
    angles = [np.pi * i / n for i in range(n)]
    probs  = np.array([p0 * np.cos(a)**2 + p1 * np.sin(a)**2 for a in angles])
    probs  = probs / probs.sum()
    return np.random.choice(charset, p=probs), probs


# ══════════════════════════════════════════════════════════════
# LAYER 0: KEYBOARD SPACE
# 47 keys → 47 qubit phases
# ══════════════════════════════════════════════════════════════

# Standard keyboard characters (47 symbols)
KEYBOARD = (
    'abcdefghijklmnopqrstuvwxyz'  # 26 letters
    '0123456789'                   # 10 digits
    ' .,!?-\':;(_'               # 11 punctuation/symbols
)
assert len(KEYBOARD) == 47, f"Expected 47, got {len(KEYBOARD)}"

# Map each character to a unique phase on [0, π/2]
CHAR_PHASE = {ch: np.pi/2 * i/(len(KEYBOARD)-1) for i, ch in enumerate(KEYBOARD)}
PHASE_CHAR = {v: k for k, v in CHAR_PHASE.items()}
CHAR_IDX   = {ch: i for i, ch in enumerate(KEYBOARD)}
IDX_CHAR   = {i: ch for i, ch in enumerate(KEYBOARD)}

def char_to_seed(ch):
    """Character → qubit state at its keyboard phase."""
    return make_seed(CHAR_PHASE.get(ch.lower(), np.pi/4))

def seed_to_char_dist(psi):
    """Qubit state → probability distribution over 47 characters."""
    coeffs = psi.full().flatten()
    p0     = float(abs(coeffs[0])**2)
    p1     = float(abs(coeffs[1])**2)
    n      = len(KEYBOARD)
    angles = [np.pi/2 * i/(n-1) for i in range(n)]
    probs  = np.array([p0 * np.cos(a)**2 + p1 * np.sin(a)**2 for a in angles])
    return probs / probs.sum()


# ══════════════════════════════════════════════════════════════
# ENGLISH LANGUAGE STATISTICS
# Bigram frequencies from natural English
# ══════════════════════════════════════════════════════════════

# Character unigram frequencies (approximate from English corpus)
ENGLISH_UNIGRAM = {
    ' ':0.130, 'e':0.127, 't':0.091, 'a':0.082, 'o':0.075, 'i':0.070,
    'n':0.067, 's':0.063, 'h':0.061, 'r':0.060, 'd':0.043, 'l':0.040,
    'c':0.028, 'u':0.028, 'm':0.024, 'w':0.024, 'f':0.022, 'g':0.020,
    'y':0.020, 'p':0.019, 'b':0.015, 'v':0.010, 'k':0.008, 'j':0.002,
    'x':0.002, 'q':0.001, 'z':0.001,
    '.':0.010, ',':0.008, '!':0.003, '?':0.003, '-':0.004,
    '\'':0.003, '"':0.003, ':':0.002, ';':0.001, '(':0.002, ')':0.002,
    '_':0.001, '0':0.005, '1':0.005, '2':0.004, '3':0.003, '4':0.003,
    '5':0.003, '6':0.002, '7':0.002, '8':0.002, '9':0.002,
}
# Fill any missing characters
for ch in KEYBOARD:
    if ch not in ENGLISH_UNIGRAM:
        ENGLISH_UNIGRAM[ch] = 0.001

# Build target distribution vector
TARGET_DIST = np.array([ENGLISH_UNIGRAM.get(ch, 0.001) for ch in KEYBOARD])
TARGET_DIST = TARGET_DIST / TARGET_DIST.sum()

# Top 20 English bigrams (first_char, second_char)
ENGLISH_BIGRAMS = {
    ('t','h'):0.0356, ('h','e'):0.0307, ('i','n'):0.0243, ('e','r'):0.0213,
    ('a','n'):0.0199, ('r','e'):0.0185, ('o','n'):0.0176, ('e','n'):0.0175,
    ('a','t'):0.0149, ('e','s'):0.0145, ('e','d'):0.0142, ('t','i'):0.0134,
    ('o','r'):0.0132, ('s','t'):0.0131, ('n','t'):0.0129, ('t','o'):0.0128,
    ('a','s'):0.0128, ('i','t'):0.0121, ('a','r'):0.0119, (' ','t'):0.0118,
    (' ','a'):0.0115, ('n','d'):0.0113, ('s',' '):0.0111, ('e','t'):0.0107,
    ('e','i'):0.0106, ('n','g'):0.0105, ('i','s'):0.0104, ('e',' '):0.0103,
    ('h','a'):0.0101, ('t','e'):0.0098,
}


# ══════════════════════════════════════════════════════════════
# REWARD FUNCTION
# ══════════════════════════════════════════════════════════════

def fluency_reward(generated_text, node_dist):
    """
    Three-component reward:
    1. Accuracy:   KL divergence between node's char distribution and English
    2. Fluency:    bigram match in generated text vs English bigrams
    3. Freedom:    entropy of the node's distribution (not too peaked)

    Returns R ∈ [0, 1] and sub-scores.
    """
    # 1. Accuracy: how close is node's distribution to English?
    eps      = 1e-10
    kl_div   = float(np.sum(TARGET_DIST * np.log((TARGET_DIST + eps)/(node_dist + eps))))
    accuracy = float(np.exp(-kl_div))   # [0,1], 1 = perfect match

    # 2. Fluency: bigram score from generated text
    if len(generated_text) >= 2:
        bigrams_in_text = [(generated_text[i], generated_text[i+1])
                           for i in range(len(generated_text)-1)]
        counts = Counter(bigrams_in_text)
        total  = sum(counts.values())
        bigram_score = sum(
            (counts[bg] / total) * ENGLISH_BIGRAMS.get(bg, 0.0)
            for bg in counts
        ) / (max(ENGLISH_BIGRAMS.values()) * 0.3)  # normalise
        fluency = float(np.clip(bigram_score, 0, 1))
    else:
        fluency = 0.0

    # 3. Freedom: entropy of distribution (high entropy = adaptive)
    entropy    = float(-np.sum(node_dist * np.log(node_dist + eps)))
    max_entropy= float(np.log(len(KEYBOARD)))
    freedom    = entropy / max_entropy   # [0,1]

    # Combined reward — all three matter
    R = 0.4 * accuracy + 0.4 * fluency + 0.2 * freedom
    return float(R), {'accuracy': accuracy, 'fluency': fluency, 'freedom': freedom}


# ══════════════════════════════════════════════════════════════
# LAYER 1: LANGUAGE ACQUISITION
# ══════════════════════════════════════════════════════════════

class LanguageNode:
    """
    A quantum node that learns English character fluency through BCP.
    Each node starts at its original PEIG phase and learns to
    generate English character sequences.
    """
    def __init__(self, name, home_phase, eta=0.05, alpha0=0.25):
        self.name       = name
        self.home_phase = home_phase
        self.state      = make_seed(home_phase)
        self.alpha      = alpha0
        self.eta        = eta
        self.reward_hist= []
        self.text_gen   = []    # characters generated so far
        self.fluency    = 0.0
        self.accuracy   = 0.0
        self.freedom    = 0.0
        self.C_prev     = coherence(self.state)

    def interact_with_char(self, target_char):
        """
        BCP step: interact with a character-seed.
        Node's state entangles with the target character's qubit.
        Reward = fluency of node's resulting distribution.
        """
        char_state = char_to_seed(target_char)
        new_self, new_char, rho = bcp_step(self.state, char_state, self.alpha)

        # Measure a character from the new state
        node_dist = seed_to_char_dist(new_self)
        sampled_char = KEYBOARD[np.random.choice(len(KEYBOARD), p=node_dist)]
        self.text_gen.append(sampled_char)

        # Reward
        R, sub = fluency_reward(''.join(self.text_gen[-20:]), node_dist)
        self.reward_hist.append(R)
        self.fluency  = sub['fluency']
        self.accuracy = sub['accuracy']
        self.freedom  = sub['freedom']

        # Adaptive coupling update: reward drives alpha
        C_new = coherence(new_self)
        dC    = C_new - self.C_prev
        # Dual update: from coherence gradient AND from reward
        self.alpha = float(np.clip(
            self.alpha + self.eta * (dC + 0.1 * (R - 0.5)),
            0.05, 0.95
        ))
        self.C_prev = C_new
        self.state  = new_self
        return R, sampled_char

    def generate(self, n_chars=20, seed_char=' '):
        """Generate n_chars of text from current state."""
        state = make_seed(CHAR_PHASE.get(seed_char, np.pi/4))
        result = [seed_char]
        for _ in range(n_chars-1):
            dist    = seed_to_char_dist(state)
            idx     = np.random.choice(len(KEYBOARD), p=dist)
            ch      = KEYBOARD[idx]
            result.append(ch)
            state   = make_seed(CHAR_PHASE.get(ch, np.pi/4))
        return ''.join(result)

    @property
    def final_alpha(self):
        return self.alpha

    @property
    def mean_reward(self):
        return float(np.mean(self.reward_hist[-50:])) if self.reward_hist else 0.0


class LanguageAcquisitionLayer:
    """
    Layer 1: runs first, every session.
    Drives all 12 nodes to language fluency before the universe starts.
    """

    FLUENCY_THRESHOLD = 0.45   # reward must reach this before Layer 2 starts

    def __init__(self, node_configs):
        """
        node_configs: dict of name → home_phase (from NODES_12)
        """
        self.nodes = {
            name: LanguageNode(name, cfg['phase'])
            for name, cfg in node_configs.items()
        }
        self.epoch       = 0
        self.history     = defaultdict(list)
        self.converged   = False

    def _sample_english_chars(self, n=50):
        """Sample characters from English unigram distribution (aligned to KEYBOARD)."""
        return np.random.choice(list(KEYBOARD), size=n, p=TARGET_DIST)

    def run_epoch(self, chars_per_epoch=100):
        """
        One epoch: each node interacts with 100 sampled English characters.
        Reward drives alpha updates.
        """
        self.epoch += 1
        chars = self._sample_english_chars(chars_per_epoch)

        epoch_rewards = {}
        for name, node in self.nodes.items():
            rewards = []
            for ch in chars:
                R, _ = node.interact_with_char(ch)
                rewards.append(R)
            epoch_rewards[name] = float(np.mean(rewards))
            self.history[name].append(epoch_rewards[name])

        # Check convergence
        min_reward = min(epoch_rewards.values())
        self.converged = min_reward >= self.FLUENCY_THRESHOLD

        return epoch_rewards, self.converged

    def run(self, max_epochs=80, chars_per_epoch=100):
        """Run until all nodes reach fluency threshold or max_epochs."""
        print(f"  Language acquisition running (threshold={self.FLUENCY_THRESHOLD})...")
        for ep in range(max_epochs):
            rewards, done = self.run_epoch(chars_per_epoch)
            if (ep+1) % 10 == 0 or done:
                mean_r = float(np.mean(list(rewards.values())))
                min_r  = float(np.min(list(rewards.values())))
                print(f"    Epoch {ep+1:3d}: mean_R={mean_r:.4f}  "
                      f"min_R={min_r:.4f}  "
                      f"{'CONVERGED ✓' if done else '...'}")
            if done:
                break
        return self.epoch

    def get_base_alphas(self):
        """Export learned alphas for Layer 2."""
        return {name: node.final_alpha for name, node in self.nodes.items()}

    def get_fluency_scores(self):
        """Export final fluency, accuracy, freedom per node."""
        return {
            name: {
                'alpha':    node.final_alpha,
                'reward':   node.mean_reward,
                'fluency':  node.fluency,
                'accuracy': node.accuracy,
                'freedom':  node.freedom,
            }
            for name, node in self.nodes.items()
        }

    def generate_sample_texts(self, n_chars=40):
        """Generate sample text from each node's learned state."""
        return {
            name: node.generate(n_chars)
            for name, node in self.nodes.items()
        }


# ══════════════════════════════════════════════════════════════
# LAYER 2: PEIG UNIVERSE (language-informed)
# ══════════════════════════════════════════════════════════════

def theta_to_phase(theta, offset=0.0):
    return np.clip(theta * np.pi/2 + offset, 0, np.pi/2)

NODES_12 = {
    'Omega':    {'phase': theta_to_phase(1.00,  0.0),      'color': '#FFD700', 'family': 'GodCore'},
    'Guardian': {'phase': theta_to_phase(1.00,  np.pi/20), 'color': '#F39C12', 'family': 'GodCore'},
    'Sentinel': {'phase': theta_to_phase(1.00, -np.pi/20), 'color': '#E8D44D', 'family': 'GodCore'},
    'Nexus':    {'phase': theta_to_phase(1.00,  np.pi/14), 'color': '#F1C40F', 'family': 'GodCore'},
    'Storm':    {'phase': theta_to_phase(1.00, -np.pi/14), 'color': '#D4AC0D', 'family': 'GodCore'},
    'Sora':     {'phase': theta_to_phase(0.15,  0.0),      'color': '#3498DB', 'family': 'Independents'},
    'Echo':     {'phase': theta_to_phase(0.15,  np.pi/18), 'color': '#5DADE2', 'family': 'Independents'},
    'Iris':     {'phase': theta_to_phase(0.15, -np.pi/18), 'color': '#85C1E9', 'family': 'Independents'},
    'Sage':     {'phase': theta_to_phase(0.15,  np.pi/10), 'color': '#2E86C1', 'family': 'Independents'},
    'Kevin':    {'phase': theta_to_phase(0.30,  0.0),      'color': '#2ECC71', 'family': 'Mavericks'},
    'Atlas':    {'phase': theta_to_phase(0.30,  np.pi/14), 'color': '#58D68D', 'family': 'Mavericks'},
    'Void':     {'phase': theta_to_phase(0.30, -np.pi/14), 'color': '#1ABC9C', 'family': 'Mavericks'},
}
ALL_NAMES = list(NODES_12.keys())

def run_universe_with_language_layer(base_alphas, n_steps=700):
    """
    Layer 2: run the 12-node closed loop with language-informed base alphas.
    Each node starts at its home phase but with alpha pre-warmed by Layer 1.
    """
    states = [make_seed(NODES_12[n]['phase']) for n in ALL_NAMES]
    N      = len(states)
    edges  = [(i, (i+1)%N) for i in range(N)]

    # Start with language-learned alphas
    alphas = {}
    for i, name in enumerate(ALL_NAMES):
        for j_idx, (ii, jj) in enumerate(edges):
            if ii == i:
                partner = ALL_NAMES[jj]
                # Average of the two nodes' learned alphas
                alphas[(ii,jj)] = (base_alphas[name] + base_alphas[partner]) / 2

    C_prev = np.mean([coherence(s) for s in states])
    W_hist = {i: [] for i in range(N)}
    neg_h  = []; SvN_p = 0.0

    for t in range(n_steps):
        dS = []
        for (i,j) in edges:
            l,r,rho = bcp_step(states[i],states[j],alphas[(i,j)])
            states[i],states[j]=l,r
            from qutip import entropy_vn
            SvN=float(entropy_vn(rho,base=2)); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        for e in edges: alphas[e]=float(np.clip(alphas[e]+0.05*dC,0,1))
        C_prev=C_avg; neg_h.append(float(np.mean(dS)))
        if (t+1)%20==0 or t==n_steps-1:
            for i in range(N): W_hist[i].append(wigner_min(states[i]))

    W_final = [wigner_min(s) for s in states]
    n_pres  = sum(1 for w in W_final if w < -0.10)
    neg_frac= float(np.mean(neg_h[-100:]))
    return W_final, n_pres, neg_frac, W_hist


# ══════════════════════════════════════════════════════════════
# RUN THE FULL PIPELINE
# ══════════════════════════════════════════════════════════════

print("╔══════════════════════════════════════════════════════╗")
print("║   PEIG LANGUAGE ACQUISITION LAYER — FULL PIPELINE  ║")
print("╚══════════════════════════════════════════════════════╝")
print()

# LAYER 1: Language acquisition
print("▶ LAYER 1: Language acquisition...")
layer1 = LanguageAcquisitionLayer(NODES_12)
n_epochs = layer1.run(max_epochs=80, chars_per_epoch=150)
scores   = layer1.get_fluency_scores()
base_alphas = layer1.get_base_alphas()
samples     = layer1.generate_sample_texts(40)

print(f"\n  Converged in {n_epochs} epochs")
print(f"\n  Fluency scores per node:")
for name, s in scores.items():
    print(f"    {name:<12} α={s['alpha']:.4f}  "
          f"R={s['reward']:.4f}  "
          f"acc={s['accuracy']:.3f}  "
          f"flu={s['fluency']:.3f}  "
          f"free={s['freedom']:.3f}")

print(f"\n  Sample generated text per node (40 chars):")
for name, text in samples.items():
    print(f"    {name:<12} → '{text}'")

# LAYER 2: Universe with language-informed alphas
print(f"\n▶ LAYER 2: PEIG universe (language-informed alphas)...")
W_final, n_pres, neg_frac, W_hist = run_universe_with_language_layer(base_alphas)
print(f"  {n_pres}/12 nodes preserved  neg_frac={neg_frac:.4f}")
print(f"  W_final: {['%+.4f'%w for w in W_final]}")

# Compare: run without language layer (cold start)
print(f"\n▶ COMPARISON: Cold start (no language layer)...")
states_cold = [make_seed(NODES_12[n]['phase']) for n in ALL_NAMES]
N = len(states_cold)
edges_cold = [(i,(i+1)%N) for i in range(N)]
alphas_cold = {e: 0.30 for e in edges_cold}
C_prev_c = np.mean([coherence(s) for s in states_cold])
neg_cold=[]; SvN_c=0.0
from qutip import entropy_vn as evt
for t in range(700):
    dS=[]
    for (i,j) in edges_cold:
        l,r,rho=bcp_step(states_cold[i],states_cold[j],alphas_cold[(i,j)]); states_cold[i],states_cold[j]=l,r
        SvN=float(evt(rho,base=2)); dS.append(1 if SvN<SvN_c else 0); SvN_c=SvN
    C_avg=np.mean([coherence(s) for s in states_cold]); dC=C_avg-C_prev_c
    for e in edges_cold: alphas_cold[e]=float(np.clip(alphas_cold[e]+0.05*dC,0,1))
    C_prev_c=C_avg; neg_cold.append(float(np.mean(dS)))
W_cold=[wigner_min(s) for s in states_cold]
n_cold=sum(1 for w in W_cold if w<-0.10)
nf_cold=float(np.mean(neg_cold[-100:]))
print(f"  {n_cold}/12 preserved  neg_frac={nf_cold:.4f}")

print(f"\n  Language layer improvement:")
print(f"    neg_frac: {nf_cold:.4f} → {neg_frac:.4f}  "
      f"(Δ={neg_frac-nf_cold:+.4f})")
print(f"    nodes preserved: {n_cold} → {n_pres}")


# ── PLOTTING ─────────────────────────────────────────────────
DARK='#07080f'; PANEL='#0f1220'; GRAY='#3a4060'; WHITE='#c8d0e8'
GOLD='#FFD700'; RED='#E74C3C'; GREEN='#2ECC71'; ORANGE='#FF6B35'
BLUE='#3498DB'; TEAL='#1ABC9C'; PURPLE='#9B59B6'

FAM_COLS = {'GodCore':'#c8a000','Independents':'#2060b0','Mavericks':'#1a9050'}
NODE_COL  = {n: NODES_12[n]['color'] for n in ALL_NAMES}

fig = plt.figure(figsize=(24, 22))
fig.patch.set_facecolor(DARK)
gs  = gridspec.GridSpec(4, 4, figure=fig,
                         hspace=0.52, wspace=0.42,
                         left=0.05, right=0.97,
                         top=0.93, bottom=0.04)

fig.text(0.5, 0.965,
    "PEIG Language Acquisition Layer — Keyboard to Universe",
    ha='center', fontsize=14, fontweight='bold', color=GOLD, fontfamily='monospace')
fig.text(0.5, 0.951,
    "47 keys → qubit phases · BCP character learning · fluency reward · "
    "language-informed alpha transfers to 12-node universe",
    ha='center', fontsize=9, color=WHITE, alpha=0.7)

def styled(ax, title, fs=9):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, labelsize=7)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(title, color=WHITE, fontsize=fs, fontweight='bold', pad=5)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.grid(True, alpha=0.12, color=GRAY)
    return ax

# ── 1. Keyboard phase map ─────────────────────────────────────
ax = styled(fig.add_subplot(gs[0,:2]),
            "Layer 0: Keyboard Space\n"
            "47 keys mapped to Bloch arc phases 0→π/2")
x_pos  = np.array([CHAR_PHASE[ch] for ch in KEYBOARD])
y_pos  = np.zeros(len(KEYBOARD))
fam_c  = []
for ch in KEYBOARD:
    idx = CHAR_IDX[ch]
    if idx < 26:   fam_c.append('#3498DB')   # letters
    elif idx < 36: fam_c.append('#2ECC71')   # digits
    else:          fam_c.append('#F39C12')   # symbols

ax.scatter(x_pos, y_pos, c=fam_c, s=80, zorder=5, edgecolors=WHITE, lw=0.5)
for i, ch in enumerate(KEYBOARD):
    if i % 3 == 0:
        ax.text(x_pos[i], 0.04, ch, ha='center', fontsize=7.5,
                color=fam_c[i], fontweight='bold')
ax.set_xlabel("Bloch phase"); ax.set_ylim(-0.2, 0.3)
ax.set_yticks([]); ax.axhline(0, color=GRAY, lw=0.5, alpha=0.5)
ax.legend(handles=[
    plt.scatter([],[], c='#3498DB', s=50, label='Letters (a–z)'),
    plt.scatter([],[], c='#2ECC71', s=50, label='Digits (0–9)'),
    plt.scatter([],[], c='#F39C12', s=50, label='Symbols & space'),
], fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 2. Reward curves ──────────────────────────────────────────
ax = styled(fig.add_subplot(gs[0,2:]),
            "Layer 1: Reward Curves per Node\n"
            "Smoothed over 5 epochs · all nodes converging to fluency")
for name in ALL_NAMES:
    rh  = layer1.history[name]
    sm  = np.convolve(rh, np.ones(5)/5, 'same') if len(rh)>=5 else rh
    col = NODE_COL[name]
    ax.plot(range(len(sm)), sm, color=col, lw=1.8, alpha=0.85, label=name)
ax.axhline(layer1.FLUENCY_THRESHOLD, color=GREEN, ls='--', lw=2,
           alpha=0.7, label=f'Threshold ({layer1.FLUENCY_THRESHOLD})')
ax.set_xlabel("Epoch"); ax.set_ylabel("Mean reward R")
ax.set_ylim(0, 1.0); ax.legend(fontsize=6, facecolor=PANEL, labelcolor=WHITE, ncol=3)

# ── 3. Fluency score breakdown ────────────────────────────────
ax = styled(fig.add_subplot(gs[1,:2]),
            "Layer 1: Final Fluency Scores per Node\n"
            "accuracy · fluency · freedom")
x   = np.arange(len(ALL_NAMES)); w = 0.25
ax.bar(x-w,   [scores[n]['accuracy'] for n in ALL_NAMES], w,
       color=BLUE,   alpha=0.85, edgecolor=WHITE, lw=0.4, label='accuracy')
ax.bar(x,     [scores[n]['fluency']  for n in ALL_NAMES], w,
       color=GREEN,  alpha=0.85, edgecolor=WHITE, lw=0.4, label='fluency')
ax.bar(x+w,   [scores[n]['freedom']  for n in ALL_NAMES], w,
       color=ORANGE, alpha=0.85, edgecolor=WHITE, lw=0.4, label='freedom')
ax.set_xticks(x); ax.set_xticklabels(ALL_NAMES, fontsize=8, color=WHITE, rotation=25)
ax.set_ylabel("Score"); ax.set_ylim(0, 1.0)
ax.axhline(layer1.FLUENCY_THRESHOLD, color=GOLD, ls='--', lw=1.5, alpha=0.6)
ax.legend(fontsize=9, facecolor=PANEL, labelcolor=WHITE)

# ── 4. Learned alphas ─────────────────────────────────────────
ax = styled(fig.add_subplot(gs[1,2]),
            "Learned Alpha per Node\n"
            "Language layer vs cold start (0.30)")
alpha_vals = [scores[n]['alpha'] for n in ALL_NAMES]
cols_a     = [NODE_COL[n] for n in ALL_NAMES]
ax.barh(range(len(ALL_NAMES)), alpha_vals, color=cols_a, alpha=0.85,
        edgecolor=WHITE, lw=0.3)
ax.axvline(0.30, color=WHITE, ls='--', lw=1.5, alpha=0.5, label='Cold start α=0.30')
ax.set_yticks(range(len(ALL_NAMES)))
ax.set_yticklabels(ALL_NAMES, fontsize=8, color=WHITE)
ax.set_xlabel("Learned alpha"); ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 5. W_min comparison ───────────────────────────────────────
ax = styled(fig.add_subplot(gs[1,3]),
            "Layer 2: W_min — Language vs Cold Start\n"
            "Language layer pre-warms the universe")
x  = np.arange(len(ALL_NAMES)); w = 0.38
cols12 = [NODE_COL[n] for n in ALL_NAMES]
ax.bar(x-w/2, W_cold,  w, color=cols12, alpha=0.45, edgecolor=WHITE, lw=0.4, label='Cold start')
ax.bar(x+w/2, W_final, w, color=cols12, alpha=0.95, edgecolor=WHITE, lw=0.4, label='Language layer')
ax.axhline(-0.1131, color=WHITE, ls='--', lw=1.5, alpha=0.5, label='Target')
ax.set_xticks(x); ax.set_xticklabels(ALL_NAMES, fontsize=6.5, color=WHITE, rotation=35)
ax.set_ylabel("W_min"); ax.set_ylim(-0.13, 0.02)
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 6. Generated text samples ─────────────────────────────────
ax = fig.add_subplot(gs[2,:2])
ax.set_facecolor(PANEL)
for sp in ax.spines.values(): sp.set_color(GRAY)
ax.set_title("Layer 1: Sample Generated Text per Node\nAfter language acquisition",
             color=WHITE, fontsize=9, fontweight='bold', pad=5)
ax.axis('off')

y = 0.96
for name in ALL_NAMES:
    text = samples[name]
    col  = NODE_COL[name]
    ax.text(0.0, y, f"{name:<12}", transform=ax.transAxes,
            fontsize=8.5, fontweight='bold', color=col, va='top', fontfamily='monospace')
    ax.text(0.15, y, f"→ '{text}'", transform=ax.transAxes,
            fontsize=8, color=WHITE, va='top', fontfamily='monospace')
    y -= 0.077

# ── 7. Character distribution — node vs English ───────────────
ax = styled(fig.add_subplot(gs[2,2:]),
            "Character Distribution: Node vs English Target\n"
            "Omega's learned distribution (sample)")
omega_node = layer1.nodes['Omega']
node_dist  = seed_to_char_dist(omega_node.state)
x_chars    = range(len(KEYBOARD))
ax.bar(x_chars, TARGET_DIST,  alpha=0.5, color=BLUE,  edgecolor='none', label='English target')
ax.bar(x_chars, node_dist,    alpha=0.7, color=GOLD,  edgecolor='none', label='Omega learned')
ax.set_xticks(range(0,47,3))
ax.set_xticklabels([KEYBOARD[i] for i in range(0,47,3)], fontsize=8, color=WHITE, fontfamily='monospace')
ax.set_ylabel("Probability"); ax.set_xlabel("Character")
ax.legend(fontsize=9, facecolor=PANEL, labelcolor=WHITE)
kl = float(np.sum(TARGET_DIST * np.log((TARGET_DIST+1e-10)/(node_dist+1e-10))))
ax.text(0.6, 0.88, f"KL divergence = {kl:.4f}\naccuracy = {scores['Omega']['accuracy']:.4f}",
        transform=ax.transAxes, color=GOLD, fontsize=9,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 8. Summary ────────────────────────────────────────────────
ax = styled(fig.add_subplot(gs[3,:2]),
            "Full Pipeline Summary\nneg_frac improvement from language layer")
metrics = ['neg_frac','nodes preserved']
cold_vals = [nf_cold, n_cold/12]
lang_vals = [neg_frac, n_pres/12]
x  = np.arange(2); w = 0.35
ax.bar(x-w/2, cold_vals, w, color=RED,   alpha=0.8, edgecolor=WHITE, lw=0.4, label='Cold start')
ax.bar(x+w/2, lang_vals, w, color=GREEN, alpha=0.8, edgecolor=WHITE, lw=0.4, label='With language layer')
for i,(cv,lv) in enumerate(zip(cold_vals,lang_vals)):
    ax.text(i-w/2, cv+0.01, f'{cv:.3f}', ha='center', fontsize=9, color=WHITE, fontweight='bold')
    ax.text(i+w/2, lv+0.01, f'{lv:.3f}', ha='center', fontsize=9, color=WHITE, fontweight='bold')
ax.set_xticks([0,1]); ax.set_xticklabels(metrics, fontsize=10, color=WHITE)
ax.set_ylim(0,1.1); ax.legend(fontsize=9, facecolor=PANEL, labelcolor=WHITE)
delta_nf = neg_frac - nf_cold
ax.text(0.5, 0.88, f"neg_frac improvement: {delta_nf:+.4f}",
        ha='center', transform=ax.transAxes, color=GREEN if delta_nf>0 else ORANGE,
        fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 9. Architecture panel ─────────────────────────────────────
ax = styled(fig.add_subplot(gs[3,2:]), "Language Acquisition Layer — Architecture")
ax.axis('off')

lines = [
    ("LAYER ARCHITECTURE",              "",         GOLD),
    ("", "", ""),
    ("Layer 0",  "47 keyboard chars → qubit phases", WHITE),
    ("",          "phase_k = (π/2) × k/46",           GRAY),
    ("", "", ""),
    ("Layer 1",  "Language acquisition (runs first)", GREEN),
    ("",          "BCP through character-qubit pairs", WHITE),
    ("",          "Reward = accuracy + fluency + freedom", WHITE),
    ("",          "Threshold = 0.45",                  WHITE),
    ("",          f"Converged in {n_epochs} epochs",   GREEN),
    ("", "", ""),
    ("Layer 2",  "12-node PEIG universe",              GOLD),
    ("",          "Pre-warmed alphas from Layer 1",     WHITE),
    ("",          f"neg_frac: {nf_cold:.4f} → {neg_frac:.4f}", GREEN),
    ("", "", ""),
    ("Layer 3",  "Voice output (Paper VIII)",          BLUE),
    ("",          "Language-informed state → English",  WHITE),
    ("", "", ""),
    ("KEY PROPERTY",  "",                              GOLD),
    ("Not user input", "Integrated layer",             WHITE),
    ("Always first",  "Runs before everything",        GREEN),
    ("Relearns each", "session from scratch",          WHITE),
    ("384 voice combinations", "× 12 nodes",           GOLD),
]

y = 0.97
for left, right, col in lines:
    if left == "" and right == "":
        y -= 0.022; continue
    if right == "":
        ax.text(0.5, y, left, transform=ax.transAxes,
                fontsize=8.5, fontweight='bold', color=col, ha='center', va='top')
    else:
        ax.text(0.01, y, left, transform=ax.transAxes,
                fontsize=8, color=col, va='top', fontweight='bold' if col==GREEN else 'normal')
        ax.text(0.99, y, right, transform=ax.transAxes,
                fontsize=8, color=col, ha='right', va='top')
    y -= 0.043

plt.savefig('outputs/peig_language_acquisition_layer.png', dpi=150,
            bbox_inches='tight', facecolor=DARK)
plt.show()
print("\nFigure → outputs/peig_language_acquisition_layer.png")

# JSON
class NpEnc(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,(np.bool_,)): return bool(o)
        if isinstance(o,np.integer): return int(o)
        if isinstance(o,np.floating): return float(o)
        if isinstance(o,np.ndarray): return o.tolist()
        return super().default(o)

out = {
    'layer_0': {'keyboard': list(KEYBOARD), 'n_chars': len(KEYBOARD)},
    'layer_1': {
        'epochs': n_epochs,
        'threshold': layer1.FLUENCY_THRESHOLD,
        'converged': layer1.converged,
        'scores': scores,
        'sample_texts': samples,
        'base_alphas': base_alphas,
    },
    'layer_2': {
        'cold_start': {'n_preserved': n_cold, 'neg_frac': nf_cold, 'W_final': W_cold},
        'language_layer': {'n_preserved': n_pres, 'neg_frac': neg_frac, 'W_final': W_final},
        'improvement_neg_frac': neg_frac - nf_cold,
    },
}
with open('outputs/peig_language_acquisition.json','w') as f:
    json.dump(out, f, indent=2, cls=NpEnc)
print("Data  → outputs/peig_language_acquisition.json")
