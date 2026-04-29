# Section 03 — The Constraint Manifold

**Repository:** Monette Research — Entropic Gravity & PEIG Framework  
**Section:** 00_FOUNDATIONAL_DEFINITIONS  
**Status:** Canonical Definition  
**Last Updated:** March 2026

---

## Purpose

This section defines the constraint manifold formalism — the mathematical
framework that describes which quantum states are physically accessible given
the laws of physics and the accumulated measurement history. It explains
precisely why NISQ quantum devices show apparent entropy plateaus at 40–50%,
why this is a measurement artifact rather than physical decoherence, and how
many measurement shots are required to escape this artifact. The full theoretical
treatment and experimental protocol appear in `01_PHYSICS_CORE/B_CONSTRAINT_MANIFOLDS/`.

---

## 3.1 The Space of Density Operators

A quantum system with $n$ qubits lives in a Hilbert space $\mathcal{H}$ of
dimension $\dim(\mathcal{H}) = 2^n$.

The **space of all valid quantum states** (density operators) is:

$$\mathcal{D}(\mathcal{H}) = \left\{ \rho \in \text{End}(\mathcal{H})
\;\middle|\; \rho \geq 0, \; \text{Tr}(\rho) = 1, \; \rho = \rho^\dagger \right\}$$

In plain terms: a density operator $\rho$ must be:
- **Positive semidefinite** ($\rho \geq 0$): all eigenvalues are non-negative,
  ensuring probabilities are non-negative
- **Unit trace** ($\text{Tr}(\rho) = 1$): probabilities sum to one
- **Hermitian** ($\rho = \rho^\dagger$): the matrix equals its conjugate
  transpose, ensuring all eigenvalues are real

The **real dimension** of $\mathcal{D}(\mathcal{H})$ for $n$ qubits is $4^n - 1$.
This means a general $n$-qubit state requires $4^n - 1$ real numbers to specify
completely. For $n = 10$ qubits, that is $4^{10} - 1 \approx 10^6$ parameters.
For $n = 50$ qubits, it is $4^{50} - 1 \approx 10^{30}$ parameters — utterly
inaccessible to any finite experiment.

---

## 3.2 The Constraint Manifold — $\mathcal{S}$

Physical quantum states do not wander freely through all of
$\mathcal{D}(\mathcal{H})$. They are restricted by conservation laws and
irreversible processes to a much smaller subset called the **constraint
manifold**:

$$\mathcal{S} = \left\{ \rho \in \mathcal{D}(\mathcal{H})
\;\middle|\; \text{Tr}(\hat{C}_i \rho) = c_i \;\; \forall i \in \mathcal{I}_{\text{irr}} \right\}$$

where:

- $\hat{C}_i$ are **constraint operators** — Hermitian operators whose
  expectation values are fixed by the physics of the system. Examples:
  - $\hat{H}$ (Hamiltonian): fixes the total energy $\text{Tr}(\hat{H}\rho) = E$
  - $\hat{Q}$ (charge operator): fixes the total charge
  - $\hat{N}$ (number operator): fixes particle number in a conserved sector
- $c_i$ are the **constraint values** — the specific numbers fixed by the
  initial conditions and history of the system
- $\mathcal{I}_{\text{irr}}$ is the **index set of irreversible constraints** —
  those constraints that have been fixed by processes that cannot be undone by
  any unitary evolution. A constraint that *could* be reversed is not yet part
  of the constraint manifold.

**Physical meaning:** $\mathcal{S}$ is the set of all density matrices that are
consistent with everything we know cannot change — the conserved quantities and
the irreversible history. It is the quantum analog of the "allowed states"
$\mathcal{S}$ from Section 01, now made mathematically explicit.

---

## 3.3 Soft Constraints — The Measure on $\mathcal{S}$

Not all constraints are hard (fixed exactly). Some constraints are **soft** —
they bias the probability distribution over $\mathcal{S}$ without eliminating
states outright. The primary example is thermodynamic equilibrium:

$$\mu(d\rho) \propto e^{-\beta \, \text{Tr}(\hat{H}\rho)} \, d\rho$$

where $\beta = 1/(k_B T)$ is the inverse temperature. This is the Gibbs
measure — it assigns higher probability to lower-energy states in proportion
to the Boltzmann factor $e^{-\beta E}$, without hard-excluding any energy.

**Distinction from hard constraints:**
- Hard constraints: $\text{Tr}(\hat{C}_i \rho) = c_i$ exactly — defines the
  manifold $\mathcal{S}$ itself
- Soft constraints: $\mu(d\rho) \propto e^{-\beta \text{Tr}(\hat{H}\rho)}$
  — defines the natural measure on $\mathcal{S}$

In practice, energy conservation is a hard constraint (total energy is fixed in
a closed system) while thermodynamic equilibrium is a soft constraint (the
system is biased toward lower-energy configurations but can fluctuate).

---

## 3.4 The Observable Subspace — $\mathcal{O}(r)$

When measurements are performed on the system, each measurement outcome
fixes an additional constraint. The sequence of all measurement outcomes up to
the present is the measurement history:

$$r = \{i_1, i_2, \ldots, i_k\}$$

Each element $i_j$ corresponds to a constraint $\text{Tr}(\hat{C}_{i_j}\rho)
= c_{i_j}$ that became irreversible when the measurement outcome was recorded.

The **observable subspace** is the portion of the constraint manifold consistent
with the full measurement history:

$$\mathcal{O}(r) = \left\{ \rho \in \mathcal{S}
\;\middle|\; \text{Tr}(\hat{C}_{i_j}\rho) = c_{i_j} \;\; \forall j \leq k \right\}$$

**Critically:** $\dim \mathcal{O}(r)$ *decreases* as more measurements are
made. Every additional independent constraint eliminates one real degree of
freedom from the accessible state space.

For $n$ qubits with $m$ independent measurement constraints:

$$\dim \mathcal{O}(r) = 4^n - m - 1$$

The $-1$ accounts for the trace normalization $\text{Tr}(\rho) = 1$ which is
always present.

**Important caveat:** This formula assumes the $m$ constraints are **linearly
independent** as operators on $\mathcal{H}$. If some constraints are redundant
(e.g., the constraint from measuring $\hat{A}$ is algebraically implied by
constraints from measuring $\hat{B}$ and $\hat{C}$), fewer than $m$ dimensions
are eliminated.

---

## 3.5 The Measurement Insufficiency Problem

When $m \ll 4^n$ — that is, when far fewer measurements have been made than
there are degrees of freedom in the state — the observable subspace
$\mathcal{O}(r)$ vastly under-samples the physical state space $\mathcal{S}$.

**The consequence:** Any estimator of the von Neumann entropy constructed
from these $m$ measurements will have **systematic bias** — it will
overestimate the true entropy because it cannot distinguish a genuinely
high-entropy (mixed) state from a low-entropy (pure or nearly pure) state that
simply hasn't been measured thoroughly enough to reveal its structure.

This is not a failure of the quantum hardware. It is a failure of the
measurement budget. The hardware may be in a nearly pure state while the
estimator reports high entropy — because the estimator doesn't have enough
information to see the purity.

**This is the origin of the 40–50% entropy plateau** observed in NISQ
experiments with 16–23+ qubits.

---

## 3.6 The Entropy Estimator and Its Bias

The standard **linear inversion entropy estimator** $\hat{S}_{\text{vN}}$
computes the von Neumann entropy of the density matrix reconstructed from
measurement outcomes. Its expected value satisfies:

$$\mathbb{E}[\hat{S}_{\text{vN}}] = S_{\text{vN}}(\rho) +
\underbrace{\frac{d-1}{2\nu}}_{\text{finite-sampling bias}} +
\underbrace{\mathcal{B}_{\text{SPAM}}}_{\text{readout errors}}$$

where:
- $S_{\text{vN}}(\rho)$ is the **true** von Neumann entropy of the physical
  state
- $d = 2^n$ is the Hilbert space dimension ($d = 1024$ for $n = 10$ qubits;
  $d \approx 3.3 \times 10^4$ for $n = 15$ qubits)
- $\nu$ is the **number of measurement shots** (repetitions of the experiment
  used to estimate probabilities)
- $(d-1)/(2\nu)$ is the **finite-sampling bias** — it is large when $d$ is
  large (many qubits) and $\nu$ is small (few shots)
- $\mathcal{B}_{\text{SPAM}}$ is the **State Preparation and Measurement
  (SPAM) error bias** — systematic errors from imperfect qubit initialization
  and readout, typically $\sim 0.5$–$1.0$ bits on current hardware

**Worked example ($n = 15$ qubits, $\nu = 10^4$ shots):**

$$d = 2^{15} \approx 3.3 \times 10^4$$

$$\text{Finite-sampling bias} = \frac{d-1}{2\nu} = \frac{3.3 \times 10^4 - 1}
{2 \times 10^4} \approx 1.65 \text{ bits}$$

The maximum possible entropy for 15 qubits is:
$$S_{\text{vN,max}} = 15 \times k_B \ln 2 \approx 10.4 \text{ bits}$$

So even for a **perfectly pure state** (true entropy = 0 bits), the estimator
reports:
$$\mathbb{E}[\hat{S}_{\text{vN}}] \approx 0 + 1.65 + \mathcal{B}_{\text{SPAM}}
\approx 2.15\text{–}2.65 \text{ bits}$$

As a fraction of maximum: $2.65/10.4 \approx 25\%$. Adding SPAM errors typical
of current hardware brings this to 40–50% of maximum — **exactly matching the
experimentally observed plateau**, without invoking any physical decoherence.

---

## 3.7 The Quantum Fisher Information and Required Shot Scaling

The variance of any **unbiased** entropy estimator $\hat{S}$ satisfies the
**quantum Cramér-Rao bound**:

$$\text{Var}[\hat{S}] \geq \frac{[F_Q(\rho)]^{-1}}{\nu}$$

where:
- $\nu$ is the number of measurement shots
- $F_Q(\rho) = \text{Tr}[\rho L^2]$ is the **quantum Fisher information**,
  with $L$ the symmetric logarithmic derivative defined implicitly by
  $\partial_\theta \rho = (\rho L + L\rho)/2$
- $[F_Q(\rho)]^{-1}$ is the reciprocal of the quantum Fisher information —
  the fundamental lower bound on estimator variance per shot

**Notation clarification:** The quantum Fisher information $F_Q(\rho)$ is a
functional of the state $\rho$, not of the scalar entropy value. Writing
$F_Q(S_{\text{vN}})$ (as sometimes appears in the literature) is an abuse of
notation — it means $F_Q$ evaluated at the state $\rho$ that has entropy
$S_{\text{vN}}(\rho)$.

For states near the **maximally mixed state** $\rho \approx \mathbb{I}/2^n$
(which is where undersampled states appear to lie):

$$F_Q(\rho) \sim 2^{-n/2}$$

This is an **exponential suppression** in qubit number. Entropy is a global
property of the full $2^n$-dimensional state — extracting it requires
interference between all $2^n$ basis states. Near the maximally mixed state,
all these interference terms are equally small, making entropy extremely hard
to estimate precisely.

**Consequence for required shots:** To achieve entropy estimation precision $\varepsilon$ (in bits), the required number of shots is:

$$\nu \gtrsim \varepsilon^{-2} \cdot 2^{n/2}$$

| $n$ (qubits) | Required shots ($\varepsilon = 0.1$ bits) | Typical NISQ budget | Gap |
|---|---|---|---|
| 5 | $10^3$ | $10^3$ | None — feasible now |
| 10 | $\sim 3 \times 10^4$ | $10^3$ | 30× underpowered |
| 15 | $\sim 10^5$ | $10^4$ | 10× underpowered |
| 20 | $\sim 3 \times 10^5$ | $10^4$ | 30× underpowered |
| 50 | $\sim 10^8$ | $10^4$ | $10^4$× underpowered |

The exponential scaling of required shots with $n/2$ means that brute-force
tomography becomes infeasible rapidly. This is not a limitation of current
hardware — it is a fundamental consequence of the quantum Fisher information
suppression.

---

## 3.8 The Falsification Criterion for Measurement Insufficiency

The measurement-insufficiency hypothesis — that the 40–50% plateau is a
sampling artifact — is falsifiable via the following criterion:

> **If** entropy estimates for $n$-qubit coherent states (e.g., GHZ states
> $|\text{GHZ}\rangle = (|0\rangle^{\otimes n} + |1\rangle^{\otimes n})/\sqrt{2}$)
> **fail to converge** to $S_{\text{vN}} < 0.1$ bits when:
> - Shot count $\nu \geq 100 \cdot 2^{n/2}$
> - SPAM correction applied via measurement calibration matrix $\Lambda$:
>   $\rho_{\text{corr}} = \Lambda^{-1}\rho_{\text{raw}}$
> - Convergence verified via bootstrap resampling (not just point estimate)
>
> **Then** the measurement-insufficiency hypothesis is **falsified**, and the
> remaining entropy reflects genuine physical decoherence beyond measurement
> limits.

Convergence to $S_{\text{vN}} < 0.1$ bits under these conditions would
confirm that the plateau is entirely a measurement artifact.

---

## 3.9 Bias Correction Formula

The explicit bias-corrected entropy estimator is:

$$\hat{S}_{\text{vN}}^{\text{corr}}(\nu) = \hat{S}_{\text{vN}}^{\text{raw}}
- \frac{d-1}{2\nu} - \hat{\mathcal{B}}_{\text{SPAM}}$$

where $\hat{\mathcal{B}}_{\text{SPAM}}$ is estimated from calibration circuits
run on the same hardware. Under the measurement-insufficiency hypothesis, the
corrected estimator should satisfy:

$$\hat{S}_{\text{vN}}^{\text{corr}}(\nu) \xrightarrow{\nu \to \infty} S_{\text{vN}}(\rho)$$

For a coherent GHZ state (true entropy ≈ 0), the corrected estimator should
converge to zero as shots increase, following:

$$\mathbb{E}[\hat{S}_{\text{vN}}^{\text{corr}}(\nu)] = \frac{d-1}{2\nu}
+ \mathcal{O}(\nu^{-2})$$

A measured deviation from this $1/\nu$ scaling law indicates physical
decoherence beyond the measurement limit.

---

## Cross-References

- **Section 01** — Universe and History: $\mathcal{O}(r)$ as the formal
  mathematical realization of conditioning on history $r$
- **Section 02** — Entropy and Information: the von Neumann entropy that
  is being estimated and the units it is measured in
- **Section 06** — Notation and Conventions: symbol definitions
- **01_PHYSICS_CORE/B_CONSTRAINT_MANIFOLDS/** — full paper with
  complete derivations and experimental protocol
- **01_PHYSICS_CORE/A_ENTROPIC_GRAVITY/** — connection between constraint
  fixation and entropy gradients that source spacetime curvature
