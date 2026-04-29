# Section 04: Environmental Screening
## The α_screen Factor and Realistic Coupling Suppression

**Paper:** A — Gravitational Coupling to Entanglement Entropy Density  
**Section:** 4 of 6  
**Status:** [HYPOTHESIS] — phenomenological ansatz; derivation from Lindblad dynamics is [OPEN PROBLEM — OP3]

---

## 4.1 Why Screening Is Necessary

The ideal coupling κ̃ = −1/4 (Section 02) applies to a perfectly isolated, maximally coherent quantum system. No such system exists in any laboratory.

Real quantum systems are continuously coupled to their environments through:
- Thermal photon scattering
- Phonon interactions with the trap structure
- Magnetic field fluctuations
- Electromagnetic interference
- Residual gas collisions

Each of these interactions is a decoherence channel — it transfers entanglement from within the system to correlations between the system and its environment. Once entanglement is shared with the environment, it no longer contributes to the internal entanglement entropy density $S_{\text{ent}}$ that sources curvature. The effective coupling is suppressed.

## 4.2 The Screening Factor — Definition

We define:

$$\tilde{\kappa}_{\text{eff}} = -\frac{1}{4} \alpha_{\text{screen}} \tag{4.1}$$

where $\alpha_{\text{screen}} \in [0, 1]$ is the fraction of the ideal coupling that survives environmental decoherence:
- $\alpha_{\text{screen}} = 1$: perfect isolation, no decoherence — ideal coupling
- $\alpha_{\text{screen}} = 0$: complete decoherence — no coupling

## 4.3 The Phenomenological Formula [HYPOTHESIS — OP3]

A physically motivated ansatz for the screening factor is:

$$\alpha_{\text{screen}} = \frac{1}{1 + (\Gamma \tau_D)^2} \cdot e^{-(R/\xi)^2} \tag{4.2}$$

where:
- $\Gamma$ is the decoherence rate (s⁻¹): rate at which environmental monitoring collapses entanglement
- $\tau_D = 1/\Gamma$ is the decoherence time (s)
- $R$ is the spatial extent of the coherent region (m)
- $\xi$ is the coherence length (m): the spatial scale over which entanglement persists

**Physical interpretation of each factor:**

The Lorentzian factor $1/(1 + (\Gamma\tau_D)^2)$: When $\Gamma\tau_D \ll 1$, the system decoheres slowly relative to its natural timescale — screening is small. When $\Gamma\tau_D \gg 1$, decoherence is fast — the system is effectively classical and the coupling is suppressed. For current NISQ hardware, $\Gamma\tau_D \sim 10^{-3}$–$10^{-2}$, giving Lorentzian suppression of approximately $1/(1 + 10^{-6})$ ≈ 1 — essentially no suppression from this factor alone.

The Gaussian factor $e^{-(R/\xi)^2}$: Entanglement does not persist over arbitrarily large spatial scales. For a system of spatial extent $R$, entanglement correlations decay on the coherence length $\xi$. When $R \gg \xi$, most of the system's volume has its entanglement destroyed by decoherence before it can contribute to the gravitational coupling.

## 4.4 Estimated Parameter Ranges

For ⁸⁷Rb atoms at 1 nK in an optical dipole trap:
- Decoherence rate (off-resonant photon scattering): $\Gamma \approx 0.01$–$1$ s⁻¹
- Decoherence time: $\tau_D \approx 1$–$100$ s
- Coherence length in BEC: $\xi \approx 1$–$10$ μm
- Ensemble radius: $R \approx 100$ μm–$1$ mm

This gives: $\alpha_{\text{screen}} \approx e^{-(100\mu\text{m}/10\mu\text{m})^2} = e^{-100} \approx 10^{-43}$ — far below [10⁻⁴, 10⁻²].

This suggests the cited range [10⁻⁴, 10⁻²] may apply to a different regime — possibly individual entangled pairs at the microscopic scale (R ≪ ξ), not a macroscopic atomic ensemble. This is a potential internal inconsistency that requires resolution.

**[OPEN PROBLEM — OP3]:** The range $\alpha_{\text{screen}} \in [10^{-4}, 10^{-2}]$ cited throughout the source corpus is not derived from first principles. The estimate above from ⁸⁷Rb parameters gives a far smaller value. Until Eq. (4.2) is derived from the Lindblad equation with explicit parameter values for the proposed experimental system, the screening factor range cannot be treated as a quantitative prediction.

**What this means for the experiment:** If $\alpha_{\text{screen}}$ is as small as $10^{-43}$ for a macroscopic ensemble, the effective coupling $|\tilde{\kappa}_{\text{eff}}|$ would be so small as to be undetectable by any foreseeable technology. The falsification criterion (Section 06) would then be triggered by the null result, providing an important upper bound. Alternatively, a microscopic version of the experiment (individual or small clusters of entangled atoms) might access larger screening factor values.

## 4.5 Effective Coupling Range (As Currently Estimated)

Retaining the [10⁻⁴, 10⁻²] range as a provisional estimate pending derivation:

$$\tilde{\kappa}_{\text{eff}} \in [-2.5 \times 10^{-3},\ -2.5 \times 10^{-5}] \tag{4.3}$$

This range is cited in experimental sensitivity comparisons in Section 05, with the understanding that it is an estimate subject to revision when OP3 is resolved.

---

*Next: Section 05 — Experimental protocol and sensitivity analysis*
