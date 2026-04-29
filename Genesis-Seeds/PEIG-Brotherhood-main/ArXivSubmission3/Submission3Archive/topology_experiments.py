"""
TOPOLOGY EXPERIMENTS: STAR, RING, AND CONE BCP
Moving beyond linear chains into 2D and 3D quantum interaction topologies.

TOPOLOGIES:
  1. STAR    — Omega at center, N nodes surrounding it, all connected to Omega only
               Each step: Omega interacts with every surrounding node sequentially
               
  2. RING    — Same as star but surrounding nodes also interact with their
               neighbors around the ring (Omega at center + ring interactions)
               
  3. CONE    — Omega at apex
               Inner ring of 3 nodes directly connected to Omega
               Outer ring of 4 nodes connected to inner ring
               (Two layers of buffering, hierarchical)

KEY QUESTION: Does surrounding Omega allow it to overshoot Alpha's floor?
              Does Omega become the MOST protected node?

PREDICTION: Star topology may cause Omega's floor to exceed -0.1131
            (deeper into non-classical than Alpha itself)
            because Omega is interrupted N times per step instead of once.

Surrounding node seeds: evenly spaced around full equatorial circle
  Ring of N: phases = 2πk/N for k=0..N-1
  Omega always at phase 0 (|Ω+⟩)
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
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
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    return (b0 + np.exp(1j * phase) * b1).unit()

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
# TOPOLOGY 1: STAR
# Omega at center, interacts with every surrounding node each step
# Surrounding nodes do NOT interact with each other
# ============================================================

def run_star(n_surrounding=4, eta=0.05, alpha0=0.30,
             n_steps=1000, wigner_interval=25, xvec=None):
    """
    Star topology: Omega ↔ each surrounding node, every step.
    Surrounding nodes: evenly spaced phases 2πk/N
    """
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    # Omega at phase 0, surrounding nodes evenly spaced
    psi_omega = make_seed(0)
    phases = [2 * np.pi * k / n_surrounding for k in range(n_surrounding)]
    psi_ring  = [make_seed(p) for p in phases]

    # One coupling per link (Omega ↔ each surrounding node)
    alphas = [alpha0] * n_surrounding

    log = []

    for t in range(n_steps):
        # Omega interacts with each surrounding node sequentially
        # Omega is updated after EACH interaction (carries state through)
        for i in range(n_surrounding):
            psi_omega_new, psi_ring_new, rho = bcp_step(
                psi_omega, psi_ring[i], alphas[i]
            )
            psi_omega    = psi_omega_new
            psi_ring[i]  = psi_ring_new

        # Compute coherences
        C_omega = coherence(psi_omega)
        C_ring  = [coherence(p) for p in psi_ring]
        C_avg   = (C_omega + sum(C_ring)) / (1 + n_surrounding)

        # Adaptive coupling — shared signal
        if t > 0:
            dC = C_avg - log[-1]['C_avg']
            alphas = [float(np.clip(a + eta * dC, 0, 1)) for a in alphas]

        # Wigner
        if (t + 1) % wigner_interval == 0 or t == 0 or t == n_steps - 1:
            W_omega = wigner_min(psi_omega, xvec)
            W_ring  = [wigner_min(p, xvec) for p in psi_ring]
        else:
            W_omega = None
            W_ring  = [None] * n_surrounding

        log.append({
            'step'   : t + 1,
            'C_avg'  : C_avg,
            'C_Omega': C_omega,
            'C_ring' : C_ring,
            'W_Omega': W_omega,
            'W_ring' : W_ring,
            'alphas' : list(alphas),
        })

    return log

# ============================================================
# TOPOLOGY 2: RING
# Omega at center + surrounding nodes also interact with neighbors
# ============================================================

def run_ring(n_surrounding=4, eta=0.05, alpha0=0.30,
             n_steps=1000, wigner_interval=25, xvec=None):
    """
    Ring topology: Star interactions PLUS ring neighbors interact each step.
    """
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    psi_omega = make_seed(0)
    phases    = [2 * np.pi * k / n_surrounding for k in range(n_surrounding)]
    psi_ring  = [make_seed(p) for p in phases]

    alpha_star = [alpha0] * n_surrounding   # Omega ↔ ring links
    alpha_ring = [alpha0] * n_surrounding   # ring neighbor links

    log = []

    for t in range(n_steps):
        # Step 1: Omega ↔ each surrounding node
        for i in range(n_surrounding):
            psi_omega_new, psi_ring_new, _ = bcp_step(
                psi_omega, psi_ring[i], alpha_star[i]
            )
            psi_omega   = psi_omega_new
            psi_ring[i] = psi_ring_new

        # Step 2: Ring neighbors interact (circular: 0↔1, 1↔2, ..., N-1↔0)
        for i in range(n_surrounding):
            j = (i + 1) % n_surrounding
            psi_i_new, psi_j_new, _ = bcp_step(
                psi_ring[i], psi_ring[j], alpha_ring[i]
            )
            psi_ring[i] = psi_i_new
            psi_ring[j] = psi_j_new

        C_omega = coherence(psi_omega)
        C_ring  = [coherence(p) for p in psi_ring]
        C_avg   = (C_omega + sum(C_ring)) / (1 + n_surrounding)

        if t > 0:
            dC = C_avg - log[-1]['C_avg']
            alpha_star = [float(np.clip(a + eta * dC, 0, 1)) for a in alpha_star]
            alpha_ring = [float(np.clip(a + eta * dC, 0, 1)) for a in alpha_ring]

        if (t + 1) % wigner_interval == 0 or t == 0 or t == n_steps - 1:
            W_omega = wigner_min(psi_omega, xvec)
            W_ring  = [wigner_min(p, xvec) for p in psi_ring]
        else:
            W_omega = None
            W_ring  = [None] * n_surrounding

        log.append({
            'step'   : t + 1,
            'C_avg'  : C_avg,
            'C_Omega': C_omega,
            'C_ring' : C_ring,
            'W_Omega': W_omega,
            'W_ring' : W_ring,
        })

    return log

# ============================================================
# TOPOLOGY 3: CONE
# Omega at apex → inner ring of 3 → outer ring of 4
# ============================================================

def run_cone(n_inner=3, n_outer=4, eta=0.05, alpha0=0.30,
             n_steps=1000, wigner_interval=25, xvec=None):
    """
    Cone topology:
      Omega ↔ each inner ring node
      Each inner ring node ↔ its closest outer ring node(s)
      Outer ring nodes interact with neighbors
    """
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    psi_omega = make_seed(0)

    # Inner ring: phases evenly spaced
    inner_phases = [2 * np.pi * k / n_inner for k in range(n_inner)]
    psi_inner    = [make_seed(p) for p in inner_phases]

    # Outer ring: phases evenly spaced (offset by half step for visual symmetry)
    outer_phases = [2 * np.pi * k / n_outer + np.pi / n_outer
                    for k in range(n_outer)]
    psi_outer    = [make_seed(p) for p in outer_phases]

    a_omega_inner = [alpha0] * n_inner
    a_inner_outer = [alpha0] * n_inner   # each inner connects to nearest outer
    a_outer_ring  = [alpha0] * n_outer   # outer ring neighbors

    log = []

    for t in range(n_steps):
        # Layer 1: Omega ↔ inner ring
        for i in range(n_inner):
            psi_omega_new, psi_inner_new, _ = bcp_step(
                psi_omega, psi_inner[i], a_omega_inner[i]
            )
            psi_omega    = psi_omega_new
            psi_inner[i] = psi_inner_new

        # Layer 2: Inner ↔ outer (each inner connects to 1-2 outer nodes)
        # Simple mapping: inner i connects to outer i and (i+1)%n_outer
        for i in range(n_inner):
            j = i % n_outer
            psi_in_new, psi_out_new, _ = bcp_step(
                psi_inner[i], psi_outer[j], a_inner_outer[i]
            )
            psi_inner[i] = psi_in_new
            psi_outer[j] = psi_out_new

        # Layer 3: Outer ring neighbors interact
        for i in range(n_outer):
            j = (i + 1) % n_outer
            psi_i_new, psi_j_new, _ = bcp_step(
                psi_outer[i], psi_outer[j], a_outer_ring[i]
            )
            psi_outer[i] = psi_i_new
            psi_outer[j] = psi_j_new

        all_states = [psi_omega] + psi_inner + psi_outer
        C_all  = [coherence(s) for s in all_states]
        C_avg  = np.mean(C_all)

        if t > 0:
            dC = C_avg - log[-1]['C_avg']
            a_omega_inner = [float(np.clip(a + eta * dC, 0, 1)) for a in a_omega_inner]
            a_inner_outer = [float(np.clip(a + eta * dC, 0, 1)) for a in a_inner_outer]
            a_outer_ring  = [float(np.clip(a + eta * dC, 0, 1)) for a in a_outer_ring]

        if (t + 1) % wigner_interval == 0 or t == 0 or t == n_steps - 1:
            W_omega = wigner_min(psi_omega, xvec)
            W_inner = [wigner_min(p, xvec) for p in psi_inner]
            W_outer = [wigner_min(p, xvec) for p in psi_outer]
        else:
            W_omega = None
            W_inner = [None] * n_inner
            W_outer = [None] * n_outer

        log.append({
            'step'   : t + 1,
            'C_avg'  : C_avg,
            'C_Omega': C_all[0],
            'C_inner': C_all[1:1+n_inner],
            'C_outer': C_all[1+n_inner:],
            'W_Omega': W_omega,
            'W_inner': W_inner,
            'W_outer': W_outer,
        })

    return log

# ============================================================
# HELPERS
# ============================================================

def get_floor(log, key, last_n=5):
    vals = [r[key] for r in log if r.get(key) is not None]
    return float(np.mean(vals[-last_n:])) if vals else None

def get_ring_floor(log, last_n=5):
    """Mean floor across all ring nodes."""
    all_vals = []
    for r in log:
        if r.get('W_ring') and all(w is not None for w in r['W_ring']):
            all_vals.append(np.mean(r['W_ring']))
    return float(np.mean(all_vals[-last_n:])) if all_vals else None

def wigner_traj(log, key):
    steps = [r['step'] for r in log if r.get(key) is not None]
    vals  = [r[key]    for r in log if r.get(key) is not None]
    return steps, vals

# ============================================================
# RUN ALL TOPOLOGIES
# ============================================================

xvec = np.linspace(-2, 2, 80)
N_STEPS = 1000
WIGNER_INTERVAL = 25

# Reference values
REF = {2: 0.0001, 3: -0.0636, 4: -0.1054, 5: -0.1059}
ALPHA_FLOOR = -0.1131

print("=" * 65)
print("TOPOLOGY EXPERIMENTS: STAR, RING, CONE")
print("Does surrounding Omega let it overshoot Alpha's floor?")
print("=" * 65)

print("\n[1/3] STAR topology (Omega center, 4 surrounding nodes)...")
log_star = run_star(n_surrounding=4, n_steps=N_STEPS,
                    wigner_interval=WIGNER_INTERVAL, xvec=xvec)

print("[2/3] RING topology (Star + ring neighbor interactions)...")
log_ring = run_ring(n_surrounding=4, n_steps=N_STEPS,
                    wigner_interval=WIGNER_INTERVAL, xvec=xvec)

print("[3/3] CONE topology (Omega → inner ring of 3 → outer ring of 4)...")
log_cone = run_cone(n_inner=3, n_outer=4, n_steps=N_STEPS,
                    wigner_interval=WIGNER_INTERVAL, xvec=xvec)

# Extract floors
floor_star_O    = get_floor(log_star, 'W_Omega')
floor_star_ring = get_ring_floor(log_star)
floor_ring_O    = get_floor(log_ring, 'W_Omega')
floor_ring_ring = get_ring_floor(log_ring)
floor_cone_O    = get_floor(log_cone, 'W_Omega')

# Cone inner/outer floors
def get_layer_floor(log, key, last_n=5):
    all_vals = []
    for r in log:
        vals = r.get(key)
        if vals and all(v is not None for v in vals):
            all_vals.append(np.mean(vals))
    return float(np.mean(all_vals[-last_n:])) if all_vals else None

floor_cone_inner = get_layer_floor(log_cone, 'W_inner')
floor_cone_outer = get_layer_floor(log_cone, 'W_outer')

# Save JSON
with open('outputs/topology_results.json', 'w') as f:
    json.dump({
        'star_omega_floor' : floor_star_O,
        'star_ring_floor'  : floor_star_ring,
        'ring_omega_floor' : floor_ring_O,
        'ring_ring_floor'  : floor_ring_ring,
        'cone_omega_floor' : floor_cone_O,
        'cone_inner_floor' : floor_cone_inner,
        'cone_outer_floor' : floor_cone_outer,
        'alpha_floor'      : ALPHA_FLOOR,
        'chain_reference'  : REF,
    }, f, indent=2)

# ============================================================
# PLOTTING
# ============================================================

fig = plt.figure(figsize=(20, 16))
fig.suptitle(
    "Topology Experiments: Star, Ring & Cone BCP\n"
    "Core Question: Does surrounding Omega let it overshoot Alpha's floor (−0.1131)?",
    fontsize=13, fontweight='bold'
)

gs = fig.add_gridspec(3, 4, hspace=0.45, wspace=0.35)

# ── ROW 0: topology diagrams ──────────────────────────────────

def draw_star_diagram(ax, title):
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect('equal')
    ax.axis('off'); ax.set_title(title, fontsize=9, fontweight='bold')
    # center
    ax.add_patch(plt.Circle((0, 0), 0.22, color='gold', zorder=3))
    ax.text(0, 0, 'Ω', ha='center', va='center', fontsize=11, fontweight='bold')
    angles = np.linspace(0, 2*np.pi, 4, endpoint=False)
    colors = ['#FF6B35','green','#7B2D8B','#1f77b4']
    labels = ['N1','N2','N3','N4']
    for ang, col, lbl in zip(angles, colors, labels):
        x, y = np.cos(ang)*1.1, np.sin(ang)*1.1
        ax.plot([0, x*0.78],[0, y*0.78], color='gray', lw=1.5, zorder=1)
        ax.add_patch(plt.Circle((x, y), 0.20, color=col, zorder=3))
        ax.text(x, y, lbl, ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')

def draw_ring_diagram(ax, title):
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect('equal')
    ax.axis('off'); ax.set_title(title, fontsize=9, fontweight='bold')
    ax.add_patch(plt.Circle((0, 0), 0.22, color='gold', zorder=3))
    ax.text(0, 0, 'Ω', ha='center', va='center', fontsize=11, fontweight='bold')
    angles = np.linspace(0, 2*np.pi, 4, endpoint=False)
    colors = ['#FF6B35','green','#7B2D8B','#1f77b4']
    labels = ['N1','N2','N3','N4']
    positions = [(np.cos(a)*1.1, np.sin(a)*1.1) for a in angles]
    for (x,y), col, lbl in zip(positions, colors, labels):
        ax.plot([0, x*0.78],[0, y*0.78], color='gray', lw=1.5, zorder=1)
        ax.add_patch(plt.Circle((x, y), 0.20, color=col, zorder=3))
        ax.text(x, y, lbl, ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')
    # ring connections
    for i in range(4):
        j = (i+1)%4
        x1,y1 = positions[i]; x2,y2 = positions[j]
        ax.plot([x1,x2],[y1,y2], color='orange', lw=2, ls='--', zorder=2, alpha=0.7)

def draw_cone_diagram(ax, title):
    ax.set_xlim(-1.8, 1.8); ax.set_ylim(-1.8, 1.8); ax.set_aspect('equal')
    ax.axis('off'); ax.set_title(title, fontsize=9, fontweight='bold')
    ax.add_patch(plt.Circle((0, 0), 0.22, color='gold', zorder=4))
    ax.text(0, 0, 'Ω', ha='center', va='center', fontsize=11, fontweight='bold')
    # inner ring
    inner_ang = np.linspace(0, 2*np.pi, 3, endpoint=False)
    inner_pos = [(np.cos(a)*0.85, np.sin(a)*0.85) for a in inner_ang]
    for (x,y) in inner_pos:
        ax.plot([0, x*0.74],[0, y*0.74], color='gray', lw=1.5, zorder=1)
        ax.add_patch(plt.Circle((x,y), 0.18, color='#FF6B35', zorder=3))
        ax.text(x, y, 'I', ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')
    for i in range(3):
        j=(i+1)%3
        x1,y1=inner_pos[i]; x2,y2=inner_pos[j]
    # outer ring
    outer_ang = np.linspace(np.pi/4, 2*np.pi+np.pi/4, 4, endpoint=False)
    outer_pos = [(np.cos(a)*1.5, np.sin(a)*1.5) for a in outer_ang]
    for k,(x,y) in enumerate(outer_pos):
        near_inner = inner_pos[k % 3]
        ax.plot([near_inner[0], x],[near_inner[1], y],
                color='gray', lw=1, ls=':', zorder=1, alpha=0.6)
        ax.add_patch(plt.Circle((x,y), 0.18, color='purple', zorder=3))
        ax.text(x, y, 'O', ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')
    for i in range(4):
        j=(i+1)%4
        x1,y1=outer_pos[i]; x2,y2=outer_pos[j]
        ax.plot([x1,x2],[y1,y2], color='purple', lw=1.5, ls='--', zorder=2, alpha=0.5)

ax_diag_star = fig.add_subplot(gs[0, 0])
ax_diag_ring = fig.add_subplot(gs[0, 1])
ax_diag_cone = fig.add_subplot(gs[0, 2])
draw_star_diagram(ax_diag_star, 'STAR Topology\n(Ω center, 4 nodes, no ring links)')
draw_ring_diagram(ax_diag_ring, 'RING Topology\n(Star + ring neighbor links)')
draw_cone_diagram(ax_diag_cone, 'CONE Topology\n(Ω → inner ring 3 → outer ring 4)')

# ── THE KEY RESULT: Omega floor comparison ──────────────────

ax_key = fig.add_subplot(gs[0, 3])
topologies  = ['2-node\nchain', '3-node\nchain', '4-node\nchain',
               '5-node\nchain', 'STAR', 'RING', 'CONE']
omega_floors = [REF[2], REF[3], REF[4], REF[5],
                floor_star_O, floor_ring_O, floor_cone_O]
bar_colors   = ['#aaaaaa','#5599dd','#ff7f0e','#2ca02c',
                'gold','#FF6B35','purple']
bars = ax_key.bar(range(len(topologies)), omega_floors,
                  color=bar_colors, alpha=0.85, edgecolor='black')
ax_key.axhline(0,       color='red',    ls='--', lw=1.5, label='Classical (0)')
ax_key.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5,
               label=f'Alpha floor ({ALPHA_FLOOR})')
for bar, val in zip(bars, omega_floors):
    if val is not None:
        ax_key.text(bar.get_x()+bar.get_width()/2, val-0.003,
                    f'{val:+.4f}', ha='center', va='top', fontsize=6.5,
                    fontweight='bold', color='white')
ax_key.set_xticks(range(len(topologies)))
ax_key.set_xticklabels(topologies, fontsize=7)
ax_key.set_title("Omega's W_min Floor\nAll Topologies", fontweight='bold', fontsize=9)
ax_key.set_ylabel('W_min(Omega)')
ax_key.legend(fontsize=7)
ax_key.grid(True, alpha=0.3, axis='y')

# ── ROW 1: Omega Wigner trajectories ──────────────────────────

ax_s1 = fig.add_subplot(gs[1, 0])
s_s, w_s = wigner_traj(log_star, 'W_Omega')
ax_s1.plot(s_s, w_s, color='gold', lw=2.5, label='Omega (Star)')
ax_s1.axhline(0, color='red', ls=':', lw=1.5)
ax_s1.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.7)
ax_s1.axhline(REF[3], color='blue', ls='--', lw=1, alpha=0.5,
              label='3-node floor')
if floor_star_O:
    ax_s1.axhline(floor_star_O, color='gold', ls='-', lw=1,
                  alpha=0.5, label=f'Star floor={floor_star_O:+.4f}')
ax_s1.fill_between(s_s, w_s, ALPHA_FLOOR,
                   where=[w < ALPHA_FLOOR for w in w_s],
                   color='gold', alpha=0.15, label='Below Alpha floor!')
ax_s1.set_title(f'STAR: Omega Wigner\nFloor={floor_star_O:+.4f}', fontweight='bold')
ax_s1.set_xlabel('Step'); ax_s1.set_ylabel('W_min(Omega)')
ax_s1.legend(fontsize=7); ax_s1.grid(True, alpha=0.3)

ax_s2 = fig.add_subplot(gs[1, 1])
s_r, w_r = wigner_traj(log_ring, 'W_Omega')
ax_s2.plot(s_r, w_r, color='#FF6B35', lw=2.5, label='Omega (Ring)')
ax_s2.axhline(0, color='red', ls=':', lw=1.5)
ax_s2.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.7)
if floor_ring_O:
    ax_s2.axhline(floor_ring_O, color='#FF6B35', ls='-', lw=1,
                  alpha=0.5, label=f'Ring floor={floor_ring_O:+.4f}')
ax_s2.fill_between(s_r, w_r, ALPHA_FLOOR,
                   where=[w < ALPHA_FLOOR for w in w_r],
                   color='#FF6B35', alpha=0.15, label='Below Alpha floor!')
ax_s2.set_title(f'RING: Omega Wigner\nFloor={floor_ring_O:+.4f}', fontweight='bold')
ax_s2.set_xlabel('Step'); ax_s2.set_ylabel('W_min(Omega)')
ax_s2.legend(fontsize=7); ax_s2.grid(True, alpha=0.3)

ax_s3 = fig.add_subplot(gs[1, 2])
s_c, w_c = wigner_traj(log_cone, 'W_Omega')
ax_s3.plot(s_c, w_c, color='purple', lw=2.5, label='Omega (Cone)')
ax_s3.axhline(0, color='red', ls=':', lw=1.5)
ax_s3.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.5)
if floor_cone_O:
    ax_s3.axhline(floor_cone_O, color='purple', ls='-', lw=1,
                  alpha=0.5, label=f'Cone floor={floor_cone_O:+.4f}')
ax_s3.fill_between(s_c, w_c, ALPHA_FLOOR,
                   where=[w < ALPHA_FLOOR for w in w_c],
                   color='purple', alpha=0.15, label='Below Alpha floor!')
ax_s3.set_title(f'CONE: Omega Wigner\nFloor={floor_cone_O:+.4f}', fontweight='bold')
ax_s3.set_xlabel('Step'); ax_s3.set_ylabel('W_min(Omega)')
ax_s3.legend(fontsize=7); ax_s3.grid(True, alpha=0.3)

# Overlay all three
ax_s4 = fig.add_subplot(gs[1, 3])
ax_s4.plot(s_s, w_s, color='gold',    lw=2, label='Star')
ax_s4.plot(s_r, w_r, color='#FF6B35', lw=2, label='Ring')
ax_s4.plot(s_c, w_c, color='purple',  lw=2, label='Cone')
ax_s4.axhline(0,           color='red',    ls=':', lw=1.5)
ax_s4.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.7)
ax_s4.axhline(REF[3],      color='blue',   ls='--', lw=1, alpha=0.5,
              label='3-node ref')
ax_s4.set_title('Omega Wigner: All Topologies\nOverlay', fontweight='bold')
ax_s4.set_xlabel('Step'); ax_s4.set_ylabel('W_min(Omega)')
ax_s4.legend(fontsize=7); ax_s4.grid(True, alpha=0.3)

# ── ROW 2: Surrounding node floors + coherence ───────────────

ax_b1 = fig.add_subplot(gs[2, 0])
# Star: all surrounding node Wigner trajectories
ring_wigs = []
for i in range(4):
    sw = [r['step'] for r in log_star if r.get('W_ring') and r['W_ring'][i] is not None]
    wv = [r['W_ring'][i] for r in log_star if r.get('W_ring') and r['W_ring'][i] is not None]
    if sw:
        ax_b1.plot(sw, wv, lw=1.5, alpha=0.7, label=f'Node {i+1}')
        ring_wigs += wv
ax_b1.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.7)
ax_b1.axhline(0, color='red', ls=':', lw=1)
ax_b1.set_title('STAR: Surrounding Nodes Wigner')
ax_b1.set_xlabel('Step'); ax_b1.set_ylabel('W_min')
ax_b1.legend(fontsize=7); ax_b1.grid(True, alpha=0.3)

ax_b2 = fig.add_subplot(gs[2, 1])
# Cone: inner vs outer layer floors
inner_wigs_by_step = {}
outer_wigs_by_step = {}
for r in log_cone:
    if r.get('W_inner') and all(w is not None for w in r['W_inner']):
        inner_wigs_by_step[r['step']] = np.mean(r['W_inner'])
    if r.get('W_outer') and all(w is not None for w in r['W_outer']):
        outer_wigs_by_step[r['step']] = np.mean(r['W_outer'])
if inner_wigs_by_step:
    ax_b2.plot(list(inner_wigs_by_step.keys()),
               list(inner_wigs_by_step.values()),
               color='#FF6B35', lw=2, label='Inner ring (mean)')
if outer_wigs_by_step:
    ax_b2.plot(list(outer_wigs_by_step.keys()),
               list(outer_wigs_by_step.values()),
               color='purple', lw=2, label='Outer ring (mean)')
ax_b2.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.5)
ax_b2.axhline(0, color='red', ls=':', lw=1)
ax_b2.set_title('CONE: Inner vs Outer Ring Wigner')
ax_b2.set_xlabel('Step'); ax_b2.set_ylabel('W_min (mean)')
ax_b2.legend(fontsize=8); ax_b2.grid(True, alpha=0.3)

ax_b3 = fig.add_subplot(gs[2, 2])
# Coherence all topologies
steps_star = [r['step'] for r in log_star]
steps_ring = [r['step'] for r in log_ring]
steps_cone = [r['step'] for r in log_cone]
ax_b3.plot(steps_star, [r['C_Omega'] for r in log_star],
           color='gold', lw=2, label='Star Ω')
ax_b3.plot(steps_ring, [r['C_Omega'] for r in log_ring],
           color='#FF6B35', lw=2, label='Ring Ω')
ax_b3.plot(steps_cone, [r['C_Omega'] for r in log_cone],
           color='purple', lw=2, label='Cone Ω')
ax_b3.axhline(1.0, color='gray', ls=':', lw=1)
ax_b3.set_title('Omega Coherence — All Topologies')
ax_b3.set_xlabel('Step'); ax_b3.set_ylabel('C_Omega')
ax_b3.legend(fontsize=8); ax_b3.grid(True, alpha=0.3)
ax_b3.set_ylim(0.95, 1.005)

# Summary table
ax_b4 = fig.add_subplot(gs[2, 3])
ax_b4.axis('off')

def pct(v):
    if v is None: return 'N/A'
    return f"{abs(v)/abs(ALPHA_FLOOR)*100:.1f}%"

def overshoot(v):
    if v is None: return 'N/A'
    return "YES ✓" if v < ALPHA_FLOOR else "no"

summary = [
    ['Topology',    'Ω floor',     '% to α',   'Overshoot?'],
    ['2-node',      f'{REF[2]:+.4f}',  pct(REF[2]),  overshoot(REF[2])],
    ['3-node',      f'{REF[3]:+.4f}',  pct(REF[3]),  overshoot(REF[3])],
    ['4-node',      f'{REF[4]:+.4f}',  pct(REF[4]),  overshoot(REF[4])],
    ['5-node',      f'{REF[5]:+.4f}',  pct(REF[5]),  overshoot(REF[5])],
    ['STAR',        f'{floor_star_O:+.4f}' if floor_star_O else 'N/A',
                    pct(floor_star_O), overshoot(floor_star_O)],
    ['RING',        f'{floor_ring_O:+.4f}' if floor_ring_O else 'N/A',
                    pct(floor_ring_O), overshoot(floor_ring_O)],
    ['CONE',        f'{floor_cone_O:+.4f}' if floor_cone_O else 'N/A',
                    pct(floor_cone_O), overshoot(floor_cone_O)],
    ['Alpha ref',   f'{ALPHA_FLOOR:+.4f}', '100%', '—'],
]
t_w = ax_b4.table(cellText=[r[1:] for r in summary[1:]],
                  colLabels=summary[0][1:],
                  rowLabels=[r[0] for r in summary[1:]],
                  loc='center', cellLoc='center')
t_w.auto_set_font_size(False)
t_w.set_fontsize(7.5)
t_w.scale(1.0, 1.55)
ax_b4.set_title('Full Topology Comparison', fontweight='bold')

plt.savefig('outputs/topology_experiments.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/topology_experiments.png")

# ============================================================
# FINAL VERDICT
# ============================================================

print("\n" + "=" * 65)
print("FULL TOPOLOGY RESULTS")
print("=" * 65)
print(f"\n{'Topology':<12} {'Omega floor':>12} {'% to Alpha':>12} {'Overshoot?':>12}")
print("-" * 52)
rows = [
    ('2-node', REF[2]), ('3-node', REF[3]),
    ('4-node', REF[4]), ('5-node', REF[5]),
    ('STAR',   floor_star_O), ('RING', floor_ring_O), ('CONE', floor_cone_O),
]
for name, val in rows:
    if val is not None:
        over = "YES ✓✓✓" if val < ALPHA_FLOOR else "no"
        print(f"{name:<12} {val:>+12.4f} {pct(val):>12} {over:>12}")

print(f"\n{'Alpha ref':<12} {ALPHA_FLOOR:>+12.4f} {'100%':>12}")

if floor_star_O and floor_star_O < ALPHA_FLOOR:
    print(f"\n★ OVERSHOOT CONFIRMED in STAR topology!")
    print(f"  Omega floor {floor_star_O:+.4f} < Alpha floor {ALPHA_FLOOR:+.4f}")
    print(f"  The attractor is MORE protected than the learner!")
    print(f"  Role inversion: surrounding Omega protects it beyond Alpha's level.")
elif floor_star_O:
    gap = ALPHA_FLOOR - floor_star_O
    print(f"\nNo overshoot. Gap to Alpha floor: {gap:+.4f}")
    print(f"Closest topology to Alpha: {min(rows, key=lambda x: abs((x[1] or 0) - ALPHA_FLOOR))[0]}")
