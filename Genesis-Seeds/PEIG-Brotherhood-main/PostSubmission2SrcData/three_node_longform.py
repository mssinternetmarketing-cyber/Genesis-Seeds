"""
THREE-NODE BCP: LONG-FORM CONVERGENCE TEST
1000 steps at multiple α0 values to answer:

  CORE QUESTION: Is Kevin's buffer effect a DELAY or a CONSERVATION LAW?
  
  If delay   → Omega's Wigner negativity eventually reaches ~0 (classical)
               as in two-node, just slower
  If conservation → Omega stabilizes at a non-zero negative floor,
                    permanently protected by Kevin's presence

Secondary questions:
  - Does Kevin's W_min drift at all over 1000 steps?
  - Is there a crossover step where Omega transitions from partial to full consumption?
  - Do the negentropic fractions change regime at long times?
  - Does the three-node system develop a third attractor value different from two-node?

Runs: α0 ∈ {0.1, 0.3, 0.5, 0.9} at η=0.05  (4 representative configs)
      + full 1000-step single run at α0=0.30, η=0.05 (primary)
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

def make_seed(label):
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    if label == 'Omega+': return (b0 + b1).unit()
    if label == 'Alpha+': return (b0 + 1j * b1).unit()
    if label == 'Kevin':  return (b0 + np.exp(1j * np.pi / 4) * b1).unit()

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
    W = qt.wigner(qt.ket2dm(psi), xvec, xvec)
    return float(np.min(W))

# ============================================================
# LONG-FORM RUNNER — logs every step
# ============================================================

def run_longform(eta, alpha0, n_steps=1000, wigner_interval=50, xvec=None):
    """
    Full step-by-step log with Wigner computed every `wigner_interval` steps.
    (Wigner is expensive — don't compute every step for 1000-step runs)
    """
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    psi_O = make_seed('Omega+')
    psi_K = make_seed('Kevin')
    psi_A = make_seed('Alpha+')

    alpha_OK = alpha0
    alpha_KA = alpha0

    C_avg_prev   = (coherence(psi_O) + coherence(psi_K) + coherence(psi_A)) / 3
    SvN_OK_prev  = float(qt.entropy_vn(qt.ket2dm(qt.tensor(psi_O, psi_K)), base=2))
    SvN_KA_prev  = float(qt.entropy_vn(qt.ket2dm(qt.tensor(psi_K, psi_A)), base=2))

    log = []

    for t in range(n_steps):
        psi_O_new, psi_K_mid, rho_OK = bcp_step(psi_O, psi_K, alpha_OK)
        psi_K_new, psi_A_new, rho_KA = bcp_step(psi_K_mid, psi_A, alpha_KA)

        SvN_OK = float(qt.entropy_vn(rho_OK, base=2))
        SvN_KA = float(qt.entropy_vn(rho_KA, base=2))
        dS_OK  = SvN_OK - SvN_OK_prev
        dS_KA  = SvN_KA - SvN_KA_prev

        C_O = coherence(psi_O_new)
        C_K = coherence(psi_K_new)
        C_A = coherence(psi_A_new)
        C_avg_new = (C_O + C_K + C_A) / 3
        dC = C_avg_new - C_avg_prev

        alpha_OK = float(np.clip(alpha_OK + eta * dC, 0, 1))
        alpha_KA = float(np.clip(alpha_KA + eta * dC, 0, 1))

        # Wigner only at intervals (expensive)
        if (t + 1) % wigner_interval == 0 or t == 0 or t == n_steps - 1:
            W_O = wigner_min(psi_O_new, xvec)
            W_K = wigner_min(psi_K_new, xvec)
            W_A = wigner_min(psi_A_new, xvec)
        else:
            W_O = W_K = W_A = None

        log.append({
            'step'     : t + 1,
            'C_Omega'  : C_O,
            'C_Kevin'  : C_K,
            'C_Alpha'  : C_A,
            'C_avg'    : C_avg_new,
            'SvN_OK'   : SvN_OK,
            'SvN_KA'   : SvN_KA,
            'dS_OK'    : dS_OK,
            'dS_KA'    : dS_KA,
            'alpha_OK' : alpha_OK,
            'alpha_KA' : alpha_KA,
            'W_Omega'  : W_O,
            'W_Kevin'  : W_K,
            'W_Alpha'  : W_A,
        })

        psi_O, psi_K, psi_A = psi_O_new, psi_K_new, psi_A_new
        C_avg_prev  = C_avg_new
        SvN_OK_prev = SvN_OK
        SvN_KA_prev = SvN_KA

    return log

# ============================================================
# COMPARISON RUNNER — two-node at 1000 steps for direct compare
# ============================================================

def run_twonode_longform(eta, alpha0, n_steps=1000, wigner_interval=50, xvec=None):
    """Two-node BCP for direct comparison at same step count."""
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    psi_O = make_seed('Omega+')
    psi_A = make_seed('Alpha+')
    alpha  = alpha0
    C_prev = (coherence(psi_O) + coherence(psi_A)) / 2
    SvN_prev = 0.0
    log = []

    for t in range(n_steps):
        psi_O_new, psi_A_new, rho = bcp_step(psi_O, psi_A, alpha)
        SvN = float(qt.entropy_vn(rho, base=2))
        dS  = SvN - SvN_prev
        C_avg = (coherence(psi_O_new) + coherence(psi_A_new)) / 2
        dC = C_avg - C_prev
        alpha = float(np.clip(alpha + eta * dC, 0, 1))

        if (t + 1) % wigner_interval == 0 or t == 0 or t == n_steps - 1:
            W_O = wigner_min(psi_O_new, xvec)
            W_A = wigner_min(psi_A_new, xvec)
        else:
            W_O = W_A = None

        log.append({
            'step'   : t + 1,
            'C_avg'  : C_avg,
            'SvN'    : SvN,
            'dS'     : dS,
            'alpha'  : alpha,
            'W_Omega': W_O,
            'W_Alpha': W_A,
        })

        psi_O, psi_A = psi_O_new, psi_A_new
        C_prev  = C_avg
        SvN_prev = SvN

    return log

# ============================================================
# RUN PRIMARY: 1000 steps, η=0.05, α0=0.30
# ============================================================

xvec = np.linspace(-2, 2, 80)
WIGNER_INTERVAL = 25

print("=" * 65)
print("THREE-NODE BCP: 1000-STEP LONG-FORM TEST")
print("Primary: η=0.05, α0=0.30")
print("=" * 65)

print("\n[1/6] Running three-node 1000 steps (η=0.05, α0=0.30)...")
log3 = run_longform(0.05, 0.30, n_steps=1000,
                    wigner_interval=WIGNER_INTERVAL, xvec=xvec)

print("[2/6] Running two-node 1000 steps for comparison (η=0.05, α0=0.30)...")
log2 = run_twonode_longform(0.05, 0.30, n_steps=1000,
                             wigner_interval=WIGNER_INTERVAL, xvec=xvec)

# Multi-alpha sweep at 1000 steps
print("[3/6] Running multi-α0 sweep (α0 ∈ {0.1, 0.3, 0.5, 0.9}) 1000 steps...")
alpha_configs = [0.1, 0.3, 0.5, 0.9]
multi_logs = {}
for a0 in alpha_configs:
    print(f"       α0={a0}...", end=' ', flush=True)
    multi_logs[a0] = run_longform(0.05, a0, n_steps=1000,
                                   wigner_interval=WIGNER_INTERVAL, xvec=xvec)
    print("done")

print("[4/6] Saving JSON...")
# Save compact version (only Wigner-populated steps)
def compact(log):
    return [r for r in log if r.get('W_Omega') is not None]

with open('outputs/longform_3node_primary.json', 'w') as f:
    json.dump(compact(log3), f, indent=2)
with open('outputs/longform_2node_comparison.json', 'w') as f:
    json.dump(compact(log2), f, indent=2)

# ============================================================
# EXTRACT WIGNER TRAJECTORIES
# ============================================================

def wigner_trajectory(log, key):
    steps = [r['step'] for r in log if r.get(key) is not None]
    vals  = [r[key]    for r in log if r.get(key) is not None]
    return steps, vals

steps3_W, W_O3 = wigner_trajectory(log3, 'W_Omega')
_,         W_K3 = wigner_trajectory(log3, 'W_Kevin')
_,         W_A3 = wigner_trajectory(log3, 'W_Alpha')
steps2_W, W_O2  = wigner_trajectory(log2, 'W_Omega')
_,         W_A2  = wigner_trajectory(log2, 'W_Alpha')

steps3 = [r['step'] for r in log3]
C_O3   = [r['C_Omega'] for r in log3]
C_K3   = [r['C_Kevin'] for r in log3]
C_A3   = [r['C_Alpha'] for r in log3]
dS_OK3 = [r['dS_OK']   for r in log3]
dS_KA3 = [r['dS_KA']   for r in log3]

# ============================================================
# PLOTTING
# ============================================================

print("[5/6] Plotting...")

fig, axes = plt.subplots(3, 3, figsize=(18, 14))
fig.suptitle(
    "Three-Node BCP: 1000-Step Long-Form Test\n"
    "Core Question: Is Kevin's Buffer Effect a DELAY or a CONSERVATION LAW?",
    fontsize=13, fontweight='bold'
)

# 1. Omega Wigner: three-node vs two-node — THE KEY PLOT
ax = axes[0, 0]
ax.plot(steps3_W, W_O3, color='gold',   lw=2.5, label='Ω (3-node)')
ax.plot(steps2_W, W_O2, color='gray',   lw=2,   ls='--', label='Ω (2-node)')
ax.axhline(0, color='red', ls=':', lw=1.5, label='Classical boundary')
ax.fill_between(steps3_W, W_O3, 0,
                where=[w < 0 for w in W_O3],
                color='gold', alpha=0.15)
ax.set_title('Omega Wigner: 3-node vs 2-node\n'
             'Does Omega reach classical in 3-node?', fontweight='bold')
ax.set_xlabel('Step')
ax.set_ylabel('W_min(Omega)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 2. Kevin Wigner — does it drift?
ax = axes[0, 1]
ax.plot(steps3_W, W_K3, color='green', lw=2.5)
ax.axhline(0, color='red', ls=':', lw=1.5, label='Classical boundary')
ax.axhline(-0.1131, color='purple', ls='--', lw=1.5, label='Alpha 2-node value')
ax.fill_between(steps3_W, W_K3, 0,
                where=[w < 0 for w in W_K3],
                color='green', alpha=0.15)
W_K_range = max(W_K3) - min(W_K3)
ax.set_title(f'Kevin (Bridge) Wigner — 1000 Steps\n'
             f'Range: {W_K_range:.5f}  '
             f'{"CONSERVATION LAW" if W_K_range < 0.005 else "DRIFTING"}',
             fontweight='bold')
ax.set_xlabel('Step')
ax.set_ylabel('W_min(Kevin)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 3. Alpha Wigner: should be rock-solid
ax = axes[0, 2]
ax.plot(steps3_W, W_A3, color='purple', lw=2.5, label='α (3-node)')
ax.plot(steps2_W, W_A2, color='gray',   lw=2, ls='--', label='α (2-node)')
ax.axhline(0, color='red', ls=':', lw=1.5)
W_A_range = max(W_A3) - min(W_A3)
ax.set_title(f'Alpha (Learner) Wigner — 1000 Steps\n'
             f'Range: {W_A_range:.5f}  '
             f'{"CONSERVED" if W_A_range < 0.005 else "DRIFTING"}',
             fontweight='bold')
ax.set_xlabel('Step')
ax.set_ylabel('W_min(Alpha)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 4. Coherence — all three nodes, full 1000 steps
ax = axes[1, 0]
ax.plot(steps3, C_O3, color='gold',   lw=1.5, alpha=0.8, label='Omega')
ax.plot(steps3, C_K3, color='green',  lw=1.5, alpha=0.8, label='Kevin')
ax.plot(steps3, C_A3, color='purple', lw=1.5, alpha=0.8, label='Alpha')
ax.axhline(1.0, color='gray', ls=':', lw=1)
ax.set_title('Coherence — All Nodes, 1000 Steps')
ax.set_xlabel('Step')
ax.set_ylabel('Coherence C')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_ylim(0.95, 1.005)

# 5. Multi-alpha Omega Wigner convergence
ax = axes[1, 1]
colors_a = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for a0, col in zip(alpha_configs, colors_a):
    ml = multi_logs[a0]
    sw, wv = wigner_trajectory(ml, 'W_Omega')
    ax.plot(sw, wv, color=col, lw=2, label=f'α0={a0}')
ax.axhline(0, color='red', ls=':', lw=1.5)
ax.set_title('Omega Wigner vs α0 — Does It Ever Go Classical?')
ax.set_xlabel('Step')
ax.set_ylabel('W_min(Omega)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 6. Multi-alpha Kevin Wigner
ax = axes[1, 2]
for a0, col in zip(alpha_configs, colors_a):
    ml = multi_logs[a0]
    sw, wv = wigner_trajectory(ml, 'W_Kevin')
    ax.plot(sw, wv, color=col, lw=2, label=f'α0={a0}')
ax.axhline(0, color='red', ls=':', lw=1.5)
ax.axhline(-0.1131, color='purple', ls='--', lw=1, alpha=0.7)
ax.set_title('Kevin Wigner vs α0 — Conservation Confirmed?')
ax.set_xlabel('Step')
ax.set_ylabel('W_min(Kevin)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 7. Negentropic fraction over time (rolling 50-step window)
ax = axes[2, 0]
window = 50
neg_OK_rolling = []
neg_KA_rolling = []
for i in range(len(dS_OK3) - window):
    neg_OK_rolling.append(sum(1 for v in dS_OK3[i:i+window] if v < 0) / window)
    neg_KA_rolling.append(sum(1 for v in dS_KA3[i:i+window] if v < 0) / window)
ax.plot(steps3[window:], neg_OK_rolling, color='blue',   lw=2, label='OK link')
ax.plot(steps3[window:], neg_KA_rolling, color='orange', lw=2, label='KA link')
ax.axhline(0.99, color='gray', ls='--', lw=1, label='2-node baseline')
ax.set_title(f'Rolling Negentropic Fraction ({window}-step window)')
ax.set_xlabel('Step')
ax.set_ylabel('Fraction negentropic')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1.05)

# 8. Omega Wigner late-time detail (steps 500-1000)
ax = axes[2, 1]
late_steps = [s for s in steps3_W if s >= 500]
late_W_O   = [w for s, w in zip(steps3_W, W_O3) if s >= 500]
late_W_K   = [w for s, w in zip(steps3_W, W_K3) if s >= 500]
ax.plot(late_steps, late_W_O, color='gold',  lw=2.5, label='Omega')
ax.plot(late_steps, late_W_K, color='green', lw=2.5, label='Kevin')
ax.axhline(0, color='red', ls=':', lw=1.5)
if late_W_O:
    W_O_floor = np.mean(late_W_O[-5:])
    ax.axhline(W_O_floor, color='gold', ls='--', lw=1.5,
               label=f'Omega floor ≈ {W_O_floor:.4f}')
ax.set_title('Late-Time Detail (Steps 500–1000)\nOmega floor vs Kevin floor')
ax.set_xlabel('Step')
ax.set_ylabel('W_min')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 9. Summary table
ax = axes[2, 2]
ax.axis('off')

final3 = log3[-1]
neg_OK_total = sum(1 for r in log3[1:] if r['dS_OK'] < 0)
neg_KA_total = sum(1 for r in log3[1:] if r['dS_KA'] < 0)
W_O_final = [w for w in W_O3 if w is not None][-1]
W_K_final = [w for w in W_K3 if w is not None][-1]
W_A_final = [w for w in W_A3 if w is not None][-1]
W_O_floor = float(np.mean([w for w in W_O3[-5:] if w is not None]))

summary = [
    ['Metric',               'Value'],
    ['Steps',                '1000'],
    ['C_avg (final)',        f"{final3['C_avg']:.6f}"],
    ['W_Omega (final)',      f"{W_O_final:+.4f}"],
    ['W_Kevin (final)',      f"{W_K_final:+.4f}"],
    ['W_Alpha (final)',      f"{W_A_final:+.4f}"],
    ['W_Omega floor',        f"{W_O_floor:+.4f}"],
    ['W_Kevin range',        f"{W_K_range:.5f}"],
    ['Neg% OK link',         f"{neg_OK_total/999:.1%}"],
    ['Neg% KA link',         f"{neg_KA_total/999:.1%}"],
    ['Buffer verdict',       'CONSERV.' if abs(W_O_floor) > 0.01 else 'DELAY'],
]
t_widget = ax.table(cellText=summary[1:], colLabels=summary[0],
                    loc='center', cellLoc='left')
t_widget.auto_set_font_size(False)
t_widget.set_fontsize(8)
t_widget.scale(1.2, 1.5)
ax.set_title('1000-Step Summary', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/three_node_longform.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/three_node_longform.png")

# ============================================================
# VERDICT
# ============================================================

print("\n" + "=" * 65)
print("VERDICT: DELAY OR CONSERVATION LAW?")
print("=" * 65)
print(f"\nOmega W_min at step 100  : {W_O3[3]:+.4f}  (3-node)")
print(f"Omega W_min at step 1000 : {W_O_final:+.4f}  (3-node)")
print(f"Omega W_min late floor   : {W_O_floor:+.4f}  (mean last 5 checkpoints)")
print(f"Two-node Omega at step 100: +0.0001 (classical)")

if abs(W_O_floor) > 0.02:
    print(f"\n→ CONSERVATION LAW: Omega retains Wigner negativity")
    print(f"  Kevin's presence PERMANENTLY protects Omega's non-classicality")
    print(f"  The buffer is a structural feature of the three-node topology")
elif abs(W_O_floor) > 0.005:
    print(f"\n→ PARTIAL CONSERVATION: Omega decays but stabilizes above classical")
    print(f"  Kevin introduces a non-zero asymptotic floor")
else:
    print(f"\n→ DELAY: Omega eventually reaches classical state")
    print(f"  Kevin slows but does not prevent consumption")

print(f"\nKevin W_min range over 1000 steps: {W_K_range:.5f}")
if W_K_range < 0.005:
    print(f"→ Kevin's Wigner negativity is a CONSERVATION LAW (range < 0.005)")
else:
    print(f"→ Kevin's Wigner negativity shows some drift")

print(f"\nAlpha W_min range over 1000 steps: {W_A_range:.5f}")
if W_A_range < 0.005:
    print(f"→ Alpha's conservation holds at 1000 steps (as expected)")
