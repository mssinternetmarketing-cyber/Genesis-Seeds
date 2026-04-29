# Section 02 — Entropy and Information

**Repository:** Monette Research — Entropic Gravity & PEIG Framework  
**Section:** 00_FOUNDATIONAL_DEFINITIONS  
**Status:** Canonical Definition  
**Last Updated:** March 2026

---

## Purpose

This section defines every entropy-related quantity used across the research
program, resolves the critical distinction between information-theoretic and
thermodynamic entropy, and establishes the **bit-to-entropy conversion protocol**
that ensures dimensional consistency throughout all physics calculations.

Failing to distinguish these quantities precisely is the single most common
source of error in information-theoretic gravity papers. Every equation in this
repository uses the definitions established here.

---

## 2.1 Boltzmann Entropy — The Counting Definition

The most fundamental definition of entropy comes from statistical mechanics. For
a system with $\Omega$ equally accessible microstates:

$$S = k_B \ln \Omega$$

where:
- $S$ is the **thermodynamic entropy** — a physical quantity with units of
  joules per kelvin (J/K)
- $k_B = 1.380649 \times 10^{-23}$ J/K is **Boltzmann's constant**, the
  conversion factor between temperature (an average kinetic energy) and entropy
  (a count of accessible states)
- $\Omega$ is the **number of accessible microstates** — a pure dimensionless
  count

**Physical meaning:** Entropy measures how many different microscopic
arrangements of a system are consistent with its macroscopic description. A
high-entropy state is one where many microscopic arrangements look the same from
the outside. A low-entropy state is one where very few arrangements are
consistent with the observable macroscopic description.

**For a closed quantum system (the universe):** The second law of thermodynamics
requires:

$$\frac{dS_{\text{universe}}}{dt} \geq 0$$

Entropy of the closed universe never decreases. It can increase (irreversible
processes) or remain constant (perfectly reversible processes, which are
idealizations). It can never decrease. This is not a law imposed from outside —
it follows from the counting definition combined with the overwhelming
probability that systems evolve toward configurations accessible in more ways.

---

## 2.2 Von Neumann Entropy — The Quantum Definition

For a quantum system described by a density operator $\rho$ (a positive
semidefinite, Hermitian matrix with unit trace acting on Hilbert space
$\mathcal{H}$), the quantum generalization of entropy is:

$$S_{\text{vN}}(\rho) = -k_B \, \text{Tr}(\rho \ln \rho)$$

**How to read this formula step by step:**

1. $\rho$ is the **density matrix** — a complete description of the quantum
   state of a system, including all quantum superpositions and classical
   statistical mixtures. For a pure state $|\psi\rangle$, it equals
   $\rho = |\psi\rangle\langle\psi|$.
2. $\ln \rho$ is the **matrix logarithm** of $\rho$. If $\rho$ has eigenvalues
   $\lambda_i$ (which are real, non-negative, and sum to 1 because $\rho$ is a
   valid density matrix), then $\ln \rho$ has eigenvalues $\ln \lambda_i$.
3. $\rho \ln \rho$ is the **matrix product** of $\rho$ with its own logarithm.
4. $\text{Tr}(\rho \ln \rho) = \sum_i \lambda_i \ln \lambda_i$ is the
   **trace** — the sum of diagonal elements, which equals the sum of eigenvalues.
5. The negative sign ensures that $S_{\text{vN}} \geq 0$ always, since
   $\lambda_i \in [0,1]$ implies $\ln \lambda_i \leq 0$, making
   $\sum_i \lambda_i \ln \lambda_i \leq 0$.

**Special cases:**
- **Pure state** $\rho = |\psi\rangle\langle\psi|$: All eigenvalues are 0
  except one which equals 1. Therefore $S_{\text{vN}} = -k_B(1 \cdot \ln 1)
  = 0$. A pure state has zero entropy — it is perfectly known.
- **Maximally mixed state** $\rho = \mathbb{I}/d$ where $d$ is the Hilbert
  space dimension: All $d$ eigenvalues equal $1/d$. Therefore
  $S_{\text{vN}} = -k_B \sum_{i=1}^d (1/d)\ln(1/d) = k_B \ln d$. This is
  maximum entropy — the state of complete ignorance.

**For $n$ qubits:** The Hilbert space dimension is $d = 2^n$, so:
$$S_{\text{vN,max}} = k_B \ln(2^n) = n \cdot k_B \ln 2$$

This is the maximum possible entropy for an $n$-qubit system.

---

## 2.3 Shannon Entropy — The Information-Theoretic Definition

For a discrete probability distribution $\{p_i\}$ over outcomes
$\{x_1, x_2, \ldots, x_n\}$:

$$H = -\sum_i p_i \log_2 p_i$$

where:
- $H$ is **Shannon entropy**, measured in **bits** (because $\log_2$ is used)
- $p_i$ is the probability of outcome $x_i$, with $\sum_i p_i = 1$
- The **bit** here is a counting unit — it is **dimensionless**

**Physical meaning:** Shannon entropy measures the average number of binary
questions you need to ask to identify which outcome occurred. If $H = 3$ bits,
you need approximately 3 yes/no questions on average to identify the outcome.

**Relationship to von Neumann entropy:** Von Neumann entropy is the quantum
generalization of Shannon entropy. When the density matrix $\rho$ is diagonal
(i.e., the quantum system has no coherence — only classical probabilities), the
von Neumann entropy equals the Shannon entropy of those diagonal probabilities:

$$S_{\text{vN}}(\rho_{\text{diagonal}}) = k_B \ln 2 \cdot H(\{p_i\})$$

The factor $k_B \ln 2$ converts bits (Shannon, dimensionless) into joules per
kelvin (thermodynamic, physical units).

---

## 2.4 The Bit-to-Entropy Conversion Protocol

This conversion is the most critical dimensional bookkeeping step in this
entire research program. **All errors in entropic gravity literature that involve
inconsistent units trace back to mishandling this conversion.**

**The fundamental conversion:**

$$\mathcal{S} = I \cdot k_B \ln 2$$

where:
- $I$ is information measured in **bits** — a **dimensionless** counting unit
- $\mathcal{S}$ is thermodynamic entropy measured in **J/K** — a physical
  quantity
- $k_B = 1.380649 \times 10^{-23}$ J/K is Boltzmann's constant
- $\ln 2 \approx 0.6931$ is dimensionless — it arises because Shannon entropy
  uses $\log_2$ while thermodynamic entropy uses $\ln = \log_e$

**The complete conversion table** (canonical for this repository):

| Quantity | Symbol | Units | Definition |
|---|---|---|---|
| Information (counting) | $I$ | dimensionless (bit) | $I = -\sum_i p_i \log_2 p_i$ |
| Thermodynamic entropy | $\mathcal{S}$ | J/K | $\mathcal{S} = I \cdot k_B \ln 2$ |
| Entanglement entropy density | $S_{\text{ent}}$ | bit/m³ | $S_{\text{ent}} = I/V$ |
| Physical entropy density | $\mathcal{S}_{\text{ent}}$ | J/(K·m³) | $\mathcal{S}_{\text{ent}} = S_{\text{ent}} \cdot k_B \ln 2$ |

**Why this matters for the modified Einstein equation:**

The Einstein tensor $G_{\mu\nu}$ has units of m⁻². The stress-energy tensor
$T_{\mu\nu}$ has units of kg·m⁻¹·s⁻² (equivalently, Pa = N/m² = J/m³). For
the entanglement entropy source term to have the same units as $T_{\mu\nu}$
after multiplication by $8\pi G$ (units: m·kg⁻¹·s⁻²), the entropy density must
enter in physical units J/(K·m³), not dimensionless bit/m³.

This is why the coupling constant in the modified Einstein equation takes the
form $\tilde{\kappa} \cdot c^4/(k_B \ln 2)$ — the factor $c^4/(k_B \ln 2)$
converts entanglement entropy density (bit/m³) into units compatible with the
stress-energy tensor. See Section 03 and `01_PHYSICS_CORE/A_ENTROPIC_GRAVITY`
for the full dimensional verification.

---

## 2.5 Entanglement Entropy — The Quantum Correlation Measure

When a quantum system is divided into two subsystems $A$ and $B$
(so the total Hilbert space $\mathcal{H} = \mathcal{H}_A \otimes \mathcal{H}_B$),
the **entanglement entropy** of subsystem $A$ is:

$$S_{\text{ent}}(A) = S_{\text{vN}}(\rho_A) = -k_B \, \text{Tr}(\rho_A \ln \rho_A)$$

where $\rho_A = \text{Tr}_B(\rho_{AB})$ is the **reduced density matrix** of $A$,
obtained by tracing over (averaging out) all degrees of freedom of subsystem $B$.

**Physical meaning:** Entanglement entropy measures how much quantum information
is shared between $A$ and $B$ — how much of what happens in $A$ is correlated
with what happens in $B$ in a way that cannot be explained by any classical
probability distribution. A pure product state $|\psi\rangle = |\phi\rangle_A
\otimes |\chi\rangle_B$ has $S_{\text{ent}}(A) = 0$ — no entanglement. A
maximally entangled Bell state has $S_{\text{ent}}(A) = k_B \ln 2$ per qubit
pair.

**Key distinction — vacuum vs. operational entanglement entropy:**

| Type | Symbol | Scale | Law | Relevant to gravity? |
|---|---|---|---|---|
| Vacuum entanglement | $S_{\text{vac}}$ | Planck scale | Area law: $S_{\text{vac}} \propto A/4G$ | Yes, at causal horizons |
| Operational entanglement | $S_{\text{ent}}^{(\text{op})}$ | Laboratory scale | Volume law | Hypothesis: yes |

The **vacuum entanglement entropy** is the entanglement of quantum fields across
a causal boundary (like a black hole horizon). It obeys an area law — it scales
with the area of the boundary, not the volume of the region. This is the basis
of the Bekenstein-Hawking entropy formula.

The **operational entanglement entropy** is the entanglement in a finite
laboratory system after tracing over environmental and high-energy degrees of
freedom. It is defined as:

$$S_{\text{ent}}^{(\text{op})} = \int \frac{S_{\text{ent}}}{V} \, dV$$

This is the quantity that appears in the modified Einstein equation in this
research program. It is **not** the same as vacuum entanglement in the
holographic sense. The extension from vacuum (horizon-area) entanglement to
operational (laboratory-volume) entanglement is an explicit extrapolation
hypothesis — see `01_PHYSICS_CORE/A_ENTROPIC_GRAVITY/sections/
03_extrapolation_boundary.tex` for the precise statement of what is proven vs.
what is hypothesized.

---

## 2.6 Negentropy — Deviation from Maximum Disorder

**Definition:** For a state $\rho$ on a Hilbert space with maximally mixed
reference state $\rho_{\text{max}} = \mathbb{I}/d$:

$$\mathcal{N}(\rho) = S_{\text{vN}}(\rho_{\text{max}}) - S_{\text{vN}}(\rho)
= k_B \ln d - S_{\text{vN}}(\rho)$$

**Physical meaning:** Negentropy measures how far a system is from maximum
disorder. A pure state (zero entropy) has maximum negentropy $k_B \ln d$. The
maximally mixed state has zero negentropy.

**Critical warnings about negentropy in this framework:**

1. **Negentropy is not conserved.** Unlike energy or charge, negentropy can be
   created (by measurement, cooling, or information erasure) and destroyed (by
   decoherence and thermalization). It is not a conserved charge.

2. **Negentropy is not the same as Shannon information.** It is a thermodynamic
   quantity measuring physical structure relative to a reference, not an
   abstract count of distinguishable messages.

3. **Negentropy cannot be substituted for entanglement entropy in the modified
   Einstein equation.** This substitution produces a logical contradiction:
   a maximally entangled state (high $S_{\text{ent}}$, maximum repulsive
   curvature) has *zero* negentropy, while a pure unentangled state (zero
   $S_{\text{ent}}$, zero repulsive curvature) has *maximum* negentropy. The
   two quantities make opposite physical predictions and must not be conflated.
   The gravitational source term uses $S_{\text{ent}}$ (absolute entropy
   density), not $\mathcal{N}$ (relative negentropy).

4. **Negentropy is used in the PEIG framework** (Section 04) as a measure of
   system identity and structure, where the context is cognitive/systems science
   rather than gravitational physics. In that context, the distinction from
   entanglement entropy must still be maintained.

---

## 2.7 Entropy Partitioning — Universe Sectors

For the purposes of this research program, we partition the total entropy of
the universe into operationally distinct sectors:

$$S_{\text{universe}} = S_{\text{matter}} + S_{\text{ent}}^{(\text{env})} \geq \text{constant}$$

where:
- $S_{\text{matter}}$ is the entropy of ordinary matter degrees of freedom
  (thermal, kinetic, chemical)
- $S_{\text{ent}}^{(\text{env})}$ is the entropy associated with vacuum
  correlations and coarse-grained entanglement degrees of freedom

**Physical interpretation of the inequality:** No physical process destroys
global quantum state accessibility. Entropy may be redistributed between sectors
(e.g., matter entropy decreasing while entanglement entropy increases during a
measurement) but the total cannot decrease. This is the second law applied at
the level of the full quantum state of the universe.

---

## 2.8 Entropy Density — The Local Field Quantity

For the modified Einstein equation to be a local field equation (as general
relativity requires — it relates curvature at a point to source density at that
same point), entropy must be expressed as a **density**:

$$\rho_S(\mathbf{x}) = \frac{S_{\text{ent}}}{V}$$

with units of bit/m³ (dimensionless entropy per unit volume). The corresponding
physical entropy density is:

$$\mathcal{S}_{\text{ent}}(\mathbf{x}) = \rho_S(\mathbf{x}) \cdot k_B \ln 2
\quad \text{[J/(K·m³)]}$$

The spatial gradient of entropy density:

$$\nabla \rho_S = \nabla \left(\frac{S_{\text{ent}}}{V}\right)$$

measures how quantum correlations vary across space. A nonzero gradient means
entanglement is inhomogeneous — more concentrated in some regions than others.
This inhomogeneity is the proposed physical driver of gravitational effects in
the entropic gravity framework.

**Area law vs. volume law:** In holographic systems at causal horizons, entropy
scales with area: $S \propto A$. In the laboratory systems considered here,
entropy scales with volume: $S \propto V$. This difference is physically
significant and is the reason the extrapolation from horizon physics to
laboratory physics is a hypothesis rather than a derivation.

---

## Cross-References

- **Section 01** — Universe and History: the ontological context in which
  entropy is defined
- **Section 03** — Constraint Manifold: how entropy is estimated in finite-shot
  quantum tomography and why that estimation fails at large qubit number
- **Section 06** — Notation and Conventions: complete symbol table
- **01_PHYSICS_CORE/A_ENTROPIC_GRAVITY** — the modified Einstein equation
  where $S_{\text{ent}}$ appears as a gravitational source term
- **01_PHYSICS_CORE/B_CONSTRAINT_MANIFOLDS** — the von Neumann entropy
  estimator bias analysis and shot-scaling requirements
- **01_PHYSICS_CORE/C_LANDAUER_ETI** — the thermodynamic cost of
  logically irreversible operations, expressed in terms of $k_B T \ln 2$
