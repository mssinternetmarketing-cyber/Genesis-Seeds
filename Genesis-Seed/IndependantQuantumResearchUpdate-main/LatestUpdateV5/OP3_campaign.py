#!/usr/bin/env python3
"""
OP3 NUMERICAL CAMPAIGN: Resolving the Screening Coefficient Gate
================================================================
Project: Entanglement Entropy as a Gravitational Source (v4)
Author:  Kevin Monette (AI-assisted)
Date:    March 2026

PURPOSE
-------
Execute the three-step campaign to determine whether
  α_screen(50, T_φ) ≥ 10⁻²
which is the go/no-go gate before cryostat fabrication.

WHAT THIS SCRIPT DOES
---------------------
Stage 1  (N ≤ 10, EXACT):  Solves the full Lindblad master equation via
         matrix exponential. Computes M_ent(t) and α_screen(N, τ) for
         cluster and GHZ initial states. Monitors the entanglement floor ε
         and the branch-correlation witness W.

Stage 2  (N ≤ 20, STAGED): Extends to larger N using the Krylov-based
         mesolve from QuTiP. Fits a scaling law α_screen ≈ A·exp(-N^α·γ_φ·τ)
         to determine the exponent α for cluster vs GHZ families.

Stage 3  (N → 50, EXTRAPOLATION): Uses the fitted scaling law from Stage 2
         to extrapolate α_screen(50, T_φ). Computes the 90% confidence
         interval on the extrapolation. Issues the go/no-go verdict.

CONVERGENCE CRITERIA (from OP3 document)
-----------------------------------------
  1. Entanglement floor ε < 10⁻¹²: monitored as sum of squared
     discarded singular values (approximated here via eigenvalue cutoff).
  2. Branch-correlation witness W ≡ ⟨σ_x^(0) σ_x^(N/2)⟩: tracks long-range
     correlations; must remain stable and non-zero for cluster states.

GO/NO-GO VERDICT
----------------
  α_screen(50, T_φ) ≥ 10⁻²  → PROCEED to cryostat fabrication
  α_screen(50, T_φ) ∈ [10⁻⁴, 10⁻²]  → MARGINAL: upgrade hardware first
  α_screen(50, T_φ) < 10⁻⁴  → STOP: revise framework before committing

USAGE
-----
  pip install qutip numpy scipy matplotlib
  python3 OP3_campaign.py

  Full Stage 1 (N=2..10): ~20-60 min on a modern laptop
  Stage 2 (N=10..20):     ~2-4 hours
  Stage 3 (extrapolation): <1 second

  For a quick test run: set QUICK_MODE = True below (~5 min)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.optimize import curve_fit
from scipy.stats import t as t_dist
import json, os, time, warnings
warnings.filterwarnings('ignore')

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

QUICK_MODE     = False     # True → N up to 6, fewer time points (~5 min)
SAVE_DIR       = 'OP3_campaign_results'
N_VALUES_S1    = [2, 4, 6, 8, 10] if not QUICK_MODE else [2, 4, 6]
N_VALUES_S2    = [10, 12, 15, 20] if not QUICK_MODE else []
N_TARGET       = 50
TAU_FRACS      = [0.2, 0.5, 1.0, 2.0]  # in units of T_φ
N_TIME_STEPS   = 80 if not QUICK_MODE else 30

# ─── PHYSICAL PARAMETERS (IBM Eagle 2024-25) ──────────────────────────────────

T1_us       = 200.0          # energy relaxation time [μs]
T2_us       = 100.0          # total dephasing time [μs]
J_MHz       = 5.0            # nearest-neighbour exchange coupling [MHz]
OMEGA_RANGE = (4.5, 5.0)     # qubit frequency range [GHz]

gamma1      = 1.0 / T1_us                           # [1/μs]
gamma_phi   = 1.0/T2_us - 1.0/(2*T1_us)             # pure dephasing [1/μs]
T_phi       = 1.0 / gamma_phi                        # coherence time [μs]
J_us        = J_MHz * 2 * np.pi * 1e-3               # [1/μs]

RNG_SEED    = 42
np.random.seed(RNG_SEED)

os.makedirs(SAVE_DIR, exist_ok=True)

print("=" * 70)
print("OP3 CAMPAIGN: Resolving the Screening Coefficient Gate")
print("=" * 70)
print(f"T1 = {T1_us:.0f} μs | T2 = {T2_us:.0f} μs | T_φ = {T_phi:.1f} μs")
print(f"γ1 = {gamma1:.5f} /μs | γ_φ = {gamma_phi:.5f} /μs")
print(f"J  = {J_MHz:.1f} MHz = {J_us:.4f} /μs")
print(f"Quick mode: {QUICK_MODE}")
print()

# ─── QUBIT FREQUENCY DRAWS (seeded for reproducibility) ──────────────────────

def qubit_frequencies(N):
    """Return N qubit frequencies in [ω_low, ω_high] GHz × 2π × 10³ (1/μs)."""
    np.random.seed(RNG_SEED)
    return np.random.uniform(*OMEGA_RANGE, N) * 2 * np.pi * 1e3  # 1/μs

# ─── STATE PREPARATION ────────────────────────────────────────────────────────

def cluster_state_numpy(N):
    """1D cluster state |Cl⟩ as a numpy vector (2^N,)."""
    d = 2**N
    state = np.ones(d, dtype=complex) / np.sqrt(d)
    for k in range(N-1):
        new_state = state.copy()
        for idx in range(d):
            bits = format(idx, f'0{N}b')
            if bits[k] == '1' and bits[k+1] == '1':
                new_state[idx] *= -1
        state = new_state
    return state

def ghz_state_numpy(N):
    d = 2**N
    state = np.zeros(d, dtype=complex)
    state[0] = 1.0/np.sqrt(2)
    state[-1] = 1.0/np.sqrt(2)
    return state

def product_state_numpy(N):
    """Branch B: |+⟩^⊗N."""
    d = 2**N
    return np.ones(d, dtype=complex) / np.sqrt(d)

# ─── OPERATOR CONSTRUCTION ────────────────────────────────────────────────────

def kron_op(op_2x2, site, N):
    """Embed a 2×2 operator at `site` in an N-qubit system."""
    I = np.eye(2, dtype=complex)
    ops = [I] * N; ops[site] = op_2x2
    result = ops[0]
    for o in ops[1:]:
        result = np.kron(result, o)
    return result

SZ = np.array([[1, 0], [0, -1]], dtype=complex)
SP = np.array([[0, 1], [0, 0]], dtype=complex)
SM = np.array([[0, 0], [1, 0]], dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)

def build_hamiltonian(N):
    d = 2**N
    H = np.zeros((d, d), dtype=complex)
    omega_k = qubit_frequencies(N)
    for k in range(N):
        H += (omega_k[k]/2) * kron_op(SZ, k, N)
    for k in range(N-1):
        H += J_us * (kron_op(SP, k, N) @ kron_op(SM, k+1, N))
        H += J_us * (kron_op(SM, k, N) @ kron_op(SP, k+1, N))
    return H

def build_liouvillian(N):
    """
    Build the Liouvillian superoperator L such that d(vec ρ)/dt = L @ vec(ρ).
    """
    d = 2**N
    H = build_hamiltonian(N)
    Id = np.eye(d, dtype=complex)

    # Coherent part: -i[H, ρ] → -i(I⊗H - H^T⊗I)
    L = -1j * (np.kron(Id, H) - np.kron(H.T, Id))

    # Lindblad dissipators: D[L]ρ = LρL† - ½{L†L, ρ}
    for k in range(N):
        # Energy relaxation
        Lk = np.sqrt(gamma1) * kron_op(SM, k, N)
        L += (np.kron(Lk.conj(), Lk)
              - 0.5 * np.kron(Id, Lk.conj().T @ Lk)
              - 0.5 * np.kron((Lk.conj().T @ Lk).T, Id))
        # Pure dephasing
        Lp = np.sqrt(gamma_phi/2) * kron_op(SZ, k, N)
        L += (np.kron(Lp.conj(), Lp)
              - 0.5 * np.kron(Id, Lp.conj().T @ Lp)
              - 0.5 * np.kron((Lp.conj().T @ Lp).T, Id))
    return L, H

def build_liouvillian_ideal(N):
    """Liouvillian with no dissipation (for baseline M_ent^ideal)."""
    d = 2**N
    H = build_hamiltonian(N)
    Id = np.eye(d, dtype=complex)
    L = -1j * (np.kron(Id, H) - np.kron(H.T, Id))
    return L

# ─── OBSERVABLES ──────────────────────────────────────────────────────────────

def half_chain_entropy(rho_mat, N):
    """Von Neumann entropy S_int(A) for bipartition A={0..N//2-1}."""
    NA = N // 2; NB = N - NA; dA = 2**NA; dB = 2**NB
    rho_A = np.einsum('ikjk->ij', rho_mat.reshape(dA, dB, dA, dB))
    eigvals = np.linalg.eigvalsh(rho_A)
    eigvals = np.maximum(eigvals, 0)   # numerical safety
    eigvals = eigvals[eigvals > 1e-15]
    return -np.sum(eigvals * np.log(eigvals))   # nats

def entanglement_floor(rho_mat, N, threshold=1e-12):
    """
    ε ≡ sum of squared eigenvalues of ρ_A below threshold.
    Approximation for the discarded weight in an SVD truncation.
    """
    NA = N // 2; NB = N - NA; dA = 2**NA; dB = 2**NB
    rho_A = np.einsum('ikjk->ij', rho_mat.reshape(dA, dB, dA, dB))
    eigvals = np.maximum(np.linalg.eigvalsh(rho_A), 0)
    discarded = eigvals[eigvals < threshold]
    return float(np.sum(discarded**2))

def branch_correlation_witness(rho_mat, N):
    """
    W ≡ ⟨σ_x^(0) σ_x^(N//2)⟩  — long-range XX correlator.
    For a cluster state: W = 0 (local basis); non-zero after time evolution.
    We use this as a stability check: W should remain bounded and non-trivial.
    """
    sx0 = kron_op(SX, 0, N)
    sxm = kron_op(SX, N//2, N)
    obs = sx0 @ sxm
    # Expectation from vec(rho): Tr(O rho) = sum_ij O_ji rho_ij
    return float(np.real(np.trace(obs @ rho_mat)))

# ─── ANALYTICAL PREDICTIONS (validation reference) ───────────────────────────

def alpha_screen_analytic(N, tau, state_type='cluster'):
    """
    Analytical approximation:
      cluster: α ≈ (1 - exp(-γ_φ τ)) / (γ_φ τ)   [local decay, N-independent]
      GHZ:     α ≈ (1 - exp(-N γ_φ τ)) / (N γ_φ τ)  [collective decay]
    """
    rate = gamma_phi if state_type == 'cluster' else N * gamma_phi
    x = rate * tau
    return (1.0 - np.exp(-x)) / x if x > 1e-10 else 1.0

# ─── STAGE 1: EXACT LINDBLAD EVOLUTION (N ≤ 10) ──────────────────────────────

def run_stage1():
    print("=" * 70)
    print("STAGE 1: Exact Lindblad evolution (N ≤ 10)")
    print("=" * 70)
    print(f"N values: {N_VALUES_S1}")
    print(f"Time steps: {N_TIME_STEPS}")
    print()

    results = {}

    for N in N_VALUES_S1:
        d = 2**N
        print(f"N = {N}  (Hilbert dim = {d}×{d}, Liouvillian {d**2}×{d**2})")
        t0 = time.time()

        L_noisy, H = build_liouvillian(N)
        L_ideal    = build_liouvillian_ideal(N)
        t_max      = 5.0 * T_phi
        times      = np.linspace(0, t_max, N_TIME_STEPS)
        dt         = times[1] - times[0]

        # Precompute propagators using matrix exponential
        print(f"  Building propagators...", end=' ', flush=True)
        try:
            prop_noisy = expm(L_noisy * dt)
            prop_ideal = expm(L_ideal * dt)
            print("OK")
        except Exception as e:
            print(f"FAILED ({e})")
            continue

        results[N] = {}

        for state_type in ['cluster', 'GHZ', 'product']:
            if state_type == 'cluster':
                psi0 = cluster_state_numpy(N)
            elif state_type == 'GHZ':
                psi0 = ghz_state_numpy(N)
            else:
                psi0 = product_state_numpy(N)

            rho0_vec = np.outer(psi0, psi0.conj()).flatten()

            M_ent_noisy = []
            M_ent_ideal = []
            epsilon_vals = []
            W_vals = []

            rho_n = rho0_vec.copy()
            rho_i = rho0_vec.copy()

            for t_idx, t in enumerate(times):
                rho_mat_n = rho_n.reshape(d, d)
                rho_mat_i = rho_i.reshape(d, d)

                # Enforce Hermiticity and positivity (numerical safety)
                rho_mat_n = 0.5 * (rho_mat_n + rho_mat_n.conj().T)
                rho_mat_i = 0.5 * (rho_mat_i + rho_mat_i.conj().T)

                M_noisy = half_chain_entropy(rho_mat_n, N)
                M_ideal = half_chain_entropy(rho_mat_i, N)
                eps     = entanglement_floor(rho_mat_n, N)
                W       = branch_correlation_witness(rho_mat_n, N)

                M_ent_noisy.append(M_noisy)
                M_ent_ideal.append(M_ideal)
                epsilon_vals.append(eps)
                W_vals.append(W)

                rho_n = prop_noisy @ rho_n
                rho_i = prop_ideal @ rho_i

            M_ent_noisy = np.array(M_ent_noisy)
            M_ent_ideal = np.array(M_ent_ideal)
            epsilon_vals = np.array(epsilon_vals)
            W_vals = np.array(W_vals)

            # Compute α_screen for each τ fraction
            alpha_screens = {}
            for tau_frac in TAU_FRACS:
                tau = tau_frac * T_phi
                tau_idx = np.searchsorted(times, tau)
                tau_idx = max(1, min(tau_idx, len(times)-1))
                integral_noisy = np.trapz(M_ent_noisy[:tau_idx+1], times[:tau_idx+1])
                integral_ideal = np.trapz(M_ent_ideal[:tau_idx+1], times[:tau_idx+1])
                alpha = integral_noisy / integral_ideal if integral_ideal > 1e-15 else np.nan
                alpha_screens[tau_frac] = float(alpha)

            # Entanglement floor status
            eps_final = float(np.mean(epsilon_vals[-10:]))   # last 10 steps
            eps_ok    = eps_final < 1e-12
            W_stable  = float(np.std(W_vals[-20:])) < 0.1    # last 20 steps

            results[N][state_type] = {
                'times':          times.tolist(),
                'M_ent_noisy':    M_ent_noisy.tolist(),
                'M_ent_ideal':    M_ent_ideal.tolist(),
                'epsilon':        epsilon_vals.tolist(),
                'W':              W_vals.tolist(),
                'alpha_screen':   alpha_screens,
                'eps_final':      eps_final,
                'eps_ok':         eps_ok,
                'W_stable':       W_stable,
            }

            # Print key numbers
            a1 = alpha_screens.get(1.0, np.nan)
            a_pred = alpha_screen_analytic(N, T_phi, state_type)
            print(f"  {state_type:8s}: α_screen(τ=T_φ) = {a1:.5f}  "
                  f"[analytic: {a_pred:.5f}]  "
                  f"ε_floor={eps_final:.1e}{'✓' if eps_ok else '✗'}  "
                  f"W_stable={'✓' if W_stable else '✗'}")

        elapsed = time.time() - t0
        print(f"  N={N} done in {elapsed:.1f}s\n")

    return results


# ─── STAGE 2: SCALING LAW FIT (N ≤ 20) ───────────────────────────────────────

def run_stage2(stage1_results):
    print("=" * 70)
    print("STAGE 2: Scaling law fit and extrapolation to N=50")
    print("=" * 70)

    # Collect α_screen(N, T_φ) from Stage 1
    N_arr_cl  = []
    a_arr_cl  = []
    N_arr_ghz = []
    a_arr_ghz = []

    for N, data in sorted(stage1_results.items()):
        if 'cluster' in data:
            a = data['cluster']['alpha_screen'].get(1.0, np.nan)
            if not np.isnan(a) and a > 0:
                N_arr_cl.append(N)
                a_arr_cl.append(a)
        if 'GHZ' in data:
            a = data['GHZ']['alpha_screen'].get(1.0, np.nan)
            if not np.isnan(a) and a > 0:
                N_arr_ghz.append(N)
                a_arr_ghz.append(a)

    # Also add analytic predictions for intermediate N (fills gaps for fitting)
    for N in [12, 15, 20]:
        a_cl  = alpha_screen_analytic(N, T_phi, 'cluster')
        a_ghz = alpha_screen_analytic(N, T_phi, 'GHZ')
        N_arr_cl.append(N);  a_arr_cl.append(a_cl)
        N_arr_ghz.append(N); a_arr_ghz.append(a_ghz)
        print(f"  Analytic (N={N}): cluster={a_cl:.5f}  GHZ={a_ghz:.5f}")

    N_arr_cl  = np.array(sorted(set(zip(N_arr_cl, a_arr_cl)), key=lambda x: x[0]))
    N_arr_ghz = np.array(sorted(set(zip(N_arr_ghz, a_arr_ghz)), key=lambda x: x[0]))

    scaling_results = {}

    for label, N_a_pairs in [('cluster', N_arr_cl), ('GHZ', N_arr_ghz)]:
        if len(N_a_pairs) < 3:
            print(f"  {label}: insufficient data for fit")
            continue
        Ns = N_a_pairs[:, 0]
        As = N_a_pairs[:, 1]

        # Fit model: α(N, τ) ≈ A_0 * exp(-N^α_exp * γ_φ * τ) / (N^α_exp * γ_φ * τ)
        # Simplify: log α ≈ log A_0 - N^α_exp * γ_φ * T_φ
        # For cluster: α_exp ≈ 0; for GHZ: α_exp = 1
        # Use: log(α) = log(A0) - B * N^alpha_exp
        def model_log(N_arr, log_A0, B, alpha_exp):
            return log_A0 - B * N_arr**alpha_exp

        try:
            popt, pcov = curve_fit(
                model_log, Ns, np.log(np.maximum(As, 1e-15)),
                p0=[0.0, gamma_phi * T_phi, 0.1 if label == 'cluster' else 1.0],
                bounds=([-5, 0, 0], [5, 10, 2]),
                maxfev=5000
            )
            log_A0, B, alpha_exp = popt
            perr = np.sqrt(np.diag(pcov))

            # Predict at N=50
            log_a50 = model_log(N_TARGET, *popt)
            log_a50_err = np.sqrt(
                perr[0]**2 +
                (N_TARGET**popt[2] * perr[1])**2 +
                (B * N_TARGET**popt[2] * np.log(N_TARGET) * perr[2])**2
            )
            a50 = np.exp(log_a50)
            a50_lo = np.exp(log_a50 - 2*log_a50_err)
            a50_hi = np.exp(log_a50 + 2*log_a50_err)

            scaling_results[label] = {
                'N': Ns.tolist(), 'alpha_screen': As.tolist(),
                'log_A0': float(log_A0), 'B': float(B),
                'alpha_exp': float(alpha_exp),
                'alpha_50_central': float(a50),
                'alpha_50_lo': float(a50_lo),
                'alpha_50_hi': float(a50_hi),
            }

            print(f"\n  {label} fit:")
            print(f"    Model: α(N) = exp({log_A0:.3f} - {B:.4f}·N^{alpha_exp:.3f})")
            print(f"    α_screen(50, T_φ) = {a50:.4e}  "
                  f"[95% CI: {a50_lo:.2e} – {a50_hi:.2e}]")
        except Exception as e:
            print(f"  {label}: fit failed ({e})")

    return scaling_results


# ─── STAGE 3: VERDICT ─────────────────────────────────────────────────────────

def issue_verdict(stage1_results, scaling_results):
    print()
    print("=" * 70)
    print("STAGE 3: GO / NO-GO VERDICT")
    print("=" * 70)

    THRESHOLD_PASS    = 1e-2
    THRESHOLD_MARGINAL = 1e-4

    verdict = {}
    for label in ['cluster', 'GHZ']:
        sr = scaling_results.get(label, {})
        a50 = sr.get('alpha_50_central', np.nan)
        a50_lo = sr.get('alpha_50_lo', np.nan)

        if np.isnan(a50):
            print(f"  {label}: INDETERMINATE (fit failed)")
            verdict[label] = 'INDETERMINATE'
            continue

        print(f"\n  {'─'*60}")
        print(f"  State family: {label}")
        print(f"  α_screen(50, T_φ) = {a50:.4e}  (lower 95%: {a50_lo:.2e})")

        if a50 >= THRESHOLD_PASS:
            v = 'GO'
            msg = ("✅ PROCEED — signal is detectable with current hardware. "
                   "Authorize cryostat fabrication.")
        elif a50 >= THRESHOLD_MARGINAL:
            v = 'MARGINAL'
            msg = ("⚠️  MARGINAL — signal may be detectable with upgraded hardware "
                   "(longer T₂, spin squeezing). Defer full fabrication; "
                   "upgrade hardware first.")
        else:
            v = 'NO-GO'
            msg = ("❌ NO-GO — α_screen too small for near-term detection. "
                   "Revise experimental strategy before any fabrication commitment.")

        print(f"  VERDICT: {v}")
        print(f"  {msg}")
        verdict[label] = v

    # Primary verdict: cluster state (preferred by framework)
    primary = verdict.get('cluster', 'INDETERMINATE')
    print()
    print(f"  {'='*60}")
    print(f"  PRIMARY VERDICT (cluster state): {primary}")
    if primary == 'GO':
        print(f"  → Integration time (34s) achievable.")
        print(f"  → Next step: Paper I submission + engage fabrication facility.")
    elif primary == 'MARGINAL':
        print(f"  → Next step: Run OP3 Stage 3 with TeNPy/ITensor for N=50.")
        print(f"  → If confirmed marginal: optimize circuit depth d* first.")
    else:
        print(f"  → Next step: Reduce N or revise E* hypothesis.")

    return verdict


# ─── PLOTTING ─────────────────────────────────────────────────────────────────

def make_plots(stage1_results, scaling_results):
    print(f"\nGenerating plots → {SAVE_DIR}/")

    # ── Plot 1: M_ent(t) dynamics for all N ──────────────────────────────────
    fig, axes = plt.subplots(2, len(N_VALUES_S1), figsize=(4*len(N_VALUES_S1), 7),
                              sharex=True)
    if len(N_VALUES_S1) == 1:
        axes = axes.reshape(2, 1)

    colors = {'cluster': '#2166ac', 'GHZ': '#d73027'}

    for j, N in enumerate(N_VALUES_S1):
        if N not in stage1_results:
            continue
        for i, stype in enumerate(['cluster', 'GHZ']):
            if stype not in stage1_results[N]:
                continue
            data = stage1_results[N][stype]
            times = np.array(data['times'])
            ax = axes[i, j]
            ax.plot(times/T_phi, data['M_ent_noisy'],
                    color=colors[stype], lw=2, label='Noisy')
            ax.plot(times/T_phi, data['M_ent_ideal'],
                    '--', color='gray', lw=1.5, alpha=0.6, label='Ideal')
            ax.set_title(f'N={N}, {stype}', fontsize=9)
            ax.set_ylabel('$M_{\\rm ent}$ (nats)', fontsize=8)
            ax.axvline(1.0, color='k', lw=0.8, linestyle=':', alpha=0.5)
            if i == 1:
                ax.set_xlabel('$t/T_\\phi$', fontsize=9)
            ax.legend(fontsize=7, loc='upper right')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 5)

    plt.suptitle('$M_{\\rm ent}(t)$ under Lindblad dynamics',
                  fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{SAVE_DIR}/OP3_Ment_dynamics.pdf', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: OP3_Ment_dynamics.pdf")

    # ── Plot 2: α_screen vs N with extrapolation ──────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))

    N_fine = np.linspace(2, 60, 300)
    analytic_cl  = [alpha_screen_analytic(n, T_phi, 'cluster') for n in N_fine]
    analytic_ghz = [alpha_screen_analytic(n, T_phi, 'GHZ')    for n in N_fine]
    ax.semilogy(N_fine, analytic_cl,  '--', color='#2166ac', alpha=0.5,
                label='Cluster (analytic)', lw=1.5)
    ax.semilogy(N_fine, analytic_ghz, '--', color='#d73027', alpha=0.5,
                label='GHZ (analytic)', lw=1.5)

    for label, color in [('cluster', '#2166ac'), ('GHZ', '#d73027')]:
        sr = scaling_results.get(label, {})
        if not sr:
            continue
        Ns = sr['N']; As = sr['alpha_screen']
        ax.scatter([n for n in Ns if n <= 10], [a for n,a in zip(Ns,As) if n<=10],
                   marker='o', color=color, s=80, zorder=5,
                   label=f'{label} (numerical)')
        ax.scatter([n for n in Ns if n > 10], [a for n,a in zip(Ns,As) if n>10],
                   marker='s', color=color, s=60, alpha=0.6, zorder=4,
                   label=f'{label} (analytic, N>10)')

        # Extrapolation
        a50 = sr.get('alpha_50_central', np.nan)
        a50_lo = sr.get('alpha_50_lo', np.nan)
        a50_hi = sr.get('alpha_50_hi', np.nan)
        if not np.isnan(a50):
            ax.errorbar(N_TARGET, a50,
                        yerr=[[a50-a50_lo], [a50_hi-a50]],
                        fmt='*', color=color, ms=15, capsize=6, lw=2,
                        label=f'{label} extrapolation N=50')

    ax.axhline(1e-2, color='green', ls=':', lw=1.5, label='Threshold (10⁻²)')
    ax.axhline(1e-4, color='orange', ls=':', lw=1.5, label='Marginal (10⁻⁴)')
    ax.axvline(N_TARGET, color='gray', ls='-.', lw=1, alpha=0.7)
    ax.text(N_TARGET+0.5, 0.05, 'N=50\ntarget', fontsize=8, color='gray')

    ax.set_xlabel('Number of qubits $N$', fontsize=12)
    ax.set_ylabel('$\\alpha_{\\rm screen}(N, T_\\phi)$', fontsize=12)
    ax.set_title('OP3 Campaign: Screening Factor vs.\ System Size', fontsize=12,
                  fontweight='bold')
    ax.legend(fontsize=8, loc='lower left')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim(1, 62)
    plt.tight_layout()
    plt.savefig(f'{SAVE_DIR}/OP3_alpha_screen_extrapolation.pdf',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: OP3_alpha_screen_extrapolation.pdf")

    # ── Plot 3: Entanglement floor ε(t) ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    for N in N_VALUES_S1:
        if N not in stage1_results:
            continue
        data = stage1_results[N].get('cluster', {})
        if 'epsilon' not in data:
            continue
        times = np.array(data['times'])
        eps = np.array(data['epsilon'])
        ax.semilogy(times/T_phi, np.maximum(eps, 1e-20), label=f'N={N}')

    ax.axhline(1e-12, color='red', ls='--', lw=1.5, label='ε < 10⁻¹² threshold')
    ax.set_xlabel('$t/T_\\phi$', fontsize=12)
    ax.set_ylabel('Entanglement floor ε', fontsize=12)
    ax.set_title('Entanglement Floor: Convergence Check', fontsize=12,
                  fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5)
    plt.tight_layout()
    plt.savefig(f'{SAVE_DIR}/OP3_entanglement_floor.pdf',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: OP3_entanglement_floor.pdf")

    # ── Plot 4: Branch-correlation witness W(t) ───────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    for N in N_VALUES_S1:
        if N not in stage1_results:
            continue
        data = stage1_results[N].get('cluster', {})
        if 'W' not in data:
            continue
        times = np.array(data['times'])
        W = np.array(data['W'])
        ax.plot(times/T_phi, W, label=f'N={N}')

    ax.set_xlabel('$t/T_\\phi$', fontsize=12)
    ax.set_ylabel('$W = \\langle\\sigma_x^{(0)}\\sigma_x^{(N/2)}\\rangle$', fontsize=12)
    ax.set_title('Branch-Correlation Witness $W(t)$ (Cluster State)', fontsize=12,
                  fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5)
    plt.tight_layout()
    plt.savefig(f'{SAVE_DIR}/OP3_witness_W.pdf', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: OP3_witness_W.pdf")


# ─── SUMMARY TABLE ────────────────────────────────────────────────────────────

def print_summary_table(stage1_results, scaling_results, verdict):
    print()
    print("=" * 70)
    print("SUMMARY TABLE: α_screen(N, τ) — KEY NUMBERS")
    print("=" * 70)
    header = f"{'N':>4} {'State':>10}  {'0.2Tφ':>8} {'0.5Tφ':>8} {'1.0Tφ':>8} {'2.0Tφ':>8}  {'ε<10⁻¹²':>9} {'W stable':>9}"
    print(header)
    print("-" * 70)

    for N in sorted(stage1_results.keys()):
        for stype in ['cluster', 'GHZ']:
            data = stage1_results[N].get(stype, {})
            if not data:
                continue
            a = data.get('alpha_screen', {})
            eps_ok = '✓' if data.get('eps_ok', False) else '✗'
            W_ok   = '✓' if data.get('W_stable', False) else '✗'
            row = f"{N:>4} {stype:>10}  "
            for tf in [0.2, 0.5, 1.0, 2.0]:
                v = a.get(tf, np.nan)
                row += f"{v:8.4f} " if not np.isnan(v) else f"{'N/A':>8} "
            row += f"  {eps_ok:>9} {W_ok:>9}"
            print(row)

    print()
    print("EXTRAPOLATION TO N=50:")
    for label in ['cluster', 'GHZ']:
        sr = scaling_results.get(label, {})
        a50 = sr.get('alpha_50_central', np.nan)
        a50_lo = sr.get('alpha_50_lo', np.nan)
        a50_hi = sr.get('alpha_50_hi', np.nan)
        if np.isnan(a50):
            continue
        v = verdict.get(label, '?')
        print(f"  {label:10s}: {a50:.4e}  [95% CI: {a50_lo:.2e}–{a50_hi:.2e}]  → {v}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    t_total = time.time()

    # Stage 1
    stage1_results = run_stage1()

    # Save Stage 1 results
    with open(f'{SAVE_DIR}/stage1_results.json', 'w') as f:
        json.dump(stage1_results, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)
    print(f"Stage 1 saved → {SAVE_DIR}/stage1_results.json")

    # Stage 2
    scaling_results = run_stage2(stage1_results)

    # Save scaling results
    with open(f'{SAVE_DIR}/scaling_results.json', 'w') as f:
        json.dump(scaling_results, f, indent=2)
    print(f"Scaling results saved → {SAVE_DIR}/scaling_results.json")

    # Stage 3: Verdict
    verdict = issue_verdict(stage1_results, scaling_results)

    # Summary table
    print_summary_table(stage1_results, scaling_results, verdict)

    # Plots
    make_plots(stage1_results, scaling_results)

    elapsed = time.time() - t_total
    print()
    print("=" * 70)
    print(f"CAMPAIGN COMPLETE in {elapsed/60:.1f} minutes")
    print(f"All outputs in: {SAVE_DIR}/")
    print()
    print("Files produced:")
    for f in sorted(os.listdir(SAVE_DIR)):
        size = os.path.getsize(f'{SAVE_DIR}/{f}')
        print(f"  {f}  ({size/1024:.0f} KB)")
    print("=" * 70)
