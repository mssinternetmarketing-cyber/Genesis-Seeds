"""
FC-2: T1 Functional Form Test  --  AWS Braket / IonQ
=============================================================
Tests whether S_A decays as h2(exp(-t/2T1)) [Theorem 1] or
as exp(-Gamma*t) [prior heuristic].

The two models diverge sharply at depth > ~6 gate pairs.
Model discrimination uses AIC (Akaike Information Criterion).

CIRCUIT COUNT:  8 depths × 3 bases = 24 circuits
SHOTS:          256 per circuit  (~6,144 total)
RUNTIME:        ~60-80 s on IonQ Aria; instant on local sim

COST ESTIMATE (AWS Braket):
    IonQ Aria:    ~$9 task + $0.00145/shot × 6144  ≈  $18
    Local sim:    FREE

USAGE:
    python3 braket_fc2_t1_functional_form.py --device local
    python3 braket_fc2_t1_functional_form.py --device aria
    python3 braket_fc2_t1_functional_form.py --device harmony
=============================================================
"""

import os, sys, json, argparse, numpy as np
from datetime import datetime
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from scipy.optimize import curve_fit

# ── Device ARNs ──────────────────────────────────────────────────────────────
DEVICES = {
    'local'    : None,
    'ionq-sim' : 'arn:aws:braket:us-east-1::device/qpu/ionq/ionQdevice',
    'harmony'  : 'arn:aws:braket:us-east-1::device/qpu/ionq/Harmony',
    'aria'     : 'arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1',
    'rigetti'  : 'arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3',
}

# ── Config ───────────────────────────────────────────────────────────────────
SHOTS       = 256
# 8 depths spanning the discriminating regime (depth > ~6 is where models diverge)
IDLE_DEPTHS = [0, 2, 4, 8, 14, 22, 34, 52]
BASES       = ['ZZ', 'XZ', 'YZ']

# ── Circuit helpers ───────────────────────────────────────────────────────────
def bell() -> Circuit:
    return Circuit().h(0).cnot(0, 1)

def add_idle(circ: Circuit, qubit: int, depth: int) -> None:
    for _ in range(depth):
        circ.x(qubit)
        circ.x(qubit)

def add_basis(circ: Circuit, basis: str) -> None:
    for qubit, b in enumerate(basis):
        if b == 'X':
            circ.h(qubit)
        elif b == 'Y':
            circ.si(qubit)
            circ.h(qubit)

def build_circuits():
    labels, circuits = [], []
    for depth in IDLE_DEPTHS:
        for basis in BASES:
            circ = bell()
            if depth > 0:
                add_idle(circ, 0, depth)
                add_idle(circ, 1, depth)
            add_basis(circ, basis)
            labels.append(f"d{depth}_{basis}")
            circuits.append(circ)
    n = len(circuits)
    print(f"[FC-2] Built {n} circuits  "
          f"({len(IDLE_DEPTHS)} depths × {len(BASES)} bases)")
    print(f"       {n * SHOTS:,} total shots")
    return labels, circuits

# ── Bloch entropy helpers ─────────────────────────────────────────────────────
def bloch_ev(counts: dict, qubit: int) -> float:
    total = max(sum(counts.values()), 1)
    ev = 0.0
    for bits, n in counts.items():
        bits = bits.zfill(2)
        s = +1 if bits[qubit] == '0' else -1
        ev += s * n / total
    return ev

def entropy_bloch(rx, ry, rz) -> float:
    r  = float(np.clip(np.sqrt(rx**2 + ry**2 + rz**2), 0.0, 1.0))
    lp = np.clip((1 + r) / 2, 1e-15, 1 - 1e-15)
    lm = np.clip((1 - r) / 2, 1e-15, 1 - 1e-15)
    return float(-lp * np.log(lp) - lm * np.log(lm))

# ── Model functions for curve fitting ────────────────────────────────────────
def model_theorem1(t_arr, T1_gates):
    """
    Theorem 1: S_A(t) = h2(exp(-t / (2 * T1_gates)))
    t_arr: array of effective times in gate units (depth * 2 gates)
    T1_gates: T1 in units of single-qubit gate times (fitted parameter)
    """
    results = []
    for t in t_arr:
        lam = np.clip(0.5 * np.exp(-t / (2 * T1_gates)), 1e-15, 1 - 1e-15)
        h2  = -lam * np.log(lam) - (1 - lam) * np.log(1 - lam)
        results.append(h2)
    return np.array(results)

def model_heuristic(t_arr, A, Gamma):
    """
    Prior heuristic: S_A(t) = A * exp(-Gamma * t)
    Two free parameters: amplitude A and decay rate Gamma.
    """
    return A * np.exp(-np.array(t_arr) * Gamma)

def aic(n, k, sse):
    """Akaike Information Criterion. Lower = better fit."""
    if sse <= 0 or n <= k:
        return np.inf
    return n * np.log(sse / n) + 2 * k

# ── Analysis ──────────────────────────────────────────────────────────────────
def analyse(labels, all_counts):
    from collections import defaultdict
    data = defaultdict(dict)

    for label, counts in zip(labels, all_counts):
        d_str, basis = label.split('_')
        depth = int(d_str[1:])
        data[depth][basis] = counts

    # Extract S_A at each depth
    t_vals, SA_vals = [], []
    print("\n-- Raw S_A measurements --")
    for depth in sorted(data.keys()):
        d = data[depth]
        rx = bloch_ev(d.get('XZ', {}), 0)
        ry = bloch_ev(d.get('YZ', {}), 0)
        rz = bloch_ev(d.get('ZZ', {}), 0)
        SA = entropy_bloch(rx, ry, rz)
        t_eff = depth * 2   # effective gate count
        t_vals.append(float(t_eff))
        SA_vals.append(SA)
        print(f"  depth={depth:>3}  t_eff={t_eff:>4}  "
              f"S_A={SA:.4f} nats  alpha={SA/np.log(2):.4f}")

    t_arr  = np.array(t_vals)
    SA_arr = np.array(SA_vals)
    sigma  = np.full_like(SA_arr, max(0.02, SA_arr[0] * 0.03))

    # ── Fit Model A: Theorem 1 ───────────────────────────────────────────────
    print("\n-- Fitting Model A  (Theorem 1: h2 shape) --")
    try:
        popt_A, _ = curve_fit(model_theorem1, t_arr, SA_arr,
                               p0=[500.0], bounds=([10.0], [1e6]))
        T1_fit    = popt_A[0]
        pred_A    = model_theorem1(t_arr, T1_fit)
        sse_A     = float(np.sum((SA_arr - pred_A)**2))
        aic_A     = aic(len(t_arr), 1, sse_A)
        chi2_A    = sse_A / (len(t_arr) - 1)
        print(f"  T1_fit = {T1_fit:.1f} gate-times")
        print(f"  SSE = {sse_A:.6f}    AIC = {aic_A:.3f}")
    except Exception as e:
        print(f"  Fit failed: {e}")
        T1_fit, sse_A, aic_A, chi2_A = None, np.inf, np.inf, np.inf

    # ── Fit Model B: Heuristic exponential ───────────────────────────────────
    print("\n-- Fitting Model B  (Heuristic: exponential) --")
    try:
        popt_B, _ = curve_fit(model_heuristic, t_arr, SA_arr,
                               p0=[np.log(2), 1/500.0],
                               bounds=([0.0, 1e-8], [2.0, 1.0]))
        A_fit, Gamma_fit = popt_B
        pred_B = model_heuristic(t_arr, A_fit, Gamma_fit)
        sse_B  = float(np.sum((SA_arr - pred_B)**2))
        aic_B  = aic(len(t_arr), 2, sse_B)
        print(f"  A = {A_fit:.4f}  1/Gamma = {1/Gamma_fit:.1f} gate-times")
        print(f"  SSE = {sse_B:.6f}    AIC = {aic_B:.3f}")
    except Exception as e:
        print(f"  Fit failed: {e}")
        A_fit = Gamma_fit = None
        sse_B, aic_B = np.inf, np.inf

    # ── Comparison table ─────────────────────────────────────────────────────
    print("\n-- Point-by-point comparison --")
    print(f"{'Depth':>6} | {'S_A meas':>9} | {'Thm1 pred':>10} | "
          f"{'Heur pred':>10} | {'Thm1 err%':>10} | {'Heur err%':>10}")
    print("-"*68)
    for i, depth in enumerate(sorted(data.keys())):
        t_eff  = depth * 2
        sa_m   = SA_vals[i]
        sa_A   = float(model_theorem1(np.array([t_eff]), T1_fit)[0]) if T1_fit else float('nan')
        sa_B   = float(model_heuristic(np.array([t_eff]), A_fit, Gamma_fit)[0]) \
                 if Gamma_fit else float('nan')
        err_A  = abs(sa_m - sa_A) / max(sa_m, 1e-6) * 100 if T1_fit else float('nan')
        err_B  = abs(sa_m - sa_B) / max(sa_m, 1e-6) * 100 if Gamma_fit else float('nan')
        print(f"d={depth:>4} | {sa_m:>9.4f} | {sa_A:>10.4f} | "
              f"{sa_B:>10.4f} | {err_A:>9.1f}% | {err_B:>9.1f}%")

    # ── Verdict ───────────────────────────────────────────────────────────────
    delta_aic = aic_A - aic_B
    print("\n" + "="*68)
    print("FC-2  FUNCTIONAL FORM VERDICT")
    print("="*68)
    print(f"  AIC (Model A, Theorem 1):   {aic_A:.3f}")
    print(f"  AIC (Model B, Heuristic):   {aic_B:.3f}")
    print(f"  Delta-AIC (A - B):          {delta_aic:.3f}")
    print(f"  (negative = Theorem 1 h2-shape fits better)")
    print()
    if delta_aic < -5:
        verdict = f"THEOREM 1 CONFIRMED: h2 shape preferred  (ΔAIC={delta_aic:.1f})"
    elif delta_aic > 5:
        verdict = f"THEOREM 1 CHALLENGED: exponential preferred  (ΔAIC={delta_aic:.1f})"
    else:
        verdict = f"AMBIGUOUS: models indistinguishable at this noise level"
    print(f"  VERDICT: {verdict}")
    print("="*68)

    return dict(
        t_vals=t_vals, SA_vals=SA_vals,
        T1_fit_gates=float(T1_fit) if T1_fit else None,
        Gamma_fit=float(Gamma_fit) if Gamma_fit else None,
        sse_A=float(sse_A), sse_B=float(sse_B),
        aic_A=float(aic_A), aic_B=float(aic_B),
        delta_aic=float(delta_aic),
        verdict=verdict
    )

# ── Device runner ─────────────────────────────────────────────────────────────
def get_device(name):
    if name == 'local':
        return LocalSimulator(), 'local'
    from braket.aws import AwsDevice
    arn = DEVICES.get(name)
    if not arn:
        print(f"Unknown device '{name}'.  Choices: {list(DEVICES.keys())}")
        sys.exit(1)
    return AwsDevice(arn), arn

def run_all(device, device_name, circuits):
    all_counts = []
    print(f"  Submitting {len(circuits)} circuits to {device_name}...")
    tasks = [device.run(circ, shots=SHOTS) for circ in circuits]
    for i, task in enumerate(tasks):
        result = task.result()
        all_counts.append(dict(result.measurement_counts))
        if (i + 1) % 4 == 0:
            print(f"  ... {i+1}/{len(tasks)} done")
    return all_counts

# ── Argument parsing ──────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="FC-2 T1 Functional Form Test -- Braket/IonQ")
    p.add_argument('--device', default='local',
                   choices=list(DEVICES.keys()))
    p.add_argument('--dry-run', action='store_true')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("="*68)
    print("FC-2: T1 Functional Form Test  (Paper 1, Section FC-2)")
    print(f"Device: {args.device}   Started: {ts}")
    print("="*68)

    labels, circuits = build_circuits()

    if args.dry_run:
        print("\n[DRY RUN] d0_ZZ (baseline Bell):")
        print(circuits[0])
        print("\n[DRY RUN] d14_ZZ (deep idle):")
        for lbl, c in zip(labels, circuits):
            if lbl == 'd14_ZZ':
                print(c); break
        return

    device, device_name = get_device(args.device)
    all_counts = run_all(device, device_name, circuits)
    results    = analyse(labels, all_counts)

    outfile = f"braket_fc2_results_{ts}.json"
    with open(outfile, 'w') as f:
        json.dump({'device': args.device, 'timestamp': ts,
                   'shots': SHOTS, 'idle_depths': IDLE_DEPTHS,
                   'results': results}, f, indent=2)
    print(f"\nSaved to {outfile}")

if __name__ == '__main__':
    main()
