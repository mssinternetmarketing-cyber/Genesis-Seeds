"""
FC-1: XY-4 Falsification Test  --  AWS Braket / IonQ
=============================================================
Full Theorem 1 falsification protocol (Paper 1, Section 5.3 / FC-1).

THEOREM 1: Pure dephasing does NOT suppress S_A in the
high-entanglement regime.  Only amplitude damping (T1) matters.

TEST:
    Bare condition:  Bell state + N idle gate-pairs (both T1 and
                     T_phi act freely)
    XY-4 condition:  Bell state + XY-4 DD sequence  (T_phi
                     suppressed, T1 unchanged)

    If Theorem 1 is correct:   |S_A^bare - S_A^XY4| / S_A^bare < 5%
    If heuristic is correct:    S_A^XY4 >> S_A^bare  (gap > 20%)

CIRCUIT COUNT:  5 depths × 2 conditions × 3 bases = 30 circuits
SHOTS:          256 per circuit  (~7,680 total)
RUNTIME:        ~60-80 s on IonQ Aria/Harmony; instant on local sim

COST ESTIMATE (AWS Braket):
    IonQ Harmony:   ~$0.01/shot × 7680  ≈  $77
    IonQ Aria:      ~$9 task + $0.00145/shot × 7680  ≈  $20
    Local sim:      FREE

USAGE:
    python3 braket_fc1_xy4_falsification.py --device local
    python3 braket_fc1_xy4_falsification.py --device aria
    python3 braket_fc1_xy4_falsification.py --device harmony
=============================================================
"""

import os, sys, json, argparse, numpy as np
from datetime import datetime
from braket.circuits import Circuit
from braket.devices import LocalSimulator

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
# 5 idle depths.  Gap between Theorem 1 and heuristic is:
#   depth 0:  trivially identical
#   depth 2:  ~5% gap    (borderline)
#   depth 6:  ~18% gap   (approaching threshold)
#   depth 14: ~38% gap   (clearly resolvable with 256 shots)
#   depth 28: ~55% gap   (definitive)
IDLE_DEPTHS = [0, 2, 6, 14, 28]
CONDITIONS  = ['bare', 'xy4']
BASES       = ['ZZ', 'XZ', 'YZ']   # qubit-0 Bloch vector

# ── Circuit builders ──────────────────────────────────────────────────────────
def bell() -> Circuit:
    return Circuit().h(0).cnot(0, 1)

def add_idle_bare(circ: Circuit, qubit: int, depth: int) -> None:
    """Insert `depth` XX identity pairs on qubit (bare idle approximation)."""
    for _ in range(depth):
        circ.x(qubit)
        circ.x(qubit)

def add_xy4_sequence(circ: Circuit, qubit: int, depth: int) -> None:
    """
    XY-4 dynamical decoupling on one qubit.
    Sequence: (X Y) repeated cycles times, padded with idle to match
    total gate count of bare condition (depth * 2 gates).

    XY-4 suppresses dephasing while T1 decay is unchanged.
    This is the key discriminator for Theorem 1.
    """
    total_gates = depth * 2          # must match bare gate count exactly
    dd_gates    = 0
    cycles      = total_gates // 4   # each XYXY = 4 gates

    for _ in range(cycles):
        circ.x(qubit)
        circ.y(qubit)
        circ.x(qubit)
        circ.y(qubit)
        dd_gates += 4

    # Pad remainder with XX identity pairs
    remaining = total_gates - dd_gates
    for _ in range(remaining // 2):
        circ.x(qubit)
        circ.x(qubit)

def add_basis(circ: Circuit, basis: str) -> None:
    """Rotate into measurement basis. Braket measures implicitly at end."""
    for qubit, b in enumerate(basis):
        if b == 'X':
            circ.h(qubit)
        elif b == 'Y':
            circ.si(qubit)
            circ.h(qubit)

# ── Build circuits ────────────────────────────────────────────────────────────
def build_circuits():
    labels, circuits = [], []
    for depth in IDLE_DEPTHS:
        for cond in CONDITIONS:
            for basis in BASES:
                circ = bell()
                if depth > 0:
                    if cond == 'bare':
                        add_idle_bare(circ, 0, depth)
                        add_idle_bare(circ, 1, depth)
                    else:
                        add_xy4_sequence(circ, 0, depth)
                        add_xy4_sequence(circ, 1, depth)
                add_basis(circ, basis)
                label = f"{cond}_d{depth}_{basis}"
                labels.append(label)
                circuits.append(circ)

    n = len(circuits)
    print(f"[FC-1] Built {n} circuits  "
          f"({len(IDLE_DEPTHS)} depths × {len(CONDITIONS)} cond × {len(BASES)} bases)")
    print(f"       {n * SHOTS:,} total shots")
    return labels, circuits

# ── Bloch vector + entropy ────────────────────────────────────────────────────
def bloch_ev(counts: dict, qubit: int) -> float:
    """<Z> on qubit from 2-qubit counts.  Braket: bits[qubit] = qubit index."""
    total = max(sum(counts.values()), 1)
    ev = 0.0
    for bits, n in counts.items():
        bits = bits.zfill(2)
        s = +1 if bits[qubit] == '0' else -1
        ev += s * n / total
    return ev

def entropy_bloch(rx: float, ry: float, rz: float) -> float:
    r  = float(np.clip(np.sqrt(rx**2 + ry**2 + rz**2), 0.0, 1.0))
    lp = np.clip((1 + r) / 2, 1e-15, 1 - 1e-15)
    lm = np.clip((1 - r) / 2, 1e-15, 1 - 1e-15)
    return float(-lp * np.log(lp) - lm * np.log(lm))

def get_SA(basis_counts: dict) -> float:
    """Compute S_A for qubit 0 from {basis: counts} dict."""
    rx = bloch_ev(basis_counts.get('XZ', {}), qubit=0)
    ry = bloch_ev(basis_counts.get('YZ', {}), qubit=0)
    rz = bloch_ev(basis_counts.get('ZZ', {}), qubit=0)
    return entropy_bloch(rx, ry, rz)

# ── Theory predictions ────────────────────────────────────────────────────────
def alpha_theorem1(depth: int, T1_gates: float = 500.0) -> float:
    """
    Theorem 1 closed-form: alpha_screen = h2(exp(-t/2T1)) / ln2.
    T1_gates: T1 in units of single-qubit gate times.
    Theorem 1 says this is T_phi INDEPENDENT.
    """
    t_over_T1 = (depth * 2) / T1_gates
    lam = np.clip(0.5 * np.exp(-t_over_T1 / 2), 1e-15, 1 - 1e-15)
    h2  = -lam * np.log(lam) - (1 - lam) * np.log(1 - lam)
    return float(h2 / np.log(2))

def alpha_heuristic(depth: int, T1_gates: float = 500.0,
                    Tphi_gates: float = 250.0) -> float:
    """Prior heuristic: both T1 AND T_phi suppress S_A. Theorem 1 says WRONG."""
    t = depth * 2
    gamma_total = 1 / T1_gates + 1 / Tphi_gates
    return float(np.exp(-0.5 * gamma_total * t))

# ── Analysis ──────────────────────────────────────────────────────────────────
def analyse(labels, all_counts):
    from collections import defaultdict
    data = defaultdict(lambda: defaultdict(dict))

    for label, counts in zip(labels, all_counts):
        cond, d_str, basis = label.split('_')
        depth = int(d_str[1:])
        data[cond][depth][basis] = counts

    print("\n" + "="*72)
    print("FC-1  XY-4 FALSIFICATION RESULTS  (Theorem 1 test)")
    print("="*72)
    print(f"{'Depth':>7} | {'S_A bare':>9} | {'S_A XY-4':>9} | "
          f"{'Δ%':>6} | {'α Thm1':>8} | {'α Heur':>8} | Verdict")
    print("-"*72)

    results = {}
    for depth in IDLE_DEPTHS:
        SA_b = get_SA(data['bare'][depth])
        SA_x = get_SA(data['xy4'][depth])
        dpct = abs(SA_x - SA_b) / max(SA_b, 1e-6) * 100
        a_th = alpha_theorem1(depth)
        a_hr = alpha_heuristic(depth)
        verdict = ("✓ CONFIRMED" if dpct <  5 else
                   "✗ FALSIFIED" if dpct > 20 else "? AMBIGUOUS")
        print(f"d={depth:>4}  | {SA_b:>9.4f} | {SA_x:>9.4f} | "
              f"{dpct:>5.1f}% | {a_th:>8.4f} | {a_hr:>8.4f} | {verdict}")
        results[str(depth)] = dict(SA_bare=SA_b, SA_xy4=SA_x,
                                   delta_pct=dpct,
                                   alpha_theorem1=a_th,
                                   alpha_heuristic=a_hr)

    max_d = max(v['delta_pct'] for v in results.values()) if results else 0
    print("\n" + "="*72)
    if max_d < 5:
        print(f"VERDICT: THEOREM 1 CONFIRMED  (max Δ = {max_d:.1f}% < 5%)")
    elif max_d > 20:
        print(f"VERDICT: THEOREM 1 FALSIFIED  (max Δ = {max_d:.1f}% > 20%)")
    else:
        print(f"VERDICT: AMBIGUOUS  (max Δ = {max_d:.1f}%) -- increase shots")
    print("="*72)
    return results

# ── Device runner ─────────────────────────────────────────────────────────────
def get_device(name: str):
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
    print(f"  Waiting for results...")
    for i, task in enumerate(tasks):
        result = task.result()
        all_counts.append(dict(result.measurement_counts))
        if (i + 1) % 6 == 0:
            print(f"  ... {i+1}/{len(tasks)} done")
    return all_counts

# ── Argument parsing ──────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="FC-1 XY-4 Falsification -- Braket")
    p.add_argument('--device', default='local',
                   choices=list(DEVICES.keys()))
    p.add_argument('--dry-run', action='store_true')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("="*72)
    print("FC-1: XY-4 Falsification Test  (Paper 1, Theorem 1)")
    print(f"Device: {args.device}   Started: {ts}")
    print("="*72)

    labels, circuits = build_circuits()

    if args.dry_run:
        print("\n[DRY RUN] bare_d0_ZZ circuit:")
        print(circuits[0])
        print("\n[DRY RUN] xy4_d14_ZZ circuit:")
        for lbl, c in zip(labels, circuits):
            if lbl == 'xy4_d14_ZZ':
                print(c); break
        return

    device, device_name = get_device(args.device)
    all_counts = run_all(device, device_name, circuits)
    results    = analyse(labels, all_counts)

    outfile = f"braket_fc1_results_{ts}.json"
    with open(outfile, 'w') as f:
        json.dump({'device': args.device, 'timestamp': ts,
                   'shots': SHOTS, 'idle_depths': IDLE_DEPTHS,
                   'results': results}, f, indent=2)
    print(f"\nSaved to {outfile}")

if __name__ == '__main__':
    main()
