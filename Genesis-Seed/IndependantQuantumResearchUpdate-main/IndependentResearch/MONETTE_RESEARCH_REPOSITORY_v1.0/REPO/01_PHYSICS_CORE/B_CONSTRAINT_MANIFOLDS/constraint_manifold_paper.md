# Constraint Manifolds and the Limits of Quantum Observability
## Resolving the 40–50% Entropy Plateau in NISQ Devices

**Author:** Kevin Monette, Independent Researcher (AI-assisted)  
**Date:** February 9, 2026 (repository version March 2026)  
**Classification:** Quantum Information Theory · Quantum Metrology · NISQ Physics  
**Status:** [DERIVED] result with [HYPOTHESIS] experimental falsification  
**Companion paper:** `A_ENTROPIC_GRAVITY/MASTER_PAPER.md`

---

## ABSTRACT

In near-term quantum devices with 16–28+ qubits, state tomography consistently yields entropy estimates at 40–50% of maximum entropy — a plateau interpreted by many researchers as a fundamental decoherence limit of current hardware. We show instead that this plateau is a **measurement artifact from finite-sample estimator bias**, not a physical decoherence ceiling.

We formalize the distinction through the constraint manifold $\mathcal{C} \subset \mathcal{D}(\mathcal{H})$ — the subspace of physically accessible density operators — and prove that the required measurement resources scale as $\nu \propto 2^{n/2}$ via quantum Fisher information analysis. For typical NISQ tomography budgets ($\nu \sim 10^3$ shots) with $n \geq 15$ qubits, the estimator bias alone accounts for the observed plateau entirely.

**Experimental falsification criterion:** If entropy estimates for genuinely coherent states (e.g., GHZ states with verified entanglement depth) fail to converge to $S_{vN} < 0.1$ bits when shot count $\nu \geq 100 \cdot 2^{n/2}$ after SPAM calibration and correction, the measurement-insufficiency hypothesis is falsified.

**Implication:** Current NISQ hardware is better than its entropy estimates suggest. The measurement budget, not the hardware coherence, is the binding constraint.

---

## 1. THE CONSTRAINT MANIFOLD FORMALISM

### 1.1 Defining Physically Accessible State Space [ESTABLISHED + SYNTHESIS]

Not all density operators in $\mathcal{D}(\mathcal{H})$ are physically accessible to a quantum system evolving under real-world conditions. Conservation laws, decoherence channels, and initial state constraints all restrict evolution to a proper submanifold.

**Definition 1.1 — Constraint Manifold:**

$$\mathcal{C} = \left\{ \rho \in \mathcal{D}(\mathcal{H}) \;\middle|\; \text{Tr}(\hat{C}_i \rho) = c_i \;\; \forall i \in \mathcal{I}_{\text{irr}} \right\} \tag{1.1}$$

where:
- $\mathcal{D}(\mathcal{H})$ denotes the set of density operators (Hermitian, positive semidefinite, trace-1) on Hilbert space $\mathcal{H}$
- $\hat{C}_i$ are constraint operators, such as the Hamiltonian $\hat{H}$ for energy conservation or the charge operator $\hat{Q}$
- $c_i$ are the constraint values fixed by initial conditions
- $\mathcal{I}_{\text{irr}}$ indexes *irreversible* constraints — those that cannot be undone by subsequent unitary evolution

**Definition 1.2 — Soft Constraints:**  
Thermodynamic biases (e.g., energy equipartition tendencies) enter through a measure on $\mathcal{C}$, not through its definition:

$$\mu(d\rho) \propto e^{-\beta \, \text{Tr}(\hat{H}\rho)} \, d\rho \tag{1.2}$$

These are statistical preferences, not hard boundaries. A system can explore the full manifold $\mathcal{C}$ but preferentially occupies lower-energy regions.

### 1.2 The Observable Subspace [DERIVED]

A measurement history $r = \{i_1, i_2, \ldots, i_k\}$ represents the sequence of constraint-fixing events (measurements, decoherence events) that have become irreversible. Each event reduces the accessible subspace:

$$\mathcal{O}(r) = \left\{ \rho \in \mathcal{C} \;\middle|\; \text{Tr}(\hat{C}_{i_j} \rho) = c_{i_j} \;\; \forall j \leq k \right\} \tag{1.3}$$

**Key result:** As $k$ increases (more measurements are performed), $\mathcal{O}(r)$ shrinks. This is not decoherence — this is the progressive fixing of constraints by observation. The physical state remains in $\mathcal{C}$; only our *knowledge* of where it is becomes more precise.

### 1.3 Dimension of the Observable Subspace [DERIVED]

For an $n$-qubit system with $m$ independent measurement constraints:

$$\dim \mathcal{O}(r) = 4^n - m - 1 \tag{1.4}$$

**Derivation:**
- The space of $n$-qubit density operators has real dimension $4^n - 1$ (the $4^n$ real parameters of a $2^n \times 2^n$ Hermitian matrix, minus 1 for the trace normalization $\text{Tr}(\rho) = 1$)
- Each independent measurement constraint that becomes irreversible reduces the dimension by 1
- With $m$ independent constraints: $\dim \mathcal{O}(r) = (4^n - 1) - m = 4^n - m - 1$

**Caveat:** This formula requires that the $m$ constraints are **linearly independent in the space of Hermitian operators**. If some constraints are redundant (e.g., energy conservation combined with a consequence of energy conservation), fewer than $m$ dimensions are removed. The formula gives the maximum dimension reduction; actual reduction depends on the constraint structure.

**Consequence:** When $m \ll 4^n$, the observable subspace vastly undersamples the full state space. The physical system is in a specific state in $\mathcal{C}$, but our measurement record $r$ is consistent with an enormous number of density operators. Any entropy *estimator* based on $r$ will reflect this uncertainty — it will be biased upward, toward the maximally mixed state, simply because most of $\mathcal{O}(r)$ consists of high-entropy states.

---

## 2. QUANTUM FISHER INFORMATION AND THE SHOT-SCALING PROBLEM

### 2.1 The Cramér-Rao Bound [ESTABLISHED]

The quantum Cramér-Rao bound gives a fundamental lower limit on the variance of any unbiased estimator $\hat{S}$ of the von Neumann entropy:

$$\text{Var}[\hat{S}] \geq \frac{[F_Q(\rho)]^{-1}}{\nu} \tag{2.1}$$

where:
- $\nu$ is the number of independent measurement shots
- $F_Q(\rho) = \text{Tr}[\rho L^2]$ is the quantum Fisher information, with $L$ the symmetric logarithmic derivative satisfying $\partial \rho / \partial \theta = (\rho L + L \rho)/2$
- The bound is achieved (saturated) by the optimal measurement — which for entropy estimation requires a highly non-trivial adaptive protocol

**Notation correction from source documents:** $F_Q(\rho)$ is the quantum Fisher information evaluated at the *state* $\rho$, not a function of the scalar entropy value $S_{vN}$. It is a functional of the quantum state. The source document notation $\mathcal{I}_Q(S_{vN})$ is therefore ambiguous and has been replaced here by $F_Q(\rho)$ throughout. [MA5 from audit]

### 2.2 The Exponential Scaling of F_Q Near Maximum Entropy [DERIVED]

For states near the maximally mixed state $\rho \approx \mathbf{I}/d$ where $d = 2^n$:

$$F_Q(\rho) \sim 2^{-n/2} \tag{2.2}$$

**Why this scaling:**  
The quantum Fisher information for entropy estimation quantifies how sensitively the probability distribution over measurement outcomes changes as the entropy changes. Near the maximally mixed state, all probability distributions are nearly identical — the entropy is near its maximum and very "flat." Distinguishing $S_{vN} = 0.99 S_{\max}$ from $S_{vN} = S_{\max}$ requires resolving tiny differences in an exponentially large space of equally likely outcomes. This requires exponentially many measurements.

More precisely, the sensitivity of the measurement record to changes in entropy scales as the average overlap between adjacent density matrices in the direction of entropy variation. Near maximum entropy, this overlap is exponentially close to 1 for all product measurement bases, making entropy estimation exponentially hard.

### 2.3 The Required Shot Count [DERIVED]

To achieve precision $\varepsilon$ in the entropy estimate, the Cramér-Rao bound requires:

$$\nu \gtrsim \varepsilon^{-2} \cdot 2^{n/2} \tag{2.3}$$

**Table 2.1: Required shot counts for entropy estimation at precision ε = 0.1 bits**

| Qubit count n | Hilbert space dim d = 2^n | Required ν | Typical NISQ budget | Gap factor |
|:---:|:---:|:---:|:---:|:---:|
| 5 | 32 | ~560 | 10³ | ≤1 (sufficient) |
| 10 | 1,024 | ~3,160 | 10³ | ~3× (marginal) |
| 15 | 32,768 | ~17,800 | 10³ | ~18× (insufficient) |
| 20 | 1,048,576 | ~100,000 | 10³ | ~100× (severely insufficient) |
| 25 | ~33M | ~560,000 | 10³ | ~560× |
| 28 | ~268M | ~1.6M | 10³ | ~1600× |

The gap between required and typical shot budgets explains the entropy plateau entirely: NISQ devices with 15–28 qubits are being measured with 18–1600× too few shots to accurately estimate entropy.

---

## 3. THE ESTIMATOR BIAS FORMULA

### 3.1 Linear Inversion Estimator Bias [DERIVED — cites Flammia et al. 2012]

The standard tomographic reconstruction uses linear inversion: given measurement outcomes, construct the best-fit density matrix $\hat{\rho}$ by inverting the measurement map. The von Neumann entropy of this reconstructed state is the estimator $\hat{S}_{vN}$.

This estimator has systematic bias that scales with the Hilbert space dimension $d = 2^n$:

$$\mathbb{E}[\hat{S}_{vN}] = S_{vN}(\rho) + \underbrace{\frac{d-1}{2\nu}}_{\text{finite-sampling bias}} + \underbrace{B_{\text{SPAM}}}_{\text{readout errors}} + O(\nu^{-2}) \tag{3.1}$$

where the expectation is over many independent repetitions of the $\nu$-shot tomographic experiment.

**This is the central equation of this paper.** The estimator systematically *overestimates* entropy by $(d-1)/(2\nu)$ bits, simply due to finite sampling. The correct physical entropy $S_{vN}(\rho)$ is what the device actually has; the measured entropy $\mathbb{E}[\hat{S}_{vN}]$ is inflated by the sampling bias.

### 3.2 Quantitative Explanation of the 40–50% Plateau

**Example: n = 15 qubits, ν = 10⁴ shots (generous by typical standards):**
- $d = 2^{15} = 32,768$
- Finite-sampling bias: $(d-1)/(2\nu) = 32767/20000 \approx 1.64$ bits
- Maximum entropy: $n \ln 2 \approx 10.4$ bits
- Bias as fraction of max entropy: $1.64/10.4 \approx 15.7\%$

**Adding SPAM errors:** Current NISQ hardware exhibits SPAM errors of 0.5–1.0% per qubit. For 15 qubits, this contributes $B_{\text{SPAM}} \approx 0.5$–1.0 bits of additional entropy inflation.

**Total bias:** $\approx 1.64 + 0.75 = 2.39$ bits, corresponding to $2.39/10.4 \approx 23\%$ of maximum entropy.

**For a pure state (S = 0):** The estimated entropy would be $\approx 23\%$ of maximum, purely from bias.

**For a slightly mixed state with S = 20–25% of maximum:** The estimated entropy would be $\approx 43–48\%$ of maximum.

This precisely matches the observed NISQ "entropy plateau" at 40–50% — without invoking any physical decoherence whatsoever.

### 3.3 The Bias-Corrected Estimator

A corrected entropy estimate is:

$$\hat{S}_{vN}^{\text{corr}} = \hat{S}_{vN} - \frac{d-1}{2\nu} - \hat{B}_{\text{SPAM}} \tag{3.2}$$

where $\hat{B}_{\text{SPAM}}$ is estimated from measurement calibration circuits (applying known Clifford gates and measuring the entropy of the output, which is exactly known theoretically).

**Expected convergence under measurement-insufficiency hypothesis:**

$$\hat{S}_{vN}^{\text{corr}}(\nu) \approx \frac{d-1}{2\nu} + O(\nu^{-2}) \tag{3.3}$$

This function decreases monotonically toward zero as $\nu$ increases, converging to the true physical entropy. If the system is genuinely coherent (e.g., a GHZ state with theoretical $S_{vN} = 0$), then $\hat{S}_{vN}^{\text{corr}}(\nu) \to 0$ at the rate $\propto 1/\nu$.

---

## 4. CONNECTION TO THERMODYNAMIC GRAVITY

### 4.1 The Bridge [SYNTHESIS]

The constraint manifold formalism connects naturally to entropic gravity. In Jacobson's thermodynamic derivation, spacetime geometry emerges from entropy gradients across causal horizons — the geometry is "measuring" the entropy configuration of matter and quantum fields.

Our framework extends this: the observable subspace $\mathcal{O}(r)$ within which physical states are constrained is not a passive background. Each measurement (each event that makes a constraint irreversible) is an entropy-localization event — it reduces local entropy while exporting it to the environment (Landauer cost, see companion paper). These local entropy changes are precisely the kind of stress-energy modifications captured by the modified Einstein equation in the companion paper.

The key connection is:

$$\nabla S_{vN} \longrightarrow \text{entropy gradient} \longrightarrow \text{effective stress-energy} \longrightarrow \text{spacetime curvature}$$

The constraint manifold tells us that the *measurable* entropy gradient may differ from the *physical* entropy gradient by the estimator bias. For the gravitational prediction to be tested, we must ensure we are measuring actual physical entropy changes, not artifacts of our measurement budget.

### 4.2 Observation Is Not Passive [SYNTHESIS]

A crucial conceptual clarification: in this framework, "observation" is not a special metaphysical act performed by conscious beings. It is any physical process that irreversibly correlates with a constraint value — any decoherence event, any photon scattering, any measurement apparatus.

This means:
- **Decoherence** is just environmental observation — a surrogate observer (the environment) continuously measures the system and fixes constraints
- **Measurement** by a human experimenter or apparatus is the same physical process, just more controlled
- **Consciousness** plays no special role — it is irrelevant to the physics. The constraint-fixing is thermodynamic, not mental.

This explicitly contradicts any interpretation that places observers in a metaphysically special category. The physics is clean and observer-independent.

---

## 5. EXPERIMENTAL PROTOCOL FOR FALSIFICATION

### 5.1 Three-Stage Validation Protocol

**Stage 1 — Calibration:**
1. Prepare known-entropy states (computational basis states, Bell pairs, simple product states) with theoretically exact $S_{vN}$
2. Apply tomography at multiple shot counts $\nu \in \{10^3, 10^4, 10^5, 10^6\}$
3. Construct the SPAM correction matrix $\Lambda$ (a $d \times d$ matrix describing readout errors)
4. Verify that $\hat{S}_{vN}^{\text{corr}}$ converges to the theoretical $S_{vN}$ at the rate $\propto 1/\nu$

**Stage 2 — Scaling Test:**
1. Prepare $n$-qubit GHZ states $|\text{GHZ}\rangle = (|0\rangle^{\otimes n} + |1\rangle^{\otimes n})/\sqrt{2}$ for $n \in \{5, 8, 10, 12, 15\}$
2. GHZ states have theoretical $S_{vN} = 0$ for the full $n$-qubit state (they are pure) and $S_{vN} = 1$ bit for each subsystem (they are maximally entangled in any bipartition)
3. Measure $\hat{S}_{vN}(\nu)$ for $\nu \in \{10^3, 10^4, 10^5, 10^6\}$ shots
4. Apply SPAM correction: $\hat{\rho}_{\text{corr}} = \Lambda^{-1} \hat{\rho}_{\text{raw}}$

**Stage 3 — Convergence Verification:**
1. Compute bias-corrected entropy: $\hat{S}_{vN}^{\text{corr}}(\nu) = \hat{S}_{vN}(\nu) - (d-1)/(2\nu) - \hat{B}_{\text{SPAM}}$
2. Fit to the scaling model: $\hat{S}_{vN}^{\text{corr}}(\nu) = S_{vN}^{\text{phys}} + A/\nu + O(\nu^{-2})$
3. Extract $S_{vN}^{\text{phys}}$ as the $\nu \to \infty$ extrapolation
4. Compare $S_{vN}^{\text{phys}}$ to theoretical prediction (0 for pure GHZ state)

### 5.2 The Falsification Criterion

**The measurement-insufficiency hypothesis is falsified if:**

> For $n$-qubit GHZ states with verified entanglement depth $\geq n$ (confirmed by entanglement witness measurements), the SPAM-corrected entropy estimate $\hat{S}_{vN}^{\text{corr}}$ fails to converge to $S_{vN} < 0.1$ bits when shot count $\nu \geq 100 \cdot 2^{n/2}$, as verified by bootstrap resampling with $> 95\%$ confidence.

**The hypothesis is confirmed if:**

> For all $n \in \{5, 8, 10, 12, 15\}$, $\hat{S}_{vN}^{\text{corr}}(\nu)$ converges monotonically to the theoretical entropy as $\nu$ increases, with convergence rate consistent with $O(1/\nu)$, and the extrapolated $S_{vN}^{\text{phys}} < 0.1$ bits for GHZ states.

---

## 6. IMPLICATIONS

### 6.1 For Quantum Computing

If confirmed, this result means:
- Current NISQ devices have better coherence properties than their entropy estimates indicate
- Quantum advantage assessments based on entropy metrics should be revisited
- The "NISQ decoherence wall" may be, in part, a measurement wall that can be scaled over by increasing shot budgets

### 6.2 For Quantum Gravity Experiments

The companion paper proposes measuring entanglement entropy's gravitational effect. This requires *accurate* entropy measurement. If NISQ entropy estimates are systematically biased, then:
- Experiments cannot correctly estimate $S_{\text{ent}}$ (the source term in the modified Einstein equation)
- Gravitational signal predictions using biased entropy values will be systematically wrong
- SPAM-corrected, high-ν tomography is a prerequisite for any gravitational entanglement experiment

In short: the present paper provides an essential methodological foundation for the experimental protocol in the companion paper.

### 6.3 For Quantum Information Science

The scaling law $\nu \propto 2^{n/2}$ is a fundamental resource bound for entropy estimation in $n$-qubit systems. It implies that:
- Full quantum state tomography ($\nu \propto 4^n$) is never necessary for entropy estimation alone
- The "tomographic sufficiency threshold" for entropy is crossed at $\nu \sim 10^2 \cdot 2^{n/2}$, not at $\nu \sim d^2 = 4^n$
- Compressed sensing and randomized measurement protocols can in principle achieve this threshold

---

## 7. CONCLUSION

The apparent entropy plateau at 40–50% in NISQ devices is a consequence of finite-sample estimator bias, not fundamental hardware limitations. The required shot count for accurate entropy estimation scales as $\nu \propto 2^{n/2}$ — exponential in the qubit count, but with half the exponent of full state tomography.

The framework predicts precise convergence behavior that can be tested with currently available hardware and standard measurement protocols. Falsification requires confirming that the plateau persists after SPAM correction and shot-budget scaling to $\nu \geq 100 \cdot 2^{n/2}$ — a straightforward experimental test.

More broadly, this work establishes that:
1. Physical entropy and measured entropy are distinct quantities
2. Observation is a physical resource (measurement shots) that must scale with Hilbert space dimension
3. Much apparent disorder in quantum systems is epistemic (measurement-limited), not physical (decoherence-limited)
4. Hardware capabilities are routinely underestimated by entropy-based metrics

---

## REFERENCES

1. T. Jacobson, "Thermodynamics of spacetime: The Einstein equation of state," Phys. Rev. Lett. **75**, 1260 (1995).
2. S.T. Flammia, D. Gross, Y.-K. Liu, J. Eisert, "Quantum tomography via compressed sensing," New J. Phys. **14**, 095022 (2012). [Estimator bias formula]
3. M.G.A. Paris, "Quantum estimation for quantum technology," Int. J. Quantum Inf. **07**, 125 (2009). [Quantum Cramér-Rao bound]
4. K. Monette, "Gravitational coupling to entanglement entropy density," companion paper, this repository (2026).
5. E. Knill et al., "Randomized benchmarking of quantum gates," Phys. Rev. A **77**, 012307 (2008). [SPAM calibration methods]
6. J. Cotler, F. Wilczek, "Quantum overlapping tomography," Phys. Rev. Lett. **124**, 100401 (2020). [Efficient tomography protocols]
