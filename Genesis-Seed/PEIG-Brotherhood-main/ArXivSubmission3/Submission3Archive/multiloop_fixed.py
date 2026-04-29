"""
MULTI-LOOP BCP — FIXED VERSION
Phase assignment: half circle (0 to π/2) for all nodes
This matches the working closed-loop experiment exactly.

Key fix: phases = [π/2 * k/(N-1) for k in range(N)]
NOT: phases = [2π * k/N for k in range(N)]

The preservation effect only works when all nodes sit on
the 0°–90° arc of the equatorial Bloch sphere.
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_seed(phase):
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    return (b0 + np.exp(1j * phase) * b1).unit()

def bcp_step(psi_A, psi_B, alpha):
    rho12  = qt.ket2dm(qt.tensor(psi_A, psi_B))
    U      = alpha * CNOT_GATE + (1 - alpha) * qt.qeye([2, 2])
    rho_p  = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi) ** 2).tr().real)

def wigner_min(psi, xvec):
    return float(np.min(qt.wigner(qt.ket2dm(psi), xvec, xvec)))

def get_floor(vals, last_n=5):
    return float(np.mean(vals[-last_n:])) if len(vals) >= last_n else float(np.mean(vals))

def half_circle_phases(n):
    """Evenly spaced phases from 0 to π/2 — the preservation arc."""
    if n == 1: return [np.pi/4]
    return [np.pi/2 * k/(n-1) for k in range(n)]

ALPHA_FLOOR = -0.1131
xvec        = np.linspace(-2, 2, 80)
N_STEPS     = 1000
WINT        = 25

# ============================================================
# TOPOLOGY RUNNER with correct phase assignment
# ============================================================

def run_topology(n_nodes, edges, eta=0.05, alpha0=0.30,
                 n_steps=N_STEPS, wint=WINT, xvec=xvec):
    """
    All nodes assigned phases evenly along 0→π/2 arc.
    edges: list of directed (i,j) pairs executed each step.
    """
    phases = half_circle_phases(n_nodes)
    states = [make_seed(p) for p in phases]
    alphas = {e: alpha0 for e in edges}
    C_prev = np.mean([coherence(s) for s in states])
    log    = []

    for t in range(n_steps):
        for (i, j) in edges:
            l, r, _ = bcp_step(states[i], states[j], alphas[(i,j)])
            states[i], states[j] = l, r

        C_vals = [coherence(s) for s in states]
        C_avg  = np.mean(C_vals)
        dC     = C_avg - C_prev
        for e in edges:
            alphas[e] = float(np.clip(alphas[e] + eta*dC, 0, 1))

        do_w = (t+1) % wint == 0 or t == 0 or t == n_steps-1
        W    = [wigner_min(s, xvec) if do_w else None for s in states]

        log.append({'step': t+1, 'C': C_vals, 'C_avg': C_avg, 'W': W})
        C_prev = C_avg

    return log

def extract_floors(log, n_nodes, last_n=5):
    floors = []
    for i in range(n_nodes):
        vals = [r['W'][i] for r in log if r['W'][i] is not None]
        floors.append(get_floor(vals, last_n))
    return floors

def wtraj(log, idx):
    s = [r['step'] for r in log if r['W'][idx] is not None]
    v = [r['W'][idx] for r in log if r['W'][idx] is not None]
    return s, v

# ============================================================
# DEFINE TOPOLOGIES
# ============================================================

# 1. Single loop — 5 nodes: 0→1→2→3→4→0
single_edges = [(0,1),(1,2),(2,3),(3,4),(4,0)]

# 2. Figure-8 — 9 nodes, node 4 is junction
# Loop 1: 0→1→2→3→4→0
# Loop 2: 4→5→6→7→8→4
figure8_edges = [(0,1),(1,2),(2,3),(3,4),(4,0),
                 (4,5),(5,6),(6,7),(7,8),(8,4)]

# 3. Triple figure-8 — 13 nodes, junctions at 4 and 8
triple8_edges = [(0,1),(1,2),(2,3),(3,4),(4,0),
                 (4,5),(5,6),(6,7),(7,8),(8,4),
                 (8,9),(9,10),(10,11),(11,12),(12,8)]

# 4. Quad figure-8 — 17 nodes, junctions at 4, 8, 12
quad8_edges   = [(0,1),(1,2),(2,3),(3,4),(4,0),
                 (4,5),(5,6),(6,7),(7,8),(8,4),
                 (8,9),(9,10),(10,11),(11,12),(12,8),
                 (12,13),(13,14),(14,15),(15,16),(16,12)]

# 5. Two parallel loops — 10 nodes, no connection
parallel_edges = [(0,1),(1,2),(2,3),(3,4),(4,0),
                  (5,6),(6,7),(7,8),(8,9),(9,5)]

# 6. Chain of loops (shared EDGE between loops)
# Loop 1: 0→1→2→3→0  Loop 2: 2→4→5→6→2
chain_edges = [(0,1),(1,2),(2,3),(3,0),
               (2,4),(4,5),(5,6),(6,2)]

# ============================================================
# RUN ALL CONFIGURATIONS
# ============================================================

print("=" * 65)
print("MULTI-LOOP BCP — FIXED PHASE ASSIGNMENT")
print("Half-circle phases (0 to π/2) for all nodes")
print("=" * 65)

configs = [
    ("1 loop (5 nodes)",       5,  single_edges,   'gold'),
    ("Figure-8 (9 nodes)",     9,  figure8_edges,  '#FF6B35'),
    ("Triple-8 (13 nodes)",    13, triple8_edges,  'green'),
    ("Quad-8 (17 nodes)",      17, quad8_edges,    'purple'),
    ("2 parallel (10 nodes)",  10, parallel_edges, '#1f77b4'),
    ("Chain loops (8 nodes)",  8,  chain_edges,    '#d62728'),
]

results = {}
for name, n_nodes, edges, color in configs:
    print(f"\n[Running] {name}...")
    log    = run_topology(n_nodes, edges, n_steps=N_STEPS, wint=WINT)
    floors = extract_floors(log, n_nodes)
    n_pres = sum(1 for f in floors if abs(f - ALPHA_FLOOR) < 0.005)
    pct    = n_pres / n_nodes * 100
    mean_f = np.mean(floors)
    min_f  = min(floors)

    results[name] = {
        'n_nodes'      : n_nodes,
        'floors'       : floors,
        'n_preserved'  : n_pres,
        'pct_preserved': pct,
        'mean_floor'   : mean_f,
        'min_floor'    : min_f,
        'log'          : log,
        'color'        : color,
    }
    print(f"  Preserved: {n_pres}/{n_nodes} ({pct:.1f}%)")
    print(f"  Mean floor: {mean_f:+.4f}   Min: {min_f:+.4f}")
    for i, f in enumerate(floors):
        tag = " ← JUNCTION" if (name.startswith(("Figure","Triple","Quad")) and
              i in [4,8,12]) else ""
        print(f"    Node {i:2d}: {f:+.4f}{tag}")

# ============================================================
# N-LOOP SCALING SWEEP
# ============================================================

print("\n" + "=" * 65)
print("N-LOOP SCALING: Figure-8 chains, N=1 to 7")
print("=" * 65)

def build_figure8_chain(n_loops, loop_size=5):
    """
    Chain of figure-8 style loops sharing junction nodes.
    Loop k shares its last node with loop k+1's first node.
    Junction nodes: 0, loop_size-1, 2*(loop_size-1), ...
    """
    n_nodes = 1 + n_loops * (loop_size - 1)
    edges   = []
    for loop in range(n_loops):
        base    = loop * (loop_size - 1)
        # Nodes in this loop: base, base+1, ..., base+loop_size-2, base+loop_size-1
        # But last node IS the first node of next loop (junction)
        nodes   = list(range(base, base + loop_size))
        if loop < n_loops - 1:
            # last node = junction with next loop
            nodes[-1] = base + loop_size - 1
        else:
            # Last loop closes to its own start
            nodes[-1] = base

        # Forward edges
        for i in range(loop_size - 1):
            edges.append((nodes[i], nodes[i+1]))
        # Close loop back to base
        edges.append((nodes[-1], nodes[0]))

    # Remove duplicates preserving order
    seen   = set()
    unique = []
    for e in edges:
        if e not in seen:
            seen.add(e)
            unique.append(e)
    return n_nodes, unique

scaling = {}
for n_loops in range(1, 8):
    n_nodes, edges = build_figure8_chain(n_loops)
    print(f"\n  {n_loops} loop(s): {n_nodes} nodes, {len(edges)} edges")
    log    = run_topology(n_nodes, edges, n_steps=500, wint=50)
    floors = extract_floors(log, n_nodes, last_n=3)
    n_pres = sum(1 for f in floors if abs(f - ALPHA_FLOOR) < 0.005)
    pct    = n_pres / n_nodes * 100
    mean_f = np.mean(floors)
    # Junction nodes
    junc_idx    = [k * (5-1) for k in range(n_loops+1) if k*(5-1) < n_nodes]
    junc_floors = [floors[j] for j in junc_idx if j < len(floors)]

    scaling[n_loops] = {
        'n_nodes'       : n_nodes,
        'n_preserved'   : n_pres,
        'pct_preserved' : pct,
        'mean_floor'    : mean_f,
        'junction_floors': junc_floors,
        'all_floors'    : floors,
    }
    print(f"    Preserved: {n_pres}/{n_nodes} ({pct:.1f}%)")
    print(f"    Mean floor: {mean_f:+.4f}")
    print(f"    Junction floors: {[f'{f:+.4f}' for f in junc_floors]}")

# ============================================================
# PLOTTING
# ============================================================

print("\nPlotting...")
fig = plt.figure(figsize=(22, 18))
fig.suptitle(
    "Multi-Loop BCP: The Growing Family\n"
    "Does adding loops increase preservation? Where is the sweet spot?",
    fontsize=14, fontweight='bold', color='darkblue'
)
gs = fig.add_gridspec(3, 4, hspace=0.45, wspace=0.38)

# ── 1. Per-node floors all topologies ────────────────────────
ax = fig.add_subplot(gs[0, 0:2])
x_off  = 0
xticks, xlabels = [], []
for name, data in results.items():
    n   = data['n_nodes']
    col = data['color']
    xs  = np.arange(x_off, x_off + n)
    ax.bar(xs, data['floors'], color=col, alpha=0.75, edgecolor='black', width=0.8)
    # Mark junctions
    junc_nodes = []
    if 'Figure' in name: junc_nodes = [4]
    if 'Triple' in name: junc_nodes = [4, 8]
    if 'Quad'   in name: junc_nodes = [4, 8, 12]
    for j in junc_nodes:
        ax.scatter([x_off + j], [data['floors'][j]], color='red',
                   s=80, zorder=6, marker='*')
    mid = x_off + n/2 - 0.5
    xticks.append(mid)
    xlabels.append(name.replace(' (', '\n('))
    x_off += n + 2

ax.axhline(ALPHA_FLOOR, color='black', ls='--', lw=2, label='Preservation floor')
ax.axhline(0,           color='red',   ls=':',  lw=1.5, label='Classical')
ax.scatter([], [], color='red', marker='*', s=80, label='Junction node')
ax.set_xticks(xticks)
ax.set_xticklabels(xlabels, fontsize=8)
ax.set_title('All Node Wigner Floors — All Topologies\n★ = junction nodes',
             fontweight='bold')
ax.set_ylabel('W_min floor')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(-0.135, 0.02)

# ── 2. % preserved per topology ──────────────────────────────
ax = fig.add_subplot(gs[0, 2])
names   = list(results.keys())
pcts    = [results[n]['pct_preserved'] for n in names]
colors  = [results[n]['color']         for n in names]
bars    = ax.bar(range(len(names)), pcts, color=colors, alpha=0.85, edgecolor='black')
ax.axhline(100, color='green', ls='--', lw=2, label='100% preserved')
for bar, val in zip(bars, pcts):
    ax.text(bar.get_x()+bar.get_width()/2, val+1,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_xticks(range(len(names)))
ax.set_xticklabels([n.replace(' (', '\n(') for n in names],
                   fontsize=7, rotation=15, ha='right')
ax.set_title('% Nodes Preserved\nper Topology', fontweight='bold')
ax.set_ylabel('% preserved')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, 115)

# ── 3. Figure-8 Wigner trajectories ──────────────────────────
ax = fig.add_subplot(gs[0, 3])
log_f8 = results["Figure-8 (9 nodes)"]['log']
for i in range(9):
    s, v = wtraj(log_f8, i)
    is_j = i == 4
    ax.plot(s, v, lw=3 if is_j else 1.5,
            color='red' if is_j else ('#FF6B35' if i < 4 else 'purple'),
            alpha=1.0 if is_j else 0.6,
            label=f'Node {i} (JUNCTION)' if is_j else None)
ax.axhline(ALPHA_FLOOR, color='black', ls='--', lw=2)
ax.axhline(0, color='red', ls=':', lw=1.5)
ax.set_title('Figure-8: Junction Node Wigner\nDoes sharing loops sacrifice it?',
             fontweight='bold')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# ── 4. N-loop scaling: % preserved ───────────────────────────
ax = fig.add_subplot(gs[1, 0])
n_list   = sorted(scaling.keys())
pct_list = [scaling[n]['pct_preserved'] for n in n_list]
n_list_n = [scaling[n]['n_nodes']       for n in n_list]

ax.plot(n_list, pct_list, 'o-', color='#1f77b4', lw=2.5, ms=12)
ax.axhline(100, color='green', ls='--', lw=1.5)
for n, p, nn in zip(n_list, pct_list, n_list_n):
    ax.annotate(f'{p:.1f}%\n({nn}n)', (n, p),
                textcoords='offset points', xytext=(0, 10), ha='center', fontsize=8)
ax.set_xticks(n_list)
ax.set_xticklabels([f'{n} loop' + ('s' if n>1 else '') for n in n_list], fontsize=8)
ax.set_title('N-Loop Scaling: % Preserved\nWhere is the sweet spot?', fontweight='bold')
ax.set_ylabel('% preserved'); ax.grid(True, alpha=0.3)
ax.set_ylim(0, 115)

# ── 5. N-loop scaling: mean floor ────────────────────────────
ax = fig.add_subplot(gs[1, 1])
mean_list = [scaling[n]['mean_floor'] for n in n_list]
ax.plot(n_list, mean_list, 's-', color='purple', lw=2.5, ms=12)
ax.axhline(ALPHA_FLOOR, color='black', ls='--', lw=2, label=f'Full preservation')
ax.axhline(0, color='red', ls=':', lw=1.5)
for n, m in zip(n_list, mean_list):
    ax.annotate(f'{m:+.4f}', (n, m),
                textcoords='offset points', xytext=(0, 8), ha='center', fontsize=8)
ax.set_xticks(n_list)
ax.set_xticklabels([f'{n} loop' + ('s' if n>1 else '') for n in n_list], fontsize=8)
ax.set_title('Mean W_min Floor vs N Loops', fontweight='bold')
ax.set_ylabel('Mean W_min'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# ── 6. Junction floors across loop chain ─────────────────────
ax = fig.add_subplot(gs[1, 2])
for n in n_list:
    jf = scaling[n]['junction_floors']
    # Junction position along chain
    for k, f in enumerate(jf):
        ax.scatter([n], [f], s=90, zorder=5,
                   color='red' if abs(f-ALPHA_FLOOR) > 0.005 else 'green',
                   marker='*' if abs(f-ALPHA_FLOOR) < 0.005 else 'o')
ax.axhline(ALPHA_FLOOR, color='black', ls='--', lw=2, label='Full preservation')
ax.axhline(0, color='red', ls=':', lw=1.5, label='Classical')
from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([0],[0],marker='*',color='w',markerfacecolor='green',markersize=10,label='Preserved junction'),
    Line2D([0],[0],marker='o',color='w',markerfacecolor='red',  markersize=10,label='Sacrificed junction'),
], fontsize=8)
ax.set_xticks(n_list)
ax.set_title('Junction Node Status vs N Loops\n★green=preserved, ●red=sacrificed',
             fontweight='bold')
ax.set_ylabel('Junction W_min'); ax.set_xlabel('N loops')
ax.grid(True, alpha=0.3)

# ── 7. Triple-8 full trajectory ──────────────────────────────
ax = fig.add_subplot(gs[1, 3])
log_t8 = results["Triple-8 (13 nodes)"]['log']
for i in range(13):
    s, v = wtraj(log_t8, i)
    is_j = i in [4, 8]
    ax.plot(s, v, lw=3 if is_j else 1,
            color='red' if is_j else 'green' if i < 4 else
                  'blue' if i < 8 else 'purple',
            alpha=1.0 if is_j else 0.4,
            label=f'Junction {i}' if is_j else None)
ax.axhline(ALPHA_FLOOR, color='black', ls='--', lw=2)
ax.axhline(0, color='red', ls=':', lw=1.5)
ax.set_title('Triple Figure-8 Wigner\nThree loops, two junctions', fontweight='bold')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# ── 8. Coherence across topologies ───────────────────────────
ax = fig.add_subplot(gs[2, 0:2])
for name, data in results.items():
    steps = [r['step'] for r in data['log']]
    C_avg = [r['C_avg'] for r in data['log']]
    ax.plot(steps, C_avg, color=data['color'], lw=2, alpha=0.8,
            label=name.split('(')[0].strip())
ax.axhline(1.0, color='gray', ls=':', lw=1)
ax.set_title('Mean Coherence — All Topologies\nDoes adding loops maintain C=1?',
             fontweight='bold')
ax.set_xlabel('Step'); ax.set_ylabel('C_avg')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
ax.set_ylim(0.95, 1.005)

# ── 9. Summary table ─────────────────────────────────────────
ax = fig.add_subplot(gs[2, 2:])
ax.axis('off')

rows = [['Config', 'Nodes', 'Preserved', '%', 'Mean W', 'Sweet spot?']]
for name, data in results.items():
    rows.append([
        name[:20],
        str(data['n_nodes']),
        f"{data['n_preserved']}/{data['n_nodes']}",
        f"{data['pct_preserved']:.1f}%",
        f"{data['mean_floor']:+.4f}",
        '✓ YES' if data['pct_preserved'] == 100 else '—',
    ])
rows.append(['--- Scaling ---', '', '', '', '', ''])
for n in n_list:
    sr = scaling[n]
    rows.append([
        f'{n} loop chain',
        str(sr['n_nodes']),
        f"{sr['n_preserved']}/{sr['n_nodes']}",
        f"{sr['pct_preserved']:.1f}%",
        f"{sr['mean_floor']:+.4f}",
        '✓' if sr['pct_preserved'] == 100 else '—',
    ])

t_w = ax.table(
    cellText  = [r[1:] for r in rows[1:]],
    colLabels = rows[0][1:],
    rowLabels = [r[0] for r in rows[1:]],
    loc='center', cellLoc='center'
)
t_w.auto_set_font_size(False)
t_w.set_fontsize(7.5)
t_w.scale(1.0, 1.28)
ax.set_title('Complete Multi-Loop Results Summary', fontweight='bold', fontsize=11)

plt.savefig('outputs/multiloop_fixed.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/multiloop_fixed.png")

# ============================================================
# SAVE & VERDICT
# ============================================================

with open('outputs/multiloop_fixed_results.json', 'w') as f:
    json.dump({
        'topologies': {
            name: {k: v for k, v in data.items() if k != 'log'}
            for name, data in results.items()
        },
        'n_loop_scaling': {
            str(n): v for n, v in scaling.items()
        },
        'alpha_floor': ALPHA_FLOOR,
    }, f, indent=2)

print("\n" + "=" * 65)
print("MULTI-LOOP VERDICT")
print("=" * 65)

print(f"\n{'Config':<28} {'% Preserved':>12} {'Mean Floor':>12} {'Verdict':>12}")
print("-" * 68)
for name, data in results.items():
    verdict = "✓ ALL" if data['pct_preserved'] == 100 else \
              f"{data['n_preserved']}/{data['n_nodes']}"
    print(f"{name:<28} {data['pct_preserved']:>11.1f}% "
          f"{data['mean_floor']:>+12.4f} {verdict:>12}")

print(f"\nN-loop scaling:")
for n in n_list:
    sr = scaling[n]
    print(f"  {n} loop(s): {sr['n_nodes']:2d} nodes  "
          f"{sr['n_preserved']:2d}/{sr['n_nodes']:2d} ({sr['pct_preserved']:.1f}%)  "
          f"mean={sr['mean_floor']:+.4f}")

# Find sweet spot
sweet = max(n_list, key=lambda n: scaling[n]['pct_preserved'])
print(f"\n→ Best preservation: {sweet} loop(s) "
      f"({scaling[sweet]['pct_preserved']:.1f}%)")

# Junction analysis
f8_j = results["Figure-8 (9 nodes)"]['floors'][4]
print(f"\nFigure-8 junction floor: {f8_j:+.4f}")
print(f"Junction status: {'PRESERVED ✓' if abs(f8_j-ALPHA_FLOOR)<0.005 else 'sacrificed'}")
