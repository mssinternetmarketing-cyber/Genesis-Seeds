# White Paper: Entanglement Entropy Density as a Gravitational Source
## Radial Scaling, Screening, and a Revised Experimental Program

**Authors:** Kevin Monette et al.  
**Date:** March 2026  
**Status:** Canonical document — supersedes earlier drafts on OP4 and α_screen  
**Folder:** `02_MATHEMATICAL_CORRECTIONS/`  
**Purpose:** Formal resolution of OP4, elevation of the screening crisis, and revised experimental program. This document is the authoritative source for the Section 2 (radial scaling) and Section 4 (experimental program) content of Paper A revision.

---

## Abstract

We assess the internal consistency and experimental plausibility of a proposed coupling between entanglement entropy density and gravity. We focus on three issues: (i) the radial scaling of the predicted acceleration correction Δa(R) under spherical symmetry (OP4), (ii) the numerical stability and regime of validity of the screening factor α_screen, and (iii) the compatibility of the experimental protocol with current atom-interferometric and satellite tests of the equivalence principle.

Under a modified Poisson equation with an entropic source term, we show that Δa(R) must depend on an enclosed entropic "mass" M_ent(<R), leading generically to an exterior 1/R² law for bounded sources and to a 1/R correction only for suitably extended profiles such as ρ_ent(r) ∝ 1/r². The earlier 1/R formula therefore encodes a hidden assumption about the spatial structure of the entanglement source rather than a universal prediction.

Using a Gaussian screening model, the effective screening factor for a macroscopic ⁸⁷Rb ensemble can be driven to values as small as α_screen ~ 10⁻⁴³, radically below earlier heuristic estimates (10⁻⁴–10⁻²). This 39-order-of-magnitude mismatch undermines the justification for a million-atom neutral-atom test as the primary near-term experiment and motivates a shift to a 50–100 qubit NISQ-scale platform as the more conceptually clean testbed.

We place these developments in context with Verlinde's emergent gravity proposal at galactic scales, atom-interferometric equivalence-principle tests at the 10⁻¹² level, and MICROSCOPE's 10⁻¹⁵-level constraint on the Eötvös parameter.

---

## 1. Introduction

The working hypothesis of this program is that entanglement entropy density s_ent(x) enters the low-energy gravitational field equations as an additional source term, analogously to how energy density and pressure appear in the Einstein equations. In the nonrelativistic limit:

$$\nabla^2 \Psi = 4\pi G \rho_{\text{mass}} + \kappa \rho_{\text{ent}} \tag{1}$$

where ρ_mass is the ordinary mass density, ρ_ent is a coarse-grained entanglement-related density, and κ is a phenomenological coupling constant to be constrained experimentally.

This program is conceptually adjacent to emergent-gravity approaches in which gravity arises from entanglement and thermodynamic properties of microscopic degrees of freedom, notably Verlinde's 2017 SciPost Physics proposal "Emergent Gravity and the Dark Universe." In that work, coarse-grained entanglement and horizon thermodynamics lead to an additional elastic-like gravitational contribution that can mimic dark matter phenomenology at galactic scales. Here, by contrast, we seek a microscopic, laboratory-scale realization in which controllable entangled states act as tunable sources for an effective gravitational response.

The experimental ambition is to design controlled tests in which high-entanglement and low-entanglement states of a well-characterized quantum system are compared under otherwise identical conditions, looking for a reproducible difference in acceleration, phase, or related observables. A null result in a regime with well-understood systematics and source modeling would constitute a nontrivial bound or falsification of the entanglement–gravity coupling.

---

## 2. Radial Scaling from the Modified Poisson Equation (OP4 — CLOSED)

### 2.1 Spherical Symmetry and Enclosed Entropic Source

Assuming spherical symmetry, Eq. (1) reduces to:

$$\frac{1}{R^2} \frac{d}{dR}\left[R^2 \frac{d\Psi_{\text{ent}}}{dR}\right] = \kappa \rho_{\text{ent}}(R) \tag{2}$$

Define the enclosed entropic "mass":

$$M_{\text{ent}}(<R) = 4\pi \int_0^R \rho_{\text{ent}}(r) \, r^2 \, dr \tag{3}$$

Integrating Eq. (2) once, with C = 0 from regularity at the origin and vanishing at infinity:

$$\Delta a(R) \equiv -\frac{d\Psi_{\text{ent}}}{dR} = \frac{\kappa}{R^2} M_{\text{ent}}(<R) \tag{4}$$

**Equation (4) is the key structural result:** the explicit 1/R² factor is universal. Deviations from the 1/R² law arise from nontrivial radial dependence of M_ent(<R).

### 2.2 Bounded vs. Extended Entropic Sources

**Bounded source** (compact support within R₀): For R > R₀, M_ent(<R) → constant, giving:

$$\Delta a(R) \propto \frac{1}{R^2}, \quad R > R_0 \tag{5}$$

**Extended 1/r² profile**: For ρ_ent(r) = A/r² with suitable cutoffs, M_ent(<R) ∝ R, giving:

$$\Delta a(R) \propto \frac{1}{R}, \quad r_{\min} \ll R < r_{\max} \tag{6}$$

### 2.3 Resolution of OP4

The 1/R formula in earlier source documents treated the 1/R scaling as if it were a universal consequence of spherical symmetry. Eq. (4) shows it is not — it encodes a hidden assumption that M_ent(<R) ∝ R, which requires ρ_ent ∝ 1/r².

**OP4 is therefore resolved by making the following explicit choice in the theory section:**

For a compact atomic ensemble (bounded source): the exterior prediction is 1/R².  
For a 1/R prediction: one must explicitly posit and physically justify ρ_ent(r) ∝ 1/r².

Until a specific source profile is committed to, any attempt to map δa onto δ|κ̃| necessarily carries ambiguity in both normalization and radial scaling.

---

## 3. Screening and the α_screen Crisis

### 3.1 Role of α_screen

The screening factor parameterizes the extent to which microscopic entanglement is "visible" to the emergent gravitational response:

$$\rho_{\text{ent,eff}}(x) = \alpha_{\text{screen}} \cdot s_{\text{ent}}(x) \tag{7}$$

Early order-of-magnitude estimates placed α_screen ∈ [10⁻⁴, 10⁻²], based on heuristic arguments about coherence lengths and environment couplings in few-qubit systems.

### 3.2 Macroscopic ⁸⁷Rb Calculation

A careful calculation using the Gaussian screening model for a macroscopic BEC (N ~ 10⁶, cloud size ~ mm, coherence lengths ~ μm) yields:

$$\alpha_{\text{screen}} \sim 10^{-43} \tag{8}$$

This is 39 orders of magnitude below the earlier heuristic range.

### 3.3 Interpretations

Two interpretations are equally plausible:

1. **Regime mismatch:** The Gaussian formula was derived for microscopic/mesoscopic systems. Its naive extrapolation to a million-atom BEC lies outside its domain of validity.

2. **Definition mismatch:** The quantity labeled α_screen may be playing two distinct roles — in some places as a microscopic overlap or coherence factor per cluster, and in others as a bulk phenomenological prefactor — without a consistent mapping between these two uses.

In both cases the scientific conclusion is identical: quantitative sensitivity cannot be claimed for macroscopic neutral-atom tests without first deriving or bounding α_screen in the appropriate regime.

### 3.4 Conservative Stance

The only scientifically conservative stance is to treat the magnitude of the entanglement-induced signal as **indeterminate** pending a controlled derivation or bounding of α_screen in the relevant regime. The structure of the signal — its dependence on κ̃, S_ent, and the radial profile — remains meaningful. But any numeric forecast must carry an explicit caveat.

---

## 4. Experimental Program: From Macroscopic BEC to NISQ-Scale

### 4.1 Original Concept (Superseded)

The original Section 05 proposed N ≳ 10⁶ ⁸⁷Rb atoms in a GHZ-like state. Under earlier α_screen assumptions, this led to δ|κ̃| ≈ 3.7 × 10⁻¹³. Given the α_screen crisis, this target is no longer well-motivated as the primary near-term experiment.

### 4.2 Atom-Interferometric Benchmarks [VERIFIED]

The 2020 experiment by Asenbaum, Overstreet, Kim, Curti, and Kasevich used a dual-species ⁸⁵Rb/⁸⁷Rb interferometer with T ~ 2 s of free fall:

$$\eta = [1.6 \pm 1.8 \text{ (stat)} \pm 3.4 \text{ (syst)}] \times 10^{-12} \tag{9}$$

Per-shot resolution reached ~ 1.4 × 10⁻¹¹ g. These results demonstrate atom interferometers can probe differential accelerations at or below 10⁻¹² m/s² in carefully controlled configurations. Any entanglement-induced effect behaving like a composition-dependent fifth force must respect these bounds, or couple in a way genuinely orthogonal to composition.

### 4.3 MICROSCOPE Constraints [UNRESOLVED MAPPING]

MICROSCOPE constrains the Eötvös parameter at ~ 10⁻¹⁵. A mapping from this bound to a constraint on κ̃ has not been worked out. Both test masses are classical solids with S_ent ≈ 0; the entanglement source term contributes essentially equally (zero) to both trajectories, leaving η ≈ 0 independent of κ̃.

**Until the mapping is derived, any MICROSCOPE-derived bound on κ̃ must be regarded as conjectural and should not appear in summary tables.**

### 4.4 Revised Near-Term Target: 50–100 Qubit NISQ [ADOPTED]

The revised experimental target is a 50–100 qubit NISQ-scale experiment with:

- **Platform:** Neutral-atom array, trapped ions, or superconducting qubits
- **Branch A:** Highly entangled state (GHZ-like, cluster state, high entanglement depth)
- **Branch B:** Minimally entangled reference state with same qubit count and control schedule
- **Observable:** Differential phase, frequency shift, or effective acceleration proxy sensitive to entanglement-dependent coupling

**Advantages over macroscopic ensembles:**
- Entanglement characterizable directly via witnesses, subsystem tomography, or randomized benchmarking
- Highly programmable geometry — simplifies modeling ρ_ent(x)
- Closer to microscopic open-system models — makes deriving or bounding α_screen more tractable
- At present, the goal is not to claim existing NISQ devices have sufficient sensitivity to detect the effect. The goal is a regime where: if a signal is observed it can be attributed to entanglement; if no signal is observed the null result translates into a meaningful bound on κ̃ once α_screen and the source profile are understood.

### 4.5 Systematics in the Revised Protocol

| Systematic | Concern | Mitigation |
|-----------|---------|-----------|
| Imperfect state preparation | Deviations from target state mimic reduced signal | Embed entanglement verification (witnesses, depth measures) in protocol |
| Decoherence drift | Time-dependent drift changes contrast between branches | Randomize branch order; frequent calibration runs |
| Geometry-dependent coupling | Mapping from theory to signal depends on device geometry | Explicit modeling of ρ_ent(x) for each architecture |
| Platform-specific cross-talk | Spurious differences between branches | Symmetrize control pulses; include null reference circuits |
| Ambiguous screening regime | α_screen is uncontrolled | Treat signal magnitude as indeterminate; focus on structure of entanglement dependence |

---

## 5. Open Problems

### OP3: Lindblad Derivation of α_screen

A first-principles derivation requires: specifying a Hamiltonian for entanglement-bearing degrees of freedom, coupling to an explicit environment (phonons, photons, technical noise), deriving a Lindblad master equation, and computing how relevant entanglement components contributing to the gravitational source decay under environmental coupling. The outcome: α_screen[geometry, bath, T, ...] as a computable function. This is a graduate-level project and is not a prerequisite for stating the current theory, but without it α_screen must be treated as an unknown parameter.

### OP10: Planck-Scale Renormalization

Whether a low-energy entanglement–gravity coupling κ can be derived as an emergent, renormalized parameter in some UV-complete theory, and whether such a derivation imposes sign, magnitude, or universality constraints on κ, remains open. Tools from AdS/CFT and holographic renormalization group are potentially relevant.

---

## 6. Outlook and Action Items

1. **Commit to source profile:** State explicitly in the theory section whether S_ent is a bounded source (→ 1/R² exterior) or an extended profile (→ justify ρ_ent ∝ 1/r²).

2. **Remove MICROSCOPE bound** from Table 7.1 until the explicit mapping from satellite observables to κ̃ is constructed.

3. **Develop the NISQ proposal** with specified hardware, target states, observables, and error budget for circulation to experimental collaborators.

4. **Treat α_screen as open parameter** — prioritize OP3 as a medium-term theoretical objective.

With these steps, the framework becomes both more conservative and more falsifiable: conservative in not over-claiming experimental reach; falsifiable in that well-designed NISQ-scale tests can either detect an entanglement-dependent gravitational response or rule out large classes of couplings.
