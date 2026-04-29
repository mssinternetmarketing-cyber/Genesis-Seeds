# Section 06 — Notation and Conventions

**Repository:** Monette Research — Entropic Gravity & PEIG Framework  
**Section:** 00_FOUNDATIONAL_DEFINITIONS  
**Status:** Canonical Reference — Applies to All Files in This Repository  
**Last Updated:** March 2026

---

## Purpose

This section is the single authoritative reference for every symbol, unit,
sign convention, and notational choice used across this repository. When any
file in the repository uses a symbol, that symbol is defined here. Any
discrepancy between a file and this section should be resolved in favor of
this section — treat this as the master key.

---

## 6.1 Fundamental Physical Constants

All values are exact or best-current NIST values as of 2026.

| Symbol | Name | Value | Units |
|---|---|---|---|
| $c$ | Speed of light in vacuum | $2.99792458 \times 10^8$ | m/s |
| $\hbar$ | Reduced Planck constant | $1.054571817 \times 10^{-34}$ | J·s |
| $h$ | Planck constant | $6.62607015 \times 10^{-34}$ | J·s |
| $k_B$ | Boltzmann constant | $1.380649 \times 10^{-23}$ | J/K |
| $G$ | Gravitational constant | $6.67430 \times 10^{-11}$ | m³/(kg·s²) |
| $\ell_P$ | Planck length $= \sqrt{\hbar G/c^3}$ | $1.616255 \times 10^{-35}$ | m |
| $m_P$ | Planck mass $= \sqrt{\hbar c/G}$ | $2.176434 \times 10^{-8}$ | kg |
| $T_P$ | Planck temperature $= m_P c^2/k_B$ | $1.416784 \times 10^{32}$ | K |
| $\ln 2$ | Natural log of 2 | $0.693147\ldots$ | dimensionless |

---

## 6.2 Spacetime and Geometry

**Metric signature:** All calculations in this repository use the
**"mostly plus" signature** $(-,+,+,+)$.

The line element is:
$$ds^2 = g_{\mu\nu} dx^\mu dx^\nu = -c^2 dt^2 + dx^2 + dy^2 + dz^2$$
(in flat spacetime / Minkowski coordinates)

**Index conventions:**
- Greek indices $\mu, \nu, \rho, \sigma, \ldots$ run over spacetime:
  $\mu \in \{0, 1, 2, 3\}$ where $0$ is the time coordinate
- Latin indices $i, j, k, \ldots$ run over spatial coordinates:
  $i \in \{1, 2, 3\}$
- Repeated upper+lower indices imply Einstein summation:
  $A^\mu B_\mu \equiv \sum_{\mu=0}^3 A^\mu B_\mu$

| Symbol | Name | Units | Definition |
|---|---|---|---|
| $g_{\mu\nu}$ | Metric tensor | dimensionless | Encodes spacetime geometry |
| $g^{\mu\nu}$ | Inverse metric | dimensionless | $g^{\mu\rho}g_{\rho\nu} = \delta^\mu{}_\nu$ |
| $R^\rho{}_{\sigma\mu\nu}$ | Riemann curvature tensor | m⁻² | Measures spacetime curvature |
| $R_{\mu\nu}$ | Ricci tensor | m⁻² | $R_{\mu\nu} = R^\rho{}_{\mu\rho\nu}$ |
| $R$ | Ricci scalar | m⁻² | $R = g^{\mu\nu}R_{\mu\nu}$ |
| $G_{\mu\nu}$ | Einstein tensor | m⁻² | $G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu}$ |
| $\kappa_\mu$ | Surface gravity | m/s² | Acceleration at horizon |
| $\nabla_\mu$ | Covariant derivative | — | Accounts for spacetime curvature |

**Repulsive gravity condition:** Under signature $(-,+,+,+)$, repulsive
gravitational acceleration occurs when the effective source satisfies:

$$\rho_{\text{grav}} + \frac{3p_{\text{grav}}}{c^2} < 0$$

For the entanglement entropy source term with $\tilde{\kappa} < 0$ and
$S_{\text{ent}} > 0$, this condition is satisfied. See
`01_PHYSICS_CORE/A_ENTROPIC_GRAVITY/sections/01_theory.tex` for verification.

---

## 6.3 Entropy Symbols

This is the most critical section for avoiding the notational errors identified
in the Phase 2 audit. **Use these symbols exactly as defined here.**

| Symbol | Name | Units | Definition |
|---|---|---|---|
| $S_{\text{vN}}(\rho)$ | Von Neumann entropy | J/K | $-k_B\,\text{Tr}(\rho\ln\rho)$ |
| $H(\{p_i\})$ | Shannon entropy | bit (dimensionless) | $-\sum_i p_i \log_2 p_i$ |
| $\mathcal{S}$ | Thermodynamic entropy (general) | J/K | Physical entropy; always has units |
| $S_{\text{ent}}$ | Entanglement entropy density | bit/m³ | Entanglement entropy per unit volume |
| $\mathcal{S}_{\text{ent}}$ | Physical entropy density | J/(K·m³) | $\mathcal{S}_{\text{ent}} = S_{\text{ent}} \cdot k_B \ln 2$ |
| $S_{\text{vac}}$ | Vacuum entanglement entropy | J/K | Horizon-area entropy; $\propto A/4G$ |
| $S_{\text{ent}}^{(\text{op})}$ | Operational entanglement entropy | bit | Laboratory-scale; volume law |
| $\mathcal{N}(\rho)$ | Negentropy | J/K | $S_{\text{vN}}(\rho_{\text{max}}) - S_{\text{vN}}(\rho)$ |
| $\Omega$ | Number of accessible microstates | dimensionless | Used in $S = k_B \ln \Omega$ |
| $S_{\text{max}}$ | Maximum entropy | J/K | $k_B \ln d$ for $d$-dimensional system |
| $\hat{S}_{\text{vN}}$ | Von Neumann entropy estimator | J/K | Statistical estimate from finite shots |

**Critical warnings:**

1. **Never write $S_{\text{ent}}$ for total entropy.** Use $\mathcal{S}$ or
   $S_{\text{vN}}(\rho)$ for total entropy. $S_{\text{ent}}$ is reserved
   exclusively for entanglement entropy *density* (bit/m³).

2. **Never substitute $\mathcal{N}$ for $S_{\text{ent}}$ in the Einstein
   equation.** Negentropy and entanglement entropy density have opposite
   physical predictions and cannot be interchanged. See Section 02.6 for
   full explanation.

3. **Always specify which entropy** when writing $S$ alone — the unadorned
   symbol $S$ is ambiguous and is not used in this repository.

---

## 6.4 Coupling Constants

| Symbol | Name | Units | Value/Range |
|---|---|---|---|
| $\tilde{\kappa}$ | Dimensionless entanglement-gravity coupling | dimensionless | Ideal: $-1/4$; Realistic: $\in[-2.5\times10^{-3}, -2.5\times10^{-5}]$ |
| $\kappa$ | Dimensionful coupling constant | m⁵·kg⁻¹·s⁻²·bit⁻¹ | $\kappa = \frac{c^4}{8\pi G} \cdot \tilde{\kappa} \cdot \frac{1}{k_B\ln 2}$ |
| $\alpha_{\text{screen}}$ | Environmental screening factor | dimensionless | $\in [10^{-4}, 10^{-2}]$ |
| $\Gamma$ | Decoherence rate | s⁻¹ | System-dependent |
| $\tau_D$ | Decoherence time | s | $\sim 1/\Gamma$ |
| $\xi$ | Coherence length | m | Spatial scale of entanglement |

**Disambiguation: $\kappa$ vs. $\tilde{\kappa}$:**
- $\kappa$ (without tilde): **dimensionful** coupling, units
  m⁵·kg⁻¹·s⁻²·bit⁻¹. Rarely used directly.
- $\tilde{\kappa}$ (with tilde): **dimensionless** coupling. This is the
  physically meaningful parameter that experiments constrain. Always prefer
  $\tilde{\kappa}$ in equations.
- $\kappa_\mu$: **surface gravity** (subscript $\mu$, not tilde). Completely
  different quantity — acceleration at a gravitational horizon. Context
  always disambiguates.

---

## 6.5 Quantum Mechanics Symbols

| Symbol | Name | Units | Definition |
|---|---|---|---|
| $\mathcal{H}$ | Hilbert space | — | State space of quantum system |
| $\mathcal{D}(\mathcal{H})$ | Space of density operators | — | Valid quantum states on $\mathcal{H}$ |
| $\rho$ | Density matrix / density operator | dimensionless | $\rho \geq 0$, $\text{Tr}(\rho)=1$, $\rho=\rho^\dagger$ |
| $\rho_A$ | Reduced density matrix of subsystem $A$ | dimensionless | $\rho_A = \text{Tr}_B(\rho_{AB})$ |
| $\hat{H}$ | Hamiltonian operator | J | Total energy operator |
| $\hat{C}_i$ | Constraint operator $i$ | Domain-specific | $\text{Tr}(\hat{C}_i\rho) = c_i$ |
| $\hat{Q}$ | Charge operator | C | Electric charge |
| $|\psi\rangle$ | Pure quantum state (ket) | dimensionless | Element of $\mathcal{H}$ |
| $\langle\psi|$ | Dual state (bra) | dimensionless | Element of dual $\mathcal{H}^*$ |
| $U(t)$ | Unitary time evolution operator | dimensionless | $U = e^{-i\hat{H}t/\hbar}$ |
| $\mathcal{E}$ | CPTP map | — | $\mathcal{E}(\rho) = \sum_k K_k\rho K_k^\dagger$ |
| $\mathbb{I}$ | Identity operator | dimensionless | $\mathbb{I}|\psi\rangle = |\psi\rangle$ |
| $d$ | Hilbert space dimension | dimensionless | $d = 2^n$ for $n$ qubits |
| $n$ | Number of qubits | dimensionless | Integer $\geq 1$ |

---

## 6.6 Measurement and Tomography Symbols

| Symbol | Name | Units | Definition |
|---|---|---|---|
| $\nu$ | Number of measurement shots | dimensionless | Repetitions of experimental protocol |
| $m$ | Number of independent constraints | dimensionless | From measurement history $r$ |
| $F_Q(\rho)$ | Quantum Fisher information | dimensionless | $F_Q = \text{Tr}[\rho L^2]$; $L$ is sym. log. deriv. |
| $\hat{S}_{\text{vN}}$ | Von Neumann entropy estimator | J/K | Statistical estimate of $S_{\text{vN}}(\rho)$ |
| $\mathcal{B}_{\text{SPAM}}$ | SPAM error bias | J/K | Systematic bias from state prep./meas. errors |
| $\varepsilon$ | Estimation precision target | J/K (or bit) | Desired accuracy of $\hat{S}$ |
| $\Lambda$ | SPAM correction matrix | dimensionless | $\rho_{\text{corr}} = \Lambda^{-1}\rho_{\text{raw}}$ |

**Cramér-Rao bound notation:** The correct form is:

$$\text{Var}[\hat{S}] \geq \frac{[F_Q(\rho)]^{-1}}{\nu}$$

**Not** $\mathcal{I}_Q^{-1}(S_{\text{vN}})$ — this notation confuses the Fisher
information (a functional of $\rho$) with a function of the scalar entropy
value. The quantum Fisher information depends on the full state $\rho$, not
just its entropy.

---

## 6.7 Constraint Manifold Symbols

| Symbol | Name | Definition |
|---|---|---|
| $\mathcal{S}$ | Constraint manifold | Set of physically allowed states |
| $\mathcal{O}(r)$ | Observable subspace | States consistent with measurement history $r$ |
| $r$ | Measurement history | Ordered sequence of irreversible constraint fixations |
| $\mathcal{I}_{\text{irr}}$ | Index set of irreversible constraints | Subscript "irr" for irreversible |
| $\mathcal{I}_{\text{soft}}$ | Index set of soft constraints | Enter via measure $\mu$, not manifold definition |
| $c_i$ | Constraint value for constraint $i$ | $\text{Tr}(\hat{C}_i\rho) = c_i$ |
| $\mu(d\rho)$ | Natural measure on $\mathcal{S}$ | $\propto e^{-\beta\,\text{Tr}(\hat{H}\rho)}d\rho$ |

**Dimension formula** (n qubits, m independent constraints):

$$\dim\mathcal{O}(r) = 4^n - m - 1$$

Valid when: (i) the $m$ constraints are linearly independent as Hermitian
operators on $\mathcal{H}$, and (ii) each constraint removes exactly one
real degree of freedom.

---

## 6.8 PEIG Framework Symbols

| Symbol | Name | Range | Definition |
|---|---|---|---|
| $\mathbf{q}$ | PEIG state vector | $[0,1]^4$ | $(P, E, I, G)$ |
| $P$ | Potential dimension | $[0,1]$ | $H(\mathcal{S})/H_{\text{max}}$ |
| $E$ | Energy dimension | $[0,1]$ | Weighted sum of throughput, efficiency, robustness |
| $I$ | Identity dimension | $[0,1]$ | Weighted sum of coherence, consistency, plasticity |
| $G$ | Curvature dimension | $[-1,1]$ | $G^+ - G^-$ (positive minus negative influence) |
| $Q(\mathbf{q})$ | Quality score | $[0,1]$ | $\mathbf{w}\cdot\mathbf{q}$ |
| $\mathbf{w}$ | Weight vector | $[0,1]^4$, sums to 1 | Default: $(0.25, 0.25, 0.25, 0.25)$ |
| $\alpha$ | Identity crystallization rate | s⁻¹ | Rate at which Energy builds Identity |
| $\beta$ | Identity decay rate | s⁻¹ | Rate at which Identity dissolves without driving |
| $\Omega$ | Omega node | — | $\arg\max_{\mathbf{q}\in\mathcal{F}} Q(\mathbf{q})$ |
| $\mathcal{F}$ | Feasibility set | — | Achievable PEIG vectors under real constraints |

**PEIG dynamical equation for Identity:**

$$\frac{dI}{dt} = \alpha E - \beta I$$

Solution for constant $E$:
$$I(t) = \frac{\alpha}{\beta}E + \left(I_0 - \frac{\alpha}{\beta}E\right)e^{-\beta t}$$

Attractor: $I_\infty = \frac{\alpha}{\beta}E$, time constant $\tau = 1/\beta$.

---

## 6.9 Landauer and ETI Symbols

| Symbol | Name | Units | Definition |
|---|---|---|---|
| $\mathcal{U}$ | The universe (closed system) | — | All causally connected physical reality |
| $\mathcal{M}$ | Logical state space | — | $\{0,1\}^n$ for $n$-bit memory |
| $f$ | Logical operation | — | $f: \mathcal{M} \to \mathcal{M}$ |
| $Q_{\min}$ | Minimum heat dissipation per bit reset | J | $k_B T \ln 2$ |
| $T$ | Temperature of reservoir | K | Thermodynamic temperature |
| $\mathcal{N}(\rho)$ | Negentropy | J/K | $S_{\text{vN}}(\rho_{\text{max}}) - S_{\text{vN}}(\rho)$ |
| A1–A5 | ETI Axioms | — | See Section 05 |
| L1–L5 | ETI Lemmas | — | See Section 05 |
| P1–P3 | ETI Predictions | — | See Section 05 |

---

## 6.10 Experimental Protocol Symbols

| Symbol | Name | Units | Value |
|---|---|---|---|
| $N$ | Number of entangled atoms/qubits | dimensionless | $\geq 10^6$ (target) |
| $\delta a$ | Atom interferometer acceleration sensitivity | m/s² | $1.2\times10^{-12}$ |
| $\delta|\tilde{\kappa}|$ | Coupling constant sensitivity | dimensionless | $3.7\times10^{-13}$ |
| $\Delta a(R)$ | Differential acceleration at radius $R$ | m/s² | See entropic gravity paper |
| $R$ | Distance from coherent ensemble center | m | Variable |
| $\rho_{\text{mass}}$ | Mass density of test ensemble | kg/m³ | Specified per experiment |
| $\Delta p$ | Pressure sensitivity threshold | Pa | $< 10^{-6}$ (falsification threshold) |
| $n_{\text{runs}}$ | Number of experimental runs | dimensionless | $\geq 1000$ (falsification threshold) |

---

## 6.11 Sign Conventions Summary

**Metric:** $(-,+,+,+)$ throughout.

**Einstein equation:** 

$$G_{\mu\nu} = 8\pi G\, T_{\mu\nu}$$

with positive right-hand side for attractive sources ($T_{00} = \rho c^2 > 0$
for ordinary matter).

**Modified Einstein equation:**

$$G_{\mu\nu} = 8\pi G\, T_{\mu\nu} + \tilde{\kappa}\, \frac{c^4}{k_B\ln 2}\,
S_{\text{ent}}\, g_{\mu\nu}$$

with $\tilde{\kappa} < 0$ for repulsive entanglement-entropy contribution.

**Repulsion condition:** $\tilde{\kappa} < 0$ and $S_{\text{ent}} > 0$ together
give a negative effective pressure contribution, satisfying the repulsion
condition $\rho_{\text{grav}} + 3p_{\text{grav}}/c^2 < 0$.

**Von Neumann entropy:** $S_{\text{vN}}(\rho) = -k_B\,\text{Tr}(\rho\ln\rho)$
with the negative sign ensuring $S_{\text{vN}} \geq 0$.

**Negentropy:** $\mathcal{N}(\rho) = S_{\text{max}} - S_{\text{vN}}(\rho) \geq 0$.

**Cramér-Rao:** $\text{Var}[\hat{S}] \geq [F_Q(\rho)]^{-1}/\nu$
(not $F_Q^{-1}$ applied as a function to $S_{\text{vN}}$).

---

## 6.12 What This Repository Does Not Use

To avoid confusion, the following symbols and conventions are explicitly
**not used** in this repository, even though they appear in the source files:

| Avoided symbol | Reason | Replaced by |
|---|---|---|
| $S$ alone (unadorned) | Ambiguous between vN, Shannon, Boltzmann | Always subscripted |
| $\mathcal{I}_Q^{-1}(S_{\text{vN}})$ | Confuses Fisher info with function of scalar | $[F_Q(\rho)]^{-1}$ |
| $\kappa$ alone for dimensionless coupling | Ambiguous with surface gravity | $\tilde{\kappa}$ for dimensionless |
| "Bit" with physical units | Bits are dimensionless | Convert: $\mathcal{S} = I\cdot k_B\ln 2$ |
| $\alpha_{\text{screen}} \in [10^{-5}, 10^{-3}]$ | Appears once erroneously | Always: $[10^{-4}, 10^{-2}]$ |
| $S_{\text{ent}} \to \mathcal{N}$ substitution | Logically contradictory — see §2.6 | Never substitute negentropy for entropy |

---

## Cross-References

This section applies to every file in this repository. When reading any paper
or document, return here for symbol definitions. Discrepancies between this
section and any other file in the repository should be reported as issues on
GitHub and resolved in favor of this section.

- **Section 01–05** — All symbols used in those sections are defined here
- **01_PHYSICS_CORE/** — All physics papers use the conventions in §6.2–6.6
- **03_PEIG_FRAMEWORK/** — All PEIG documents use the conventions in §6.8
- **02_MATHEMATICAL_CORRECTIONS/** — Corrected equations use these symbols
