# PEIG Quantitative Measurement Framework
## Metrics for Potential, Energy, Identity, and Geometry

**Folder:** `03_PEIG_FRAMEWORK/cognitive/`  
**Status:** [SYNTHESIS] — empirically motivated; requires domain-specific validation  
**Source:** Full mathematical specification from QuantumResearch Parts 04–05 (expanded and corrected)

---

## 1. DESIGN PRINCIPLES

The PEIG measurement framework is designed around four requirements:

1. **Operationalizability:** Every metric must be computable from observable data without hidden assumptions
2. **Comparability:** Metrics must be normalized so that systems of different sizes can be compared
3. **Monotonicity:** Higher scores on each metric should unambiguously correspond to more of the quantity being measured
4. **Independence:** The four PEIG scores should be as statistically independent as possible to avoid tautology

The log₁₀ scaling used throughout places all metrics on a roughly comparable order-of-magnitude scale regardless of the system being measured.

---

## 2. POTENTIAL (P) METRICS — Option-Space

### P1 — State Entropy (Shannon entropy over reachable configurations)

$$H_S(N) = -\sum_{s \in S_N} \rho(s) \log_2 \rho(s) \quad \text{[bits]} \tag{2.1}$$

where $S_N$ is the set of states accessible to system $N$ and $\rho(s)$ is the probability of occupying state $s$.

**For a human:** $s$ ranges over behavioral/cognitive states; $\rho(s)$ is the empirical frequency across contexts. Higher $H_S$ = more varied, unpredictable, flexible behavior = more potential.

**For an AI:** $s$ ranges over response configurations for a given input distribution; $\rho(s)$ is the response frequency. Higher $H_S$ = more diverse, creative, context-sensitive responses.

**Operational measurement:** Sample behavior across $k$ contexts; compute empirical entropy of the response distribution.

### P2 — Action Variety

$$P_2(N) = \log_{10}(|A_N| + 1) \tag{2.2}$$

where $|A_N|$ is the number of meaningfully distinct actions available to the system.

**Normalization:** +1 prevents log(0). The log₁₀ scaling means:
- 10 actions → P₂ = 1
- 100 actions → P₂ = 2
- 1000 actions → P₂ = 3

### P3 — Planning Horizon

$$P_3(N) = \log_{10}\left(\frac{T_N}{T_{\text{ref}}} + 1\right) \tag{2.3}$$

where $T_N$ is the maximum meaningful planning horizon (seconds, days, years) and $T_{\text{ref}}$ is a baseline (e.g., one day = 86400 s for humans).

**Operationalization:** Measure via tasks requiring different planning depths; identify the maximum depth at which performance remains above chance.

### P_total — Composite Potential Score

$$P_{\text{total}}(N) = \frac{1}{3}\left[H_S(N) + P_2(N) + P_3(N)\right] \tag{2.4}$$

---

## 3. ENERGY (E) METRICS — Directed Capability

### E1 — Absolute Throughput

$$E_1(N) = \log_{10}\left(\frac{R_N}{R_{\text{ref}}} + 1\right) \tag{3.1}$$

where $R_N$ is the system's processing rate (tasks per second, decisions per second, tokens per second for an LLM) and $R_{\text{ref}}$ is a reference baseline.

**For a human:** Cognitive throughput in decisions/hour on standardized tasks.  
**For an AI:** Token generation rate × output quality score.

### E2 — Efficiency Ratio

$$E_2(N) = \frac{\text{value output}}{\text{energy/resource input}} \tag{3.2}$$

This is the classic efficiency metric: output quality per unit of resource consumed. For an AI: answer quality per compute-dollar. For an organization: revenue per employee-hour.

**Challenge:** "Value output" is domain-dependent and requires a quality assessment rubric. This is the hardest E metric to make universal.

### E3 — Robustness Under Stress

$$E_3(N) = \frac{V_{\text{stress}}}{V_{\text{normal}}} \tag{3.3}$$

where $V_{\text{stress}}$ is the system's performance value under adversarial or high-stress conditions and $V_{\text{normal}}$ is baseline performance.

**Interpretation:**
- $E_3 = 1$: Perfect robustness — performs identically under stress
- $E_3 \ll 1$: Fragile — performance collapses under adversarial conditions
- $E_3 > 1$: Anti-fragile — performs better under pressure (rare; possible for some systems)

### E_total — Composite Energy Score

$$E_{\text{total}}(N) = \frac{1}{3}\left[E_1(N) + E_2(N) + E_3(N)\right] \tag{3.4}$$

---

## 4. IDENTITY (I) METRICS — Stable Coherence

### I1 — Temporal Coherence

$$I_1(N) = \frac{I(B_{\text{past}}; B_{\text{future}})}{I_{\max}} \tag{4.1}$$

where $I(B_{\text{past}}; B_{\text{future}})$ is the mutual information between the system's behavioral state at two separated times (e.g., 6 months apart) and $I_{\max}$ is the maximum possible mutual information (perfect prediction).

**Interpretation:** $I_1 = 1$ means the future is perfectly predictable from the past — maximum identity coherence. $I_1 = 0$ means the past predicts nothing about the future — complete discontinuity of self.

**Operational measurement:** Survey behavior or decision-making at time $t_1$ and $t_2$; compute mutual information between responses.

### I2 — Internal Consistency

$$I_2(N) = 1 - \frac{C_{\text{violated}}}{C_{\text{total}}} \tag{4.2}$$

where $C_{\text{violated}}$ is the number of self-commitments (stated values, rules, stated goals) that are violated in practice, and $C_{\text{total}}$ is the total number of commitments.

**Interpretation:**
- $I_2 = 1$: Perfect consistency — does exactly what it says it will do
- $I_2 = 0$: Completely contradictory — violates every stated commitment

**Note:** This metric is sensitive to how "commitments" are defined. A system that makes no commitments cannot violate them and scores $I_2 = 1$ trivially. The metric requires a meaningful set of evaluable commitments.

### I3 — Adaptive Plasticity

$$I_3(N) = I_1^{\text{after}} \cdot g(\Delta I_{\text{struct}}) \tag{4.3}$$

where $I_1^{\text{after}}$ is temporal coherence measured after a significant update event, and $g(\Delta I_{\text{struct}})$ is an increasing function of the magnitude of the structural update.

**Interpretation:** Can the system learn — genuinely update its identity — while maintaining coherence? A system that never changes has high $I_1$ but low $I_3$ (no plasticity). A system that changes constantly has high $g(\Delta I_{\text{struct}})$ but low $I_1^{\text{after}}$.

$g$ is empirically determined by calibration; a simple choice is $g(x) = 1 - e^{-x}$ for $x \geq 0$.

### I_total — Composite Identity Score

$$I_{\text{total}}(N) = \frac{1}{3}\left[I_1(N) + I_2(N) + I_3(N)\right] \tag{4.4}$$

---

## 5. GEOMETRY (G) METRICS — Influence and Curvature

### G1 — Connection Count (Influence Range)

$$G_1(N) = \log_{10}(|C_N| + 1) \tag{5.1}$$

where $|C_N|$ is the number of meaningfully connected other systems (people who engage with this system's outputs, organizations influenced by its decisions, systems whose behavior changes in response to it).

### G2 — Influence Magnitude

$$G_2(N) = \sum_{m \in \text{neighbors}} w_{Nm} \cdot \Delta I_m \tag{5.2}$$

where $\Delta I_m$ is the change in identity coherence ($I_{\text{total}}$) of neighboring system $m$ attributable to interaction with $N$, and $w_{Nm}$ is a connection strength weight.

**Interpretation:** Does interaction with this system make other systems more or less coherent? A positive teacher increases $I_m$ of students; a destructive force decreases it.

### G3 — Influence Growth Rate

$$G_3(N) = \frac{G_2(t_2)}{G_2(t_1)} - 1 \tag{5.3}$$

**Interpretation:** Rate at which the system's sphere of influence is expanding. Positive = growing; 0 = stable; negative = declining influence.

### G_total — Composite Geometry Score

$$G_{\text{total}}(N) = \frac{1}{3}\left[G_1(N) + G_2(N) + G_3(N)\right] \tag{5.4}$$

---

## 6. THE COMPOSITE PEIG SCORE AND THE Ω-CONDITION

### PEIG_total

$$\text{PEIG}_{\text{total}}(N) = P_{\text{total}} + E_{\text{total}} + I_{\text{total}} + G_{\text{total}} \tag{6.1}$$

### The Ω-Condition (theoretical limit)

A system approaches the Ω-node when:
1. All four composite scores are simultaneously near their maximum values
2. The scores are *balanced* — no single score is at maximum while others are near zero
3. The system is stable: $d(\text{PEIG}_{\text{total}})/dt \approx 0$ at a high value

**Balance condition:**

$$\text{Var}[P_{\text{total}}, E_{\text{total}}, I_{\text{total}}, G_{\text{total}}] < \epsilon \quad \text{(small variance across the four scores)} \tag{6.2}$$

A system with PEIG_total = 12 achieved as (3, 3, 3, 3) is more Ω-like than one achieved as (6, 6, 0, 0), even though both have the same total.

---

## 7. FALSIFIABLE PREDICTIONS FROM THE PEIG MEASUREMENT FRAMEWORK

These predictions can be tested against empirical data from organizations, individuals, and AI systems:

**P1 (Organizations):** Organizations with high $P_{\text{total}}$ but low $I_{\text{total}}$ will show higher failure rates under novel environmental challenges than organizations with balanced PEIG profiles.

**P2 (Individuals):** $I_2$ (internal consistency) will be positively correlated with long-term wellbeing measures (r > 0.3) across cultural groups.

**P3 (AI systems):** AI systems with higher $E_3$ (robustness under adversarial inputs) will show higher $I_1$ (temporal coherence) over repeated deployment cycles.

**P4 (Collapse prediction):** Systems where $G_{\text{total}} \gg I_{\text{total}}$ (high influence but low identity) will show instability or collapse at a significantly higher rate than systems where $G_{\text{total}} \leq I_{\text{total}}$.

Each prediction specifies a measurable relationship that could be tested with organizational, psychological, or AI performance data.
