"""
FC-1: XY-4 Falsification Test  --  PRIORITY 1
=====================================================================
THEOREM 1 (Paper 1, Section 5.3):
    Pure dephasing T_phi does NOT suppress S_A in the high-entanglement
    regime.  Only amplitude damping T1 matters.

TEST LOGIC:
    Prepare Bell state |Phi+> = (|00>+|11>)/sqrt(2).
    Run two conditions at each idle time t:
        BARE:   no decoupling  (both T1 and T_phi act)
        XY-4:   dynamical decoupling sequence (T_phi suppressed ~10x,
                T1 unchanged)
    Measure S_A via 2-qubit state tomography.

PREDICTION (Theorem 1 CONFIRMED):
    |S_A^BARE(t) - S_A^XY4(t)| / S_A^BARE(t)  <  5%
    Both curves follow  h2(exp(-t/(2*T1))) / ln2

PREDICTION (Theorem 1 FALSIFIED / prior heuristic correct):
    S_A^XY4(t)  >>  S_A^BARE(t)   (>20% gap)

CIRCUIT COUNT:  6 delay points x 2 conditions x 9 tomo bases = 108 circuits
SHOTS:          512 per circuit  (~55k total shots, fits in ~3 min on Heron r2)
RUNTIME:        ~2.5 minutes typical queue+run
=====================================================================
USAGE:
    python fc1_xy4_falsification.py --token YOUR_IBM_TOKEN --backend ibm_brisbane
    OR set environment variable IBM_QUANTUM_TOKEN before running.
=====================================================================
"""

import os
import sys
import json
import argparse
import numpy as np
from datetime import datetime

# ── Qiskit imports ──────────────────────────────────────────────────────────
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, Session

# ── Constants ───────────────────────────────────────────────────────────────
SHOTS        = 512           # per circuit -- fast but statistically meaningful
DELAY_US     = [0, 5, 15, 30, 60, 100]  # microseconds idle time
NUM_QUBITS   = 2
TOMO_BASES   = ['XX','XY','XZ','YX','YY','YZ','ZX','ZY','ZZ']

# ── Argument parsing ─────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="FC-1 XY-4 Falsification Test")
    p.add_argument('--token',   default=os.environ.get('IBM_QUANTUM_TOKEN',''),
                   help='IBM Quantum token (or set IBM_QUANTUM_TOKEN env var)')
    p.add_argument('--backend', default='ibm_brisbane',
                   help='Backend name, e.g. ibm_brisbane, ibm_torino')
    p.add_argument('--instance', default='ibm-q/open/main',
                   help='IBM Quantum instance (hub/group/project)')
    p.add_argument('--dry-run', action='store_true',
                   help='Build circuits only, do not submit to hardware')
    return p.parse_args()

# ── Bell state preparation ───────────────────────────────────────────────────
def bell_prep():
    """Return QuantumCircuit that prepares |Phi+> = (|00>+|11>)/sqrt(2)."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc

# ── XY-4 dynamical decoupling sequence ───────────────────────────────────────
def xy4_sequence(qc: QuantumCircuit, qubit: int, delay_us: float,
                 dt_ns: float = 0.5):
    """
    Insert XY-4 DD sequence on `qubit` spanning total time `delay_us` us.
    XY-4: tau/2 -- X -- tau -- Y -- tau -- X -- tau -- Y -- tau/2
    This suppresses dephasing to ~O((T_phi/T2)^4) while leaving T1 unchanged.
    dt_ns: backend dt in nanoseconds (default 0.5 ns for Heron r2).
    """
    if delay_us <= 0:
        return
    total_dt = int(delay_us * 1000 / dt_ns)   # delay in dt units
    tau_dt   = total_dt // 8                   # each of 8 segments
    if tau_dt < 1:
        tau_dt = 1

    qc.delay(tau_dt, qubit, unit='dt')
    qc.x(qubit)
    qc.delay(2 * tau_dt, qubit, unit='dt')
    qc.y(qubit)
    qc.delay(2 * tau_dt, qubit, unit='dt')
    qc.x(qubit)
    qc.delay(2 * tau_dt, qubit, unit='dt')
    qc.y(qubit)
    qc.delay(tau_dt, qubit, unit='dt')

# ── Basis rotation for tomography ────────────────────────────────────────────
def apply_basis_rotation(qc: QuantumCircuit, basis: str):
    """
    Rotate into the measurement basis.
    basis: two-char string, each char in {X, Y, Z}.
    X: apply H before measure
    Y: apply S_dag then H before measure
    Z: no rotation
    """
    for i, b in enumerate(basis):
        if b == 'X':
            qc.h(i)
        elif b == 'Y':
            qc.sdg(i)
            qc.h(i)
        # Z: nothing
    qc.measure_all()

# ── Build all circuits ────────────────────────────────────────────────────────
def build_circuits(delay_us_list, dt_ns=0.5):
    """
    Returns list of (label, QuantumCircuit) pairs.
    label: 'bare_<delay>us_<basis>' or 'xy4_<delay>us_<basis>'
    """
    circuits = []
    for delay in delay_us_list:
        for condition in ['bare', 'xy4']:
            for basis in TOMO_BASES:
                qc = bell_prep()
                qc.barrier()

                if delay > 0:
                    if condition == 'bare':
                        # Simple idle delay on both qubits
                        delay_dt = int(delay * 1000 / dt_ns)
                        qc.delay(delay_dt, 0, unit='dt')
                        qc.delay(delay_dt, 1, unit='dt')
                    else:  # xy4
                        xy4_sequence(qc, 0, delay, dt_ns)
                        xy4_sequence(qc, 1, delay, dt_ns)

                qc.barrier()
                apply_basis_rotation(qc, basis)
                label = f"{condition}_{delay}us_{basis}"
                circuits.append((label, qc))

    print(f"[FC-1] Built {len(circuits)} circuits "
          f"({len(delay_us_list)} delays × 2 conditions × {len(TOMO_BASES)} bases)")
    return circuits

# ── Density matrix from tomography counts ────────────────────────────────────
def counts_to_probs(counts: dict, n_qubits: int = 2) -> dict:
    """Normalise raw counts dict to probabilities."""
    total = sum(counts.values())
    states = [format(i, f'0{n_qubits}b') for i in range(2**n_qubits)]
    return {s: counts.get(s, 0) / total for s in states}

def reconstruct_density_matrix(tomo_probs: dict) -> np.ndarray:
    """
    Maximum-likelihood-free linear inversion of 2-qubit state tomography.
    tomo_probs: dict mapping basis (e.g. 'XX') to prob dict {'00':p,'01':p,...}
    Returns 4x4 density matrix (may have small negative eigenvalues due to noise).
    """
    # Pauli basis
    I  = np.eye(2)
    sx = np.array([[0,1],[1,0]])
    sy = np.array([[0,-1j],[1j,0]])
    sz = np.array([[1,0],[0,-1]])
    paulis = {'I': I, 'X': sx, 'Y': sy, 'Z': sz}

    # Build Pauli expectation values from tomography results
    exp_vals = {}
    for basis, probs in tomo_probs.items():
        b0, b1 = basis[0], basis[1]
        ev = 0.0
        for bits, p in probs.items():
            s0 = +1 if bits[1] == '0' else -1   # Qiskit bit order is reversed
            s1 = +1 if bits[0] == '0' else -1
            eigenval = s0 * s1
            ev += eigenval * p
        exp_vals[(b0, b1)] = ev

    # Reconstruct via Pauli expansion: rho = sum_{A,B} <A*B> A*B / 4
    rho = np.zeros((4, 4), dtype=complex)
    pairs = [('I','I'),('I','X'),('I','Y'),('I','Z'),
             ('X','I'),('X','X'),('X','Y'),('X','Z'),
             ('Y','I'),('Y','X'),('Y','Y'),('Y','Z'),
             ('Z','I'),('Z','X'),('Z','Y'),('Z','Z')]
    # Set <II> = 1 (normalisation)
    exp_vals[('I','I')] = 1.0
    # For single-qubit terms, need single-qubit measurements
    # We approximate by tracing over the other qubit
    for ab in [('I','X'),('I','Y'),('I','Z'),('X','I'),('Y','I'),('Z','I')]:
        a, b = ab
        # For IX: use any row with X in second position
        if a == 'I':
            key_cands = [(k0, b) for k0 in 'XYZ']
        else:
            key_cands = [(a, k1) for k1 in 'XYZ']
        # Average over available measurements
        vals = [exp_vals.get((k0,k1), None) for k0,k1 in key_cands
                if (k0,k1) in exp_vals]
        exp_vals[ab] = np.mean(vals) if vals else 0.0

    for a, b in pairs:
        mat = np.kron(paulis[a], paulis[b])
        rho += exp_vals.get((a, b), 0.0) * mat
    rho /= 4.0
    return rho

def von_neumann_entropy(rho: np.ndarray, subsystem: int = 0) -> float:
    """
    Compute S_A for qubit `subsystem` (0 or 1) by partial trace then
    eigendecomposition.
    """
    if subsystem == 0:
        # Trace over qubit 1
        rho_A = rho[0:2, 0:2] + rho[2:4, 2:4]
    else:
        # Trace over qubit 0
        rho_A = np.array([[rho[0,0]+rho[1,1], rho[0,2]+rho[1,3]],
                          [rho[2,0]+rho[3,1], rho[2,2]+rho[3,3]]])
    eigvals = np.linalg.eigvalsh(rho_A)
    eigvals = np.clip(eigvals.real, 1e-15, 1.0)
    return float(-np.sum(eigvals * np.log(eigvals)))

# ── Theoretical predictions ───────────────────────────────────────────────────
def alpha_screen_theorem1(t_us: float, T1_us: float = 200.0) -> float:
    """Closed-form screening factor from Theorem 1 (T_phi independent)."""
    lam = np.clip(0.5 * np.exp(-t_us / (2 * T1_us)), 1e-15, 1 - 1e-15)
    h2  = -lam * np.log(lam) - (1 - lam) * np.log(1 - lam)
    return h2 / np.log(2)

def alpha_screen_heuristic(t_us: float, T1_us: float = 200.0,
                            Tphi_us: float = 100.0) -> float:
    """Prior heuristic: exp(-c*(gamma1 + gamma_phi)*t). THEOREM 1 SAYS THIS IS WRONG."""
    gamma_total = 1/T1_us + 1/Tphi_us
    return float(np.exp(-0.5 * gamma_total * t_us))

# ── Analysis ──────────────────────────────────────────────────────────────────
def analyse_results(labels, job_results, shots=SHOTS):
    """
    Parse job results, reconstruct density matrices, compute S_A,
    compare bare vs XY-4, compare to theory.
    """
    print("\n" + "="*68)
    print("FC-1 XY-4 FALSIFICATION RESULTS")
    print("="*68)
    print(f"{'Delay':>8} | {'S_A bare':>10} | {'S_A XY-4':>10} | "
          f"{'Δ%':>7} | {'Thm1':>8} | {'Heur':>8}")
    print("-"*68)

    # Group circuits by (condition, delay)
    from collections import defaultdict
    tomo_data = defaultdict(dict)  # (condition, delay) -> basis -> probs

    for i, (label, qr) in enumerate(zip(labels, job_results)):
        parts     = label.split('_')
        condition = parts[0]               # bare or xy4
        delay     = float(parts[1].replace('us',''))
        basis     = parts[2]

        try:
            counts = qr.data.meas.get_counts()
        except Exception:
            # Fallback for different result formats
            try:
                counts = dict(qr.data.get('meas', qr.data))
            except Exception:
                counts = {}

        probs = counts_to_probs(counts, NUM_QUBITS)
        tomo_data[(condition, delay)][basis] = probs

    # For each delay, reconstruct and compare
    results_out = {}
    for delay in sorted(set(d for _, d in tomo_data.keys())):
        bare_probs = tomo_data.get(('bare', delay), {})
        xy4_probs  = tomo_data.get(('xy4',  delay), {})

        if not bare_probs or not xy4_probs:
            continue

        rho_bare = reconstruct_density_matrix(bare_probs)
        rho_xy4  = reconstruct_density_matrix(xy4_probs)

        SA_bare = von_neumann_entropy(rho_bare, subsystem=0)
        SA_xy4  = von_neumann_entropy(rho_xy4,  subsystem=0)

        delta_pct = abs(SA_xy4 - SA_bare) / max(SA_bare, 1e-6) * 100
        thm1      = alpha_screen_theorem1(delay) * np.log(2)
        heur      = alpha_screen_heuristic(delay) * np.log(2)

        status = "✓ THML CONFIRMED" if delta_pct < 5 else \
                 ("✗ FALSIFIED"     if delta_pct > 20 else "? AMBIGUOUS")

        print(f"{delay:>6}us | {SA_bare:>10.4f} | {SA_xy4:>10.4f} | "
              f"{delta_pct:>6.1f}% | {thm1:>8.4f} | {heur:>8.4f}   {status}")

        results_out[delay] = dict(SA_bare=SA_bare, SA_xy4=SA_xy4,
                                  delta_pct=delta_pct, thm1_pred=thm1,
                                  heuristic_pred=heur)

    # Overall verdict
    if results_out:
        max_delta = max(v['delta_pct'] for v in results_out.values())
        print("\n" + "="*68)
        if max_delta < 5:
            print("VERDICT: THEOREM 1 CONFIRMED  (max Δ = "
                  f"{max_delta:.1f}% < 5% threshold)")
        elif max_delta > 20:
            print(f"VERDICT: THEOREM 1 FALSIFIED  (max Δ = {max_delta:.1f}% > 20%)")
        else:
            print(f"VERDICT: AMBIGUOUS  (max Δ = {max_delta:.1f}%, need more shots)")
        print("="*68)

    return results_out

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("="*68)
    print("FC-1: XY-4 Falsification Test  (Paper 1, Theorem 1)")
    print(f"Timestamp: {timestamp}")
    print("="*68)

    # ── Build circuits ───────────────────────────────────────────────────────
    circuit_pairs = build_circuits(DELAY_US)
    labels   = [lbl for lbl, _ in circuit_pairs]
    circuits = [qc  for _, qc in circuit_pairs]

    if args.dry_run:
        print("\n[DRY RUN] Circuits built. Circuit 0 (bare_0us_XX):")
        print(circuits[0].draw(output='text', fold=80))
        print(f"\n[DRY RUN] Circuit 6 (xy4_5us_XX):")
        print(circuits[6].draw(output='text', fold=80))
        print(f"\nTotal circuits: {len(circuits)}")
        print(f"Total shots:    {len(circuits) * SHOTS:,}")
        print("[DRY RUN] Done. Pass --token to submit to hardware.")
        return

    # ── Connect to IBM ───────────────────────────────────────────────────────
    if not args.token:
        print("ERROR: No IBM token. Set IBM_QUANTUM_TOKEN or pass --token.")
        sys.exit(1)

    print(f"\n[1/4] Connecting to IBM Quantum ({args.backend})...")
    service = QiskitRuntimeService(channel='ibm_quantum',
                                   token=args.token,
                                   instance=args.instance)
    backend = service.backend(args.backend)
    print(f"      Backend: {backend.name}  "
          f"(qubits: {backend.num_qubits}, "
          f"status: {backend.status().status_msg})")

    # ── Transpile ────────────────────────────────────────────────────────────
    print(f"\n[2/4] Transpiling {len(circuits)} circuits...")
    transpiled = transpile(circuits, backend=backend,
                           optimization_level=1,
                           initial_layout=[0, 1])
    print(f"      Done.")

    # ── Submit ───────────────────────────────────────────────────────────────
    print(f"\n[3/4] Submitting job (shots={SHOTS} per circuit)...")
    with Session(backend=backend) as session:
        sampler = SamplerV2(session=session)
        job = sampler.run(transpiled, shots=SHOTS)
        print(f"      Job ID: {job.job_id()}")
        print("      Waiting for results (typically 1-3 min)...")
        result = job.result()
    print("      Results received.")

    # ── Analyse ──────────────────────────────────────────────────────────────
    print("\n[4/4] Analysing results...")
    pub_results = result
    results = analyse_results(labels, pub_results, SHOTS)

    # ── Save ─────────────────────────────────────────────────────────────────
    outfile = f"fc1_results_{timestamp}.json"
    with open(outfile, 'w') as f:
        json.dump({'job_id': job.job_id(),
                   'backend': args.backend,
                   'timestamp': timestamp,
                   'delays_us': DELAY_US,
                   'shots': SHOTS,
                   'results': {str(k): v for k, v in results.items()}},
                  f, indent=2)
    print(f"\nResults saved to {outfile}")

if __name__ == '__main__':
    main()
