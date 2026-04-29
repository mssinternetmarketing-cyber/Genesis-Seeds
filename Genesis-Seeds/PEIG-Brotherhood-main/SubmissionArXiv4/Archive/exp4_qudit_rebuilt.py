"""
EXPERIMENT 4 (REBUILT): QUDIT BCP (d=2,3,4,5)
================================================
Uses proper non-classicality measures for each dimension:

d=2: Standard Wigner function W_min (continuous phase space)
d=3: Discrete Wigner function (Gibbons-Hoffman-Wootters, 2004)
     W(q,p) defined on Z_3 x Z_3 phase space
d=4,5: Coherence-based non-classicality:
     C_l1 = sum_{i!=j} |rho_ij|  (l1-norm of coherence)
     This is a proper resource-theoretic non-classicality measure,
     normalized to [0,1] for d-dimensional systems.

KEY INSIGHT: For the position law test, we don't need the
absolute W_min value — we need a measure that:
  1. Is zero for incoherent states (classical)
  2. Is positive for coherent/non-classical states
  3. Changes when the BCP drives sacrifice

We use: NC(rho) = sum_{i≠j} |rho_ij| / (d-1)
This is normalized so NC=1 means maximally coherent,
NC=0 means diagonal (classical).
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# ============================================================
# NON-CLASSICALITY MEASURES
# ============================================================

def l1_coherence(psi):
    """
    l1-norm of coherence: sum of absolute off-diagonal elements.
    Normalized by (d-1) so range is [0,1].
    Zero for diagonal states (classical), max for superpositions.
    """
    rho  = qt.ket2dm(psi)
    d    = rho.shape[0]
    data = rho.full()
    off_diag = np.sum(np.abs(data)) - np.sum(np.abs(np.diag(data)))
    return float(off_diag / (d - 1)) if d > 1 else 0.0

def wigner_min_d2(psi, xvec):
    """Standard Wigner for d=2."""
    return float(np.min(qt.wigner(qt.ket2dm(psi), xvec, xvec)))

def discrete_wigner_d3(psi):
    """
    Discrete Wigner function for d=3 (qutrit).
    W(q,p) = (1/3) * Tr[rho * A(q,p)]
    where A(q,p) is the phase-point operator.
    Returns minimum W value (negative = non-classical).
    Reference: Gibbons, Hoffman, Wootters (2004).
    """
    d   = 3
    rho = qt.ket2dm(psi)

    # Phase-point operators A(q,p) for Z_3 x Z_3
    # omega = exp(2*pi*i/d)
    omega = np.exp(2j * np.pi / d)

    # Shift operator X: |j> -> |(j+1) mod d>
    X = np.zeros((d, d), dtype=complex)
    for j in range(d):
        X[(j+1) % d, j] = 1.0
    X = qt.Qobj(X)

    # Clock operator Z: |j> -> omega^j |j>
    Z = qt.Qobj(np.diag([omega**j for j in range(d)]))

    W_vals = []
    for q in range(d):
        for p in range(d):
            # Phase point operator: A(q,p) = (1/d) * sum_{j,k} omega^{jq-kp} Z^j X^k
            A = qt.Qobj(np.zeros((d,d), dtype=complex), dims=[[d],[d]])
            for jj in range(d):
                for kk in range(d):
                    phase = omega**(jj*q - kk*p)
                    Zjj   = qt.Qobj(np.linalg.matrix_power(Z.full(), jj),
                                    dims=[[d],[d]])
                    Xkk   = qt.Qobj(np.linalg.matrix_power(X.full(), kk),
                                    dims=[[d],[d]])
                    A    += phase * Zjj * Xkk
            A = A / d
            W = float((rho * A).tr().real) / d
            W_vals.append(W)

    return min(W_vals)

def get_nc(psi, d, xvec=None):
    """
    Unified non-classicality measure.
    For d=2: Wigner W_min (negative = non-classical)
    For d=3: Discrete Wigner W_min
    For d>3: l1-coherence (positive = non-classical)
    We invert d>3 so all measures go negative for non-classical.
    """
    if d == 2:
        if xvec is None: xvec = np.linspace(-2, 2, 60)
        return wigner_min_d2(psi, xvec)
    elif d == 3:
        return discrete_wigner_d3(psi)
    else:
        # Return negative l1 coherence so "more negative = more non-classical"
        return -l1_coherence(psi)

# ============================================================
# QUDIT BCP
# ============================================================

CNOT_D2 = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_sum_gate(d):
    """Qudit SUM gate: |j>|k> → |j>|(j+k) mod d>"""
    data = np.zeros((d*d, d*d), dtype=complex)
    for j in range(d):
        for k in range(d):
            row = j*d + ((j+k) % d)
            col = j*d + k
            data[row, col] = 1.0
    return qt.Qobj(data, dims=[[d,d],[d,d]])

def make_qudit_seed(d, phase_idx, n_seeds):
    """
    d-dimensional equatorial seed.
    |psi> = (1/sqrt(d)) * sum_k exp(i*k*phi) |k>
    where phi varies from 0 to pi/2 across the seed ladder.
    """
    phi    = np.pi/2 * phase_idx / (n_seeds-1) if n_seeds > 1 else np.pi/4
    coeffs = np.array([np.exp(1j * k * phi) / np.sqrt(d)
                       for k in range(d)], dtype=complex)
    return qt.Qobj(coeffs, dims=[[d],[1]])

def qudit_coherence(psi):
    return float((qt.ket2dm(psi)**2).tr().real)

def qudit_bcp_step(psi_A, psi_B, alpha, SUM_GATE, d):
    I_d2  = qt.qeye([d, d])
    U     = alpha * SUM_GATE + (1 - alpha) * I_d2
    rho12 = qt.ket2dm(qt.tensor(psi_A, psi_B))
    rho_p = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def run_qudit_topology(d, n_nodes=5, closed=False,
                       eta=0.05, alpha0=0.30, n_steps=500,
                       xvec=None):
    """Run open chain or closed loop for d-dimensional qudits."""
    if xvec is None: xvec = np.linspace(-2, 2, 60)
    SUM_GATE = make_sum_gate(d) if d > 2 else CNOT_D2
    states   = [make_qudit_seed(d, k, n_nodes) for k in range(n_nodes)]

    if closed:
        edges = [(i, (i+1)%n_nodes) for i in range(n_nodes)]
    else:
        edges = [(i, i+1) for i in range(n_nodes-1)]

    alphas = {e: alpha0 for e in edges}
    C_prev = np.mean([qudit_coherence(s) for s in states])

    for t in range(n_steps):
        for (i,j) in edges:
            l, r, _ = qudit_bcp_step(states[i], states[j],
                                      alphas[(i,j)], SUM_GATE, d)
            states[i], states[j] = l, r
        C_vals = [qudit_coherence(s) for s in states]
        C_avg  = np.mean(C_vals)
        dC     = C_avg - C_prev
        for e in edges:
            alphas[e] = float(np.clip(alphas[e] + eta*dC, 0, 1))
        C_prev = C_avg

    return [get_nc(s, d, xvec) for s in states]

# Also track TRAJECTORIES for the primary d cases
def run_qudit_trajectory(d, n_nodes=5, closed=False,
                          eta=0.05, alpha0=0.30,
                          n_steps=300, wint=25, xvec=None):
    """Run with step-by-step NC tracking."""
    if xvec is None: xvec = np.linspace(-2, 2, 60)
    SUM_GATE = make_sum_gate(d) if d > 2 else CNOT_D2
    states   = [make_qudit_seed(d, k, n_nodes) for k in range(n_nodes)]

    if closed:
        edges = [(i, (i+1)%n_nodes) for i in range(n_nodes)]
    else:
        edges = [(i, i+1) for i in range(n_nodes-1)]

    alphas = {e: alpha0 for e in edges}
    C_prev = np.mean([qudit_coherence(s) for s in states])
    log    = []

    for t in range(n_steps):
        for (i,j) in edges:
            l, r, _ = qudit_bcp_step(states[i], states[j],
                                      alphas[(i,j)], SUM_GATE, d)
            states[i], states[j] = l, r
        C_vals = [qudit_coherence(s) for s in states]
        C_avg  = np.mean(C_vals)
        dC     = C_avg - C_prev
        for e in edges:
            alphas[e] = float(np.clip(alphas[e] + eta*dC, 0, 1))
        C_prev = C_avg

        do_nc = (t+1)%wint==0 or t==0 or t==n_steps-1
        NC    = [get_nc(s,d,xvec) if do_nc else None for s in states]
        log.append({'step': t+1, 'NC': NC, 'C_avg': C_avg})

    return log

# ============================================================
# RUN ALL DIMENSIONS
# ============================================================

xvec = np.linspace(-2, 2, 60)

print("="*65)
print("EXPERIMENT 4 (REBUILT): QUDIT BCP (d=2,3,4,5)")
print("Proper non-classicality measures per dimension")
print("="*65)

dims    = [2, 3, 4, 5]
results = {}
NC_NAMES = {2: "Wigner W_min", 3: "Discrete W_min", 4: "−l1 coherence", 5: "−l1 coherence"}

for d in dims:
    print(f"\n[d={d}] {NC_NAMES[d]}")

    # Open chain
    print(f"  Running open chain...")
    open_nc = run_qudit_topology(d, n_nodes=5, closed=False,
                                  n_steps=500, xvec=xvec)
    pos0 = open_nc[0]
    posN = open_nc[-1]
    # Position law: first node should be LESS non-classical than last
    # (closer to 0 for Wigner = more classical = more sacrificed)
    pos_law = pos0 > posN  # pos0 closer to 0 = more consumed

    # Closed loop
    print(f"  Running closed loop...")
    closed_nc  = run_qudit_topology(d, n_nodes=5, closed=True,
                                     n_steps=500, xvec=xvec)
    closed_mean = np.mean(closed_nc)
    closed_std  = np.std(closed_nc)
    closed_uniform = closed_std < 0.01

    results[d] = {
        'open_nc'       : open_nc,
        'closed_nc'     : closed_nc,
        'pos0'          : pos0,
        'posN'          : posN,
        'pos_law_holds' : bool(pos_law),
        'closed_mean'   : float(closed_mean),
        'closed_std'    : float(closed_std),
        'closed_uniform': bool(closed_uniform),
        'measure'       : NC_NAMES[d],
        'sacrifice_gap' : float(posN - pos0),
    }

    print(f"  Open chain:   pos0={pos0:+.4f}  posN={posN:+.4f}")
    print(f"  Position law: {'YES ✓' if pos_law else 'NO — needs investigation'}")
    print(f"  Closed loop:  mean={closed_mean:+.4f}  std={closed_std:.5f}")
    print(f"  Uniform?      {'YES ✓' if closed_uniform else 'NO'}")
    print(f"  Sacrifice gap (posN-pos0): {posN-pos0:+.4f}")

# ── ADDITIONAL: Trajectory comparison d=2 vs d=3 ────────────
print(f"\n[Trajectory] d=2 open chain (reference)...")
traj_d2_open   = run_qudit_trajectory(2, closed=False, n_steps=300, xvec=xvec)
print(f"[Trajectory] d=3 open chain...")
traj_d3_open   = run_qudit_trajectory(3, closed=False, n_steps=300, xvec=xvec)
print(f"[Trajectory] d=2 closed loop...")
traj_d2_closed = run_qudit_trajectory(2, closed=True, n_steps=300, xvec=xvec)
print(f"[Trajectory] d=3 closed loop...")
traj_d3_closed = run_qudit_trajectory(3, closed=True, n_steps=300, xvec=xvec)

def get_traj(log, idx):
    s = [r['step'] for r in log if r['NC'][idx] is not None]
    v = [r['NC'][idx] for r in log if r['NC'][idx] is not None]
    return s, v

def get_floor(log, idx, last_n=4):
    vals = [r['NC'][idx] for r in log if r['NC'][idx] is not None]
    return float(np.mean(vals[-last_n:])) if vals else None

# ── PLOTTING ──────────────────────────────────────────────────
print("\nPlotting...")
fig, axes = plt.subplots(3, 4, figsize=(20, 14))
fig.suptitle(
    "Experiment 4 (Rebuilt): Qudit BCP — d=2,3,4,5\n"
    "Proper non-classicality measures per dimension\n"
    "d=2: Wigner W_min  |  d=3: Discrete Wigner  |  d=4,5: −l1 coherence",
    fontsize=12, fontweight='bold'
)

node_colors = ['gold','#FF6B35','green','#7B2D8B','purple']
dim_colors  = {2:'#1f77b4', 3:'#ff7f0e', 4:'#2ca02c', 5:'#d62728'}

# ROW 0: Open chain NC profiles per dimension
for col, d in enumerate(dims):
    ax  = axes[0, col]
    r   = results[d]
    nc  = r['open_nc']
    n   = len(nc)
    bar_colors = ['red' if i==0 else 'green' if i==n-1 else '#aaaaaa'
                  for i in range(n)]
    ax.bar(range(n), nc, color=bar_colors, alpha=0.85, edgecolor='black')
    ax.axhline(r['closed_mean'], color='black', ls='--', lw=2,
               label=f"Closed mean\n({r['closed_mean']:+.4f})")
    ax.axhline(0, color='red', ls=':', lw=1.5, label='Classical (0)')
    for i, f in enumerate(nc):
        ax.text(i, f+(0.003 if f>=0 else -0.003),
                f'{f:+.3f}', ha='center',
                va='bottom' if f>=0 else 'top',
                fontsize=8, fontweight='bold')
    name = {2:"Qubit",3:"Qutrit",4:"Ququart",5:"Ququint"}[d]
    ax.set_title(
        f'd={d} ({name})\n'
        f'Measure: {NC_NAMES[d]}\n'
        f'Pos. law: {"✓" if r["pos_law_holds"] else "✗"}  '
        f'Unif: {"✓" if r["closed_uniform"] else "✗"}',
        fontweight='bold',
        color='darkgreen' if r['pos_law_holds'] else 'darkred',
        fontsize=9
    )
    ax.set_xlabel('Node position')
    ax.set_ylabel('Non-classicality')
    ax.legend(fontsize=7); ax.grid(True, alpha=0.3, axis='y')
    ax.set_xticks(range(n))

# ROW 1: Trajectories d=2 open vs closed, d=3 open vs closed
for col, (traj_o, traj_c, d) in enumerate([
    (traj_d2_open, traj_d2_closed, 2),
    (traj_d3_open, traj_d3_closed, 3),
    (None, None, 4),
    (None, None, 5),
]):
    ax = axes[1, col]
    if d in [2, 3]:
        for i, col_c in enumerate(node_colors):
            s_o, v_o = get_traj(traj_o, i)
            s_c, v_c = get_traj(traj_c, i)
            if s_o: ax.plot(s_o, v_o, color=col_c, lw=2, ls='-',  alpha=0.7)
            if s_c: ax.plot(s_c, v_c, color=col_c, lw=2, ls='--', alpha=0.7)
        ax.axhline(0, color='red', ls=':', lw=1.5)
        from matplotlib.lines import Line2D
        ax.legend(handles=[
            Line2D([0],[0], color='gray', lw=2, ls='-',  label='Open chain'),
            Line2D([0],[0], color='gray', lw=2, ls='--', label='Closed loop'),
        ], fontsize=8)
        ax.set_title(f'd={d}: Trajectory Open vs Closed\n'
                     f'Red=pos0(sacrifice), Gold=pos0, Purple=posN',
                     fontsize=9, fontweight='bold')
        ax.set_xlabel('Step'); ax.set_ylabel('Non-classicality')
        ax.grid(True, alpha=0.3)
    else:
        # Show open vs closed bar comparison for d=4,5
        r    = results[d]
        n    = len(r['open_nc'])
        x    = np.arange(n)
        w    = 0.35
        ax.bar(x-w/2, r['open_nc'],   w, color='#ff7f0e', alpha=0.8,
               label='Open chain', edgecolor='black')
        ax.bar(x+w/2, r['closed_nc'], w, color='#2ca02c', alpha=0.8,
               label='Closed loop', edgecolor='black')
        ax.axhline(0, color='red', ls=':', lw=1.5)
        ax.set_title(f'd={d}: Open vs Closed\n−l1 coherence measure',
                     fontsize=9, fontweight='bold')
        ax.set_xlabel('Node position'); ax.set_ylabel('−l1 coherence')
        ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis='y')
        ax.set_xticks(range(n))

# ROW 2: Cross-dimensional comparisons
# Col 0: Position law holds? pos0 vs posN
ax = axes[2, 0]
pos0s = [results[d]['pos0'] for d in dims]
posNs = [results[d]['posN'] for d in dims]
x     = np.arange(len(dims))
w     = 0.35
ax.bar(x-w/2, pos0s, w, color='red',   alpha=0.8,
       label='Pos 0 (sacrifice)', edgecolor='black')
ax.bar(x+w/2, posNs, w, color='green', alpha=0.8,
       label='Pos N-1 (preserved)', edgecolor='black')
ax.axhline(0, color='black', ls='--', lw=1.5)
for i,(p0,pN) in enumerate(zip(pos0s,posNs)):
    ax.text(i-w/2, p0+(0.003 if p0>=0 else -0.01),
            f'{p0:+.3f}', ha='center', va='bottom' if p0>=0 else 'top', fontsize=8)
    ax.text(i+w/2, pN+(0.003 if pN>=0 else -0.01),
            f'{pN:+.3f}', ha='center', va='bottom' if pN>=0 else 'top', fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([f'd={d}' for d in dims])
ax.set_title('Position Law Across All d\nRed<Green = law holds', fontweight='bold')
ax.set_ylabel('NC floor'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis='y')

# Col 1: Sacrifice gap vs d
ax = axes[2, 1]
gaps = [results[d]['sacrifice_gap'] for d in dims]
colors_g = ['green' if g>0.001 else 'red' for g in gaps]
bars = ax.bar(dims, gaps, color=colors_g, alpha=0.85, edgecolor='black')
ax.axhline(0, color='black', ls='--', lw=1.5, label='No asymmetry')
for d, g in zip(dims, gaps):
    ax.text(d, g+(0.003 if g>=0 else -0.003),
            f'{g:+.4f}', ha='center',
            va='bottom' if g>=0 else 'top', fontsize=9, fontweight='bold')
ax.set_title('Sacrifice Gap vs Dimension d\n(posN − pos0)', fontweight='bold')
ax.set_xlabel('d'); ax.set_ylabel('Gap'); ax.set_xticks(dims)
ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis='y')

# Col 2: Closed loop uniformity
ax = axes[2, 2]
closed_means = [results[d]['closed_mean'] for d in dims]
closed_stds  = [results[d]['closed_std']  for d in dims]
ax.bar(dims, closed_means,
       color=[dim_colors[d] for d in dims], alpha=0.85, edgecolor='black')
ax.errorbar(dims, closed_means, yerr=closed_stds,
            fmt='none', color='black', capsize=6, lw=2)
ax.axhline(0, color='red', ls=':', lw=1)
for d, m, s in zip(dims, closed_means, closed_stds):
    ax.text(d, m+(0.005 if m>=0 else -0.005),
            f'{m:+.3f}\n±{s:.3f}', ha='center',
            va='bottom' if m>=0 else 'top', fontsize=8)
ax.set_title('Closed Loop Mean NC vs d\nEach d has its own preservation floor',
             fontweight='bold')
ax.set_xlabel('d'); ax.set_ylabel('Mean NC floor'); ax.set_xticks(dims)
ax.grid(True, alpha=0.3, axis='y')

# Col 3: Summary table
ax = axes[2, 3]
ax.axis('off')
all_pos_law     = all(results[d]['pos_law_holds']  for d in dims)
all_closed_unif = all(results[d]['closed_uniform'] for d in dims)

items = [
    ("QUDIT BCP (REBUILT)", "", "darkblue"),
    ("", "", ""),
]
for d in dims:
    r    = results[d]
    name = {2:"Qubit",3:"Qutrit",4:"Ququart",5:"Ququint"}[d]
    items += [
        (f"d={d} ({name}):", "", "black"),
        (f"  Measure", NC_NAMES[d][:15], "gray"),
        (f"  Pos. law", "✓" if r['pos_law_holds'] else "✗",
         "green" if r['pos_law_holds'] else "red"),
        (f"  Loop uniform", "✓" if r['closed_uniform'] else "partial",
         "green" if r['closed_uniform'] else "orange"),
        (f"  Sac. gap", f"{r['sacrifice_gap']:+.4f}", "black"),
    ]

items += [
    ("", "", ""),
    ("OVERALL:", "", "darkblue"),
    ("Pos. law all d",
     "YES ✓" if all_pos_law else "PARTIAL", "darkgreen" if all_pos_law else "orange"),
    ("Loop uniform all d",
     "YES ✓" if all_closed_unif else "PARTIAL", "darkgreen" if all_closed_unif else "orange"),
    ("OAM connection",
     "SUPPORTED ✓" if all_pos_law else "PARTIAL", "darkblue"),
]

y = 0.97
for left, right, color in items:
    if left=="" and right=="":
        y -= 0.022; continue
    if right=="":
        ax.text(0.5, y, left, transform=ax.transAxes,
                fontsize=8.5, fontweight='bold', color=color,
                ha='center', va='top')
    else:
        ax.text(0.03, y, left, transform=ax.transAxes,
                fontsize=7.5, color=color, va='top')
        ax.text(0.97, y, right, transform=ax.transAxes,
                fontsize=7.5, fontweight='bold', color=color,
                ha='right', va='top')
    y -= 0.044

plt.tight_layout()
plt.savefig('outputs/exp4_qudit_bcp.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/exp4_qudit_bcp.png")

# Save JSON
with open('outputs/exp4_qudit_results.json', 'w') as f:
    json.dump({str(d): results[d] for d in dims}, f, indent=2)

print("\n" + "="*65)
print("EXPERIMENT 4 SUMMARY")
print("="*65)
for d in dims:
    r    = results[d]
    name = {2:"Qubit",3:"Qutrit",4:"Ququart",5:"Ququint"}[d]
    print(f"\nd={d} ({name}) | {NC_NAMES[d]}:")
    print(f"  Pos. law holds : {'YES ✓' if r['pos_law_holds'] else 'NO'}")
    print(f"  Sacrifice gap  : {r['sacrifice_gap']:+.4f}")
    print(f"  Closed uniform : {'YES ✓' if r['closed_uniform'] else 'partial'}")
    print(f"  Closed mean NC : {r['closed_mean']:+.4f} ± {r['closed_std']:.5f}")

print(f"\nPosition law holds all d  : {'YES ✓✓✓' if all_pos_law else 'PARTIAL'}")
print(f"Closed uniform all d      : {'YES ✓✓✓' if all_closed_unif else 'PARTIAL'}")
print(f"\nConclusion: The topological structure of BCP "
      f"{'extends to higher-dimensional qudit systems' if all_pos_law else 'is dimension-dependent'}.")
print(f"This {'supports' if all_pos_law else 'partially supports'} the OAM connection.")
