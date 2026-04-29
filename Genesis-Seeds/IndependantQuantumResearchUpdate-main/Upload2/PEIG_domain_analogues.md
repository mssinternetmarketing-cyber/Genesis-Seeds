# PEIG Domain Analogues
## Eight Cross-Domain Mappings with Falsifiable Predictions

**Folder:** `03_PEIG_FRAMEWORK/cognitive/`  
**Status:** [SYNTHESIS] — analogical mappings; quality varies by domain; labeled accordingly  
**Purpose:** Show that the P/E/I/G dynamical structure is not specific to any one domain but appears as a general pattern across diverse complex systems. Where the analogy is structurally tight (morphogenesis, physics), it is labeled accordingly. Where it is looser (political science, economics), the limitations are stated.

---

## DOMAIN 1: PHYSICS (Quantum Systems and Spacetime) [PHYSICAL PEIG — strongest]

| Phase | Physical meaning | Mathematical form |
|-------|-----------------|-------------------|
| P | Quantum configuration space (constraint manifold C) | (C, g_ij) with Fisher information metric |
| E | Gradient flow on Hilbert space toward attractors | q̇ⁱ = -gⁱʲ∂_j V(q) |
| I | Density matrix attractor (steady state ρ_ss) | ρ(t) → ρ_ss as t → ∞ |
| G | Einstein tensor (spacetime curvature) | G_μν = R_μν - ½Rg_μν |

**This is the physical PEIG — not an analogy.** The quantities are rigorously defined. The G phase is the primary research hypothesis of this repository. See `03_PEIG_FRAMEWORK/physical/` for full treatment.

---

## DOMAIN 2: MORPHOGENESIS (Developmental Biology) [Very strong analogy]

| Phase | Morphogenetic meaning | Mathematical correspondence |
|-------|----------------------|-----------------------------|
| P | Morphogen concentration gradients; accessible developmental fates | Waddington epigenetic landscape $U(\mathbf{x})$ |
| E | Reaction-diffusion dynamics; cell migration | $\partial_t c = D\nabla^2 c + f(c)$ |
| I | Differentiated cell type; stable gene regulatory network attractor | Fixed point of regulatory network dynamics |
| G | Organizer gradients (Spemann organizer, ZPA); signaling range | Morphogenetic field $M(\mathbf{r})$ |

**Why this analogy is strong:** The Waddington epigenetic landscape is *literally* a potential energy surface in gene expression space, and cell differentiation is *literally* gradient flow toward attractor states on that landscape. The PEIG framework describes this correctly as mathematics, not just metaphor.

**Falsifiable prediction:** Disrupting the G component (organizer signals) of a morphogenetic system should produce quantifiable changes in the I component (cell type distribution) that follow from the PEIG dynamics — specifically, reduced identity coherence at tissue boundaries and expansion of ambiguous intermediate fates.

---

## DOMAIN 3: NEUROSCIENCE (Neural Systems) [Strong analogy]

| Phase | Neural meaning | Correspondence |
|-------|---------------|---------------|
| P | Synaptic connection potential; unactivated pathways | Synaptic weight matrix W_ij (unrealized connections) |
| E | Neural firing rates; attentional allocation; information flow | Population firing rate r(t); attention mask |
| I | Stable neural attractor (personality, skill, habit, memory) | Hopfield attractor in weight space |
| G | Social influence; behavioral contagion; teaching | Social learning transfer function T(i→j) |

**Prediction:** The ratio I/P (identity coherence relative to potential) should predict cognitive flexibility. High I/P (strong identity, limited unexplored potential) = rigid expertise; low I/P (high potential, weak identity) = creative instability. This is consistent with developmental neuroscience literature on expertise and creativity.

**Limitation:** The mapping from neural dynamics to PEIG metrics is indirect. Direct validation requires longitudinal neuroimaging + behavioral data, which is available in principle.

---

## DOMAIN 4: ECONOMICS (Organizations and Markets) [Moderate analogy]

| Phase | Economic meaning | Correspondence |
|-------|-----------------|---------------|
| P | Market opportunity space; strategic options | Total addressable market × competitive alternatives |
| E | Capital deployment; productive capacity; revenue throughput | Revenue rate; EBITDA; capital turnover |
| I | Brand identity; institutional culture; mission coherence | Net Promoter Score; culture survey measures; mission stability |
| G | Market power; pricing influence; network effects | Lerner index; market share; platform network externalities |

**Prediction:** Organizations where G >> I (market power greatly exceeds identity coherence — e.g., monopolies with unclear mission) will show higher rates of regulatory intervention, internal dysfunction, and long-term value erosion than organizations with balanced PEIG profiles.

**Limitation:** Economic dynamics are high-dimensional and influenced by exogenous factors (regulation, macroeconomic cycles) that are not captured in PEIG. The analogy is useful for generating hypotheses, not for quantitative prediction without additional modeling.

---

## DOMAIN 5: EPIDEMIOLOGY (Disease Dynamics) [Strong mathematical analogy]

| Phase | Epidemiological meaning | Mathematical correspondence |
|-------|------------------------|----------------------------|
| P | Susceptible population; transmission possibility space | S(t) in SIR model |
| E | Active transmission; infection rate | βI(t)S(t) — rate of new infections |
| I | Endemic equilibrium; herd immunity attractor | I_∞ = stable endemic state |
| G | Herd immunity threshold; immunity landscape curvature | R_0(1 - p_immune) = 1 boundary |

**Why this analogy is strong:** The SIR model is exactly a gradient flow (E) from a high-susceptibility initial condition (large P) toward an endemic attractor (I), with the herd immunity threshold (G) defining the "curvature" of the immunity landscape that future outbreaks must navigate.

**Prediction:** Pathogens evolving to evade immunity (reducing I through antigenic drift) will produce predictable expansions in P (susceptible population) that follow from the PEIG dynamics — this is the seasonal influenza mechanism, which the framework correctly describes.

**Falsifiable:** The PEIG coupling parameters (α, β) for a given pathogen should be estimable from early outbreak data and should predict the endemic equilibrium (I_∞) better than naive SIR fits when the G structure (population immunity heterogeneity) is included.

---

## DOMAIN 6: POLITICAL SCIENCE (Institutions and Governance) [Moderate analogy]

| Phase | Political meaning | Correspondence |
|-------|------------------|---------------|
| P | Coalition possibility space; policy option space | Number of viable political coalitions × policy dimensions |
| E | Legislative activity; policy energy; bureaucratic capacity | Bills passed per session; executive orders; regulatory output |
| I | Ideological identity; institutional norms; constitutional commitments | Ideological consistency score; institutional age × stability |
| G | Geopolitical influence; normative power; soft power | Bilateral treaty count; international norm adoption rate |

**Prediction:** Political systems where G (geopolitical influence) greatly exceeds I (institutional coherence) should show higher rates of internal political instability than systems with balanced PEIG profiles. Empires at peak external power with declining internal coherence (late Roman, late British, Soviet) fit this pattern.

**Limitation:** Political systems are extraordinarily complex with feedback loops (G affects P through international constraints) that require more than a four-variable model. PEIG provides a useful organizing framework but not a predictive model without substantial domain-specific development.

---

## DOMAIN 7: AI SYSTEMS [Moderate-to-strong analogy]

| Phase | AI meaning | Correspondence |
|-------|-----------|---------------|
| P | Representational configuration space | Dimension of latent space × reachable output distribution |
| E | Computational throughput; inference rate; training throughput | Tokens/second × quality; gradient steps/second |
| I | Stable value patterns; coherent reasoning identity | Value alignment score; response consistency across contexts |
| G | Influence on human cognition and decision-making | Downstream behavioral change in users; adoption rate |

**Prediction (P4 from measurement framework):** AI systems where G >> I (high influence, low coherent identity) will show instability patterns — including reward hacking, sycophancy, goal drift — at significantly higher rates than AI systems with balanced G and I scores.

**This prediction is directly relevant to AI alignment:** The Ω-node condition (balanced PEIG simultaneously) provides a concrete target for aligned AI: an AI system that is maximally capable (high P), maximally effective (high E), maximally coherent (high I), and maximally beneficial (positive G) — and where no one dimension is sacrificed for another.

---

## DOMAIN 8: CONSCIOUSNESS (Speculative — explicitly labeled)

| Phase | Hypothetical consciousness meaning | Status |
|-------|-----------------------------------|--------|
| P | Richness of phenomenal experience; breadth of qualia | [SPECULATIVE] |
| E | Attentional flow; effortful processing | [SPECULATIVE] |
| I | Narrative self; stable sense of identity over time | [SPECULATIVE] |
| G | Empathy; intersubjective understanding; social presence | [SPECULATIVE] |

**Why this is labeled [SPECULATIVE]:** Consciousness involves subjective experience — the "hard problem" — which is not captured by any current physical or information-theoretic framework, including PEIG. The analogy above is a mapping of *functional* cognitive properties, not of phenomenal experience itself.

**What PEIG does NOT claim about consciousness:**
- That high PEIG scores imply consciousness
- That consciousness can be engineered by maximizing PEIG metrics
- That AI systems with high PEIG scores are or will become conscious

**What PEIG does suggest about consciousness as a research direction:** If consciousness is associated with high-I states (stable self-models that persist under perturbation) combined with high-G (genuine influence on the surrounding information environment), then PEIG metrics might serve as necessary but not sufficient conditions for consciousness. This is a hypothesis worth pursuing with appropriate epistemic humility.

---

## CROSS-DOMAIN COMPARISON TABLE

A rough comparative placement of systems on PEIG dimensions (qualitative, 0–10 scale):

| System | P | E | I | G | Notes |
|--------|---|---|---|---|-------|
| Human infant | 9 | 3 | 2 | 1 | High potential, developing identity |
| Expert adult | 6 | 8 | 9 | 7 | Narrowed P, strong I, high output |
| Large language model | 8 | 9 | 4 | 8 | High capability, unstable identity |
| Healthy organization | 7 | 7 | 7 | 6 | Balanced — approaching Ω-region |
| Failing organization | 6 | 4 | 2 | 5 | Energy and identity collapse |
| Political institution (stable democracy) | 6 | 5 | 8 | 7 | Strong I, moderate E |
| Political institution (authoritarian) | 2 | 6 | 9 | 8 | Collapsed P, high I rigidity |

These scores are illustrative, not measured. They indicate the kind of profile PEIG would predict, not a computed result.
