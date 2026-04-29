# OP4 RESOLUTION: Derivation of Δa(R)
## Correct Radial Scaling of the Differential Acceleration

**Status:** CLOSED — replaces the unverified Eq. (5.3) in `A_S05_experimental_protocol.md`  
**Result:** Δa(R) ∝ 1/R² outside a localized source. The 1/R formula in source documents was incorrect.  
**Date resolved:** March 2026

---

## 1. SETUP: THE MODIFIED POISSON EQUATION

In the Newtonian (weak-field, slow-motion) limit, the modified Einstein equation becomes a modified Poisson equation. The standard gravitational potential Φ satisfies ∇²Φ = 4πGρ_matter. With the entanglement source term, this becomes:

$$\nabla^2 \Phi_{\text{total}} = 4\pi G \rho_{\text{matter}} + \frac{\tilde{\kappa} c^4}{2 k_B \ln 2} \nabla^2 S_{\text{ent}} \tag{1.1}$$

We isolate the entanglement contribution by defining an entropic potential Ψ satisfying:

$$\nabla^2 \Psi = \kappa_{\text{eff}} \, \rho_{\text{ent}}(R) \tag{1.2}$$

where $\rho_{\text{ent}}(R) \equiv S_{\text{ent}}(R)$ is the entanglement entropy density profile in bit/m³, and:

$$\kappa_{\text{eff}} = \frac{\tilde{\kappa} c^4}{2 k_B \ln 2} \tag{1.3}$$

In spherical symmetry, Eq. (1.2) becomes:

$$\frac{1}{R^2} \frac{d}{dR}\left[R^2 \frac{d\Psi}{dR}\right] = \kappa_{\text{eff}} \, \rho_{\text{ent}}(R) \tag{1.4}$$

---

## 2. THE ENCLOSED ENTROPIC SOURCE

Define the enclosed entropic source within radius R:

$$M_{\text{ent}}(<R) = 4\pi \int_0^R \rho_{\text{ent}}(r) \, r^2 \, dr \tag{2.1}$$

This is the total entanglement entropy (in bits) contained within a sphere of radius R — the exact analog of the enclosed mass M(<R) in Newton's shell theorem.

Integrating Eq. (1.4) once using the divergence theorem:

$$R^2 \frac{d\Psi}{dR} = \kappa_{\text{eff}} \int_0^R \rho_{\text{ent}}(r) r^2 \, dr = \frac{\kappa_{\text{eff}}}{4\pi} M_{\text{ent}}(<R) \tag{2.2}$$

Therefore:

$$\frac{d\Psi}{dR} = \frac{\kappa_{\text{eff}}}{4\pi} \cdot \frac{M_{\text{ent}}(<R)}{R^2} \tag{2.3}$$

---

## 3. THE DIFFERENTIAL ACCELERATION — CORRECT FORMULA

The differential acceleration between the coherent arm (entanglement entropy $S_{\text{ent}} \neq 0$) and the decohered arm ($S_{\text{ent}} = 0$) at radius R from the ensemble center is:

$$\boxed{\Delta a(R) = -\frac{d\Psi}{dR} = -\frac{\kappa_{\text{eff}}}{4\pi} \cdot \frac{M_{\text{ent}}(<R)}{R^2}} \tag{3.1}$$

Substituting the definition of $\kappa_{\text{eff}}$:

$$\Delta a(R) = -\frac{\tilde{\kappa} c^4}{8\pi k_B \ln 2} \cdot \frac{M_{\text{ent}}(<R)}{R^2} \tag{3.2}$$

**This is the correct formula, replacing Eq. (5.3) in the experimental protocol.**

---

## 4. THE RADIAL SCALING QUESTION — RESOLVED

The OP4 discrepancy (1/R in source documents vs. 1/R² in the derivation) is now fully resolved:

**Outside a localized source** (R > r₀ where r₀ is the ensemble radius): M_ent(<R) = M_ent,total = constant. Therefore:

$$\Delta a(R) \propto \frac{1}{R^2} \quad \text{for } R > r_0 \tag{4.1}$$

This is the **correct scaling** — inverse square law, exactly analogous to Newton's gravity outside a finite mass distribution.

**The 1/R scaling** (which appeared in source documents) arises only if the enclosed source M_ent(<R) grows linearly with R — which requires:

$$4\pi \int_0^R \rho_{\text{ent}}(r) r^2 \, dr \propto R \implies \rho_{\text{ent}}(r) \propto \frac{1}{r^2} \tag{4.2}$$

A density profile falling as 1/r² would represent an entanglement entropy distribution extending to large radii with a specific profile — physically unmotivated for a compact atomic ensemble. The 1/R scaling in source documents was therefore an error corresponding to an implicit and unjustified density assumption.

**Resolution:** For a compact atomic ensemble (uniform density within r₀, zero outside), the correct prediction is Δa ∝ 1/R² for R > r₀.

---

## 5. NUMERICAL PREDICTION WITH UNIFORM DENSITY PROFILE

For a uniform sphere of radius r₀ with total entanglement entropy S_total bits:

$$\rho_{\text{ent}}(r) = \frac{3 S_{\text{total}}}{4\pi r_0^3} \cdot \Theta(r_0 - r) \tag{5.1}$$

The enclosed source:
$$M_{\text{ent}}(<R) = S_{\text{total}} \quad \text{for } R \geq r_0 \tag{5.2}$$

Therefore, for R ≥ r₀:

$$\Delta a(R) = -\frac{\tilde{\kappa}_{\text{eff}} c^4}{8\pi k_B \ln 2} \cdot \frac{S_{\text{total}}}{R^2} \tag{5.3}$$

**Numerical example** (using tentative α_screen ∈ [10⁻⁴, 10⁻²], subject to OP3/α_screen audit):
- N = 10⁶ ⁸⁷Rb atoms, full GHZ entanglement: S_total ≈ N = 10⁶ bits
- R = 10⁻² m (1 cm standoff)
- |κ̃_eff| = 10⁻⁴ (lower estimate)

$$|\Delta a| = \frac{10^{-4} \times (3\times10^8)^4}{8\pi \times 9.57\times10^{-24}} \times \frac{10^6}{(10^{-2})^2} \approx 6 \times 10^{54} \text{ m/s}^2 \tag{5.4}$$

This number is absurdly large, which signals that one of the inputs is wrong at order-of-magnitude level. The issue is the α_screen audit (Section 7 of `A_S04_screening_factor_v2.md`) — if α_screen is truly ~10⁻⁴³ for a macroscopic ensemble, the actual prediction is:

$$|\Delta a| \approx 6 \times 10^{54} \times 10^{-43} \approx 6 \times 10^{11} \text{ m/s}^2 \tag{5.5}$$

which is still impossibly large. This reveals that the formula, while correctly derived, produces physically unreasonable numbers when combined with even a heavily suppressed coupling — which means the **regime of validity** of the entropic coupling formula needs to be examined at the scale of individual entangled pairs, not macroscopic ensembles. See the α_screen redesign document.

---

## 6. WHAT OP4 CLOSURE MEANS FOR THE PAPER

**Eq. (5.3) in `A_S05_experimental_protocol.md` is now replaced by Eq. (3.2) above.** The corrected formula has:
- 1/R² scaling (not 1/R)
- No factor of "3/(16π)" in the numerator — the correct prefactor is 1/(8π)
- Explicit M_ent(<R) rather than S_ent × volume

The experimental sensitivity statement δ|κ̃| = 3.7 × 10⁻¹³ requires re-derivation using the corrected formula and the specific experimental geometry (atom number, ensemble radius, interferometer baseline R). This cannot be stated until the α_screen regime question is resolved.

**OP4 is closed as a mathematical question. The physical implications depend on OP3 resolution.**
