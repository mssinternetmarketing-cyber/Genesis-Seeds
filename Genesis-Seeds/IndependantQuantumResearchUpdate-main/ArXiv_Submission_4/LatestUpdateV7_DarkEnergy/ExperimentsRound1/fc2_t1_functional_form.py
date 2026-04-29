"""
FC-2: T1 Functional Form Test  --  PRIORITY 2
=====================================================================
PREDICTION (Paper 1, Corollary 5.4 / Section 7.4 FC-2):
    S_A(t) follows  h2(exp(-t/2T1)) / ln2  (quadratic suppression at short times)
    NOT  exp(-Gamma*t)  (linear-exponent heuristic)

The two models are distinguishable when gamma1*t > 0.3
(i.e., t > 60 us for IBM Heron T1=200us).

HOW THE TEST WORKS:
    1. Prepare Bell state, let it idle for t, do tomography.
    2. Extract S_A(t) at many time points.
    3. Fit both models:
         Model A (Theorem 1):  S_A = ln2 * h2(exp(-t/(2*T1))) / ln2
         Model B (heuristic):  S_A = ln2 * exp(-Gamma * t)
    4. Compare AIC/BIC and chi^2. If Delta-chi^2 > 5, reject worse model.

NOTE:  T1 is a FREE parameter in both fits (we measure it, not assume it).
       This means the test is not circular -- we're testing the *shape*,
       not just the scale.

CIRCUIT COUNT:  12 delay points x 9 tomo bases = 108 circuits
SHOTS:          512 per circuit
RUNTIME:        ~2.5 minutes
=====================================================================
USAGE:
    python fc2_t1_functional_form.py --token YOUR_IBM_TOKEN --backend ibm_brisbane

    If you already ran FC-1 and want to reuse results:
    python fc2_t1_functional_form.py --results-file fc1_results_*.json
=====================================================================
"""

import os
import sys
import json
import argparse
import numpy as np
from datetime import datetime
from scipy.optimize import curve_fit
from scipy.special import xlogy

# ── Qiskit imports ──────────────────────────────────────────────────────────
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, Session

# ── Config ───────────────────────────────────────────────────────────────────
SHOTS = 512
# Wider time range than FC-1 to catch the regime where models diverge (t > 60us)
DELAY_US = [0, 5, 15, 30, 60, 90, 120, 160, 200, 260, 320, 400]
TOMO_BASES = ['XX','XY','XZ','YX','YY','YZ','ZX','ZY','ZZ']

# ── Reuse helpers from FC-1 ──────────────────────────────────────────────────
def bell_prep():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc

def apply_basis_rotation(qc, basis):
    for i, b in enumerate(basis):
        if b == 'X':
            qc.h(i)
        elif b == 'Y':
            qc.sdg(i)
            qc.h(i)
    qc.measure_all()

def counts_to_probs(counts, n_qubits=2):
    total  = sum(counts.values())
    states = [format(i, f'0{n_qubits}b') for i in range(2**n_qubits)]
    return {s: counts.get(s, 0) / total for s in states}

def reconstruct_rho_A(tomo_probs):
    """
    Reconstruct 2x2 reduced density matrix on qubit 0 from 9-basis tomography.
    Uses only the ZZ, XZ, YZ measurements for a minimal linear inversion on qubit 0.
    """
    # Z basis expectation value on qubit 0: use ZZ measurement, trace over qubit 1
    def single_bloch(probs_zz, component):
        """Bloch vector component for qubit 0 from measurement probs."""
        ev = 0.0
        for bits, p in probs_zz.items():
            # bits[1] = qubit 0 result (Qiskit reverse order)
            s0 = +1 if bits[1] == '0' else -1
            ev += s0 * p
        return ev

    zz_probs = tomo_probs.get('ZZ', {})
    xz_probs = tomo_probs.get('XZ', {})
    yz_probs = tomo_probs.get('YZ', {})

    rx = single_bloch(xz_probs, 'X')
    ry = single_bloch(yz_probs, 'Y')
    rz = single_bloch(zz_probs, 'Z')

    rho_A = 0.5 * (np.eye(2) + rx * np.array([[0,1],[1,0]])
                               + ry * np.array([[0,-1j],[1j,0]])
                               + rz * np.array([[1,0],[0,-1]]))
    return rho_A

def von_neumann_entropy_2x2(rho_A):
    eigvals = np.linalg.eigvalsh(rho_A)
    eigvals = np.clip(eigvals.real, 1e-15, 1.0)
    return float(-np.sum(eigvals * np.log(eigvals)))

# ── Circuit builder ───────────────────────────────────────────────────────────
def build_circuits(delay_us_list, dt_ns=0.5):
    circuits, labels = [], []
    for delay in delay_us_list:
        for basis in TOMO_BASES:
            qc = bell_prep()
            qc.barrier()
            if delay > 0:
                delay_dt = int(delay * 1000 / dt_ns)
                qc.delay(delay_dt, 0, unit='dt')
                qc.delay(delay_dt, 1, unit='dt')
            qc.barrier()
            apply_basis_rotation(qc, basis)
            labels.append(f"{delay}us_{basis}")
            circuits.append(qc)
    print(f"[FC-2] Built {len(circuits)} circuits "
          f"({len(delay_us_list)} delays x {len(TOMO_BASES)} bases)")
    return labels, circuits

# ── Model definitions ─────────────────────────────────────────────────────────
def model_theorem1(t, T1):
    """
    Theorem 1 prediction: S_A(t) = h2(exp(-t/(2*T1)))
    T1 in microseconds.
    """
    lam = np.clip(0.5 * np.exp(-t / (2 * T1)), 1e-15, 1 - 1e-15)
    return -lam * np.log(lam) - (1 - lam) * np.log(1 - lam)

def model_heuristic(t, Gamma):
    """
    Prior heuristic: S_A(t) = ln2 * exp(-Gamma * t)
    Gamma in 1/microseconds.
    """
    return np.log(2) * np.exp(-Gamma * t)

def model_heuristic_2param(t, A, Gamma):
    """Heuristic with amplitude free."""
    return A * np.exp(-Gamma * t)

# ── AIC / BIC helpers ─────────────────────────────────────────────────────────
def aic(n, k, sse):
    """Akaike Information Criterion.  Lower is better."""
    return n * np.log(sse / n) + 2 * k

def chi2_reduced(observed, predicted, sigma, n_params):
    chi2 = np.sum(((observed - predicted) / sigma) ** 2)
    return chi2 / (len(observed) - n_params)

# ── Analysis ──────────────────────────────────────────────────────────────────
def analyse_results(labels, job_results, delays_us):
    from collections import defaultdict

    # Parse tomography data
    tomo_data = defaultdict(dict)
    for label, qr in zip(labels, job_results):
        parts = label.split('_')
        delay = float(parts[0].replace('us', ''))
        basis = parts[1]
        try:
            counts = qr.data.meas.get_counts()
        except Exception:
            counts = {}
        tomo_data[delay][basis] = counts_to_probs(counts)

    # Compute S_A at each delay
    t_vals  = []
    SA_vals = []
    for delay in sorted(tomo_data.keys()):
        rho_A = reconstruct_rho_A(tomo_data[delay])
        SA    = von_neumann_entropy_2x2(rho_A)
        t_vals.append(delay)
        SA_vals.append(SA)
        print(f"  t={delay:6.0f} us   S_A={SA:.4f} nats  "
              f"(alpha_screen={SA/np.log(2):.4f})")

    t_arr  = np.array(t_vals,  dtype=float)
    SA_arr = np.array(SA_vals, dtype=float)
    sigma  = np.full_like(SA_arr, 0.02)   # ~2% shot noise estimate

    # ── Fit Model A: Theorem 1 ───────────────────────────────────────────────
    print("\n-- Fitting Model A (Theorem 1: h2 shape) --")
    try:
        popt_A, pcov_A = curve_fit(model_theorem1, t_arr, SA_arr,
                                   p0=[200.0], bounds=([10.0], [2000.0]))
        T1_fit = popt_A[0]
        SA_pred_A = model_theorem1(t_arr, *popt_A)
        sse_A  = np.sum((SA_arr - SA_pred_A)**2)
        chi2_A = chi2_reduced(SA_arr, SA_pred_A, sigma, n_params=1)
        aic_A  = aic(len(t_arr), 1, sse_A)
        print(f"  T1_fit = {T1_fit:.1f} us   chi2_red = {chi2_A:.3f}   AIC = {aic_A:.2f}")
    except Exception as e:
        print(f"  Fit failed: {e}")
        T1_fit, sse_A, chi2_A, aic_A = None, np.inf, np.inf, np.inf
        SA_pred_A = np.full_like(SA_arr, np.nan)

    # ── Fit Model B: Heuristic exponential ───────────────────────────────────
    print("\n-- Fitting Model B (Heuristic: exponential) --")
    try:
        popt_B, pcov_B = curve_fit(model_heuristic_2param, t_arr, SA_arr,
                                   p0=[np.log(2), 0.005],
                                   bounds=([0, 1e-6], [2.0, 1.0]))
        A_fit, Gamma_fit = popt_B
        SA_pred_B = model_heuristic_2param(t_arr, *popt_B)
        sse_B  = np.sum((SA_arr - SA_pred_B)**2)
        chi2_B = chi2_reduced(SA_arr, SA_pred_B, sigma, n_params=2)
        aic_B  = aic(len(t_arr), 2, sse_B)
        print(f"  A={A_fit:.4f}, 1/Gamma={1/Gamma_fit:.1f} us   "
              f"chi2_red = {chi2_B:.3f}   AIC = {aic_B:.2f}")
    except Exception as e:
        print(f"  Fit failed: {e}")
        Gamma_fit, sse_B, chi2_B, aic_B = None, np.inf, np.inf, np.inf
        SA_pred_B = np.full_like(SA_arr, np.nan)

    # ── Verdict ───────────────────────────────────────────────────────────────
    delta_aic = aic_A - aic_B   # negative = Model A is better
    print("\n" + "="*60)
    print("FC-2 FUNCTIONAL FORM VERDICT")
    print("="*60)
    print(f"  Delta-AIC (A-B) = {delta_aic:.2f}")
    print(f"  (negative = Theorem 1 h2-shape fits better)")
    if delta_aic < -5:
        verdict = "THEOREM 1 CONFIRMED: h2 shape preferred (ΔAIC={:.1f})".format(delta_aic)
    elif delta_aic > 5:
        verdict = "THEOREM 1 CHALLENGED: exponential preferred (ΔAIC={:.1f})".format(delta_aic)
    else:
        verdict = "AMBIGUOUS: models indistinguishable at this noise level"
    print(f"  VERDICT: {verdict}")
    print("="*60)

    return dict(t_vals=t_vals, SA_vals=SA_vals,
                T1_fit=T1_fit, Gamma_fit=float(Gamma_fit) if Gamma_fit else None,
                chi2_A=float(chi2_A), chi2_B=float(chi2_B),
                aic_A=float(aic_A), aic_B=float(aic_B),
                delta_aic=float(delta_aic), verdict=verdict)

# ── Argument parsing ──────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="FC-2 T1 Functional Form Test")
    p.add_argument('--token',   default=os.environ.get('IBM_QUANTUM_TOKEN',''))
    p.add_argument('--backend', default='ibm_brisbane')
    p.add_argument('--instance', default='ibm-q/open/main')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--results-file', default=None,
                   help='Reuse existing JSON results from FC-1 (skips hardware)')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args      = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("="*60)
    print("FC-2: T1 Functional Form Test  (Paper 1, Section FC-2)")
    print(f"Timestamp: {timestamp}")
    print("="*60)

    labels, circuits = build_circuits(DELAY_US)

    if args.dry_run:
        print(f"\n[DRY RUN] {len(circuits)} circuits, {len(circuits)*SHOTS:,} shots.")
        print("Pass --token to submit to hardware.")
        return

    if not args.token:
        print("ERROR: No IBM token.")
        sys.exit(1)

    print(f"\n[1/4] Connecting to {args.backend}...")
    service = QiskitRuntimeService(channel='ibm_quantum',
                                   token=args.token,
                                   instance=args.instance)
    backend = service.backend(args.backend)

    print(f"[2/4] Transpiling {len(circuits)} circuits...")
    transpiled = transpile(circuits, backend=backend,
                           optimization_level=1, initial_layout=[0, 1])

    print(f"[3/4] Submitting ({SHOTS} shots/circuit)...")
    with Session(backend=backend) as session:
        sampler = SamplerV2(session=session)
        job     = sampler.run(transpiled, shots=SHOTS)
        print(f"      Job ID: {job.job_id()}")
        result  = job.result()

    print("[4/4] Analysing...")
    results = analyse_results(labels, result, DELAY_US)

    outfile = f"fc2_results_{timestamp}.json"
    with open(outfile, 'w') as f:
        json.dump({'job_id': job.job_id(), 'backend': args.backend,
                   'timestamp': timestamp, 'results': results}, f, indent=2)
    print(f"\nResults saved to {outfile}")

if __name__ == '__main__':
    main()
