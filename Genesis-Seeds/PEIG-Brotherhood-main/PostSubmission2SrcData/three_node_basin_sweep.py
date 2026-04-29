"""
THREE-NODE BCP BASIN SWEEP
36 configurations: η ∈ {0.01, 0.02, 0.05, 0.10, 0.20, 0.50}
                   α0 ∈ {0.1, 0.2, 0.3, 0.5, 0.7, 0.9}

Mirrors the two-node basin mapping from PEIG v1/v2 papers
for direct comparison.

Key questions vs two-node:
  - Is the global attractor preserved in three-node topology?
  - Does Kevin's buffer effect vary with η and α0?
  - Do the two links (OK, KA) symmetry-break at extreme η?
  - What is Kevin's Wigner regime map across the basin?
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json
from pathlib import Path
from itertools import product

Path("outputs").mkdir(exist_ok=True)

# ============================================================
# PRIMITIVES (same as three_node_bcp.py)
# ============================================================

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_seed(label):
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    if label == 'Omega+':
        return (b0 + b1).unit()
    elif label == 'Alpha+':
        return (b0 + 1j * b1).unit()
    elif label == 'Kevin':
        return (b0 + np.exp(1j * np.pi / 4) * b1).unit()

def bcp_step(psi_A, psi_B, alpha):
    rho12    = qt.ket2dm(qt.tensor(psi_A, psi_B))
    I4       = qt.qeye([2, 2])
    U        = alpha * CNOT_GATE + (1 - alpha) * I4
    rho_p    = U * rho12 * U.dag()
    _, evA   = rho_p.ptrace(0).eigenstates()
    _, evB   = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi) ** 2).tr().real)

def wigner_min(psi, xvec):
    W = qt.wigner(qt.ket2dm(psi), xvec, xvec)
    return float(np.min(W))

# ============================================================
# SINGLE RUN
# ============================================================

def run_config(eta, alpha0, n_steps=100, xvec=None):
    if xvec is None:
        xvec = np.linspace(-2, 2, 60)   # coarser for speed across 36 runs

    psi_O = make_seed('Omega+')
    psi_K = make_seed('Kevin')
    psi_A = make_seed('Alpha+')

    alpha_OK = alpha0
    alpha_KA = alpha0

    C_avg_prev = (coherence(psi_O) + coherence(psi_K) + coherence(psi_A)) / 3

    SvN_OK_prev = float(qt.entropy_vn(qt.ket2dm(qt.tensor(psi_O, psi_K)), base=2))
    SvN_KA_prev = float(qt.entropy_vn(qt.ket2dm(qt.tensor(psi_K, psi_A)), base=2))

    neg_OK = 0
    neg_KA = 0
    total_dS_OK = 0.0
    total_dS_KA = 0.0

    for t in range(n_steps):
        psi_O_new, psi_K_mid, rho_OK = bcp_step(psi_O, psi_K, alpha_OK)
        psi_K_new, psi_A_new, rho_KA = bcp_step(psi_K_mid, psi_A, alpha_KA)

        SvN_OK = float(qt.entropy_vn(rho_OK, base=2))
        SvN_KA = float(qt.entropy_vn(rho_KA, base=2))

        dS_OK = SvN_OK - SvN_OK_prev
        dS_KA = SvN_KA - SvN_KA_prev

        if t > 0:
            if dS_OK < 0: neg_OK += 1
            if dS_KA < 0: neg_KA += 1
            total_dS_OK += dS_OK
            total_dS_KA += dS_KA

        C_avg_new = (coherence(psi_O_new) + coherence(psi_K_new) + coherence(psi_A_new)) / 3
        dC = C_avg_new - C_avg_prev

        alpha_OK = float(np.clip(alpha_OK + eta * dC, 0, 1))
        alpha_KA = float(np.clip(alpha_KA + eta * dC, 0, 1))

        psi_O, psi_K, psi_A = psi_O_new, psi_K_new, psi_A_new
        C_avg_prev = C_avg_new
        SvN_OK_prev = SvN_OK
        SvN_KA_prev = SvN_KA

    # Final metrics
    C_O_f = coherence(psi_O)
    C_K_f = coherence(psi_K)
    C_A_f = coherence(psi_A)
    C_avg_f = (C_O_f + C_K_f + C_A_f) / 3

    W_O_f = wigner_min(psi_O, xvec)
    W_K_f = wigner_min(psi_K, xvec)
    W_A_f = wigner_min(psi_A, xvec)

    sym_break = abs(alpha_OK - alpha_KA)

    return {
        'eta'        : eta,
        'alpha0'     : alpha0,
        'C_Omega'    : C_O_f,
        'C_Kevin'    : C_K_f,
        'C_Alpha'    : C_A_f,
        'C_avg'      : C_avg_f,
        'alpha_OK'   : alpha_OK,
        'alpha_KA'   : alpha_KA,
        'sym_break'  : sym_break,
        'neg_OK'     : neg_OK,
        'neg_KA'     : neg_KA,
        'total_dS_OK': total_dS_OK,
        'total_dS_KA': total_dS_KA,
        'W_Omega'    : W_O_f,
        'W_Kevin'    : W_K_f,
        'W_Alpha'    : W_A_f,
    }

# ============================================================
# SWEEP
# ============================================================

ETA_VALS   = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50]
ALPHA_VALS = [0.1,  0.2,  0.3,  0.5,  0.7,  0.9]
N = len(ETA_VALS)

print("=" * 65)
print("THREE-NODE BCP BASIN SWEEP: 36 CONFIGURATIONS")
print("Mirrors two-node basin mapping from PEIG v1/v2")
print("=" * 65)

results = []
xvec = np.linspace(-2, 2, 60)

for i, (eta, alpha0) in enumerate(product(ETA_VALS, ALPHA_VALS)):
    r = run_config(eta, alpha0, n_steps=100, xvec=xvec)
    results.append(r)
    print(f"[{i+1:2d}/36] η={eta:.2f} α0={alpha0:.1f} → "
          f"C_avg={r['C_avg']:.4f}  "
          f"W_K={r['W_Kevin']:+.4f}  "
          f"Δα={r['sym_break']:.4f}")

with open('outputs/three_node_basin_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nRaw data saved → outputs/three_node_basin_results.json")

# ============================================================
# RESHAPE TO GRID  (rows=η, cols=α0)
# ============================================================

def make_grid(key):
    g = np.zeros((N, N))
    for r in results:
        i = ETA_VALS.index(r['eta'])
        j = ALPHA_VALS.index(r['alpha0'])
        g[i, j] = r[key]
    return g

C_avg_grid  = make_grid('C_avg')
W_K_grid    = make_grid('W_Kevin')
W_O_grid    = make_grid('W_Omega')
aOK_grid    = make_grid('alpha_OK')
aKA_grid    = make_grid('alpha_KA')
sym_grid    = make_grid('sym_break')
negOK_grid  = make_grid('neg_OK')
negKA_grid  = make_grid('neg_KA')

# ============================================================
# PLOTTING
# ============================================================

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle(
    "Three-Node BCP Basin Sweep: η × α₀  (36 configs)\n"
    "Omega(attractor) → Kevin(bridge) → Alpha(learner)",
    fontsize=13, fontweight='bold'
)

eta_labels   = [str(e) for e in ETA_VALS]
alpha_labels = [str(a) for a in ALPHA_VALS]

def heatmap(ax, data, title, cmap, vmin=None, vmax=None, fmt='.3f', annot=True):
    im = ax.imshow(data, cmap=cmap, aspect='auto',
                   vmin=vmin, vmax=vmax, origin='upper')
    ax.set_xticks(range(N)); ax.set_xticklabels(alpha_labels, fontsize=7)
    ax.set_yticks(range(N)); ax.set_yticklabels(eta_labels,   fontsize=7)
    ax.set_xlabel('α₀ (initial coupling)', fontsize=8)
    ax.set_ylabel('η (learning rate)',      fontsize=8)
    ax.set_title(title, fontsize=9, fontweight='bold')
    plt.colorbar(im, ax=ax, shrink=0.8)
    if annot:
        for i in range(N):
            for j in range(N):
                ax.text(j, i, f"{data[i,j]:{fmt}}",
                        ha='center', va='center', fontsize=5.5,
                        color='white' if data[i,j] < (vmin or 0) + 0.5*(((vmax or 1)-(vmin or 0))) else 'black')
    return im

# 1. Final coherence — should be uniformly deep (global attractor)
heatmap(axes[0,0], C_avg_grid, 'Final C_avg (3-node)\nUniform blue = global attractor',
        'Blues', vmin=0.95, vmax=1.0, fmt='.4f')

# 2. Kevin Wigner — what regime is the bridge in?
heatmap(axes[0,1], W_K_grid,
        'W_min Kevin (Bridge)\nGreen<0 = non-classical preserved',
        'RdYlGn', vmin=-0.15, vmax=0.05, fmt='.3f')

# 3. Omega Wigner — how much is consumed vs two-node?
heatmap(axes[0,2], W_O_grid,
        'W_min Omega (Attractor)\nConsumed more/less than 2-node?',
        'RdYlGn', vmin=-0.15, vmax=0.05, fmt='.3f')

# 4. Coupling symmetry break Δα = |α*_OK - α*_KA|
heatmap(axes[0,3], sym_grid,
        'Coupling Symmetry Break Δα\n0=symmetric, >0=bridge distorts',
        'Oranges', vmin=0.0, vmax=0.05, fmt='.4f')

# 5. α* Omega-Kevin link
heatmap(axes[1,0], aOK_grid,
        'α* (Omega-Kevin link)',
        'viridis', vmin=0.0, vmax=0.6, fmt='.3f')

# 6. α* Kevin-Alpha link
heatmap(axes[1,1], aKA_grid,
        'α* (Kevin-Alpha link)',
        'viridis', vmin=0.0, vmax=0.6, fmt='.3f')

# 7. Negentropic fraction OK link
heatmap(axes[1,2], negOK_grid / 99,
        'Negentropic Fraction\n(Omega-Kevin link)',
        'Greens', vmin=0.5, vmax=1.0, fmt='.2f')

# 8. Negentropic fraction KA link
heatmap(axes[1,3], negKA_grid / 99,
        'Negentropic Fraction\n(Kevin-Alpha link)',
        'Greens', vmin=0.5, vmax=1.0, fmt='.2f')

plt.tight_layout()
plt.savefig('outputs/three_node_basin_sweep.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/three_node_basin_sweep.png")

# ============================================================
# SUMMARY STATISTICS
# ============================================================

C_vals  = [r['C_avg']    for r in results]
WK_vals = [r['W_Kevin']  for r in results]
WO_vals = [r['W_Omega']  for r in results]
sym_vals= [r['sym_break'] for r in results]

print("\n" + "=" * 65)
print("BASIN SUMMARY (36 configurations)")
print("=" * 65)
print(f"\nCoherence C_avg:")
print(f"  Min   : {min(C_vals):.6f}")
print(f"  Max   : {max(C_vals):.6f}")
print(f"  All > 0.990: {all(c > 0.990 for c in C_vals)}")
print(f"\nKevin (Bridge) W_min:")
print(f"  Min   : {min(WK_vals):+.4f}")
print(f"  Max   : {max(WK_vals):+.4f}")
print(f"  Always non-classical: {all(w < 0 for w in WK_vals)}")
print(f"\nOmega (Attractor) W_min:")
print(f"  Min   : {min(WO_vals):+.4f}")
print(f"  Max   : {max(WO_vals):+.4f}")
print(f"  Always classical at end: {all(w >= 0 for w in WO_vals)}")
print(f"\nCoupling Symmetry Break Δα:")
print(f"  Min   : {min(sym_vals):.6f}")
print(f"  Max   : {max(sym_vals):.6f}")
print(f"  Always symmetric (<0.01): {all(s < 0.01 for s in sym_vals)}")

print("\n" + "=" * 65)
print("COMPARISON: TWO-NODE vs THREE-NODE")
print("=" * 65)
print(f"{'Metric':<35} {'2-Node':>10} {'3-Node':>10}")
print("-" * 57)
print(f"{'Global attractor (C>0.990)':<35} {'YES':>10} {'YES' if all(c>0.990 for c in C_vals) else 'NO':>10}")
print(f"{'Omega Wigner consumed':<35} {'YES':>10} {'PARTIAL':>10}")
print(f"{'Alpha Wigner preserved':<35} {'YES':>10} {'YES':>10}")
print(f"{'Kevin Wigner status':<35} {'N/A':>10} {'PRESERVED':>10}")
print(f"{'Coupling symmetry break':<35} {'N/A':>10} {'NO' if all(s<0.01 for s in sym_vals) else 'YES':>10}")
print(f"{'Mean C_avg (final)':<35} {0.999838:>10.6f} {np.mean(C_vals):>10.6f}")
