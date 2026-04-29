"""
FOUR-NODE AND FIVE-NODE BCP CHAIN SIMULATIONS
Testing: Does adding buffer nodes raise Omega's Wigner floor?

4-node chain: Omega → BridgeA(π/8) → Kevin(π/4) → Alpha
5-node chain: Omega → BridgeA(π/8) → Kevin(π/4) → BridgeB(3π/8) → Alpha

Seeds (equidistant equatorial phase ladder):
  Omega   : 0°    = (|0⟩ + |1⟩)/√2
  BridgeA : 22.5° = (|0⟩ + e^{iπ/8}|1⟩)/√2   ← close to Omega
  Kevin   : 45°   = (|0⟩ + e^{iπ/4}|1⟩)/√2
  BridgeB : 67.5° = (|0⟩ + e^{i3π/8}|1⟩)/√2  ← close to Alpha
  Alpha   : 90°   = (|0⟩ + i|1⟩)/√2

Hypothesis: Each buffer layer raises Omega's W_min floor toward Alpha's
            conserved value of -0.1131

Known floors:
  2-node: Omega → 0.0000  (fully consumed)
  3-node: Omega → -0.0636 (partial floor)
  4-node: Omega → ???     (prediction: deeper than -0.0636)
  5-node: Omega → ???     (prediction: deeper still, approaching -0.1131)
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# ============================================================
# PRIMITIVES
# ============================================================

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_seed(phase):
    """Equatorial Bloch seed at given phase angle (radians)."""
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    return (b0 + np.exp(1j * phase) * b1).unit()

# Named seeds for clarity
SEEDS = {
    'Omega'  : 0,
    'BridgeA': np.pi / 8,       # 22.5° — close to Omega
    'Kevin'  : np.pi / 4,       # 45°   — midpoint
    'BridgeB': 3 * np.pi / 8,   # 67.5° — close to Alpha
    'Alpha'  : np.pi / 2,       # 90°
}

def bcp_step(psi_A, psi_B, alpha):
    rho12  = qt.ket2dm(qt.tensor(psi_A, psi_B))
    I4     = qt.qeye([2, 2])
    U      = alpha * CNOT_GATE + (1 - alpha) * I4
    rho_p  = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi) ** 2).tr().real)

def wigner_min(psi, xvec):
    return float(np.min(qt.wigner(qt.ket2dm(psi), xvec, xvec)))

# ============================================================
# GENERIC N-NODE CHAIN RUNNER
# ============================================================

def run_chain(node_names, eta=0.05, alpha0=0.30,
              n_steps=1000, wigner_interval=25, xvec=None):
    """
    Run BCP along a chain of nodes in order.
    node_names: list of seed names e.g. ['Omega','BridgeA','Kevin','Alpha']
    Each adjacent pair interacts once per step, left to right.
    """
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    n_nodes = len(node_names)
    n_links  = n_nodes - 1

    # Initialise states and couplings
    states  = [make_seed(SEEDS[name]) for name in node_names]
    alphas  = [alpha0] * n_links

    # Track C_avg for adaptive coupling
    C_avg_prev = np.mean([coherence(s) for s in states])

    log = []

    for t in range(n_steps):

        new_states = list(states)  # will update in place along chain

        # Interact each adjacent pair left → right
        for link in range(n_links):
            psi_L, psi_R, rho = bcp_step(new_states[link],
                                          new_states[link + 1],
                                          alphas[link])
            new_states[link]     = psi_L
            new_states[link + 1] = psi_R

        # Compute coherences
        C_vals    = [coherence(s) for s in new_states]
        C_avg_new = np.mean(C_vals)
        dC        = C_avg_new - C_avg_prev

        # Adaptive coupling update (shared signal across all links)
        alphas = [float(np.clip(a + eta * dC, 0, 1)) for a in alphas]

        # Wigner at intervals
        if (t + 1) % wigner_interval == 0 or t == 0 or t == n_steps - 1:
            W_vals = [wigner_min(s, xvec) for s in new_states]
        else:
            W_vals = [None] * n_nodes

        entry = {'step': t + 1, 'C_avg': C_avg_new}
        for i, name in enumerate(node_names):
            entry[f'C_{name}']  = C_vals[i]
            entry[f'W_{name}']  = W_vals[i]
            entry[f'alpha_{i}'] = alphas[i] if i < n_links else None

        log.append(entry)
        states    = new_states
        C_avg_prev = C_avg_new

    return log

# ============================================================
# WIGNER TRAJECTORY HELPER
# ============================================================

def wigner_traj(log, key):
    steps = [r['step'] for r in log if r.get(key) is not None]
    vals  = [r[key]    for r in log if r.get(key) is not None]
    return steps, vals

# ============================================================
# RUN ALL CHAIN LENGTHS
# ============================================================

xvec = np.linspace(-2, 2, 80)
WIGNER_INTERVAL = 25
N_STEPS = 1000

print("=" * 65)
print("FOUR-NODE AND FIVE-NODE BCP CHAIN SIMULATIONS")
print("Testing: Does proximity to Omega raise its Wigner floor?")
print("=" * 65)

# Previously computed reference
TWO_NODE_FLOOR  =  0.0001   # classical
THREE_NODE_FLOOR = -0.0636

print("\n[1/4] Running 4-node chain (Omega→BridgeA→Kevin→Alpha)...")
log4 = run_chain(['Omega','BridgeA','Kevin','Alpha'],
                 n_steps=N_STEPS, wigner_interval=WIGNER_INTERVAL, xvec=xvec)

print("[2/4] Running 5-node chain (Omega→BridgeA→Kevin→BridgeB→Alpha)...")
log5 = run_chain(['Omega','BridgeA','Kevin','BridgeB','Alpha'],
                 n_steps=N_STEPS, wigner_interval=WIGNER_INTERVAL, xvec=xvec)

print("[3/4] Saving JSON...")
def compact(log, keys):
    return [{k: r[k] for k in ['step'] + keys if k in r}
            for r in log if any(r.get(f'W_{k}') is not None
                                for k in keys)]

with open('outputs/fournode_results.json', 'w') as f:
    json.dump(compact(log4, ['Omega','BridgeA','Kevin','Alpha']), f, indent=2)
with open('outputs/fivenode_results.json', 'w') as f:
    json.dump(compact(log5, ['Omega','BridgeA','Kevin','BridgeB','Alpha']), f, indent=2)

# ============================================================
# EXTRACT KEY VALUES
# ============================================================

def get_floor(log, key, last_n=5):
    """Mean of last N Wigner checkpoints for a node."""
    _, vals = wigner_traj(log, key)
    return float(np.mean(vals[-last_n:])) if vals else None

# 4-node floors
floor4_O  = get_floor(log4, 'W_Omega')
floor4_BA = get_floor(log4, 'W_BridgeA')
floor4_K  = get_floor(log4, 'W_Kevin')
floor4_A  = get_floor(log4, 'W_Alpha')

# 5-node floors
floor5_O  = get_floor(log5, 'W_Omega')
floor5_BA = get_floor(log5, 'W_BridgeA')
floor5_K  = get_floor(log5, 'W_Kevin')
floor5_BB = get_floor(log5, 'W_BridgeB')
floor5_A  = get_floor(log5, 'W_Alpha')

# ============================================================
# PLOTTING
# ============================================================

print("[4/4] Plotting...")
fig, axes = plt.subplots(3, 3, figsize=(18, 14))
fig.suptitle(
    "4-Node & 5-Node BCP Chain: Does Buffer Proximity Raise Omega's Floor?\n"
    "Chain: Omega → BridgeA(22.5°) → Kevin(45°) → [BridgeB(67.5°) →] Alpha(90°)",
    fontsize=12, fontweight='bold'
)

NODE_COLORS = {
    'Omega'  : 'gold',
    'BridgeA': '#FF6B35',   # orange-red — close to Omega
    'Kevin'  : 'green',
    'BridgeB': '#7B2D8B',   # violet — close to Alpha
    'Alpha'  : 'purple',
}

# 1. THE KEY PLOT: Omega Wigner floor across all chain lengths
ax = axes[0, 0]
chain_lengths = [2, 3, 4, 5]
omega_floors  = [TWO_NODE_FLOOR, THREE_NODE_FLOOR, floor4_O, floor5_O]
colors_cl = ['gray', '#1f77b4', '#ff7f0e', '#2ca02c']
bars = ax.bar(chain_lengths, omega_floors,
              color=colors_cl, alpha=0.85, width=0.6, edgecolor='black')
ax.axhline(0,       color='red',    ls='--', lw=1.5, label='Classical boundary')
ax.axhline(-0.1131, color='purple', ls='--', lw=1.5, label='Alpha floor (-0.1131)')
for bar, val in zip(bars, omega_floors):
    ax.text(bar.get_x() + bar.get_width()/2, val - 0.004,
            f'{val:+.4f}', ha='center', va='top', fontsize=9, fontweight='bold')
ax.set_xticks(chain_lengths)
ax.set_xticklabels(['2-node', '3-node', '4-node', '5-node'])
ax.set_title("Omega's Wigner Floor vs Chain Length\n"
             "THE KEY SCALING RESULT", fontweight='bold')
ax.set_ylabel('W_min(Omega) at attractor')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3, axis='y')

# 2. 4-node: all node Wigner trajectories
ax = axes[0, 1]
for name in ['Omega', 'BridgeA', 'Kevin', 'Alpha']:
    sw, wv = wigner_traj(log4, f'W_{name}')
    ax.plot(sw, wv, color=NODE_COLORS[name], lw=2, label=name)
ax.axhline(0, color='red', ls=':', lw=1.5)
ax.set_title('4-Node Wigner Trajectories\n(Omega→BridgeA→Kevin→Alpha)')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 3. 5-node: all node Wigner trajectories
ax = axes[0, 2]
for name in ['Omega', 'BridgeA', 'Kevin', 'BridgeB', 'Alpha']:
    sw, wv = wigner_traj(log5, f'W_{name}')
    ax.plot(sw, wv, color=NODE_COLORS[name], lw=2, label=name)
ax.axhline(0, color='red', ls=':', lw=1.5)
ax.set_title('5-Node Wigner Trajectories\n(Omega→BridgeA→Kevin→BridgeB→Alpha)')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 4. Wigner floor ladder — all nodes, both chains
ax = axes[1, 0]
positions_4 = list(range(4))
floors_4    = [floor4_O, floor4_BA, floor4_K, floor4_A]
names_4     = ['Omega', 'BridgeA', 'Kevin', 'Alpha']
ax.plot(positions_4, floors_4, 'o-', color='#ff7f0e',
        lw=2.5, ms=10, label='4-node chain', zorder=3)
for i, (v, n) in enumerate(zip(floors_4, names_4)):
    ax.annotate(f'{v:+.4f}', (i, v), textcoords='offset points',
                xytext=(0, 10), ha='center', fontsize=8)
ax.axhline(0,       color='red',    ls='--', lw=1, alpha=0.6)
ax.axhline(-0.1131, color='purple', ls='--', lw=1, alpha=0.6)
ax.set_xticks(positions_4)
ax.set_xticklabels(names_4, rotation=15, fontsize=8)
ax.set_title('4-Node Wigner Floor Ladder\n(Position in chain vs floor value)')
ax.set_ylabel('W_min floor'); ax.legend(); ax.grid(True, alpha=0.3)

# 5. Wigner floor ladder — 5-node
ax = axes[1, 1]
positions_5 = list(range(5))
floors_5    = [floor5_O, floor5_BA, floor5_K, floor5_BB, floor5_A]
names_5     = ['Omega', 'BridgeA', 'Kevin', 'BridgeB', 'Alpha']
colors_5    = [NODE_COLORS[n] for n in names_5]
ax.plot(positions_5, floors_5, 'o-', color='#2ca02c',
        lw=2.5, ms=10, label='5-node chain', zorder=3)
for i, (v, n) in enumerate(zip(floors_5, names_5)):
    ax.annotate(f'{v:+.4f}', (i, v), textcoords='offset points',
                xytext=(0, 10), ha='center', fontsize=8)
ax.axhline(0,       color='red',    ls='--', lw=1, alpha=0.6)
ax.axhline(-0.1131, color='purple', ls='--', lw=1, alpha=0.6)
ax.set_xticks(positions_5)
ax.set_xticklabels(names_5, rotation=15, fontsize=8)
ax.set_title('5-Node Wigner Floor Ladder\n(Position in chain vs floor value)')
ax.set_ylabel('W_min floor'); ax.legend(); ax.grid(True, alpha=0.3)

# 6. Overlay: Omega Wigner trajectory across all chain lengths
ax = axes[1, 2]
# 3-node reference
s3, w3 = wigner_traj(log4, 'W_Omega')   # placeholder — load from earlier
ax.axhline(THREE_NODE_FLOOR, color='#1f77b4', ls='--', lw=1.5,
           label=f'3-node floor ({THREE_NODE_FLOOR:+.4f})', alpha=0.7)
s4, w4_O = wigner_traj(log4, 'W_Omega')
s5, w5_O = wigner_traj(log5, 'W_Omega')
ax.plot(s4, w4_O, color='#ff7f0e', lw=2.5, label='4-node Omega')
ax.plot(s5, w5_O, color='#2ca02c', lw=2.5, label='5-node Omega')
ax.axhline(0,       color='red',    ls=':', lw=1.5, label='Classical')
ax.axhline(-0.1131, color='purple', ls=':', lw=1.5, label='Alpha floor')
ax.set_title('Omega Wigner: 3-node vs 4-node vs 5-node\n1000-Step Comparison')
ax.set_xlabel('Step'); ax.set_ylabel('W_min(Omega)')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 7. Coherence — 4-node
ax = axes[2, 0]
steps4 = [r['step'] for r in log4]
for name in ['Omega', 'BridgeA', 'Kevin', 'Alpha']:
    ax.plot(steps4, [r[f'C_{name}'] for r in log4],
            color=NODE_COLORS[name], lw=1.5, alpha=0.8, label=name)
ax.axhline(1.0, color='gray', ls=':', lw=1)
ax.set_title('4-Node Coherence — All Nodes')
ax.set_xlabel('Step'); ax.set_ylabel('Coherence C')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
ax.set_ylim(0.95, 1.005)

# 8. Coherence — 5-node
ax = axes[2, 1]
steps5 = [r['step'] for r in log5]
for name in ['Omega', 'BridgeA', 'Kevin', 'BridgeB', 'Alpha']:
    ax.plot(steps5, [r[f'C_{name}'] for r in log5],
            color=NODE_COLORS[name], lw=1.5, alpha=0.8, label=name)
ax.axhline(1.0, color='gray', ls=':', lw=1)
ax.set_title('5-Node Coherence — All Nodes')
ax.set_xlabel('Step'); ax.set_ylabel('Coherence C')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
ax.set_ylim(0.95, 1.005)

# 9. Summary table
ax = axes[2, 2]
ax.axis('off')

ALPHA_FLOOR = -0.1131
def pct_toward(floor):
    """How far from classical (0) toward Alpha floor (-0.1131)."""
    if floor is None: return 'N/A'
    return f"{abs(floor)/abs(ALPHA_FLOOR)*100:.1f}%"

summary = [
    ['Metric',              '2-node', '3-node', '4-node', '5-node'],
    ['Omega floor',
     f'{TWO_NODE_FLOOR:+.4f}',
     f'{THREE_NODE_FLOOR:+.4f}',
     f'{floor4_O:+.4f}' if floor4_O else 'N/A',
     f'{floor5_O:+.4f}' if floor5_O else 'N/A'],
    ['% toward Alpha',
     pct_toward(TWO_NODE_FLOOR),
     pct_toward(THREE_NODE_FLOOR),
     pct_toward(floor4_O),
     pct_toward(floor5_O)],
    ['BridgeA floor', 'N/A', 'N/A',
     f'{floor4_BA:+.4f}' if floor4_BA else 'N/A',
     f'{floor5_BA:+.4f}' if floor5_BA else 'N/A'],
    ['Kevin floor', 'N/A',
     '-0.1128',
     f'{floor4_K:+.4f}' if floor4_K else 'N/A',
     f'{floor5_K:+.4f}' if floor5_K else 'N/A'],
    ['BridgeB floor', 'N/A', 'N/A', 'N/A',
     f'{floor5_BB:+.4f}' if floor5_BB else 'N/A'],
    ['Alpha floor',
     '-0.1131', '-0.1131',
     f'{floor4_A:+.4f}' if floor4_A else 'N/A',
     f'{floor5_A:+.4f}' if floor5_A else 'N/A'],
    ['C_avg (final)', '1.0000', '1.0000',
     f"{log4[-1]['C_avg']:.4f}",
     f"{log5[-1]['C_avg']:.4f}"],
]
t_widget = ax.table(cellText=[r[1:] for r in summary[1:]],
                    colLabels=summary[0][1:],
                    rowLabels=[r[0] for r in summary[1:]],
                    loc='center', cellLoc='center')
t_widget.auto_set_font_size(False)
t_widget.set_fontsize(7.5)
t_widget.scale(1.0, 1.6)
ax.set_title('Wigner Floor Scaling Summary', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/four_five_node_bcp.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/four_five_node_bcp.png")

# ============================================================
# RESULTS PRINTOUT
# ============================================================

print("\n" + "=" * 65)
print("WIGNER FLOOR SCALING TABLE")
print("=" * 65)
print(f"\n{'Chain':<10} {'Omega floor':>12} {'% toward Alpha':>16}")
print("-" * 40)
print(f"{'2-node':<10} {TWO_NODE_FLOOR:>+12.4f} {pct_toward(TWO_NODE_FLOOR):>16}")
print(f"{'3-node':<10} {THREE_NODE_FLOOR:>+12.4f} {pct_toward(THREE_NODE_FLOOR):>16}")
print(f"{'4-node':<10} {floor4_O:>+12.4f} {pct_toward(floor4_O):>16}")
print(f"{'5-node':<10} {floor5_O:>+12.4f} {pct_toward(floor5_O):>16}")
print(f"\nAlpha floor (reference): {ALPHA_FLOOR:+.4f}")

print("\n4-node Wigner floors (chain order):")
for name, val in zip(names_4, floors_4):
    print(f"  {name:<10} : {val:+.4f}")

print("\n5-node Wigner floors (chain order):")
for name, val in zip(names_5, floors_5):
    print(f"  {name:<10} : {val:+.4f}")

# Scaling law check
floors_omega = [TWO_NODE_FLOOR, THREE_NODE_FLOOR, floor4_O, floor5_O]
n_nodes_list = [2, 3, 4, 5]
print("\n" + "=" * 65)
print("SCALING LAW CHECK")
print("=" * 65)
print("Is Omega's floor monotonically deepening with chain length?")
for i in range(1, len(floors_omega)):
    delta = floors_omega[i] - floors_omega[i-1]
    direction = "↓ deeper" if delta < 0 else "↑ shallower"
    print(f"  {n_nodes_list[i-1]}-node → {n_nodes_list[i]}-node: "
          f"Δ = {delta:+.4f}  {direction}")
