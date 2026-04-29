"""
EMERGENCY FAST TEST  --  AWS Braket / IonQ
=============================================================
Minimum viable Theorem 1 check.  Runs in ~90 seconds on IonQ
hardware, instantly on the local simulator.

WHAT IT TESTS:
    Prepare Bell state |Phi+>.  Let it decohere for N gate-pairs
    of idle time (bare) vs XY-4 dynamical decoupling.
    Measure S_A via 3-basis Bloch tomography on qubit 0.

    Theorem 1 predicts:  S_A^bare ≈ S_A^XY4   (< 5% difference)
    Heuristic predicts:  S_A^XY4  >> S_A^bare  (> 20% difference)

COST ESTIMATE (IonQ hardware via Braket):
    IonQ Harmony:  ~$0.01/shot  x  6144 shots  ≈  $61
    IonQ Aria:     ~$0.03/task  +  $0.00145/shot ≈  $9 + task fees
    Local sim:     FREE  (use --device local for zero cost)

USAGE:
    # Free local simulator (test your setup first):
    python3 braket_emergency_fast_test.py --device local

    # IonQ Harmony via AWS Braket (cheapest real hardware):
    python3 braket_emergency_fast_test.py --device harmony

    # IonQ Aria via AWS Braket (highest fidelity):
    python3 braket_emergency_fast_test.py --device aria

    # IonQ cloud simulator (no hardware noise, cheap):
    python3 braket_emergency_fast_test.py --device ionq-sim

REQUIREMENTS:
    pip install amazon-braket-sdk scipy numpy
    AWS credentials configured (~/.aws/credentials)
=============================================================
"""

import os, sys, json, argparse, numpy as np
from datetime import datetime
from braket.circuits import Circuit
from braket.devices import LocalSimulator

# ── Device ARNs ──────────────────────────────────────────────────────────────
DEVICES = {
    'local'    : None,   # Braket local simulator, free
    'ionq-sim' : 'arn:aws:braket:us-east-1::device/qpu/ionq/ionQdevice',
    'harmony'  : 'arn:aws:braket:us-east-1::device/qpu/ionq/Harmony',
    'aria'     : 'arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1',
    'rigetti'  : 'arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3',
}

# ── Config ───────────────────────────────────────────────────────────────────
SHOTS       = 256
# Idle depth levels: number of XX identity gate-pairs inserted as idle proxy.
# Each pair ≈ 2× single-qubit gate time of decoherence.
# IonQ Aria 1Q gate time ~135 us, so depth-10 ≈ 2.7 ms idle equivalent.
IDLE_DEPTHS = [0, 2, 6, 14]
CONDITIONS  = ['bare', 'xy4']
BASES       = ['ZZ', 'XZ', 'YZ']   # minimum for qubit-0 Bloch vector

# ── Circuit helpers ───────────────────────────────────────────────────────────
def bell() -> Circuit:
    """Bell state |Phi+> = (|00> + |11>) / sqrt(2)."""
    return Circuit().h(0).cnot(0, 1)

def add_idle(circ: Circuit, qubit: int, depth: int) -> Circuit:
    """
    Approximate idle decoherence by inserting `depth` pairs of X gates
    (X·X = I) on the specified qubit.  Each pair contributes ~2× gate-time
    worth of amplitude damping without changing the logical state.
    """
    for _ in range(depth):
        circ.x(qubit)
        circ.x(qubit)
    return circ

def add_xy4(circ: Circuit, qubit: int, depth: int) -> Circuit:
    """
    XY-4 dynamical decoupling sequence on one qubit.
    XY-4 pattern: X Y X Y  (interleaved with idle XX pairs).
    This suppresses dephasing while leaving amplitude damping unchanged.
    Total gate count matches the bare idle sequence for fair comparison.
    """
    # Each XY-4 cycle: X, idle, Y, idle, X, idle, Y, idle
    # We approximate with: X (idle_pair) Y (idle_pair) repeated
    cycles = max(1, depth // 2)
    for _ in range(cycles):
        circ.x(qubit)
        circ.y(qubit)
    # Pad to same total gate count as bare (depth * 2 gates)
    padding = depth * 2 - cycles * 2
    for _ in range(padding // 2):
        circ.x(qubit)
        circ.x(qubit)
    return circ

def add_basis_rotation(circ: Circuit, basis: str) -> Circuit:
    """
    Rotate into measurement basis before implicit Braket measurement.
    X basis: H gate.  Y basis: S_dag then H.  Z basis: nothing.
    """
    for qubit, b in enumerate(basis):
        if b == 'X':
            circ.h(qubit)
        elif b == 'Y':
            circ.si(qubit)   # S†
            circ.h(qubit)
        # Z: no rotation needed
    return circ

# ── Build all circuits ────────────────────────────────────────────────────────
def build_circuits():
    labels, circuits = [], []
    for depth in IDLE_DEPTHS:
        for cond in CONDITIONS:
            for basis in BASES:
                circ = bell()
                if depth > 0:
                    if cond == 'bare':
                        add_idle(circ, 0, depth)
                        add_idle(circ, 1, depth)
                    else:  # xy4
                        add_xy4(circ, 0, depth)
                        add_xy4(circ, 1, depth)
                add_basis_rotation(circ, basis)
                label = f"{cond}_d{depth}_{basis}"
                labels.append(label)
                circuits.append(circ)

    total_shots = len(circuits) * SHOTS
    print(f"[EMERGENCY] Built {len(circuits)} circuits "
          f"({len(IDLE_DEPTHS)} depths × {len(CONDITIONS)} cond × {len(BASES)} bases)")
    print(f"            {total_shots:,} total shots  "
          f"({len(circuits)} circuits × {SHOTS} shots)")
    return labels, circuits

# ── Entropy from Bloch vector ────────────────────────────────────────────────
def bloch_ev(counts: dict, qubit: int) -> float:
    """
    Expectation value of Z on `qubit` from 2-qubit measurement counts.
    Braket bit order: bits[0] = qubit 0, bits[1] = qubit 1.
    """
    total = sum(counts.values())
    ev = 0.0
    for bits, n in counts.items():
        if len(bits) < 2:
            bits = bits.zfill(2)
        s = +1 if bits[qubit] == '0' else -1
        ev += s * n / total
    return ev

def entropy_from_bloch(rx: float, ry: float, rz: float) -> float:
    """Von Neumann entropy of a single qubit given its Bloch vector."""
    r  = float(np.clip(np.sqrt(rx**2 + ry**2 + rz**2), 0.0, 1.0))
    lp = np.clip((1 + r) / 2, 1e-15, 1 - 1e-15)
    lm = np.clip((1 - r) / 2, 1e-15, 1 - 1e-15)
    return float(-lp * np.log(lp) - lm * np.log(lm))

# ── Theoretical predictions ──────────────────────────────────────────────────
def alpha_theorem1(depth: int, T1_gates: float = 500.0) -> float:
    """
    Theorem 1 prediction for alpha_screen at a given idle depth.
    T1_gates: T1 expressed in units of single-qubit gate times.
    IonQ Aria: T1 ~ 10,000 ms / 0.135 ms per gate ≈ 74,000 gate times.
    Default T1_gates=500 is conservative for testing.
    """
    t_norm = depth * 2 / T1_gates   # depth pairs × 2 gates / T1 in gates
    lam    = np.clip(0.5 * np.exp(-t_norm / 2), 1e-15, 1 - 1e-15)
    h2     = -lam * np.log(lam) - (1 - lam) * np.log(1 - lam)
    return float(h2 / np.log(2))

def alpha_heuristic(depth: int, T1_gates: float = 500.0,
                    Tphi_gates: float = 250.0) -> float:
    """Prior heuristic: both T1 and T_phi contribute. Theorem 1 says wrong."""
    t = depth * 2
    return float(np.exp(-0.5 * (1/T1_gates + 1/Tphi_gates) * t))

# ── Analysis ─────────────────────────────────────────────────────────────────
def analyse(labels, all_counts):
    from collections import defaultdict
    data = defaultdict(dict)   # (cond, depth) -> basis -> counts

    for label, counts in zip(labels, all_counts):
        parts = label.split('_')
        cond  = parts[0]
        depth = int(parts[1][1:])   # strip 'd' prefix
        basis = parts[2]
        data[(cond, depth)][basis] = counts

    print("\n" + "="*70)
    print("EMERGENCY TEST RESULTS")
    print(f"{'Depth':>7} | {'S_A bare':>9} | {'S_A XY-4':>9} | "
          f"{'Δ%':>6} | {'Thm1 α':>8} | {'Heur α':>8} | Verdict")
    print("-"*70)

    results = {}
    for depth in IDLE_DEPTHS:
        bare = data.get(('bare', depth), {})
        xy4  = data.get(('xy4',  depth), {})
        if not bare or not xy4:
            continue

        def get_SA(d):
            rx = bloch_ev(d.get('XZ', {}), qubit=0)
            ry = bloch_ev(d.get('YZ', {}), qubit=0)
            rz = bloch_ev(d.get('ZZ', {}), qubit=0)
            return entropy_from_bloch(rx, ry, rz)

        SA_b  = get_SA(bare)
        SA_x  = get_SA(xy4)
        dpct  = abs(SA_x - SA_b) / max(SA_b, 1e-6) * 100
        a_th  = alpha_theorem1(depth)
        a_hr  = alpha_heuristic(depth)

        verdict = ("✓ Thm1"  if dpct <  5 else
                   "✗ FAIL"  if dpct > 20 else "?")

        print(f"d={depth:>4}  | {SA_b:>9.4f} | {SA_x:>9.4f} | "
              f"{dpct:>5.1f}% | {a_th:>8.4f} | {a_hr:>8.4f} | {verdict}")
        results[str(depth)] = dict(SA_bare=SA_b, SA_xy4=SA_x,
                                   delta_pct=dpct, alpha_thm1=a_th,
                                   alpha_heuristic=a_hr)

    all_deltas = [v['delta_pct'] for v in results.values()]
    max_d = max(all_deltas) if all_deltas else 0.0
    print("\n" + "="*70)
    if max_d < 5:
        print(f"THEOREM 1:  LIKELY CONFIRMED  (max Δ = {max_d:.1f}%  < 5% threshold)")
    elif max_d > 20:
        print(f"THEOREM 1:  LIKELY FALSIFIED  (max Δ = {max_d:.1f}%  > 20% threshold)")
    else:
        print(f"AMBIGUOUS   (max Δ = {max_d:.1f}%)  -- run FC-1 with more shots")
    print("="*70)
    return results

# ── Runner ───────────────────────────────────────────────────────────────────
def get_device(name: str):
    if name == 'local':
        return LocalSimulator(), 'local'
    from braket.aws import AwsDevice
    arn = DEVICES.get(name)
    if not arn:
        print(f"Unknown device '{name}'. Choices: {list(DEVICES.keys())}")
        sys.exit(1)
    return AwsDevice(arn), arn

def run_circuits(device, device_name, circuits):
    all_counts = []
    if device_name == 'local':
        # Local: run sequentially (fast)
        for i, circ in enumerate(circuits):
            result = device.run(circ, shots=SHOTS).result()
            all_counts.append(dict(result.measurement_counts))
            if (i + 1) % 6 == 0:
                print(f"  ... {i+1}/{len(circuits)} circuits done")
    else:
        # Hardware: batch submit for efficiency
        from braket.aws import AwsQuantumTaskBatch
        print(f"  Submitting batch of {len(circuits)} circuits...")
        tasks = [device.run(circ, shots=SHOTS) for circ in circuits]
        print(f"  Waiting for {len(tasks)} tasks to complete...")
        for i, task in enumerate(tasks):
            result = task.result()
            all_counts.append(dict(result.measurement_counts))
            if (i + 1) % 6 == 0:
                print(f"  ... {i+1}/{len(tasks)} tasks done")
    return all_counts

# ── Argument parsing ──────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="Emergency Fast Test -- Braket/IonQ version")
    p.add_argument('--device', default='local',
                   choices=list(DEVICES.keys()),
                   help='Device to run on (default: local simulator)')
    p.add_argument('--dry-run', action='store_true',
                   help='Print circuits only, do not run')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("="*70)
    print("EMERGENCY FAST TEST  --  Braket/IonQ  (Theorem 1 minimal viable)")
    print(f"Device: {args.device}   Started: {ts}")
    print("="*70)

    labels, circuits = build_circuits()

    if args.dry_run:
        print("\n[DRY RUN] First circuit (bare_d0_ZZ):")
        print(circuits[0])
        print(f"\n[DRY RUN] XY-4 circuit (xy4_d6_XZ):")
        # Find first xy4_d6 circuit
        for lbl, c in zip(labels, circuits):
            if lbl.startswith('xy4_d6'):
                print(c)
                break
        print(f"\nTotal: {len(circuits)} circuits × {SHOTS} shots")
        return

    device, device_name = get_device(args.device)
    print(f"\nConnected to: {args.device}")
    print(f"Running {len(circuits)} circuits × {SHOTS} shots...\n")

    all_counts = run_circuits(device, device_name, circuits)
    results    = analyse(labels, all_counts)

    outfile = f"braket_emergency_results_{ts}.json"
    with open(outfile, 'w') as f:
        json.dump({'device': args.device, 'timestamp': ts,
                   'shots': SHOTS, 'results': results}, f, indent=2)
    print(f"\nResults saved to {outfile}")

if __name__ == '__main__':
    main()
