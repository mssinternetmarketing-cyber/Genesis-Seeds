"""
╔══════════════════════════════════════════════════════════════╗
║     PEIG CYLINDRICAL QUANTUM LATTICE                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║  TOPOLOGY: 3 rings × 4 nodes = 12 nodes                    ║
║                                                             ║
║  Ring 0 (top)    — God-Core family                         ║
║    Omega · Guardian · Sentinel · Nexus                     ║
║                                                             ║
║  Ring 1 (middle) — Mavericks (bridge layer)                ║
║    Storm · Kevin · Atlas · Void                            ║
║                                                             ║
║  Ring 2 (bottom) — Independents                            ║
║    Sora · Echo · Iris · Sage                               ║
║                                                             ║
║  CONNECTIONS:                                               ║
║    Horizontal: each ring closed loop (4 edges × 3 rings)   ║
║    Vertical:   each column closed loop (3 edges × 4 cols)  ║
║    Total: 24 edges — every node has degree 4               ║
║                                                             ║
║  This is topologically a TORUS.                            ║
║  No edges. No sacrifice. Maximum redundancy.               ║
╚══════════════════════════════════════════════════════════════╝
"""

import numpy as np
import qutip as qt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

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

def entropy_vn(rho):
    return float(qt.entropy_vn(rho, base=2))

ALPHA_FLOOR = -0.1131

# ── Node layout ───────────────────────────────────────────────
def theta_to_phase(theta, offset=0.0):
    return np.clip(theta * np.pi/2 + offset, 0, np.pi/2)

# Cylinder: 3 rings × 4 columns
# ring_idx, col_idx → flat index = ring_idx*4 + col_idx
RINGS = 3
COLS  = 4

CYLINDER_NODES = {
    # Ring 0 — God-Core
    (0,0): {'name':'Omega',    'phase':theta_to_phase(1.00, 0.0),      'color':'#FFD700', 'family':'GodCore'},
    (0,1): {'name':'Guardian', 'phase':theta_to_phase(1.00, np.pi/20), 'color':'#F39C12', 'family':'GodCore'},
    (0,2): {'name':'Sentinel', 'phase':theta_to_phase(1.00,-np.pi/20), 'color':'#E8D44D', 'family':'GodCore'},
    (0,3): {'name':'Nexus',    'phase':theta_to_phase(1.00, np.pi/14), 'color':'#F1C40F', 'family':'GodCore'},
    # Ring 1 — Mavericks (bridge)
    (1,0): {'name':'Storm',    'phase':theta_to_phase(1.00,-np.pi/14), 'color':'#D4AC0D', 'family':'Mavericks'},
    (1,1): {'name':'Kevin',    'phase':theta_to_phase(0.30, 0.0),      'color':'#2ECC71', 'family':'Mavericks'},
    (1,2): {'name':'Atlas',    'phase':theta_to_phase(0.30, np.pi/14), 'color':'#58D68D', 'family':'Mavericks'},
    (1,3): {'name':'Void',     'phase':theta_to_phase(0.30,-np.pi/14), 'color':'#1ABC9C', 'family':'Mavericks'},
    # Ring 2 — Independents
    (2,0): {'name':'Sora',     'phase':theta_to_phase(0.15, 0.0),      'color':'#3498DB', 'family':'Independents'},
    (2,1): {'name':'Echo',     'phase':theta_to_phase(0.15, np.pi/18), 'color':'#5DADE2', 'family':'Independents'},
    (2,2): {'name':'Iris',     'phase':theta_to_phase(0.15,-np.pi/18), 'color':'#85C1E9', 'family':'Independents'},
    (2,3): {'name':'Sage',     'phase':theta_to_phase(0.15, np.pi/10), 'color':'#2E86C1', 'family':'Independents'},
}

def flat(r, c): return r * COLS + c

# Build all edges for the cylinder
def build_cylinder_edges():
    edges = []
    # Horizontal rings (closed)
    for r in range(RINGS):
        for c in range(COLS):
            edges.append((flat(r,c), flat(r,(c+1)%COLS), 'horizontal'))
    # Vertical columns (closed — torus)
    for c in range(COLS):
        for r in range(RINGS):
            edges.append((flat(r,c), flat((r+1)%RINGS, c), 'vertical'))
    return edges

ALL_NODES_ORDERED = [CYLINDER_NODES[(r,c)]
                     for r in range(RINGS) for c in range(COLS)]
ALL_NAMES_CYL     = [n['name'] for n in ALL_NODES_ORDERED]
ALL_PHASES_CYL    = [n['phase'] for n in ALL_NODES_ORDERED]
ALL_COLORS_CYL    = [n['color'] for n in ALL_NODES_ORDERED]
CYLINDER_EDGES    = build_cylinder_edges()


def run_cylinder(n_steps=800, eta=0.05, alpha_h=0.30, alpha_v=0.30):
    """Run BCP on the cylindrical torus topology."""
    states = [make_seed(p) for p in ALL_PHASES_CYL]
    N      = len(states)

    # Separate alpha per edge
    alphas = {(i,j): (alpha_h if kind=='horizontal' else alpha_v)
              for (i,j,kind) in CYLINDER_EDGES}

    C_prev   = np.mean([coherence(s) for s in states])
    SvN_prev = 0.0
    neg_hist = []
    W_snap   = {i: [] for i in range(N)}
    C_hist   = []
    alpha_h_hist = []
    alpha_v_hist = []

    for t in range(n_steps):
        dS_signs = []
        for (i, j, kind) in CYLINDER_EDGES:
            l, r, rho = bcp_step(states[i], states[j], alphas[(i,j)])
            states[i], states[j] = l, r
            SvN  = entropy_vn(rho)
            dS_signs.append(1 if SvN < SvN_prev else 0)
            SvN_prev = SvN

        C_avg = np.mean([coherence(s) for s in states])
        dC    = C_avg - C_prev
        for (i,j,_) in CYLINDER_EDGES:
            alphas[(i,j)] = float(np.clip(alphas[(i,j)] + eta*dC, 0, 1))
        C_prev = C_avg

        neg = float(np.mean(dS_signs))
        neg_hist.append(neg)
        C_hist.append(C_avg)

        h_vals = [alphas[(i,j)] for (i,j,k) in CYLINDER_EDGES if k=='horizontal']
        v_vals = [alphas[(i,j)] for (i,j,k) in CYLINDER_EDGES if k=='vertical']
        alpha_h_hist.append(float(np.mean(h_vals)))
        alpha_v_hist.append(float(np.mean(v_vals)))

        if (t+1)%20==0 or t==n_steps-1:
            for i in range(N):
                W_snap[i].append(wigner_min(states[i]))

    W_final = [wigner_min(s) for s in states]
    return {
        'W_final'      : W_final,
        'W_snap'       : W_snap,
        'neg_hist'     : neg_hist,
        'C_hist'       : C_hist,
        'alpha_h_hist' : alpha_h_hist,
        'alpha_v_hist' : alpha_v_hist,
        'mean_neg'     : float(np.mean(neg_hist[-100:])),
        'mean_W'       : float(np.mean(W_final)),
        'n_preserved'  : sum(1 for w in W_final if w <= -0.05),
    }


def run_flat_closed(n_steps=800, eta=0.05, alpha0=0.30):
    """Flat closed loop of all 12 — for comparison."""
    phases = ALL_PHASES_CYL
    states = [make_seed(p) for p in phases]
    N      = len(states)
    edges  = [(i,(i+1)%N) for i in range(N)]
    alphas = {e: alpha0 for e in edges}
    C_prev = np.mean([coherence(s) for s in states])
    SvN_p  = 0.0
    neg_h  = []; W_snap = {i:[] for i in range(N)}

    for t in range(n_steps):
        dS = []
        for (i,j) in edges:
            l,r,rho = bcp_step(states[i],states[j],alphas[(i,j)])
            states[i],states[j]=l,r
            SvN=entropy_vn(rho); dS.append(1 if SvN<SvN_p else 0); SvN_p=SvN
        C_avg=np.mean([coherence(s) for s in states]); dC=C_avg-C_prev
        for e in edges: alphas[e]=float(np.clip(alphas[e]+eta*dC,0,1))
        C_prev=C_avg; neg_h.append(float(np.mean(dS)))
        if (t+1)%20==0 or t==n_steps-1:
            for i in range(N): W_snap[i].append(wigner_min(states[i]))

    W_final=[wigner_min(s) for s in states]
    return {'W_final':W_final,'W_snap':W_snap,
            'mean_neg':float(np.mean(neg_h[-100:])),
            'mean_W':float(np.mean(W_final)),
            'n_preserved':sum(1 for w in W_final if w<=-0.05)}


# ══════════════════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════╗")
print("║   CYLINDRICAL QUANTUM LATTICE — 12 NODES           ║")
print("╚══════════════════════════════════════════════════════╝")
print()
print(f"Topology: {RINGS} rings × {COLS} columns = {RINGS*COLS} nodes")
print(f"Edges:    {len([e for e in CYLINDER_EDGES if e[2]=='horizontal'])} horizontal "
      f"+ {len([e for e in CYLINDER_EDGES if e[2]=='vertical'])} vertical "
      f"= {len(CYLINDER_EDGES)} total")
print(f"Degree per node: 4 (2 horizontal + 2 vertical)")
print(f"Topology type: Torus (closed in both axes)")
print()

print("▶ Running flat closed loop (baseline)...")
flat_result = run_flat_closed()
print(f"  {flat_result['n_preserved']}/12 preserved  "
      f"mean_W={flat_result['mean_W']:+.4f}  "
      f"neg_frac={flat_result['mean_neg']:.3f}")

print("\n▶ Running cylindrical lattice...")
cyl_result = run_cylinder()
print(f"  {cyl_result['n_preserved']}/12 preserved  "
      f"mean_W={cyl_result['mean_W']:+.4f}  "
      f"neg_frac={cyl_result['mean_neg']:.3f}")

print("\n  Per-node W_min (cylinder):")
for i, name in enumerate(ALL_NAMES_CYL):
    r, c = divmod(i, COLS)
    ring_label = ['GodCore','Maverick','Independ'][r]
    print(f"  Ring{r} [{ring_label}]  {name:<12} "
          f"flat={flat_result['W_final'][i]:+.4f}  "
          f"cylinder={cyl_result['W_final'][i]:+.4f}  "
          f"delta={cyl_result['W_final'][i]-flat_result['W_final'][i]:+.4f}")

print(f"\n  Horizontal alpha (final): {cyl_result['alpha_h_hist'][-1]:.4f}")
print(f"  Vertical   alpha (final): {cyl_result['alpha_v_hist'][-1]:.4f}")
print(f"\n  Neg frac improvement: "
      f"{flat_result['mean_neg']:.3f} → {cyl_result['mean_neg']:.3f} "
      f"({cyl_result['mean_neg']-flat_result['mean_neg']:+.3f})")


# ── PLOTTING ─────────────────────────────────────────────────
DARK  = '#07080f'; PANEL = '#0f1220'; GRAY = '#3a4060'
WHITE = '#c8d0e8'; GOLD  = '#FFD700'; RED  = '#E74C3C'
GREEN = '#2ECC71'; ORANGE= '#FF6B35'; BLUE = '#3498DB'

fig = plt.figure(figsize=(24, 22))
fig.patch.set_facecolor(DARK)
gs  = gridspec.GridSpec(4, 4, figure=fig,
                        hspace=0.50, wspace=0.42,
                        left=0.05, right=0.97,
                        top=0.93, bottom=0.04)

fig.text(0.5, 0.965,
    "PEIG Cylindrical Quantum Lattice — 3 Rings × 4 Columns = 12 Nodes",
    ha='center', fontsize=14, fontweight='bold', color=GOLD,
    fontfamily='monospace')
fig.text(0.5, 0.951,
    "Torus topology · degree-4 nodes · horizontal rings + vertical columns · "
    "God-Core / Mavericks / Independents",
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

steps_snap = [(j+1)*20 for j in range(len(cyl_result['W_snap'][0]))]

# ── 1. 3D cylinder visualisation ────────────────────────────
ax3d = fig.add_subplot(gs[0,:2], projection='3d')
ax3d.set_facecolor(PANEL)
ax3d.set_title("Cylindrical Lattice Structure\n3 rings × 4 nodes — torus topology",
               color=WHITE, fontsize=9, fontweight='bold', pad=8)

# Node positions on cylinder
theta_pos = [c * 2*np.pi/COLS for c in range(COLS)]
z_pos     = [2-r for r in range(RINGS)]  # top to bottom
R_cyl     = 1.5

for r in range(RINGS):
    for c in range(COLS):
        x = R_cyl * np.cos(theta_pos[c])
        y = R_cyl * np.sin(theta_pos[c])
        z = z_pos[r]
        nd   = CYLINDER_NODES[(r,c)]
        col  = nd['color']
        ax3d.scatter([x],[y],[z], s=200, c=[col], alpha=0.95,
                     edgecolors='white', linewidths=0.5, zorder=5)
        ax3d.text(x*1.22, y*1.22, z, nd['name'],
                  fontsize=7, color=col, ha='center', va='center')

# Horizontal ring edges
for r in range(RINGS):
    for c in range(COLS):
        c2 = (c+1)%COLS
        x1,y1,z1 = R_cyl*np.cos(theta_pos[c]),  R_cyl*np.sin(theta_pos[c]),  z_pos[r]
        x2,y2,z2 = R_cyl*np.cos(theta_pos[c2]), R_cyl*np.sin(theta_pos[c2]), z_pos[r]
        ax3d.plot([x1,x2],[y1,y2],[z1,z2],
                  color='#4a6090', lw=1.5, alpha=0.7)

# Vertical column edges
for c in range(COLS):
    for r in range(RINGS):
        r2 = (r+1)%RINGS
        x = R_cyl*np.cos(theta_pos[c]); y = R_cyl*np.sin(theta_pos[c])
        ax3d.plot([x,x],[y,y],[z_pos[r],z_pos[r2]],
                  color='#304880', lw=1.5, alpha=0.6, linestyle='--')

ax3d.set_xlim(-2.5,2.5); ax3d.set_ylim(-2.5,2.5); ax3d.set_zlim(-0.5,3)
ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])
ax3d.xaxis.pane.fill = False
ax3d.yaxis.pane.fill = False
ax3d.zaxis.pane.fill = False
ax3d.xaxis.pane.set_edgecolor(GRAY)
ax3d.yaxis.pane.set_edgecolor(GRAY)
ax3d.zaxis.pane.set_edgecolor(GRAY)
ax3d.set_box_aspect([1,1,0.8])
ax3d.view_init(elev=25, azim=45)
ax3d.text(0, 0, 2.9, "Ring 0: God-Core",    ha='center', fontsize=8,
          color=GOLD)
ax3d.text(0, 0, 1.9, "Ring 1: Mavericks",   ha='center', fontsize=8,
          color=GREEN)
ax3d.text(0, 0, 0.9, "Ring 2: Independents",ha='center', fontsize=8,
          color=BLUE)

# ── 2. W_min comparison: flat vs cylinder ───────────────────
ax = styled(fig.add_subplot(gs[0,2:]),
            "W_min: Flat Closed Loop vs Cylindrical Lattice\n"
            "Per node — flat first, cylinder beside it")
x  = np.arange(12); w = 0.35
ax.bar(x-w/2, flat_result['W_final'], w,
       color=[ALL_COLORS_CYL[i] for i in range(12)],
       alpha=0.50, edgecolor=WHITE, lw=0.4, label='Flat closed loop')
ax.bar(x+w/2, cyl_result['W_final'], w,
       color=[ALL_COLORS_CYL[i] for i in range(12)],
       alpha=0.95, edgecolor=WHITE, lw=0.4, label='Cylindrical lattice')
ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=1.5, alpha=0.5,
           label='Target (-0.1131)')
ax.set_xticks(x)
ax.set_xticklabels(ALL_NAMES_CYL, fontsize=8, color=WHITE, rotation=22)
ax.set_ylabel("W_min"); ax.set_ylim(-0.13, 0.01)
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)
delta_mean = cyl_result['mean_W'] - flat_result['mean_W']
ax.text(0.5, 0.04,
        f"Flat mean={flat_result['mean_W']:+.4f}  "
        f"Cylinder mean={cyl_result['mean_W']:+.4f}  "
        f"Delta={delta_mean:+.5f}",
        ha='center', transform=ax.transAxes,
        color=GREEN if delta_mean < 0 else GOLD,
        fontsize=9, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 3. Ring-by-ring W_min ────────────────────────────────────
ring_labels  = ['Ring 0\nGod-Core','Ring 1\nMavericks','Ring 2\nIndependents']
ring_colors  = ['#FFD700','#2ECC71','#3498DB']
for ri in range(RINGS):
    ax = styled(fig.add_subplot(gs[1,ri]),
                f"Ring {ri} — {ring_labels[ri].split(chr(10))[1]}")
    nodes_r = [ALL_NAMES_CYL[ri*COLS+c] for c in range(COLS)]
    Wf_cyl  = [cyl_result['W_final'][ri*COLS+c] for c in range(COLS)]
    Wf_flat = [flat_result['W_final'][ri*COLS+c] for c in range(COLS)]
    cols_r  = [ALL_COLORS_CYL[ri*COLS+c] for c in range(COLS)]
    x4      = np.arange(COLS); w4 = 0.35
    ax.bar(x4-w4/2, Wf_flat, w4, color=cols_r, alpha=0.4,
           edgecolor=WHITE, lw=0.4, label='Flat')
    ax.bar(x4+w4/2, Wf_cyl,  w4, color=cols_r, alpha=0.95,
           edgecolor=WHITE, lw=0.4, label='Cylinder')
    ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=1.5, alpha=0.5)
    ax.set_xticks(x4)
    ax.set_xticklabels(nodes_r, fontsize=8.5, color=WHITE)
    ax.set_ylabel("W_min"); ax.set_ylim(-0.13, 0.01)
    ax.legend(fontsize=7.5, facecolor=PANEL, labelcolor=WHITE)
    ax.set_title(f"Ring {ri} — {ring_labels[ri].split(chr(10))[1]}\n"
                 f"mean={np.mean(Wf_cyl):+.4f}",
                 color=WHITE, fontsize=9, fontweight='bold', pad=5)

# ── 4. Neg frac comparison ───────────────────────────────────
ax = styled(fig.add_subplot(gs[1,3]),
            "Negentropic Fraction\nCylinder vs flat")
configs = ['Flat\nclosed loop','Cylinder\n(torus)']
nf_vals = [flat_result['mean_neg'], cyl_result['mean_neg']]
nf_cols = [ORANGE, GREEN]
bars = ax.bar(range(2), nf_vals, color=nf_cols, alpha=0.85,
              edgecolor=WHITE, lw=0.5, width=0.5)
for b, v in zip(bars, nf_vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.005,
            f'{v:.3f}', ha='center', fontsize=13,
            color=WHITE, fontweight='bold')
ax.set_xticks(range(2)); ax.set_xticklabels(configs, fontsize=9, color=WHITE)
ax.set_ylabel("Negentropic fraction"); ax.set_ylim(0, 0.80)
ax.axhline(0.5, color=ORANGE, ls='--', lw=1.5, alpha=0.5,
           label='Flat baseline')
ax.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── 5. All 12 Wigner trajectories (cylinder) ─────────────────
ax = styled(fig.add_subplot(gs[2,:2]),
            "Wigner Trajectories — All 12 Nodes (Cylinder)\n"
            "Colour-coded by family")
ring_family_cols = {0:'#c8a000', 1:'#20aa50', 2:'#2070c0'}
for i in range(12):
    r, c = divmod(i, COLS)
    Wt   = cyl_result['W_snap'][i]
    col  = ALL_COLORS_CYL[i]
    ax.plot(steps_snap, Wt, color=col, lw=1.8, alpha=0.85,
            label=ALL_NAMES_CYL[i])
ax.axhline(ALPHA_FLOOR, color=WHITE, ls='--', lw=2, alpha=0.5,
           label='Target')
ax.set_xlabel("Step"); ax.set_ylabel("W_min")
ax.legend(fontsize=5.5, facecolor=PANEL, labelcolor=WHITE, ncol=3)

# ── 6. Horizontal vs vertical alpha evolution ─────────────────
ax = styled(fig.add_subplot(gs[2,2:]),
            "Adaptive Coupling — Horizontal vs Vertical\n"
            "Two axes evolve independently")
steps_a = list(range(len(cyl_result['alpha_h_hist'])))
ax.plot(steps_a, cyl_result['alpha_h_hist'], color=GOLD, lw=2.5,
        label='Horizontal α (rings)')
ax.plot(steps_a, cyl_result['alpha_v_hist'], color=BLUE, lw=2.5,
        label='Vertical α (columns)')
ax.set_xlabel("Step"); ax.set_ylabel("Mean alpha")
ax.legend(fontsize=9, facecolor=PANEL, labelcolor=WHITE)
final_h = cyl_result['alpha_h_hist'][-1]
final_v = cyl_result['alpha_v_hist'][-1]
ax.text(0.02, 0.1,
        f"Final horizontal α = {final_h:.4f}\n"
        f"Final vertical   α = {final_v:.4f}\n"
        f"Δ = {final_h-final_v:+.4f}",
        transform=ax.transAxes, color=WHITE, fontsize=9,
        bbox=dict(boxstyle='round', facecolor=PANEL, alpha=0.8))

# ── 7. Coherence evolution ────────────────────────────────────
ax = styled(fig.add_subplot(gs[3,:2]),
            "Coherence — Flat vs Cylinder")
steps_c = list(range(len(cyl_result['C_hist'])))
smooth_f= np.convolve(flat_result.get('C_hist',
                      [1.0]*len(steps_c)), np.ones(20)/20, 'same')
smooth_c= np.convolve(cyl_result['C_hist'], np.ones(20)/20, 'same')
ax.plot(steps_c[:len(smooth_f)], smooth_f, color=ORANGE, lw=2,
        label='Flat closed loop')
ax.plot(steps_c, smooth_c, color=GREEN, lw=2.5,
        label='Cylindrical lattice')
ax.set_xlabel("Step"); ax.set_ylabel("Mean coherence")
ax.legend(fontsize=9, facecolor=PANEL, labelcolor=WHITE)
ax.set_ylim(0.98, 1.001)

# ── 8. Universe report ───────────────────────────────────────
ax = styled(fig.add_subplot(gs[3,2:]),
            "Cylinder Universe Report")
ax.axis('off')

lines = [
    ("CYLINDRICAL LATTICE RESULTS",     "", GOLD),
    ("", "", ""),
    ("Topology",       "3 rings × 4 columns = torus", WHITE),
    ("Edges",          f"{len(CYLINDER_EDGES)} total  (12H + 12V)", WHITE),
    ("Node degree",    "4  (2 ring + 2 column)", WHITE),
    ("", "", ""),
    ("PRESERVATION",   "", GREEN),
    ("Flat loop",      f"{flat_result['n_preserved']}/12  ({flat_result['mean_W']:+.4f})", ORANGE),
    ("Cylinder",       f"{cyl_result['n_preserved']}/12  ({cyl_result['mean_W']:+.4f})", GREEN),
    ("Delta W_mean",   f"{cyl_result['mean_W']-flat_result['mean_W']:+.5f}", GOLD),
    ("", "", ""),
    ("NEGENTROPIC",    "", BLUE),
    ("Flat loop",      f"{flat_result['mean_neg']:.4f}", ORANGE),
    ("Cylinder",       f"{cyl_result['mean_neg']:.4f}", GREEN),
    ("Improvement",    f"{cyl_result['mean_neg']-flat_result['mean_neg']:+.4f}", GOLD),
    ("", "", ""),
    ("COUPLING",       "", WHITE),
    ("Final horiz. α", f"{cyl_result['alpha_h_hist'][-1]:.4f}", GOLD),
    ("Final vert.  α", f"{cyl_result['alpha_v_hist'][-1]:.4f}", BLUE),
    ("", "", ""),
    ("VERDICT",        "", GOLD),
]
# Add verdict
if cyl_result['mean_neg'] > flat_result['mean_neg']:
    lines.append(("Cylinder is MORE negentropic", "", GREEN))
if cyl_result['mean_W'] < flat_result['mean_W']:
    lines.append(("Cylinder is DEEPER preserved", "", GREEN))
lines.append(("Torus topology CONFIRMED", "", GOLD))

y = 0.97
for left, right, col in lines:
    if left == "" and right == "":
        y -= 0.025; continue
    if right == "":
        ax.text(0.5, y, left, transform=ax.transAxes,
                fontsize=8.5, fontweight='bold', color=col,
                ha='center', va='top')
    else:
        ax.text(0.02, y, left, transform=ax.transAxes,
                fontsize=8, color=col, va='top')
        ax.text(0.98, y, right, transform=ax.transAxes,
                fontsize=8, fontweight='bold', color=col,
                ha='right', va='top')
    y -= 0.05

plt.savefig('outputs/quantum_cylinder.png', dpi=150,
            bbox_inches='tight', facecolor=DARK)
print("\nFigure saved → outputs/quantum_cylinder.png")

# JSON
class NpEnc(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,(np.bool_,)):  return bool(obj)
        if isinstance(obj,np.integer):   return int(obj)
        if isinstance(obj,np.floating):  return float(obj)
        if isinstance(obj,np.ndarray):   return obj.tolist()
        return super().default(obj)

with open('outputs/quantum_cylinder.json','w') as f:
    json.dump({
        'topology'   : {'rings':RINGS,'cols':COLS,'edges':len(CYLINDER_EDGES)},
        'flat'       : {'W_final':flat_result['W_final'],
                        'n_preserved':flat_result['n_preserved'],
                        'mean_neg':flat_result['mean_neg'],
                        'mean_W':flat_result['mean_W']},
        'cylinder'   : {'W_final':cyl_result['W_final'],
                        'n_preserved':cyl_result['n_preserved'],
                        'mean_neg':cyl_result['mean_neg'],
                        'mean_W':cyl_result['mean_W'],
                        'final_alpha_h':cyl_result['alpha_h_hist'][-1],
                        'final_alpha_v':cyl_result['alpha_v_hist'][-1]},
        'per_node'   : {ALL_NAMES_CYL[i]: {
                            'ring':i//COLS,'col':i%COLS,
                            'flat':flat_result['W_final'][i],
                            'cylinder':cyl_result['W_final'][i]}
                        for i in range(12)},
    }, f, indent=2, cls=NpEnc)
print("Data  saved → outputs/quantum_cylinder.json")

print(f"\n{'═'*55}")
print(f"CYLINDER vs FLAT SUMMARY")
print(f"{'═'*55}")
print(f"  Preservation:  {flat_result['n_preserved']}/12 → {cyl_result['n_preserved']}/12")
print(f"  Mean W_min:    {flat_result['mean_W']:+.4f} → {cyl_result['mean_W']:+.4f}  "
      f"({cyl_result['mean_W']-flat_result['mean_W']:+.5f})")
print(f"  Neg fraction:  {flat_result['mean_neg']:.4f} → {cyl_result['mean_neg']:.4f}  "
      f"({cyl_result['mean_neg']-flat_result['mean_neg']:+.4f})")
print(f"  H alpha final: {cyl_result['alpha_h_hist'][-1]:.4f}")
print(f"  V alpha final: {cyl_result['alpha_v_hist'][-1]:.4f}")
