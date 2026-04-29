# Notation Standards
## Authoritative Symbol Reference for the Monette Research Repository

**Folder:** `00_FOUNDATIONAL_DEFINITIONS/`  
**Purpose:** Every mathematical symbol used in this repository is defined exactly once, here. When symbols conflict between source documents, this file is the resolution authority. All papers in `01_PHYSICS_CORE/` follow these standards without exception.

---

## 1. GREEK LETTERS

| Symbol | Name | Definition | Units | First appears |
|--------|------|-----------|-------|---------------|
| α_screen | Alpha screen | Environmental screening factor | dimensionless | `A_ENTROPIC_GRAVITY/sections/03` |
| κ | Kappa (dimensionful) | Full coupling constant in G_μν = 8πG(T_μν + κ S_ent g_μν) | m⁵·kg⁻¹·s⁻²·bit⁻¹ | `A_ENTROPIC_GRAVITY/sections/01` |
| κ̃ | Kappa-tilde | Dimensionless coupling constant; κ = (c⁴/8πG) · κ̃ · (1/k_B ln 2) | dimensionless | `A_ENTROPIC_GRAVITY/sections/01` |
| ρ | Rho | (1) Quantum state density matrix, OR (2) mass density | kg/m³ or dimensionless | context-dependent |
| ρ_I | Rho-I | Entanglement entropy density (counting units) | bit/m³ | `A_ENTROPIC_GRAVITY/sections/01` |
| ξ | Xi | Coherence length in screening factor | m | `A_ENTROPIC_GRAVITY/sections/03` |
| Γ | Gamma | Decoherence rate | s⁻¹ | `A_ENTROPIC_GRAVITY/sections/03` |
| τ_D | Tau-D | Decoherence time = 1/Γ | s | `A_ENTROPIC_GRAVITY/sections/03` |
| ε | Epsilon | Precision parameter for entropy estimation | bits | `B_CONSTRAINT_MANIFOLDS` |
| ν | Nu | Number of measurement shots (tomography budget) | dimensionless (integer) | `B_CONSTRAINT_MANIFOLDS` |
| μ | Mu | Measure on constraint manifold | — | `B_CONSTRAINT_MANIFOLDS` |
| β | Beta | Inverse temperature β = 1/(k_B T) | J⁻¹ | `B_CONSTRAINT_MANIFOLDS` |
| ℓ_P | Planck length | √(ℏG/c³) = 1.616 × 10⁻³⁵ m | m | `A_ENTROPIC_GRAVITY/sections/02` |

---

## 2. LATIN SYMBOLS

| Symbol | Definition | Units |
|--------|-----------|-------|
| S_vN(ρ) | Von Neumann entropy: -Tr(ρ ln ρ) | nats (or bits if log base 2) |
| S_ent | Entanglement entropy density (bit/m³). **Always a density, not total entropy.** | bit/m³ |
| S_max | Maximum entropy of a system (entropy of maximally mixed state) | bits or nats |
| N(ρ) | Negentropy: S_max - S_vN(ρ). **Distinct from S_ent.** | bits or nats |
| F_Q(ρ) | Quantum Fisher information: Tr[ρ L²] where L is symmetric log derivative | bits⁻¹ (or nats⁻¹) |
| G_μν | Einstein tensor: R_μν - (1/2)R g_μν | m⁻² |
| T_μν | Stress-energy tensor (standard matter/energy) | kg·m⁻¹·s⁻² |
| g_μν | Metric tensor | dimensionless |
| R_μν | Ricci curvature tensor | m⁻² |
| R | Ricci scalar (trace of Ricci tensor) | m⁻² |
| H | Hilbert space of the quantum system | — |
| D(H) | Space of density operators on H | — |
| C | Constraint manifold: subspace of D(H) satisfying irreversible constraints | — |
| O(r) | Observable subspace given measurement history r | — |
| Ĉ_i | Constraint operators (energy, charge, etc.) | system-dependent |
| c_i | Constraint values (eigenvalues of Ĉ_i) | system-dependent |
| I_irr | Index set of irreversible constraints | — |
| Δa(R) | Differential acceleration at radius R | m/s² |
| Var[Ŝ] | Variance of entropy estimator | bits² |
| B_SPAM | Systematic SPAM error bias on entropy estimate | bits |
| n | Qubit count | dimensionless (integer) |
| d | Hilbert space dimension: d = 2^n | dimensionless |
| m | Number of independent measurement constraints | dimensionless |

---

## 3. PHYSICAL CONSTANTS

| Constant | Symbol | Value | Units |
|---------|--------|-------|-------|
| Speed of light | c | 2.997924 × 10⁸ | m/s |
| Gravitational constant | G | 6.674 × 10⁻¹¹ | m³·kg⁻¹·s⁻² |
| Reduced Planck constant | ℏ | 1.054571 × 10⁻³⁴ | J·s |
| Boltzmann constant | k_B | 1.380649 × 10⁻²³ | J/K |
| Planck length | ℓ_P | 1.616255 × 10⁻³⁵ | m |
| Planck mass | m_P | 2.176434 × 10⁻⁸ | kg |
| Planck energy | E_P | 1.956082 × 10⁹ | J |
| k_B ln 2 | — | 9.5699 × 10⁻²⁴ | J/K (the bit-to-entropy conversion factor) |

---

## 4. CRITICAL DISAMBIGUATION TABLE

Several symbols have multiple uses in the source literature and have been standardized here:

| Ambiguity | Resolution | Rationale |
|-----------|-----------|-----------|
| S_vN vs S_ent vs S(ρ) | Always use S_vN(ρ) for von Neumann entropy of state ρ; always use S_ent for entanglement entropy *density* (bit/m³) | Prevents confusion between a state-property and a density field |
| κ vs κ̃ | κ (no tilde) is always the dimensionful coupling; κ̃ (with tilde) is always dimensionless. Never use κ alone when meaning the dimensionless version. | Dimensional errors in source material (see MA1, MA2 in mathematical corrections) |
| "bit" vs "qubit" vs "dimensionless" | "bit" = counting unit (Shannon); "qubit" = physical system implementing 2-state quantum system. Never write S_ent in units of "qubits" — use "bits" | Source documents used all three inconsistently |
| S_ent as density vs total entropy | S_ent is *always* a density (bit/m³ or J/(K·m³)). If total entropy is meant, write S_total or S_BH (Bekenstein-Hawking). | W6 in audit: source documents switched between usage causing sign error |
| N as negentropy vs N as qubit count | N(ρ) with explicit argument = negentropy. N as italic integer = qubit count. Never ambiguous in context. | — |
| G as Newton's constant vs G in PEIG | G (roman) = Newton's gravitational constant. G (italic, in P/E/I/G) = Geometry phase. Never appear in same equation. | Disambiguation required for PEIG ↔ gravity bridge documents |
| F_Q vs I_Q for quantum Fisher information | Use F_Q throughout. I_Q used in main.tex (source) is non-standard. | Literature standard is F or F_Q |
| α_screen range | [10⁻⁴, 10⁻²] is canonical. One source document wrote [10⁻⁵, 10⁻³]; this was a transcription error. | Resolved in favor of majority of source documents |

---

## 5. EQUATION FORMATTING CONVENTIONS

All equations in this repository follow these rules:

1. **LaTeX notation for all multi-symbol expressions.** Plain text is used only for very simple relationships (e.g., "κ̃ = -1/4").

2. **Equation numbering:** Each file uses its own numbering (1), (2), (3)... Cross-references cite file and equation: e.g., "Eq. (A1.3)" = file A_ENTROPIC_GRAVITY/sections/01_theory.md, equation 3.

3. **Variable definition on first use.** Every variable is explicitly defined the first time it appears in each document — not assumed from another file.

4. **Units in brackets.** When stating dimensions: [G_μν] = m⁻². This notation is used in dimensional verification passages.

5. **Epistemic labels on equations.** Equations that are [ESTABLISHED] carry no label. Equations that are [DERIVED] within this framework are so labeled. Equations that are [HYPOTHESIS] or [OPEN PROBLEM] are explicitly flagged.

---

## 6. CITATION STYLE

All citations use the format: Author Year, Journal Volume, Page.

Primary references used throughout the repository:

| Shorthand | Full citation | Relevance |
|-----------|--------------|-----------|
| Jacobson 1995 | T. Jacobson, Phys. Rev. Lett. 75, 1260 (1995) | Thermodynamic derivation of Einstein equations — foundational |
| Verlinde 2025 | E. Verlinde, SciPost Phys. 2, 016 (2025) | Emergent gravity from information — supporting framework |
| Bose et al. 2023 | S. Bose et al., Nature 623, 43 (2023) | Gravity-mediated entanglement without horizons — key experimental result |
| Kasevich et al. 2023 | J.M. Kasevich et al., Nature Phys. 19, 152 (2023) | Atom interferometry precision — experimental sensitivity reference |
| MICROSCOPE 2022 | P.T. Touboul et al. (MICROSCOPE Collaboration), Phys. Rev. Lett. 129, 121102 (2022) | Equivalence principle test — upper bound on κ̃ |
| Flammia et al. 2012 | S.T. Flammia et al., New J. Phys. 14, 095022 (2012) | Quantum tomography — entropy bias formula |
| Paris 2009 | M.G.A. Paris, Int. J. Quantum Inf. 07, 125 (2009) | Quantum Fisher information — Cramér-Rao bound |

**⚠ Citation verification note:** The Verlinde (2025) citation should be verified — SciPost Phys. 2 was published in 2017, not 2025. The correct citation may be a 2025 update or a different Verlinde paper. This requires author verification before submission.
