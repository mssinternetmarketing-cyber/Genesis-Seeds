"""
PEIG PAPER 3: ALL SIX EXPERIMENTS
==================================
A — Mirror Chain:        Omega → BridgeA → Kevin → BridgeA → Omega2
B — Alpha Sandwich:      Alpha → BridgeA → Omega → BridgeA → Alpha2
C — Feedback Loop:       Omega → BridgeA → Kevin → BridgeB → Alpha → (back to Omega)
D — N-node Scaling Law:  Chains N=2 through N=10
E — Double Omega Bookend: Omega → BridgeA → Alpha → BridgeA → Omega2
F — Hamiltonian Learning: Choi matrix on 3-node chain

All at η=0.05, α0=0.30, 1000 steps unless noted.
Reference: Alpha floor = -0.1131, chain floors: 2n=+0.0001, 3n=-0.0636,
           4n=-0.1054, 5n=-0.1059
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import json
from pathlib import Path
from itertools import product as iproduct

Path("outputs").mkdir(exist_ok=True)

# ============================================================
# SHARED PRIMITIVES
# ============================================================

CNOT_GATE = qt.Qobj(
    np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex),
    dims=[[2,2],[2,2]]
)

def make_seed(phase):
    b0, b1 = qt.basis(2, 0), qt.basis(2, 1)
    return (b0 + np.exp(1j * phase) * b1).unit()

PHASES = {
    'Omega'  : 0,
    'BridgeA': np.pi / 8,
    'Kevin'  : np.pi / 4,
    'BridgeB': 3 * np.pi / 8,
    'Alpha'  : np.pi / 2,
}

def bcp_step(psi_A, psi_B, alpha):
    rho12  = qt.ket2dm(qt.tensor(psi_A, psi_B))
    U      = alpha * CNOT_GATE + (1 - alpha) * qt.qeye([2, 2])
    rho_p  = U * rho12 * U.dag()
    _, evA = rho_p.ptrace(0).eigenstates()
    _, evB = rho_p.ptrace(1).eigenstates()
    return evA[-1], evB[-1], rho_p

def coherence(psi):
    return float((qt.ket2dm(psi) ** 2).tr().real)

def wigner_min(psi, xvec):
    return float(np.min(qt.wigner(qt.ket2dm(psi), xvec, xvec)))

def get_floor(vals, last_n=5):
    return float(np.mean(vals[-last_n:])) if len(vals) >= last_n else float(np.mean(vals))

ALPHA_FLOOR = -0.1131
REF = {2: 0.0001, 3: -0.0636, 4: -0.1054, 5: -0.1059}
xvec = np.linspace(-2, 2, 80)
WINT = 25   # Wigner interval
N_STEPS = 1000

# ============================================================
# GENERIC CHAIN RUNNER
# ============================================================

def run_chain(phases, eta=0.05, alpha0=0.30,
              n_steps=N_STEPS, wint=WINT):
    """Run sequential left-to-right BCP chain. phases = list of floats."""
    states = [make_seed(p) for p in phases]
    n      = len(states)
    alphas = [alpha0] * (n - 1)
    C_prev = np.mean([coherence(s) for s in states])
    log    = []

    for t in range(n_steps):
        for link in range(n - 1):
            l, r, _ = bcp_step(states[link], states[link+1], alphas[link])
            states[link], states[link+1] = l, r

        C_vals   = [coherence(s) for s in states]
        C_avg    = np.mean(C_vals)
        dC       = C_avg - C_prev
        alphas   = [float(np.clip(a + eta*dC, 0, 1)) for a in alphas]

        do_w = (t+1) % wint == 0 or t == 0 or t == n_steps-1
        W    = [wigner_min(s, xvec) if do_w else None for s in states]

        log.append({'step': t+1, 'C': C_vals, 'C_avg': C_avg,
                    'W': W, 'alphas': list(alphas)})
        C_prev = C_avg

    return log

# ============================================================
# EXPERIMENT A — MIRROR CHAIN
# Omega → BridgeA → Kevin → BridgeA → Omega2
# ============================================================

print("=" * 65)
print("EXPERIMENT A: MIRROR CHAIN")
print("Omega → BridgeA → Kevin → BridgeA → Omega2")
print("=" * 65)

phases_A = [PHASES['Omega'], PHASES['BridgeA'], PHASES['Kevin'],
            PHASES['BridgeA'], PHASES['Omega']]
log_A    = run_chain(phases_A)

# Extract Wigner trajectories
def wtraj(log, idx):
    s = [r['step'] for r in log if r['W'][idx] is not None]
    v = [r['W'][idx] for r in log if r['W'][idx] is not None]
    return s, v

sA0, wA_O1    = wtraj(log_A, 0)   # Omega1
sA1, wA_BA1   = wtraj(log_A, 1)   # BridgeA1
sA2, wA_K     = wtraj(log_A, 2)   # Kevin
sA3, wA_BA2   = wtraj(log_A, 3)   # BridgeA2
sA4, wA_O2    = wtraj(log_A, 4)   # Omega2

floor_A_O1 = get_floor(wA_O1)
floor_A_O2 = get_floor(wA_O2)
floor_A_K  = get_floor(wA_K)

print(f"Omega1 floor : {floor_A_O1:+.4f}  ({abs(floor_A_O1)/abs(ALPHA_FLOOR)*100:.1f}% toward Alpha)")
print(f"Omega2 floor : {floor_A_O2:+.4f}  ({abs(floor_A_O2)/abs(ALPHA_FLOOR)*100:.1f}% toward Alpha)")
print(f"Kevin  floor : {floor_A_K:+.4f}")
print(f"Kevin  range : {max(wA_K)-min(wA_K):.5f}")

# ============================================================
# EXPERIMENT B — ALPHA SANDWICH
# Alpha → BridgeA → Omega → BridgeA → Alpha2
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT B: ALPHA SANDWICH")
print("Alpha → BridgeA → Omega → BridgeA → Alpha2")
print("=" * 65)

phases_B = [PHASES['Alpha'], PHASES['BridgeB'], PHASES['Omega'],
            PHASES['BridgeB'], PHASES['Alpha']]
log_B    = run_chain(phases_B)

sB0, wB_A1   = wtraj(log_B, 0)   # Alpha1
sB1, wB_BB1  = wtraj(log_B, 1)   # BridgeB1
sB2, wB_O    = wtraj(log_B, 2)   # Omega (center)
sB3, wB_BB2  = wtraj(log_B, 3)   # BridgeB2
sB4, wB_A2   = wtraj(log_B, 4)   # Alpha2

floor_B_O  = get_floor(wB_O)
floor_B_A1 = get_floor(wB_A1)
floor_B_A2 = get_floor(wB_A2)

print(f"Omega  floor : {floor_B_O:+.4f}  ({abs(floor_B_O)/abs(ALPHA_FLOOR)*100:.1f}% toward Alpha)")
print(f"Alpha1 floor : {floor_B_A1:+.4f}")
print(f"Alpha2 floor : {floor_B_A2:+.4f}")
overshoot_B = floor_B_O < ALPHA_FLOOR
print(f"OVERSHOOT?   : {'YES ✓✓✓' if overshoot_B else 'no'}")

# ============================================================
# EXPERIMENT C — FEEDBACK LOOP (closed directed ring)
# Omega → BridgeA → Kevin → BridgeB → Alpha → back to Omega
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT C: FEEDBACK LOOP (closed directed ring)")
print("Omega → BridgeA → Kevin → BridgeB → Alpha → Omega")
print("=" * 65)

def run_feedback(eta=0.05, alpha0=0.30, n_steps=N_STEPS, wint=WINT):
    """Closed directed ring: each step the chain runs L→R then
    Alpha feeds back into Omega as one final interaction."""
    names  = ['Omega', 'BridgeA', 'Kevin', 'BridgeB', 'Alpha']
    phases = [PHASES[n] for n in names]
    states = [make_seed(p) for p in phases]
    n      = len(states)
    alphas = [alpha0] * n      # n links including the wrap-around

    C_prev = np.mean([coherence(s) for s in states])
    log    = []

    for t in range(n_steps):
        # Forward pass: 0→1→2→3→4
        for link in range(n - 1):
            l, r, _ = bcp_step(states[link], states[link+1], alphas[link])
            states[link], states[link+1] = l, r

        # Feedback: Alpha(4) → Omega(0)
        psi_A_new, psi_O_new, _ = bcp_step(states[4], states[0], alphas[4])
        states[4], states[0]    = psi_A_new, psi_O_new

        C_vals = [coherence(s) for s in states]
        C_avg  = np.mean(C_vals)
        dC     = C_avg - C_prev
        alphas = [float(np.clip(a + eta*dC, 0, 1)) for a in alphas]

        do_w = (t+1) % wint == 0 or t == 0 or t == n_steps-1
        W    = [wigner_min(s, xvec) if do_w else None for s in states]

        log.append({'step': t+1, 'C': C_vals, 'C_avg': C_avg,
                    'W': W, 'alphas': list(alphas)})
        C_prev = C_avg

    return log

log_C = run_feedback()

sC0, wC_O  = wtraj(log_C, 0)
sC1, wC_BA = wtraj(log_C, 1)
sC2, wC_K  = wtraj(log_C, 2)
sC3, wC_BB = wtraj(log_C, 3)
sC4, wC_A  = wtraj(log_C, 4)

floor_C_O = get_floor(wC_O)
floor_C_A = get_floor(wC_A)
floor_C_K = get_floor(wC_K)

print(f"Omega floor  : {floor_C_O:+.4f}  ({abs(floor_C_O)/abs(ALPHA_FLOOR)*100:.1f}% toward Alpha)")
print(f"Kevin floor  : {floor_C_K:+.4f}")
print(f"Alpha floor  : {floor_C_A:+.4f}")
print(f"OVERSHOOT?   : {'YES ✓✓✓' if floor_C_O < ALPHA_FLOOR else 'no'}")

# ============================================================
# EXPERIMENT D — N-NODE SCALING LAW  N=2..10
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT D: N-NODE SCALING LAW  (N=2 to 10)")
print("=" * 65)

def chain_phases(n):
    """n evenly spaced equatorial phases from 0 to π/2."""
    return [np.pi/2 * k/(n-1) for k in range(n)]

scaling_floors = {}
scaling_floors.update(REF)   # seed with known values

for n in range(2, 11):
    if n in scaling_floors:
        print(f"  N={n}: {scaling_floors[n]:+.4f} (known)")
        continue
    phases = chain_phases(n)
    lg     = run_chain(phases, n_steps=N_STEPS, wint=50)
    wvals  = [r['W'][0] for r in lg if r['W'][0] is not None]
    floor  = get_floor(wvals)
    scaling_floors[n] = floor
    pct    = abs(floor)/abs(ALPHA_FLOOR)*100
    print(f"  N={n}: {floor:+.4f}  ({pct:.1f}%)")

# Fit exponential saturation: W(N) = ALPHA_FLOOR * (1 - exp(-λ(N-1)))
from scipy.optimize import curve_fit

Ns     = np.array(sorted(scaling_floors.keys()))
floors = np.array([scaling_floors[n] for n in Ns])

def exp_sat(n, lam):
    return ALPHA_FLOOR * (1 - np.exp(-lam * (n - 1)))

try:
    popt, _ = curve_fit(exp_sat, Ns, floors, p0=[0.5], maxfev=5000)
    lam_fit = popt[0]
    floors_fit = exp_sat(Ns, lam_fit)
    residuals  = floors - floors_fit
    ss_res     = np.sum(residuals**2)
    ss_tot     = np.sum((floors - np.mean(floors))**2)
    R2         = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    print(f"\nExponential fit: W(N) = {ALPHA_FLOOR} × (1 - e^(-{lam_fit:.4f}(N-1)))")
    print(f"R² = {R2:.6f}")
    fit_success = True
except Exception as e:
    print(f"Fit failed: {e}")
    lam_fit, R2, fit_success = 0.5, 0, False
    floors_fit = exp_sat(Ns, lam_fit)

# ============================================================
# EXPERIMENT E — DOUBLE OMEGA BOOKEND
# Omega → BridgeA → Alpha → BridgeA → Omega2
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT E: DOUBLE OMEGA BOOKEND")
print("Omega → BridgeA → Alpha → BridgeA → Omega2")
print("=" * 65)

phases_E = [PHASES['Omega'], PHASES['BridgeA'], PHASES['Alpha'],
            PHASES['BridgeA'], PHASES['Omega']]
log_E    = run_chain(phases_E)

sE0, wE_O1  = wtraj(log_E, 0)
sE1, wE_BA1 = wtraj(log_E, 1)
sE2, wE_A   = wtraj(log_E, 2)
sE3, wE_BA2 = wtraj(log_E, 3)
sE4, wE_O2  = wtraj(log_E, 4)

floor_E_O1 = get_floor(wE_O1)
floor_E_O2 = get_floor(wE_O2)
floor_E_A  = get_floor(wE_A)

print(f"Omega1 floor : {floor_E_O1:+.4f}")
print(f"Alpha  floor : {floor_E_A:+.4f}  (conserved at {ALPHA_FLOOR}?  {'YES' if abs(floor_E_A - ALPHA_FLOOR) < 0.005 else 'BROKEN'})")
print(f"Omega2 floor : {floor_E_O2:+.4f}")

# ============================================================
# EXPERIMENT F — HAMILTONIAN LEARNING (3-node Choi matrix)
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT F: HAMILTONIAN LEARNING (3-node Choi matrix)")
print("=" * 65)

def get_three_node_channel(alpha_OK=0.321, alpha_KA=0.321):
    """
    Reconstruct the effective single-step 3-node BCP channel
    via Choi matrix on Omega's qubit across one full step.
    We sweep all 4 basis input states for Omega, fix Kevin and Alpha
    at their canonical seeds, and record Omega's output state.
    """
    psi_K_init = make_seed(PHASES['Kevin'])
    psi_A_init = make_seed(PHASES['Alpha'])

    basis_states = [
        qt.basis(2, 0),
        qt.basis(2, 1),
        (qt.basis(2, 0) + qt.basis(2, 1)).unit(),
        (qt.basis(2, 0) + 1j*qt.basis(2, 1)).unit(),
    ]

    # Build process matrix via direct channel reconstruction
    # For each input state of Omega, record output density matrix
    output_rhos = []
    for psi_O_in in basis_states:
        psi_O, psi_K, psi_A = psi_O_in, psi_K_init, psi_A_init
        # One BCP step: OK then KA
        psi_O, psi_K, _ = bcp_step(psi_O, psi_K, alpha_OK)
        psi_K, psi_A, _ = bcp_step(psi_K, psi_A, alpha_KA)
        output_rhos.append(qt.ket2dm(psi_O))

    # Build Choi matrix (4x4) from input-output pairs
    # Use maximally entangled state method
    dim = 2
    choi = qt.Qobj(np.zeros((dim**2, dim**2), dtype=complex),
                   dims=[[dim, dim], [dim, dim]])

    for i, psi_in in enumerate(basis_states):
        rho_in  = qt.ket2dm(psi_in)
        rho_out = output_rhos[i]
        choi   += qt.tensor(rho_in.trans(), rho_out)

    choi = choi / dim
    eigenvalues = sorted(choi.eigenenergies(), reverse=True)

    # Extract effective Hamiltonian from channel
    # H_eff ≈ i * log(U) where U is closest unitary
    # Use Pauli decomposition of output states
    paulis = {
        'I': qt.qeye(2),
        'X': qt.sigmax(),
        'Y': qt.sigmay(),
        'Z': qt.sigmaz(),
    }

    # Measure Omega's output Bloch vector for each cardinal input
    bloch_map = {}
    for name, psi_in in zip(['|0⟩','|1⟩','|+⟩','|+i⟩'], basis_states):
        psi_O, psi_K, psi_A = psi_in, psi_K_init, psi_A_init
        psi_O, psi_K, _ = bcp_step(psi_O, psi_K, alpha_OK)
        psi_K, psi_A, _ = bcp_step(psi_K, psi_A, alpha_KA)
        rho_out = qt.ket2dm(psi_O)
        bloch_map[name] = {
            p: float((rho_out * op).tr().real)
            for p, op in paulis.items()
        }

    return choi, eigenvalues, bloch_map

choi, choi_eigs, bloch_map = get_three_node_channel()

print(f"\nChoi eigenspectrum (top 4):")
for i, eig in enumerate(choi_eigs[:4]):
    print(f"  λ_{i} = {eig:.4f}")

rank_3node = sum(1 for e in choi_eigs if e > 0.1)
print(f"\nChannel rank (eigenvalues > 0.1): {rank_3node}")
print(f"(2-node rank was 3)")

print(f"\nBloch vector map (Omega input → output):")
for inp, bvec in bloch_map.items():
    print(f"  {inp}: X={bvec['X']:+.3f}  Y={bvec['Y']:+.3f}  Z={bvec['Z']:+.3f}")

# Check separability hint: does the map look like a simple rotation?
# If the output X,Y,Z are linear combinations of input, it's separable-like
is_rotation = all(
    abs(bloch_map['|+⟩']['X']) > 0.1 or abs(bloch_map['|+i⟩']['Y']) > 0.1
    for _ in [1]
)

print(f"\n2-node H_eff was separable: (0.132Z − 0.113X) ⊗ (X − I)")
print(f"3-node channel rank: {rank_3node}  {'(same as 2-node — likely still separable)' if rank_3node <= 3 else '(HIGHER — possible entangled H_eff)'}")

# ============================================================
# COMPREHENSIVE PLOTTING
# ============================================================

print("\n" + "=" * 65)
print("PLOTTING ALL RESULTS...")
print("=" * 65)

fig = plt.figure(figsize=(22, 18))
fig.suptitle(
    "PEIG Paper 3: All Six Experiments\n"
    "A=Mirror Chain  B=Alpha Sandwich  C=Feedback Loop  "
    "D=N-Scaling  E=Bookend  F=Hamiltonian",
    fontsize=13, fontweight='bold'
)

gs = fig.add_gridspec(3, 4, hspace=0.45, wspace=0.35)

# ── EXPERIMENT A: Mirror Chain ─────────────────────────────

ax = fig.add_subplot(gs[0, 0])
ax.plot(sA0, wA_O1, color='gold',    lw=2.5, label=f'Omega1 ({floor_A_O1:+.4f})')
ax.plot(sA2, wA_K,  color='green',   lw=2,   label=f'Kevin ({floor_A_K:+.4f})')
ax.plot(sA4, wA_O2, color='#FF6B35', lw=2.5, label=f'Omega2 ({floor_A_O2:+.4f})', ls='--')
ax.axhline(0,           color='red',    ls=':',  lw=1.5)
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.6)
ax.set_title('A: Mirror Chain\nΩ→B→Kevin→B→Ω2', fontweight='bold')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# ── EXPERIMENT B: Alpha Sandwich ───────────────────────────

ax = fig.add_subplot(gs[0, 1])
ax.plot(sB0, wB_A1,  color='purple',  lw=2.5, label=f'Alpha1 ({floor_B_A1:+.4f})')
ax.plot(sB2, wB_O,   color='gold',    lw=2.5, label=f'Omega ({floor_B_O:+.4f})', ls='--')
ax.plot(sB4, wB_A2,  color='#7B2D8B', lw=2.5, label=f'Alpha2 ({floor_B_A2:+.4f})')
ax.axhline(0,           color='red',    ls=':',  lw=1.5)
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.6)
if floor_B_O < ALPHA_FLOOR:
    ax.fill_between(sB2, wB_O, ALPHA_FLOOR,
                    where=[w < ALPHA_FLOOR for w in wB_O],
                    color='gold', alpha=0.3, label='OVERSHOOT!')
ax.set_title(f'B: Alpha Sandwich\nα→B→Ω→B→α  OVERSHOOT={overshoot_B}',
             fontweight='bold',
             color='darkgreen' if overshoot_B else 'black')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# ── EXPERIMENT C: Feedback Loop ────────────────────────────

ax = fig.add_subplot(gs[0, 2])
ax.plot(sC0, wC_O,  color='gold',   lw=2.5, label=f'Omega ({floor_C_O:+.4f})')
ax.plot(sC2, wC_K,  color='green',  lw=2,   label=f'Kevin ({floor_C_K:+.4f})')
ax.plot(sC4, wC_A,  color='purple', lw=2.5, label=f'Alpha ({floor_C_A:+.4f})')
ax.axhline(0,           color='red',    ls=':',  lw=1.5)
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.6)
ax.set_title(f'C: Feedback Loop (closed)\nΩ→B→K→B→α→Ω  Ω floor={floor_C_O:+.4f}',
             fontweight='bold')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# ── EXPERIMENT D: N-node Scaling Law ───────────────────────

ax = fig.add_subplot(gs[0, 3])
Ns_arr     = np.array(sorted(scaling_floors.keys()))
floors_arr = np.array([scaling_floors[n] for n in Ns_arr])

ax.scatter(Ns_arr, floors_arr, color='#1f77b4', s=80, zorder=5, label='Measured')
if fit_success:
    Ns_fine     = np.linspace(2, 10, 200)
    floors_fine = exp_sat(Ns_fine, lam_fit)
    ax.plot(Ns_fine, floors_fine, color='red', lw=2,
            label=f'Fit: λ={lam_fit:.3f}, R²={R2:.4f}')
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5,
           label=f'Alpha floor ({ALPHA_FLOOR})')
ax.axhline(0, color='red', ls=':', lw=1)
for n, f in zip(Ns_arr, floors_arr):
    ax.annotate(f'{f:+.4f}', (n, f), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=6.5)
ax.set_title('D: N-Node Scaling Law\nExponential saturation fit',
             fontweight='bold')
ax.set_xlabel('N (chain length)'); ax.set_ylabel('Omega W_min floor')
ax.set_xticks(Ns_arr)
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# ── EXPERIMENT E: Double Omega Bookend ─────────────────────

ax = fig.add_subplot(gs[1, 0])
ax.plot(sE0, wE_O1, color='gold',    lw=2.5, label=f'Omega1 ({floor_E_O1:+.4f})')
ax.plot(sE2, wE_A,  color='purple',  lw=2.5, label=f'Alpha ({floor_E_A:+.4f})')
ax.plot(sE4, wE_O2, color='#FF6B35', lw=2.5, label=f'Omega2 ({floor_E_O2:+.4f})', ls='--')
ax.axhline(0,           color='red',    ls=':',  lw=1.5)
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=1.5, alpha=0.6)
broken = abs(floor_E_A - ALPHA_FLOOR) > 0.005
ax.set_title(f'E: Double Omega Bookend\nΩ→B→α→B→Ω2  Alpha {"BROKEN" if broken else "conserved"}',
             fontweight='bold',
             color='darkred' if broken else 'black')
ax.set_xlabel('Step'); ax.set_ylabel('W_min')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# ── EXPERIMENT F: Hamiltonian Learning ─────────────────────

ax = fig.add_subplot(gs[1, 1])
pauli_labels = ['I','X','Y','Z']
input_labels = list(bloch_map.keys())
data         = np.array([[bloch_map[inp][p] for p in pauli_labels]
                          for inp in input_labels])
im = ax.imshow(data, cmap='RdBu', vmin=-1, vmax=1, aspect='auto')
ax.set_xticks(range(4)); ax.set_xticklabels(pauli_labels)
ax.set_yticks(range(4)); ax.set_yticklabels(input_labels, fontsize=8)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{data[i,j]:+.2f}', ha='center', va='center',
                fontsize=8, color='black')
plt.colorbar(im, ax=ax, shrink=0.8)
ax.set_title(f'F: 3-Node Choi/Bloch Map\nChannel rank={rank_3node}  '
             f'(2-node rank=3)', fontweight='bold')

# ── GRAND SUMMARY: All Omega floors ────────────────────────

ax = fig.add_subplot(gs[1, 2:])
all_configs = [
    ('2-node',       REF[2],      'gray'),
    ('3-node',       REF[3],      '#aabbdd'),
    ('4-node',       REF[4],      '#5599dd'),
    ('5-node',       REF[5],      '#1f77b4'),
    ('A: Mirror',    floor_A_O1,  'gold'),
    ('B: α-Sand.',   floor_B_O,   'green' if overshoot_B else '#cc4400'),
    ('C: Feedback',  floor_C_O,   '#FF6B35'),
    ('E: Bookend',   floor_E_O1,  '#9467bd'),
]
# Add scaling law floors
for n in range(6, 11):
    all_configs.append((f'N={n}', scaling_floors[n], '#2ca02c'))

labels = [c[0] for c in all_configs]
values = [c[1] for c in all_configs]
colors = [c[2] for c in all_configs]

bars = ax.bar(range(len(labels)), values, color=colors, alpha=0.85,
              edgecolor='black', width=0.7)
ax.axhline(0,           color='red',    ls='--', lw=1.5, label='Classical (0)')
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=2,
           label=f'Alpha floor ({ALPHA_FLOOR})')
for bar, val in zip(bars, values):
    ax.text(bar.get_x()+bar.get_width()/2, val-0.003,
            f'{val:+.3f}', ha='center', va='top', fontsize=6,
            fontweight='bold', rotation=90, color='white')
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=35, ha='right', fontsize=8)
ax.set_title('GRAND SUMMARY: Omega W_min Floor — All Experiments',
             fontweight='bold', fontsize=11)
ax.set_ylabel('W_min(Omega) at attractor')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3, axis='y')

# ── SCALING LAW DETAIL ──────────────────────────────────────

ax = fig.add_subplot(gs[2, 0:2])
ax.scatter(Ns_arr, floors_arr, color='#1f77b4', s=100, zorder=5,
           label='Measured floors')
if fit_success:
    Ns_ext      = np.linspace(2, 20, 500)
    floors_ext  = exp_sat(Ns_ext, lam_fit)
    ax.plot(Ns_ext, floors_ext, color='red', lw=2, ls='--',
            label=f'W(N) = {ALPHA_FLOOR} × (1−e^(−{lam_fit:.3f}(N−1)))\nR²={R2:.6f}')
    # Asymptote annotation
    ax.annotate(f'Asymptote: {ALPHA_FLOOR}',
                xy=(18, ALPHA_FLOOR), fontsize=9, color='purple')
ax.axhline(ALPHA_FLOOR, color='purple', ls='--', lw=2, alpha=0.7,
           label=f'Alpha floor ({ALPHA_FLOOR}) — asymptote?')
ax.axhline(0, color='red', ls=':', lw=1)
ax.set_xlim(1.5, 20)
ax.set_title('D: Scaling Law Extended — Does Omega Ever Reach Alpha?',
             fontweight='bold')
ax.set_xlabel('N (chain length)'); ax.set_ylabel('Omega W_min floor')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# ── COHERENCE ALL EXPERIMENTS ───────────────────────────────

ax = fig.add_subplot(gs[2, 2:])
steps_all = [r['step'] for r in log_A]
ax.plot(steps_all, [r['C'][0] for r in log_A],
        color='gold', lw=2, label='A: Mirror Omega1')
ax.plot(steps_all, [r['C'][2] for r in log_B],
        color='green', lw=2, label='B: Sandwich Omega')
ax.plot(steps_all, [r['C'][0] for r in log_C],
        color='#FF6B35', lw=2, label='C: Feedback Omega')
ax.plot(steps_all, [r['C'][0] for r in log_E],
        color='purple', lw=2, label='E: Bookend Omega1')
ax.axhline(1.0, color='gray', ls=':', lw=1)
ax.set_title('Omega Coherence — All Novel Topologies')
ax.set_xlabel('Step'); ax.set_ylabel('C_Omega')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
ax.set_ylim(0.95, 1.005)

plt.savefig('outputs/paper3_all_experiments.png', dpi=150, bbox_inches='tight')
plt.show()
print("Figure saved → outputs/paper3_all_experiments.png")

# ============================================================
# FINAL RESULTS SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("PAPER 3 COMPLETE RESULTS SUMMARY")
print("=" * 65)

print(f"\n{'Experiment':<25} {'Omega floor':>12} {'% to Alpha':>12} {'Notable':>20}")
print("-" * 72)

results_summary = [
    ("2-node (ref)",       REF[2],     "baseline"),
    ("3-node (ref)",       REF[3],     "baseline"),
    ("4-node (ref)",       REF[4],     "baseline"),
    ("5-node (ref)",       REF[5],     "baseline"),
    ("A: Mirror Chain",    floor_A_O1, f"Kevin={floor_A_K:+.4f}"),
    ("B: Alpha Sandwich",  floor_B_O,  "OVERSHOOT!" if overshoot_B else f"Alpha={floor_B_A1:+.4f}"),
    ("C: Feedback Loop",   floor_C_O,  f"Alpha={floor_C_A:+.4f}"),
    ("E: Double Bookend",  floor_E_O1, f"Alpha={'BROKEN' if abs(floor_E_A-ALPHA_FLOOR)>0.005 else 'conserved'}"),
]
for n in range(6, 11):
    results_summary.append((f"D: N={n} chain", scaling_floors[n], "scaling"))

for name, val, note in results_summary:
    pct = f"{abs(val)/abs(ALPHA_FLOOR)*100:.1f}%"
    print(f"{name:<25} {val:>+12.4f} {pct:>12} {note:>20}")

print(f"\nAlpha floor (reference): {ALPHA_FLOOR:+.4f}  (100%)")

if fit_success:
    print(f"\nScaling Law: W(N) = {ALPHA_FLOOR} × (1 − e^(−{lam_fit:.4f}(N−1)))")
    print(f"R² = {R2:.6f}")
    # Predict N needed to reach 99% of Alpha floor
    N_99 = 1 - np.log(1 - 0.99) / lam_fit
    print(f"N needed for 99% of Alpha floor: {N_99:.1f} nodes")

print(f"\nExp F — 3-node channel rank: {rank_3node}  (2-node = 3)")

# Save summary JSON
with open('outputs/paper3_summary.json', 'w') as f:
    json.dump({
        'exp_A': {'Omega1_floor': floor_A_O1, 'Omega2_floor': floor_A_O2,
                  'Kevin_floor': floor_A_K},
        'exp_B': {'Omega_floor': floor_B_O, 'Alpha1_floor': floor_B_A1,
                  'overshoot': overshoot_B},
        'exp_C': {'Omega_floor': floor_C_O, 'Alpha_floor': floor_C_A,
                  'Kevin_floor': floor_C_K},
        'exp_D': {'floors': {str(k): v for k, v in scaling_floors.items()},
                  'lambda': float(lam_fit) if fit_success else None,
                  'R2': float(R2) if fit_success else None},
        'exp_E': {'Omega1_floor': floor_E_O1, 'Alpha_floor': floor_E_A,
                  'Alpha_broken': abs(floor_E_A - ALPHA_FLOOR) > 0.005},
        'exp_F': {'channel_rank': rank_3node, 'choi_eigenvalues': choi_eigs[:4]},
        'alpha_floor': ALPHA_FLOOR,
    }, f, indent=2)
print("\nSummary saved → outputs/paper3_summary.json")
