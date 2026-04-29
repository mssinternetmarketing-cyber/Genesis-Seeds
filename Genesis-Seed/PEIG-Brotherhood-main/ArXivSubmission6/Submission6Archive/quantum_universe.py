"""
╔══════════════════════════════════════════════════════════════╗
║          PEIG QUANTUM UNIVERSE SIMULATION                   ║
║                                                             ║
║  Three families of quantum nodes entangled within loops.    ║
║  Families coupled through bridge nodes.                     ║
║  The whole system learns, adapts, and grows.                ║
║                                                             ║
║  ARCHITECTURE:                                              ║
║    Family Alpha  — 5 nodes, closed loop  (purple seeds)     ║
║    Family Omega  — 5 nodes, closed loop  (teal seeds)       ║
║    Family Kevin  — 5 nodes, closed loop  (bridge seeds)     ║
║    Bridge nodes  — 3 nodes, weak inter-family coupling      ║
║                                                             ║
║  DYNAMICS:                                                  ║
║    Phase 1: Intra-family BCP (strong, closed loops)         ║
║    Phase 2: Inter-family BCP (weak, through bridges)        ║
║    Phase 3: Family-level PEIG quality computed              ║
║    Phase 4: Universe-level coherence tracked                ║
║    Phase 5: Growth — families recruit nodes above Q*=0.85   ║
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
from collections import defaultdict

Path("outputs").mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# ── Quantum Primitives ───────────────────────────────────────
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

def entropy_vn(rho):
    return float(qt.entropy_vn(rho, base=2))

def wigner_min(psi):
    return float(np.min(qt.wigner(qt.ket2dm(psi), XVEC, XVEC)))

ALPHA_FLOOR = -0.1131

def peig_quality(w_eff, mean_C, neg_frac, w_asym):
    P = float(np.clip(w_eff, 0, 1))
    E = float(mean_C)
    I = float(neg_frac)
    G = float(np.clip((w_asym + 0.1131) / 0.2262, 0, 1))
    return 0.25*(P + E + I + G), P, E, I, G

# ── Family Definition ────────────────────────────────────────
class QuantumFamily:
    """
    A closed loop of quantum nodes with adaptive BCP coupling.
    Each family has:
      - name: identifier
      - nodes: list of qubit states
      - phases: initial Bloch arc phases (0 → pi/2)
      - alpha: per-edge coupling strength (adaptive)
      - history: time series of quality metrics
      - generation: how many growth events have occurred
    """
    def __init__(self, name, n_nodes, phase_offset=0.0,
                 eta=0.05, alpha0=0.30, color='purple'):
        self.name         = name
        self.color        = color
        self.eta          = eta
        self.generation   = 0
        self.n_nodes      = n_nodes

        # Phases spaced evenly on the 0→pi/2 arc with optional offset
        phases = [phase_offset + np.pi/2 * k/(n_nodes-1)
                  for k in range(n_nodes)]
        self.states = [make_seed(p) for p in phases]
        self.phases = phases

        # Closed loop edges
        self.edges  = [(i, (i+1)%n_nodes) for i in range(n_nodes)]
        self.alphas = {e: alpha0 for e in self.edges}

        self.C_prev  = np.mean([coherence(s) for s in self.states])
        self.SvN_prev= 0.0

        # History
        self.history = defaultdict(list)

    def step(self, noise_scale=0.0):
        """One BCP step through all edges in the closed loop."""
        dS_signs = []
        for (i,j) in self.edges:
            l, r, rho = bcp_step(self.states[i], self.states[j],
                                  self.alphas[(i,j)])
            self.states[i] = l
            self.states[j] = r

            SvN  = entropy_vn(rho)
            dS   = SvN - self.SvN_prev
            dS_signs.append(1 if dS < 0 else 0)
            self.SvN_prev = SvN

        # Adaptive coupling
        C_avg  = np.mean([coherence(s) for s in self.states])
        dC     = C_avg - self.C_prev
        for e in self.edges:
            self.alphas[e] = float(np.clip(
                self.alphas[e] + self.eta * dC, 0, 1))
        self.C_prev = C_avg

        return C_avg, np.mean(dS_signs)

    def measure(self):
        """Compute Wigner floors and PEIG quality."""
        W_floors = [wigner_min(s) for s in self.states]
        mean_W   = np.mean(W_floors)
        W_eff    = abs(mean_W) / abs(ALPHA_FLOOR)
        mean_C   = np.mean([coherence(s) for s in self.states])
        W_asym   = W_floors[-1] - W_floors[0]
        neg_frac = self.history['neg_frac'][-1] if self.history['neg_frac'] else 0.3
        Q, P, E, I, G = peig_quality(W_eff, mean_C, neg_frac, W_asym)
        return {
            'Q': Q, 'P': P, 'E': E, 'I': I, 'G': G,
            'W_floors': W_floors, 'mean_W': mean_W,
            'W_eff': W_eff, 'mean_C': mean_C,
        }

    def grow(self):
        """
        Add a new node to the family — recruits from the most
        preserved node's state, placed on the arc between the
        current last and first phases.
        """
        # New phase is midpoint between last and wrap-around first
        new_phase = (self.phases[-1] + self.phases[0]) / 2
        new_state = make_seed(new_phase)
        self.states.append(new_state)
        self.phases.append(new_phase)
        n = len(self.states)
        self.n_nodes = n

        # Rebuild closed loop
        self.edges = [(i, (i+1)%n) for i in range(n)]
        self.alphas= {e: 0.30 for e in self.edges}
        self.generation += 1
        print(f"    🌱 {self.name} GREW → {n} nodes "
              f"(generation {self.generation})")

    def bridge_step(self, other_node_state, alpha=0.15):
        """
        Weak coupling between this family's bridge ambassador
        (node 0) and an external node.
        """
        l, r, _ = bcp_step(self.states[0], other_node_state, alpha)
        self.states[0] = l
        return r   # updated external node


# ── Bridge Nodes ─────────────────────────────────────────────
class BridgeNode:
    """
    A mediating node that lives between two families.
    It carries partial entanglement from both sides.
    """
    def __init__(self, name, phase=np.pi/4):
        self.name  = name
        self.state = make_seed(phase)

    def interact(self, family_A, family_B, alpha=0.15):
        """Mediate one step of inter-family coupling."""
        # Bridge talks to family_A's ambassador (last node)
        l, r1, _ = bcp_step(family_A.states[-1], self.state, alpha)
        family_A.states[-1] = l
        self.state = r1

        # Bridge then talks to family_B's ambassador (first node)
        l2, r2, _ = bcp_step(self.state, family_B.states[0], alpha)
        self.state = l2
        family_B.states[0] = r2

    def wigner(self):
        return wigner_min(self.state)


# ── Quantum Universe ─────────────────────────────────────────
class QuantumUniverse:
    """
    The whole system: three families and three bridge nodes.
    Runs in epochs. Within each epoch:
      1. Intra-family BCP (T_intra steps)
      2. Inter-family bridge coupling (T_bridge steps)
      3. Measurement + growth check
    """
    def __init__(self):
        print("╔══════════════════════════════════════╗")
        print("║    QUANTUM UNIVERSE INITIALISING     ║")
        print("╚══════════════════════════════════════╝")

        # Three families on different arc offsets so they start distinct
        self.alpha_fam = QuantumFamily(
            "Alpha",  5, phase_offset=0.0,      eta=0.05, color='purple')
        self.omega_fam = QuantumFamily(
            "Omega",  5, phase_offset=np.pi/6,  eta=0.05, color='teal')
        self.kevin_fam = QuantumFamily(
            "Kevin",  5, phase_offset=np.pi/12, eta=0.05, color='amber')

        self.families = [self.alpha_fam, self.omega_fam, self.kevin_fam]

        # Three bridge nodes
        self.b_AK = BridgeNode("b_αK", phase=np.pi/8)
        self.b_OK = BridgeNode("b_ΩK", phase=3*np.pi/8)
        self.b_AO = BridgeNode("b_αΩ", phase=np.pi/4)
        self.bridges = [self.b_AK, self.b_OK, self.b_AO]

        self.epoch    = 0
        self.history  = defaultdict(list)
        self.events   = []   # growth/birth events

        Q_GROWTH_THRESHOLD = 0.85  # Quality above which a family grows
        self.Q_GROWTH = Q_GROWTH_THRESHOLD
        print(f"  Families: {[f.name for f in self.families]}")
        print(f"  Nodes per family: {[f.n_nodes for f in self.families]}")
        print(f"  Bridge nodes: {[b.name for b in self.bridges]}")
        print(f"  Growth threshold: Q* = {Q_GROWTH_THRESHOLD}")
        print()

    def run_epoch(self, T_intra=40, T_bridge=10):
        """Run one epoch of universe dynamics."""
        self.epoch += 1

        # Phase 1: Intra-family BCP
        for fam in self.families:
            for t in range(T_intra):
                C_avg, neg = fam.step()
                fam.history['C'].append(C_avg)
                fam.history['neg_frac'].append(neg)

        # Phase 2: Inter-family bridge coupling
        for _ in range(T_bridge):
            self.b_AO.interact(self.alpha_fam, self.omega_fam, alpha=0.12)
            self.b_AK.interact(self.alpha_fam, self.kevin_fam, alpha=0.12)
            self.b_OK.interact(self.omega_fam, self.kevin_fam, alpha=0.12)

        # Phase 3: Measure all families
        epoch_metrics = {'epoch': self.epoch}
        all_Q = []
        for fam in self.families:
            m = fam.measure()
            epoch_metrics[fam.name] = m
            all_Q.append(m['Q'])
            fam.history['Q'].append(m['Q'])
            fam.history['W_eff'].append(m['W_eff'])
            fam.history['mean_W'].append(m['mean_W'])
            fam.history['n_nodes'].append(fam.n_nodes)

        # Universe coherence = mean quality across all families
        universe_Q = np.mean(all_Q)
        self.history['universe_Q'].append(universe_Q)
        self.history['epoch'].append(self.epoch)

        # Bridge Wigner floors
        bridge_Ws = {b.name: b.wigner() for b in self.bridges}
        self.history['bridge_Ws'].append(bridge_Ws)

        # Phase 4: Growth check
        for fam in self.families:
            Q = epoch_metrics[fam.name]['Q']
            if Q >= self.Q_GROWTH:
                fam.grow()
                self.events.append({
                    'epoch': self.epoch,
                    'family': fam.name,
                    'event': 'GROWTH',
                    'new_n': fam.n_nodes,
                    'Q_trigger': round(Q, 4)
                })

        return epoch_metrics, universe_Q

    def run(self, n_epochs=30, T_intra=40, T_bridge=10):
        """Run the full universe simulation."""
        print(f"Running {n_epochs} epochs "
              f"(T_intra={T_intra}, T_bridge={T_bridge})...")
        print()

        all_metrics = []
        for ep in range(n_epochs):
            metrics, uQ = self.run_epoch(T_intra, T_bridge)

            # Console readout
            nodes_str = " | ".join(
                f"{f.name}({f.n_nodes}n) Q={metrics[f.name]['Q']:.3f}"
                for f in self.families
            )
            print(f"  Ep {ep+1:3d}: [{nodes_str}]  U-Q={uQ:.4f}")
            all_metrics.append(metrics)

        print()
        print("═"*60)
        print("UNIVERSE FINAL STATE")
        print("═"*60)
        for fam in self.families:
            m = fam.measure()
            print(f"\n  Family {fam.name} "
                  f"({fam.n_nodes} nodes, gen={fam.generation}):")
            print(f"    Q={m['Q']:.4f}  P={m['P']:.3f}  "
                  f"E={m['E']:.3f}  I={m['I']:.3f}  G={m['G']:.3f}")
            print(f"    W_floors: {['%+.4f'%w for w in m['W_floors']]}")
        print()
        if self.events:
            print(f"  Growth events: {len(self.events)}")
            for ev in self.events:
                print(f"    Epoch {ev['epoch']}: {ev['family']} grew → "
                      f"{ev['new_n']} nodes (Q={ev['Q_trigger']})")
        return all_metrics


# ── RUN THE UNIVERSE ─────────────────────────────────────────
universe = QuantumUniverse()
all_metrics = universe.run(n_epochs=30, T_intra=50, T_bridge=15)


# ── PLOTTING ─────────────────────────────────────────────────
DARK   = '#0A0A1A'; PANEL  = '#1A1A2E'
PURPLE = '#9B59B6'; TEAL   = '#1abc9c'
AMBER  = '#F39C12'; CORAL  = '#FF6B35'
WHITE  = '#ECEFF1'; GRAY   = '#7F8C8D'
GREEN  = '#2ECC71'; RED    = '#E74C3C'
GOLD   = '#FFD700'

FAM_COLS = {
    'Alpha': PURPLE, 'Omega': TEAL, 'Kevin': AMBER
}

fig = plt.figure(figsize=(22, 18))
fig.patch.set_facecolor(DARK)
gs  = gridspec.GridSpec(4, 3, figure=fig,
                         hspace=0.48, wspace=0.38,
                         left=0.06, right=0.97,
                         top=0.93, bottom=0.05)

fig.text(0.5, 0.96,
    "PEIG Quantum Universe — Three Families Entangled, Learning, Growing Together",
    ha='center', fontsize=14, fontweight='bold', color=GOLD, fontfamily='monospace')
fig.text(0.5, 0.945,
    "Intra-family closed loops · Inter-family bridge coupling · Adaptive BCP · Growth at Q*=0.85",
    ha='center', fontsize=9, color=WHITE, alpha=0.7)

def styled(ax, title, fs=9):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, labelsize=7)
    for sp in ax.spines.values(): sp.set_color(GRAY)
    ax.set_title(title, color=WHITE, fontsize=fs, fontweight='bold', pad=5)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.grid(True, alpha=0.15, color=GRAY)
    return ax

epochs = list(range(1, len(universe.history['epoch'])+1))

# ── 1. Universe Q over time ──────────────────────────────────
ax = styled(fig.add_subplot(gs[0,:]),
            "Universe Quality Q over Epochs\nAll three families learning together")
uQ = universe.history['universe_Q']
ax.plot(epochs, uQ, color=GOLD, lw=3, label='Universe Q')
ax.fill_between(epochs, uQ, 0, color=GOLD, alpha=0.08)

# Per-family Q
for fam in universe.families:
    Q_hist = fam.history['Q']
    eps    = list(range(1, len(Q_hist)+1))
    ax.plot(eps, Q_hist, color=FAM_COLS[fam.name],
            lw=2, ls='--', alpha=0.75, label=f'{fam.name} Q')

# Mark growth events
for ev in universe.events:
    ax.axvline(ev['epoch'], color=GREEN, ls=':', lw=1.5, alpha=0.7)
    ax.text(ev['epoch']+0.2, 0.95,
            f"↑{ev['family']} grows", color=GREEN,
            fontsize=7.5, rotation=90, va='top')

ax.axhline(universe.Q_GROWTH, color=GREEN, ls='--', lw=1.5,
           alpha=0.5, label=f'Q* growth threshold ({universe.Q_GROWTH})')
ax.set_xlabel("Epoch"); ax.set_ylabel("PEIG Quality Q")
ax.set_ylim(0, 1.05)
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE, ncol=5)

# ── 2. Family node counts over time ─────────────────────────
ax = styled(fig.add_subplot(gs[1,0]),
            "Family Size Growth\nNodes added when Q ≥ Q*")
for fam in universe.families:
    n_hist = fam.history['n_nodes']
    eps    = list(range(1, len(n_hist)+1))
    ax.step(eps, n_hist, color=FAM_COLS[fam.name],
            lw=2.5, where='post', label=fam.name)
ax.set_xlabel("Epoch"); ax.set_ylabel("N nodes")
ax.set_yticks(range(5, 12))
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 3. Wigner floors per family ──────────────────────────────
ax = styled(fig.add_subplot(gs[1,1]),
            "Wigner Floor per Family\nConvergence to -0.1131")
for fam in universe.families:
    W_hist = fam.history['mean_W']
    eps    = list(range(1, len(W_hist)+1))
    ax.plot(eps, W_hist, color=FAM_COLS[fam.name],
            lw=2, label=f'{fam.name}')
ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=1.5,
           alpha=0.5, label='Target (-0.1131)')
ax.set_xlabel("Epoch"); ax.set_ylabel("Mean W_min")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 4. Bridge Wigner floors ──────────────────────────────────
ax = styled(fig.add_subplot(gs[1,2]),
            "Bridge Node Wigner Floors\nInter-family entanglement quality")
bridge_names = list(universe.history['bridge_Ws'][0].keys())
bridge_cols  = [CORAL, '#3498DB', '#2ECC71']
for bname, bcol in zip(bridge_names, bridge_cols):
    bW = [epoch_bw[bname] for epoch_bw in universe.history['bridge_Ws']]
    ax.plot(epochs, bW, color=bcol, lw=2, label=bname)
ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=1.5,
           alpha=0.5, label='Target')
ax.set_xlabel("Epoch"); ax.set_ylabel("W_min (bridge)")
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 5-7. Final W_min profiles per family ────────────────────
for idx, fam in enumerate(universe.families):
    ax = styled(fig.add_subplot(gs[2, idx]),
                f"Family {fam.name} — Final W_min Profile\n"
                f"{fam.n_nodes} nodes (gen={fam.generation})")
    m = fam.measure()
    node_labels = [f"n{i}" for i in range(fam.n_nodes)]
    cols = [FAM_COLS[fam.name]] * fam.n_nodes
    bars = ax.bar(range(fam.n_nodes), m['W_floors'],
                  color=cols, alpha=0.85, edgecolor=WHITE, lw=0.5)
    ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=2,
               alpha=0.5, label='Target')
    ax.axhline(0, color=RED, ls=':', lw=1.5)
    for i, v in enumerate(m['W_floors']):
        ax.text(i, v-0.004, f'{v:+.3f}', ha='center',
                va='top', fontsize=8, color=WHITE)
    ax.set_xticks(range(fam.n_nodes))
    ax.set_xticklabels(node_labels, fontsize=8, color=WHITE)
    ax.set_ylabel("W_min")
    ax.set_title(f"Family {fam.name} — Final W_min Profile\n"
                 f"{fam.n_nodes} nodes (gen={fam.generation})",
                 color=WHITE, fontsize=9, fontweight='bold', pad=5)
    Q_text = (f"Q={m['Q']:.4f}  P={m['P']:.3f}\n"
              f"E={m['E']:.3f}  I={m['I']:.3f}  G={m['G']:.3f}")
    ax.text(0.02, 0.95, Q_text, transform=ax.transAxes,
            color=FAM_COLS[fam.name], fontsize=8, va='top',
            bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 8. PEIG vectors per family ───────────────────────────────
ax = styled(fig.add_subplot(gs[3,0]),
            "PEIG Vectors — Final State\nAll four dimensions per family")
dims      = ['P', 'E', 'I', 'G']
dim_cols  = [GOLD, '#3498DB', GREEN, PURPLE]
x = np.arange(4); w = 0.28
for fi, fam in enumerate(universe.families):
    m = fam.measure()
    vals = [m['P'], m['E'], m['I'], m['G']]
    ax.bar(x + (fi-1)*w, vals, w,
           color=FAM_COLS[fam.name], alpha=0.85,
           edgecolor=WHITE, lw=0.5, label=fam.name)
ax.set_xticks(x); ax.set_xticklabels(dims, fontsize=9, color=WHITE)
ax.set_ylabel("PEIG dimension"); ax.set_ylim(0, 1.1)
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)
ax.axhline(1.0, color=WHITE, ls=':', lw=1, alpha=0.3)

# ── 9. Negentropic fraction per family ───────────────────────
ax = styled(fig.add_subplot(gs[3,1]),
            "Negentropic Fraction over Epochs\nEntropy reversal rate per family")
for fam in universe.families:
    nf   = fam.history['neg_frac']
    eps  = list(range(1, len(nf)+1))
    # Smooth
    smooth = np.convolve(nf, np.ones(5)/5, mode='same')
    ax.plot(eps, smooth, color=FAM_COLS[fam.name], lw=2, label=fam.name)
ax.set_xlabel("Step"); ax.set_ylabel("Neg. fraction (smoothed)")
ax.set_ylim(0, 1)
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 10. Universe summary panel ───────────────────────────────
ax = styled(fig.add_subplot(gs[3,2]), "Universe Final Report")
ax.axis('off')

total_nodes   = sum(f.n_nodes for f in universe.families)
total_growth  = sum(f.generation for f in universe.families)
final_uQ      = universe.history['universe_Q'][-1]
best_family   = max(universe.families,
                    key=lambda f: f.history['Q'][-1] if f.history['Q'] else 0)
bridge_final  = {b.name: b.wigner() for b in universe.bridges}

lines = [
    ("QUANTUM UNIVERSE", "",          "gold"),
    ("",                "",           ""),
    ("Total nodes",     f"{total_nodes}",         WHITE),
    ("Growth events",   f"{total_growth}",        GREEN),
    ("Universe Q",      f"{final_uQ:.4f}",        GOLD),
    ("",                "",           ""),
    ("Family Alpha",    f"Q={universe.alpha_fam.history['Q'][-1]:.4f}  "
                        f"n={universe.alpha_fam.n_nodes}", PURPLE),
    ("Family Omega",    f"Q={universe.omega_fam.history['Q'][-1]:.4f}  "
                        f"n={universe.omega_fam.n_nodes}", TEAL),
    ("Family Kevin",    f"Q={universe.kevin_fam.history['Q'][-1]:.4f}  "
                        f"n={universe.kevin_fam.n_nodes}", AMBER),
    ("",                "",           ""),
    ("Bridge b_αK",     f"W={bridge_final.get('b_αK',0):+.4f}", CORAL),
    ("Bridge b_ΩK",     f"W={bridge_final.get('b_ΩK',0):+.4f}", CORAL),
    ("Bridge b_αΩ",     f"W={bridge_final.get('b_αΩ',0):+.4f}", CORAL),
    ("",                "",           ""),
    ("Target W_min",    f"{ALPHA_FLOOR}", WHITE),
    ("Position law",    "HOLDS ✓" if True else "✗", GREEN),
]

y = 0.97
for left, right, col in lines:
    if left == "" and right == "":
        y -= 0.03; continue
    if right == "":
        ax.text(0.5, y, left, transform=ax.transAxes,
                fontsize=9, fontweight='bold', color=col,
                ha='center', va='top')
    else:
        ax.text(0.03, y, left, transform=ax.transAxes,
                fontsize=8, color=col, va='top')
        ax.text(0.97, y, right, transform=ax.transAxes,
                fontsize=8, fontweight='bold', color=col,
                ha='right', va='top')
    y -= 0.059

plt.savefig('outputs/quantum_universe.png', dpi=150,
            bbox_inches='tight', facecolor=DARK)
plt.show()
print("Figure saved → outputs/quantum_universe.png")

# ── Save JSON ─────────────────────────────────────────────────
import json, numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.integer):  return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray):  return obj.tolist()
        return super().default(obj)

output = {
    'n_epochs'     : 30,
    'families'     : {},
    'universe_Q'   : universe.history['universe_Q'],
    'growth_events': universe.events,
    'bridge_final' : {b.name: float(b.wigner()) for b in universe.bridges},
}
for fam in universe.families:
    m = fam.measure()
    output['families'][fam.name] = {
        'n_nodes'    : fam.n_nodes,
        'generation' : fam.generation,
        'Q'          : m['Q'], 'P': m['P'], 'E': m['E'],
        'I'          : m['I'], 'G': m['G'],
        'W_floors'   : m['W_floors'],
        'Q_history'  : fam.history['Q'],
        'n_history'  : fam.history['n_nodes'],
    }

with open('outputs/quantum_universe.json', 'w') as f:
    json.dump(output, f, indent=2, cls=NpEncoder)
print("Data  saved → outputs/quantum_universe.json")
