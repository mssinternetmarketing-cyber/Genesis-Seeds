# PEIG: Physical Formulation
## Potential–Energy–Identity–Geometry as a Dynamical System in Physics

**Folder:** `03_PEIG_FRAMEWORK/physical/`  
**Status:** [DERIVED] mathematical framework with [OPEN PROBLEM] coupled ODE system  
**Note:** This document covers the *physical* application of PEIG (quantum systems, spacetime geometry). For the cognitive/social application, see `03_PEIG_FRAMEWORK/cognitive/`. The two applications share mathematical structure but are distinct scientific programs.

---

## 1. INTRODUCTION: WHY A FOUR-PHASE FRAMEWORK?

Jacobson's thermodynamic gravity tells us that Einstein's equations emerge from entropy maximization at causal horizons. Our companion paper extends this to laboratory volumes. But both of these are *static* — they describe what happens at a given moment, not how systems evolve over time toward the configurations that produce gravitational effects.

The P/E/I/G framework is the *dynamical* complement: it describes the temporal sequence by which quantum systems transition from high-entropy potential states to low-entropy, structured identity states that source curvature through the entanglement coupling. It answers the question: **how does entanglement entropy density evolve, and how does that evolution shape spacetime over time?**

---

## 2. THE FOUR PHASES

### 2.1 Phase P — Potential: Configuration Space [ESTABLISHED mathematics, SYNTHESIS application]

**Physical definition:** Potential is the distribution of reachable quantum configurations available to a system at time $t$. It is the accessible region of Hilbert space — the set of density operators consistent with all conservation laws and initial conditions, before any symmetry-breaking dynamics have preferentially selected configurations.

**Mathematical representation:**

$$P = (\mathcal{C}, g_{ij})$$

where:
- $\mathcal{C}$ is the constraint manifold (Section 1 of the constraint manifolds paper)
- $g_{ij}$ is the information geometry metric on $\mathcal{C}$ — the quantum Fisher information metric

$$g_{ij} = F_Q(\rho; \partial_i, \partial_j) = \text{Re}\,\text{Tr}\left[\rho \frac{\partial \ln \rho}{\partial \theta_i} \frac{\partial \ln \rho}{\partial \theta_j}\right] \tag{2.1}$$

where $\theta_i$ are coordinates on $\mathcal{C}$.

**Physical meaning:** A large $P$ space (high $\dim \mathcal{C}$, large metric volume) corresponds to a system with many accessible microstates — high entropy, high adaptability, high option-space. A collapsed $P$ space (low $\dim \mathcal{C}$) corresponds to a system tightly constrained by its history.

**Connection to gravity:** A high-entropy state in P has high $S_{\text{ent}}$ (entanglement entropy density), contributing repulsive curvature via the modified Einstein equation. Phase P is the regime of *maximal informational content* and *maximal gravitational repulsion* from entanglement.

### 2.2 Phase E — Energy: Gradient Flow [ESTABLISHED mathematics, SYNTHESIS application]

**Physical definition:** Energy is the actualization of potential — the directed flow of the system along gradients in the potential landscape, determined by the system's Hamiltonian and its coupling to the environment.

**Mathematical representation:**

$$\dot{q}^i = -g^{ij} \partial_j V(q) \tag{2.2}$$

where:
- $q^i$ are coordinates on the configuration space
- $V(q)$ is the effective potential (free energy landscape)
- $g^{ij}$ is the inverse information geometry metric

This is a gradient flow on the constraint manifold — the quantum generalization of a Langevin equation for a system descending an energy landscape.

**Physical meaning:** Phase E is the regime of dynamics — the system is transitioning from its initial high-entropy state toward lower-entropy attractors, driven by Hamiltonian evolution and environmental coupling. Entanglement is being either generated (if the system is being quantum-coupled to others) or destroyed (decoherence).

**Connection to gravity:** During Phase E, $S_{\text{ent}}$ is changing. A decreasing $S_{\text{ent}}$ (decoherence) reduces the repulsive curvature contribution. An increasing $S_{\text{ent}}$ (coherence generation) increases it. The gradient of $S_{\text{ent}}$ in Phase E is the source of the anomalous force predicted in the Bianchi identity analysis (OP8).

### 2.3 Phase I — Identity: Attractor Formation [ESTABLISHED mathematics, SYNTHESIS application]

**Physical definition:** Identity is the formation of a stable attractor — a density matrix $\rho_{ss}$ that the system returns to after perturbation. An identity state has lower entropy than Phase P (it has selected a preferred region of configuration space) and is persistent under environmental noise.

**Mathematical representation:**

An identity state is a density matrix $\rho_{ss}$ with the following properties:

1. **Stationarity:** $\mathcal{L}[\rho_{ss}] = 0$ (zero time-derivative under the full Lindblad evolution $\mathcal{L}$)
2. **Stability:** $\lim_{t\to\infty} \|\rho(t) - \rho_{ss}\| = 0$ for initial conditions in the basin of attraction
3. **Robustness:** Under perturbation $\rho_{ss} \to \rho_{ss} + \delta\rho$, the Lindblad evolution returns $\rho$ to $\rho_{ss}$

The Identity as measured by negentropy:

$$I(t) = N(\rho(t)) = S_{\max} - S_{vN}(\rho(t)) \tag{2.3}$$

This quantifies how much structure has accumulated relative to maximum disorder.

**The Identity ODE:** From the linearized Lindblad equation around the attractor:

$$\frac{dI}{dt} = \alpha E - \beta I \tag{2.4}$$

where $\alpha > 0$ is the coupling strength between energy flow and identity accumulation, and $\beta > 0$ is the decay rate (decoherence-driven loss of identity).

**Solution for constant E:**

$$I(t) = \frac{\alpha}{\beta} E + \left(I_0 - \frac{\alpha}{\beta} E\right) e^{-\beta t} \tag{2.5}$$

The system converges to the identity attractor $I_\infty = (\alpha/\beta) E$ with characteristic time $\tau_I = 1/\beta$.

**Connection to gravity:** The accumulated identity $I(t) = N(\rho)$ is the negentropy of the system. Per Section 4.2 of the entropic gravity paper, negentropy gradients source *attractive* curvature — the opposite of entanglement entropy. A highly ordered (high-identity) state gravitates like positive mass: it attracts rather than repels.

### 2.4 Phase G — Geometry: Spacetime Response [HYPOTHESIS]

**Physical definition:** Geometry is the spacetime curvature response to the accumulated information structure in Phase I. The Einstein tensor $G_{\mu\nu}$ encodes the gravitational field sourced by all stress-energy, including the entanglement and negentropy contributions.

**Mathematical representation:**

$$G_{\mu\nu} = \frac{8\pi G}{c^4} \left[ T_{\mu\nu}^{\text{matter}} + T_{\mu\nu}^{S_{\text{ent}}} + T_{\mu\nu}^{N} \right] \tag{2.6}$$

where:

$$T_{\mu\nu}^{S_{\text{ent}}} = \tilde{\kappa}_{\text{rep}} \frac{c^4}{8\pi G \, k_B \ln 2} S_{\text{ent}} \, g_{\mu\nu}, \quad \tilde{\kappa}_{\text{rep}} < 0 \quad \text{[repulsive]} \tag{2.7}$$

$$T_{\mu\nu}^{N} = \tilde{\kappa}_{\text{att}} \frac{c^4}{8\pi G \, k_B \ln 2} N \, g_{\mu\nu}, \quad \tilde{\kappa}_{\text{att}} > 0 \quad \text{[attractive]} \tag{2.8}$$

**[HYPOTHESIS]:** Equation (2.8) for the negentropy coupling is proposed but not yet derived. Its justification follows the same logic as Equation (2.7) for entanglement entropy, but with the sign inverted because negentropy is ordered (low-entropy) structure rather than disordered (high-entropy) entanglement. A derivation along the lines of Section 4 in the master paper would be needed.

**Connection to the full framework:** Phase G completes the P → E → I → G cycle by producing a modified spacetime geometry that itself affects which configurations are accessible in Phase P — closing the loop.

---

## 3. THE DYNAMICAL SEQUENCE

The four phases form a directed sequence:

$$P \xrightarrow{\text{symmetry breaking}} E \xrightarrow{\text{dissipation}} I \xrightarrow{\text{accumulation}} G$$

With the geometric backreaction closing the loop:

$$G \xrightarrow{\text{curvature constrains evolution}} P'$$

### 3.1 Physical Interpretation

- **P → E (Symmetry breaking):** The system begins in a high-entropy, high-symmetry state. An external perturbation, Hamiltonian coupling, or spontaneous symmetry breaking selects a direction of evolution. In the quantum gravity context: a region of spacetime that was in thermal equilibrium with maximum entropy is perturbed by quantum fluctuations or matter injection.

- **E → I (Dissipation):** The system flows toward lower-entropy configurations, driven by its Hamiltonian and environmental coupling. Entanglement entropy changes. In the quantum gravity context: quantum fields organize into coherent structures (stars, molecules, brains) through dissipative evolution.

- **I → G (Accumulation):** The accumulated structure (negentropy, identity) sources gravitational curvature through Eqs. (2.7)–(2.8). In the quantum gravity context: accumulated negentropy contributes to the stress-energy tensor, slightly modifying the spacetime geometry.

- **G → P' (Geometric feedback):** The modified geometry changes the dynamics available to quantum systems — it changes which configurations are accessible, how quickly decoherence occurs, and what attractor states form. This is the loop-closing step that makes the framework self-consistent.

### 3.2 Timescales

The four phases operate on very different timescales in realistic quantum systems:

| Phase transition | Physical process | Typical timescale |
|:---:|:---|:---:|
| P → E | Initial state preparation → coherent dynamics | μs–ms (BEC/trapped ions) |
| E → I | Coherent dynamics → steady state / decoherence | ms–s (NISQ hardware) |
| I → G | Accumulated structure → gravitational curvature | Instantaneous (GR) |
| G → P' | Curvature change → modified dynamics | Gravitational light-travel time |

For laboratory systems, the geometric feedback (G → P') is negligible — the curvature change produced by $10^6$ entangled atoms is too small to measurably modify their dynamics. The framework predicts this feedback becomes relevant at astrophysical scales and for cosmic evolution.

---

## 4. OBSERVATION AND LOCALIZED NEGENTROPY PRODUCTION [SYNTHESIS]

### 4.1 Quantum Measurement as a Phase I Event

A projective quantum measurement is a prototypical Phase I event: it drives the system from a high-entropy superposition (Phase P) to a low-entropy post-measurement state (Phase I).

The entropy change in the measured system:

$$\Delta S_{\text{local}} = S_{\text{post}} - S_{\text{pre}} < 0 \tag{4.1}$$

The entropy expelled to the measurement apparatus and environment:

$$\Delta S_{\text{env}} = \frac{Q}{T} \geq k_B \ln 2 \cdot I_{\text{erased}} > |\Delta S_{\text{local}}| \tag{4.2}$$

Total entropy change (second law preserved):

$$\Delta S_{\text{total}} = \Delta S_{\text{local}} + \Delta S_{\text{env}} > 0 \tag{4.3}$$

### 4.2 The Negentropy Gradient as Gravitational Source [HYPOTHESIS]

The measurement creates a localized negentropy gradient $\nabla N$ — the measured subsystem has lower entropy than its surroundings. Under the framework:

- High-$N$ regions (ordered, structured, post-measurement): source *attractive* curvature
- High-$S_{\text{ent}}$ regions (disordered, entangled, pre-measurement): source *repulsive* curvature

This creates a gravitational asymmetry between ordered and disordered quantum systems. A quantum computer performing active error correction (continuous measurement + reset) is continuously generating localized negentropy and, under this framework, is continuously producing a tiny attractive gravitational signal.

**The effect size:** For a 1000-qubit system running at 1 MHz with 10^{-3} error rate, the negentropy production rate is approximately $10^3$ bits/second. The corresponding stress-energy contribution is:

$$T^N_{00} \approx \tilde{\kappa}_{\text{att}} \frac{c^2}{k_B \ln 2} \cdot \frac{dN/dt}{V} \approx 10^{-45} \text{ Pa}$$

This is far below any conceivable sensitivity — the gravitational effect of negentropy production in current quantum computers is negligible. The prediction is, however, in principle falsifiable at the scale of $\geq 10^{18}$ entangled qubits.

---

## 5. CONNECTION TO COSMOLOGY [SYNTHESIS]

### 5.1 Dark Energy as Phase P Entanglement

The observed accelerating expansion of the universe is attributed to dark energy — an effective cosmological constant $\Lambda > 0$. Our framework suggests a possible interpretation: the large-scale entanglement entropy density of quantum fields throughout the universe acts as a repulsive source term in the Friedmann equations.

$$H^2 = \frac{8\pi G}{3}\left(\rho_{\text{matter}} + \rho_{\text{rad}} + \frac{\tilde{\kappa} c^2}{8\pi G \, k_B \ln 2} S_{\text{ent}}^{\text{cosmic}}\right) \tag{5.1}$$

**[HYPOTHESIS — highly speculative]:** If $S_{\text{ent}}^{\text{cosmic}}$ represents the entanglement entropy density of cosmic quantum fields at the horizon scale, and if $\tilde{\kappa} \approx -1/4$, then the repulsive term could be comparable in magnitude to the observed dark energy density $\rho_\Lambda \approx 6 \times 10^{-27}$ kg/m³.

This is not a prediction — it is a suggestive dimensional coincidence that motivates further investigation. The required $S_{\text{ent}}^{\text{cosmic}}$ would be approximately $10^{69}$ bits/m³ — comparable to the Bekenstein-Hawking entropy density of the observable universe. Whether this coincidence is meaningful requires detailed calculation.

### 5.2 Structure Formation as Phase E → I Transition

The formation of structure in the universe (galaxies, stars, planets) corresponds to the P → E → I transition in the PEIG framework: initially uniform, high-entropy quantum fields (Phase P) undergo symmetry breaking via gravitational instability (Phase E) and collapse into the ordered, persistent structures we observe (Phase I). These structures then source their own gravitational curvature (Phase G), which shapes the future evolution of the density field (G → P').

This is not a new cosmological model — it is a restatement of standard structure formation in the PEIG language. The value of the restatement is the connection it makes between cosmological evolution and the quantum information framework: both are describing the same P → E → I → G cycle at different scales.

---

## 6. [OPEN PROBLEM] — THE COMPLETE COUPLED SYSTEM

The full PEIG dynamical system as a set of coupled differential equations has not been written. From the physical interpretation:

$$\frac{dP}{dt} = -\gamma_P P + \eta_P(G) \tag{6.1}$$
$$\frac{dE}{dt} = -\gamma_E E + f_E(P) \tag{6.2}$$
$$\frac{dI}{dt} = \alpha E - \beta I \tag{6.3}$$
$$\frac{dG}{dt} = \kappa_G \frac{dI}{dt} \tag{6.4}$$

where:
- $\gamma_P$ is the rate at which geometry contracts the accessible configuration space
- $\eta_P(G)$ is geometric expansion of configuration space (new possibilities opened by new geometry)
- $\gamma_E$ is the rate of energy dissipation
- $f_E(P)$ describes how the potential landscape drives energy flow
- $\kappa_G$ is the coupling between identity accumulation and geometric response

**Required:** Specific functional forms for $f_E$, $\eta_P$, $\gamma_P$, $\gamma_E$, $\kappa_G$ derived from quantum dynamics and GR. Without these, the coupled system cannot be simulated, analyzed for fixed points, or compared to data.

This is an open problem with significant mathematical depth. A graduate research project could be designed around solving it.
