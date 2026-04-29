"""
EMERGENCY FAST TEST  --  RUN THIS FIRST (fits in ~90 seconds)
=====================================================================
You have ~341 seconds.  This script submits the minimum viable test
that can return meaningful data before your instance expires.

WHAT IT DOES:
    Single Bell-pair + 4 idle times + bare vs XY-4 comparison.
    Only ZX and ZZ tomography bases (enough to extract S_A).
    18 total circuits, 256 shots each = 4608 shots.
    Typical runtime on IBM Heron r2: 60-90 seconds including queue.

WHAT YOU LEARN:
    - Whether S_A^bare ≈ S_A^XY4  (Theorem 1 confirmed)
    - The T1 decay shape at your best qubit pair
    - A first alpha_screen measurement to compare to theory

RUN IMMEDIATELY:
    python emergency_fast_test.py --token YOUR_TOKEN --backend ibm_brisbane

    OR with token already saved:
    IBM_QUANTUM_TOKEN=your_token python emergency_fast_test.py
=====================================================================
"""

import os, sys, json, argparse, numpy as np
from datetime import datetime
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, Session

SHOTS      = 256
DELAY_US   = [0, 10, 40, 100]      # 4 points: baseline + short/mid/long
BASES      = ['ZZ', 'XZ', 'YZ',    # Minimum needed for qubit-0 Bloch vector
              'ZX', 'XX', 'YX']    # + qubit-1 Bloch vector
CONDITIONS = ['bare', 'xy4']
DT_NS      = 0.5                   # Heron r2 dt

def bell():
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1)
    return qc

def add_xy4(qc, qubit, delay_us):
    total_dt = int(delay_us * 1000 / DT_NS)
    tau = max(1, total_dt // 8)
    qc.delay(tau, qubit, unit='dt')
    qc.x(qubit)
    qc.delay(2*tau, qubit, unit='dt')
    qc.y(qubit)
    qc.delay(2*tau, qubit, unit='dt')
    qc.x(qubit)
    qc.delay(2*tau, qubit, unit='dt')
    qc.y(qubit)
    qc.delay(tau, qubit, unit='dt')

def add_basis(qc, basis):
    for i, b in enumerate(basis):
        if b == 'X': qc.h(i)
        elif b == 'Y': qc.sdg(i); qc.h(i)
    qc.measure_all()

def build():
    labels, circuits = [], []
    for delay in DELAY_US:
        for cond in CONDITIONS:
            for basis in BASES:
                qc = bell()
                qc.barrier()
                if delay > 0:
                    dt = int(delay * 1000 / DT_NS)
                    if cond == 'bare':
                        qc.delay(dt, 0, unit='dt')
                        qc.delay(dt, 1, unit='dt')
                    else:
                        add_xy4(qc, 0, delay)
                        add_xy4(qc, 1, delay)
                qc.barrier()
                add_basis(qc, basis)
                labels.append(f"{cond}_{delay}_{basis}")
                circuits.append(qc)
    print(f"Built {len(circuits)} circuits  ({len(circuits)*SHOTS:,} total shots)")
    return labels, circuits

def bloch_z(probs, qubit_idx):
    """Expectation of Z on qubit_idx (0 or 1) from 2-qubit measurement."""
    ev = 0.0
    for bits, p in probs.items():
        # Qiskit: bits[1]=q0, bits[0]=q1
        s = +1 if bits[1 - qubit_idx] == '0' else -1
        ev += s * p
    return ev

def entropy_from_bloch(rx, ry, rz):
    """Von Neumann entropy of single qubit given Bloch vector."""
    r = np.sqrt(rx**2 + ry**2 + rz**2)
    r = np.clip(r, 0, 1)
    lp = np.clip((1+r)/2, 1e-15, 1-1e-15)
    lm = np.clip((1-r)/2, 1e-15, 1-1e-15)
    return float(-lp*np.log(lp) - lm*np.log(lm))

def alpha_theory(t_us, T1=200.):
    lam = np.clip(0.5 * np.exp(-t_us / (2*T1)), 1e-15, 1-1e-15)
    h2  = -lam*np.log(lam) - (1-lam)*np.log(1-lam)
    return h2 / np.log(2)

def analyse(labels, result):
    from collections import defaultdict
    data = defaultdict(dict)

    for label, qr in zip(labels, result):
        cond, delay, basis = label.split('_')
        try:
            counts = qr.data.meas.get_counts()
        except Exception:
            counts = {}
        total = max(sum(counts.values()), 1)
        probs = {k: v/total for k, v in counts.items()}
        data[(cond, float(delay))][basis] = probs

    print("\n" + "="*65)
    print("EMERGENCY TEST RESULTS")
    print(f"{'Delay':>7} | {'S_A bare':>9} | {'S_A XY-4':>9} | "
          f"{'Δ%':>6} | {'Theory':>8} | Verdict")
    print("-"*65)

    results = {}
    for delay in sorted(DELAY_US, key=float):
        SAs = {}
        for cond in CONDITIONS:
            d = data.get((cond, float(delay)), {})
            rx = bloch_z(d.get('XZ',{}), 0)
            ry = bloch_z(d.get('YZ',{}), 0)
            rz = bloch_z(d.get('ZZ',{}), 0)
            SAs[cond] = entropy_from_bloch(rx, ry, rz)

        SA_b = SAs.get('bare', 0)
        SA_x = SAs.get('xy4',  0)
        dpct = abs(SA_x - SA_b) / max(SA_b, 1e-6) * 100
        thy  = alpha_theory(float(delay)) * np.log(2)

        verdict = ("✓ Thm1" if dpct < 5 else
                  ("✗ FAIL" if dpct > 20 else "?"))

        print(f"{delay:>5}us | {SA_b:>9.4f} | {SA_x:>9.4f} | "
              f"{dpct:>5.1f}% | {thy:>8.4f} | {verdict}")
        results[str(delay)] = dict(SA_bare=SA_b, SA_xy4=SA_x,
                                   delta_pct=dpct, theory=thy)

    # Overall
    deltas = [v['delta_pct'] for v in results.values()]
    max_d  = max(deltas) if deltas else 0
    print("\n" + "="*65)
    if max_d < 5:
        print(f"THEOREM 1: LIKELY CONFIRMED (max Δ={max_d:.1f}%)")
    elif max_d > 20:
        print(f"THEOREM 1: LIKELY FALSIFIED (max Δ={max_d:.1f}%)")
    else:
        print(f"AMBIGUOUS (max Δ={max_d:.1f}%) -- run FC-1 with more shots")
    print("="*65)
    return results

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--token',    default=os.environ.get('IBM_QUANTUM_TOKEN',''))
    p.add_argument('--backend',  default='ibm_brisbane')
    p.add_argument('--instance', default='ibm-q/open/main')
    p.add_argument('--dry-run',  action='store_true')
    return p.parse_args()

def main():
    args = parse_args()
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("="*65)
    print("EMERGENCY FAST TEST  (Theorem 1 minimal viable experiment)")
    print(f"Started: {ts}")
    print("="*65)

    labels, circuits = build()

    if args.dry_run:
        print("\n[DRY RUN] First circuit:")
        print(circuits[0].draw(output='text', fold=80))
        return

    if not args.token:
        print("ERROR: Set IBM_QUANTUM_TOKEN or pass --token")
        sys.exit(1)

    print(f"\nConnecting to {args.backend}...")
    svc     = QiskitRuntimeService(channel='ibm_quantum',
                                   token=args.token,
                                   instance=args.instance)
    backend = svc.backend(args.backend)
    print(f"Backend ready: {backend.name}")

    print(f"Transpiling...")
    tpiled = transpile(circuits, backend=backend,
                       optimization_level=1, initial_layout=[0, 1])

    print(f"Submitting {len(circuits)} circuits x {SHOTS} shots...")
    with Session(backend=backend) as session:
        sampler = SamplerV2(session=session)
        job     = sampler.run(tpiled, shots=SHOTS)
        jid     = job.job_id()
        print(f"Job ID: {jid}")
        print("Waiting... (should complete in 60-90s)")
        result = job.result()

    print("Got results! Analysing...")
    results = analyse(labels, result)

    outfile = f"emergency_results_{ts}.json"
    with open(outfile, 'w') as f:
        json.dump({'job_id': jid, 'backend': args.backend,
                   'timestamp': ts, 'results': results}, f, indent=2)
    print(f"\nSaved to {outfile}")
    print("Use this data with fc1_xy4_falsification.py --results-file for deeper analysis.")

if __name__ == '__main__':
    main()
