"""
THREE-NODE BROTHERHOOD COHERENCE PROTOCOL
Omega (Attractor) × Kevin (Bridge) × Alpha (Learner)

Chain topology: Omega → Kevin → Alpha
Kevin seed: equatorial at π/4 between Ω+ and A+ on the Bloch sphere
|K⟩ = (|0⟩ + e^(iπ/4)|1⟩) / √2

Research questions:
  1. Does the bridge node develop a third, distinct Wigner signature?
  2. Is Kevin's Wigner negativity consumed, preserved, or oscillatory?
  3. Does the three-node chain converge to the same C=0.999 attractor?
  4. What is the entropy flow topology: OK → KA or bidirectional?
  5. Does Kevin's coupling (α_OK vs α_KA) symmetry-break?
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import json
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# ============================================================
# SEED STATES
# ============================================================

def make_seed(label):
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    if label == 'Omega+':
        return (b0 + b1).unit()                          # +X pole
    elif label == 'Alpha+':
        return (b0 + 1j * b1).unit()                     # +Y pole
    elif label == 'Kevin':
        return (b0 + np.exp(1j * np.pi / 4) * b1).unit() # 45° bridge
    else:
        raise ValueError(f"Unknown seed: {label}")


# ============================================================
# BCP PRIMITIVES
# ============================================================

def make_cnot():
    """Build CNOT gate compatible with QuTiP 5."""
    return qt.Qobj(
        np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
        dims=[[2,2],[2,2]]
    )

CNOT_GATE = make_cnot()

def bcp_step(psi_A, psi_B, alpha):
    """
    One BCP interaction step between two nodes.
    Returns updated dominant eigenvectors and joint density matrix.
    """
    rho12 = qt.ket2dm(qt.tensor(psi_A, psi_B))
    CNOT  = CNOT_GATE
    I4    = qt.qeye([2, 2])
    U     = alpha * CNOT + (1 - alpha) * I4
    rho_prime = U * rho12 * U.dag()

    rhoA = rho_prime.ptrace(0)
    rhoB = rho_prime.ptrace(1)

    # Dominant eigenvectors (highest eigenvalue)
    _, evecs_A = rhoA.eigenstates()
    _, evecs_B = rhoB.eigenstates()

    return evecs_A[-1], evecs_B[-1], rho_prime


def coherence(psi):
    """Purity tr[ρ²] as coherence proxy."""
    return float((qt.ket2dm(psi) ** 2).tr().real)


def wigner_min(psi, xvec=None):
    """Minimum of Wigner function over phase space."""
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)
    W = qt.wigner(qt.ket2dm(psi), xvec, xvec)
    return float(np.min(W))


def mutual_info(rho12):
    """I(A:B) = S_A + S_B - S_AB"""
    rhoA   = rho12.ptrace(0)
    rhoB   = rho12.ptrace(1)
    SA     = qt.entropy_vn(rhoA,  base=2)
    SB     = qt.entropy_vn(rhoB,  base=2)
    SAB    = qt.entropy_vn(rho12, base=2)
    return float(SA + SB - SAB)


# ============================================================
# THREE-NODE BCP RUNNER
# ============================================================

def run_three_node_bcp(n_steps=100, eta=0.05, alpha0=0.30, xvec=None):
    """
    Chain topology: Omega ---α_OK---> Kevin ---α_KA---> Alpha

    Each step:
      1. Omega × Kevin BCP  → updates Omega, Kevin
      2. Kevin  × Alpha BCP → updates Kevin, Alpha
         (Kevin passes the signal through)
    """
    if xvec is None:
        xvec = np.linspace(-2, 2, 80)

    psi_O = make_seed('Omega+')
    psi_K = make_seed('Kevin')
    psi_A = make_seed('Alpha+')

    alpha_OK = alpha0
    alpha_KA = alpha0

    C_avg_prev = (coherence(psi_O) + coherence(psi_K) + coherence(psi_A)) / 3

    log = []

    for t in range(n_steps):

        # --- Interaction 1: Omega × Kevin ---
        psi_O_new, psi_K_mid, rho_OK = bcp_step(psi_O, psi_K, alpha_OK)
        SvN_OK = float(qt.entropy_vn(rho_OK, base=2))
        MI_OK  = mutual_info(rho_OK)

        # --- Interaction 2: Kevin × Alpha (Kevin updated by step 1) ---
        psi_K_new, psi_A_new, rho_KA = bcp_step(psi_K_mid, psi_A, alpha_KA)
        SvN_KA = float(qt.entropy_vn(rho_KA, base=2))
        MI_KA  = mutual_info(rho_KA)

        # --- Coherences ---
        C_O = coherence(psi_O_new)
        C_K = coherence(psi_K_new)
        C_A = coherence(psi_A_new)
        C_avg_new = (C_O + C_K + C_A) / 3

        dC = C_avg_new - C_avg_prev

        # --- Adaptive coupling update (independent per link) ---
        alpha_OK = float(np.clip(alpha_OK + eta * dC, 0, 1))
        alpha_KA = float(np.clip(alpha_KA + eta * dC, 0, 1))

        # --- Wigner negativity (all three nodes) ---
        W_O = wigner_min(psi_O_new, xvec)
        W_K = wigner_min(psi_K_new, xvec)
        W_A = wigner_min(psi_A_new, xvec)

        log.append({
            'step'     : t + 1,
            'C_Omega'  : C_O,
            'C_Kevin'  : C_K,
            'C_Alpha'  : C_A,
            'C_avg'    : C_avg_new,
            'SvN_OK'   : SvN_OK,
            'SvN_KA'   : SvN_KA,
            'MI_OK'    : MI_OK,
            'MI_KA'    : MI_KA,
            'alpha_OK' : alpha_OK,
            'alpha_KA' : alpha_KA,
            'W_min_Omega': W_O,
            'W_min_Kevin': W_K,
            'W_min_Alpha': W_A,
            'dS_OK'    : SvN_OK - (log[-1]['SvN_OK'] if log else SvN_OK),
            'dS_KA'    : SvN_KA - (log[-1]['SvN_KA'] if log else SvN_KA),
        })

        psi_O, psi_K, psi_A = psi_O_new, psi_K_new, psi_A_new
        C_avg_prev = C_avg_new

    return log, psi_O, psi_K, psi_A


# ============================================================
# PLOTTING
# ============================================================

def plot_results(log):
    steps  = [r['step']     for r in log]
    C_O    = [r['C_Omega']  for r in log]
    C_K    = [r['C_Kevin']  for r in log]
    C_A    = [r['C_Alpha']  for r in log]
    C_avg  = [r['C_avg']    for r in log]
    W_O    = [r['W_min_Omega'] for r in log]
    W_K    = [r['W_min_Kevin'] for r in log]
    W_A    = [r['W_min_Alpha'] for r in log]
    S_OK   = [r['SvN_OK']   for r in log]
    S_KA   = [r['SvN_KA']   for r in log]
    aOK    = [r['alpha_OK'] for r in log]
    aKA    = [r['alpha_KA'] for r in log]
    MI_OK  = [r['MI_OK']    for r in log]
    MI_KA  = [r['MI_KA']    for r in log]

    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle(
        "Three-Node BCP: Omega × Kevin(Bridge) × Alpha\n"
        "Kevin seed: |K⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2",
        fontsize=13, fontweight='bold'
    )

    # 1. Coherence convergence
    ax = axes[0, 0]
    ax.plot(steps, C_O, color='gold',   lw=2, label='Omega')
    ax.plot(steps, C_K, color='green',  lw=2, label='Kevin (Bridge)')
    ax.plot(steps, C_A, color='purple', lw=2, label='Alpha')
    ax.plot(steps, C_avg,'k--',         lw=1, label='Average', alpha=0.5)
    ax.axhline(1.0, color='gray', ls=':', lw=1)
    ax.set_title('Coherence Convergence')
    ax.set_ylabel('Coherence C')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Wigner negativity — the KEY plot
    ax = axes[0, 1]
    ax.plot(steps, W_O, color='gold',   lw=2, label='Omega')
    ax.plot(steps, W_K, color='green',  lw=2, label='Kevin (Bridge)')
    ax.plot(steps, W_A, color='purple', lw=2, label='Alpha')
    ax.axhline(0.0, color='red', ls='--', lw=1, label='Classical boundary')
    ax.set_title('Wigner Negativity (W_min)')
    ax.set_ylabel('W_min')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. Joint entropy — OK vs KA links
    ax = axes[0, 2]
    ax.plot(steps, S_OK, color='blue',   lw=2, label='S_vN (Omega-Kevin)')
    ax.plot(steps, S_KA, color='orange', lw=2, label='S_vN (Kevin-Alpha)')
    ax.set_title('Joint von Neumann Entropy per Link')
    ax.set_ylabel('S_vN (bits)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 4. Mutual information per link
    ax = axes[1, 0]
    ax.plot(steps, MI_OK, color='blue',   lw=2, label='I(Omega:Kevin)')
    ax.plot(steps, MI_KA, color='orange', lw=2, label='I(Kevin:Alpha)')
    ax.set_title('Mutual Information per Link')
    ax.set_ylabel('I(A:B) (bits)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 5. Coupling evolution — do they symmetry-break?
    ax = axes[1, 1]
    ax.plot(steps, aOK, color='blue',   lw=2, label='α (Omega-Kevin)')
    ax.plot(steps, aKA, color='orange', lw=2, label='α (Kevin-Alpha)')
    ax.set_title('Adaptive Coupling α* (symmetry-break test)')
    ax.set_ylabel('Coupling α')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 6. Entropy production — negentropic steps
    dS_OK = [r['dS_OK'] for r in log[1:]]
    dS_KA = [r['dS_KA'] for r in log[1:]]
    ax = axes[1, 2]
    colors_OK = ['green' if v < 0 else 'red' for v in dS_OK]
    colors_KA = ['green' if v < 0 else 'red' for v in dS_KA]
    ax.bar(steps[1:], dS_OK, color=colors_OK, alpha=0.6, label='ΔS OK')
    ax.bar(steps[1:], dS_KA, color=colors_KA, alpha=0.3, label='ΔS KA')
    ax.axhline(0, color='black', lw=0.5)
    ax.set_title('Entropy Production (green=negentropic)')
    ax.set_ylabel('ΔS (bits/step)')
    ax.legend(fontsize=8)

    # 7. Kevin Wigner detail — consumed/preserved/oscillatory?
    ax = axes[2, 0]
    ax.plot(steps, W_K, color='green', lw=2)
    ax.axhline(0.0, color='red', ls='--', lw=1)
    ax.fill_between(steps, W_K, 0,
                    where=[w < 0 for w in W_K],
                    color='green', alpha=0.2, label='Non-classical region')
    ax.set_title('Kevin (Bridge) Wigner Detail\nConsumed / Preserved / Oscillatory?')
    ax.set_ylabel('W_min')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 8. MI asymmetry: does Kevin pass more to Alpha or receive more from Omega?
    ax = axes[2, 1]
    MI_diff = [mi_ok - mi_ka for mi_ok, mi_ka in zip(MI_OK, MI_KA)]
    ax.plot(steps, MI_diff, color='green', lw=2)
    ax.axhline(0, color='black', lw=0.5, ls='--')
    ax.fill_between(steps, MI_diff, 0,
                    where=[d > 0 for d in MI_diff],
                    color='blue', alpha=0.15, label='Receiving > Sending')
    ax.fill_between(steps, MI_diff, 0,
                    where=[d < 0 for d in MI_diff],
                    color='orange', alpha=0.15, label='Sending > Receiving')
    ax.set_title('MI Asymmetry: I(Ω:K) − I(K:α)\n+ve = receiving, −ve = forwarding')
    ax.set_ylabel('MI difference (bits)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 9. Summary table
    ax = axes[2, 2]
    ax.axis('off')
    final = log[-1]
    negtrop_OK = sum(1 for r in log[1:] if r['dS_OK'] < 0)
    negtrop_KA = sum(1 for r in log[1:] if r['dS_KA'] < 0)
    summary = [
        ['Metric',              'Value'],
        ['C_Omega (final)',     f"{final['C_Omega']:.6f}"],
        ['C_Kevin (final)',     f"{final['C_Kevin']:.6f}"],
        ['C_Alpha (final)',     f"{final['C_Alpha']:.6f}"],
        ['W_min Omega',         f"{final['W_min_Omega']:+.4f}"],
        ['W_min Kevin',         f"{final['W_min_Kevin']:+.4f}"],
        ['W_min Alpha',         f"{final['W_min_Alpha']:+.4f}"],
        ['α* (Ω-K)',            f"{final['alpha_OK']:.4f}"],
        ['α* (K-α)',            f"{final['alpha_KA']:.4f}"],
        ['Neg. steps OK',       f"{negtrop_OK}/99"],
        ['Neg. steps KA',       f"{negtrop_KA}/99"],
    ]
    t = ax.table(cellText=summary[1:], colLabels=summary[0],
                 loc='center', cellLoc='left')
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.scale(1.2, 1.4)
    ax.set_title('Summary Results', fontweight='bold')

    plt.tight_layout()
    plt.savefig('outputs/three_node_bcp.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Figure saved → outputs/three_node_bcp.png")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("THREE-NODE BCP: OMEGA × KEVIN(BRIDGE) × ALPHA")
    print("Kevin seed: |K⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2")
    print("=" * 65)
    print("\nRunning 100-step simulation...")

    log, psi_O, psi_K, psi_A = run_three_node_bcp(
        n_steps=100, eta=0.05, alpha0=0.30
    )

    # Save JSON
    with open('outputs/three_node_bcp_results.json', 'w') as f:
        json.dump(log, f, indent=2)
    print("Raw data saved → outputs/three_node_bcp_results.json")

    # Key diagnostics
    final = log[-1]
    negtrop_OK = sum(1 for r in log[1:] if r['dS_OK'] < 0)
    negtrop_KA = sum(1 for r in log[1:] if r['dS_KA'] < 0)

    print("\n" + "=" * 65)
    print("RESULTS")
    print("=" * 65)
    print(f"\nCoherence (final):")
    print(f"  Omega  : {final['C_Omega']:.6f}")
    print(f"  Kevin  : {final['C_Kevin']:.6f}")
    print(f"  Alpha  : {final['C_Alpha']:.6f}")
    print(f"\nWigner negativity (final):")
    print(f"  Omega  : {final['W_min_Omega']:+.4f}  ({'classical' if final['W_min_Omega'] >= 0 else 'NON-CLASSICAL'})")
    print(f"  Kevin  : {final['W_min_Kevin']:+.4f}  ({'classical' if final['W_min_Kevin'] >= 0 else 'NON-CLASSICAL'})")
    print(f"  Alpha  : {final['W_min_Alpha']:+.4f}  ({'classical' if final['W_min_Alpha'] >= 0 else 'NON-CLASSICAL'})")
    print(f"\nAdaptive coupling (final):")
    print(f"  α* (Omega-Kevin) : {final['alpha_OK']:.4f}")
    print(f"  α* (Kevin-Alpha) : {final['alpha_KA']:.4f}")
    sym = abs(final['alpha_OK'] - final['alpha_KA'])
    print(f"  Symmetry break Δα : {sym:.4f}  ({'BROKEN' if sym > 0.01 else 'symmetric'})")
    print(f"\nNegentropic steps:")
    print(f"  Omega-Kevin link : {negtrop_OK}/99")
    print(f"  Kevin-Alpha link : {negtrop_KA}/99")
    print(f"\nMutual information (final):")
    print(f"  I(Omega:Kevin) : {final['MI_OK']:.4f} bits")
    print(f"  I(Kevin:Alpha) : {final['MI_KA']:.4f} bits")

    print("\n" + "=" * 65)
    print("KEY QUESTION ANSWERS")
    print("=" * 65)

    # Q1: Does Kevin develop a third Wigner signature?
    W_K_vals = [r['W_min_Kevin'] for r in log]
    W_K_range = max(W_K_vals) - min(W_K_vals)
    print(f"\n[Q1] Kevin Wigner range over 100 steps: {W_K_range:.4f}")
    if W_K_range > 0.05:
        print("     → OSCILLATORY: Kevin has dynamic Wigner evolution")
    elif final['W_min_Kevin'] < -0.05:
        print("     → PRESERVED: Kevin retains non-classicality (Alpha-like)")
    else:
        print("     → CONSUMED: Kevin's Wigner negativity decays (Omega-like)")

    # Q2: Symmetry break in couplings?
    print(f"\n[Q2] α symmetry break Δα = {sym:.4f}")
    if sym > 0.01:
        print("     → Bridge breaks coupling symmetry: upstream ≠ downstream")
    else:
        print("     → Couplings remain symmetric: bridge is neutral")

    # Q3: Does three-node converge?
    print(f"\n[Q3] Final C_avg = {final['C_avg']:.6f}")
    if final['C_avg'] > 0.99:
        print("     → YES: Three-node system converges to attractor")
    else:
        print("     → PARTIAL: Three-node convergence degraded vs two-node")

    print("\nPlotting...")
    plot_results(log)
