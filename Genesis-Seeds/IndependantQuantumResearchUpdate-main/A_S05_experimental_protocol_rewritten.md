# Section 05: Experimental Protocol
## Near-Term Experimental Strategy for Testing Entanglement–Gravity Coupling

**Paper:** A — Gravitational Coupling to Entanglement Entropy Density  
**Section:** 5 of 6  
**Status:** [REVISED HYPOTHESIS] — protocol updated after OP4 and screening-risk review; quantitative signal size remains indeterminate pending resolution of \(lpha_{	ext{screen}}\)

---

## 5.1 Experimental Concept

The core observable remains a **differential acceleration or phase shift** between two systems prepared to be as identical as possible except for their entanglement structure. One arm is prepared in a coherent entangled state with nonzero \(S_{	ext{ent}}\); the comparison arm is deliberately decohered or prepared in a low-entanglement reference state.

The logic of the test is unchanged: if all non-entanglement degrees of freedom are matched, any reproducible residual signal correlated with entanglement preparation would support the hypothesis that entanglement entropy contributes to the effective gravitational source term. Conversely, a null result at validated sensitivity contributes directly to falsification constraints.

## 5.2 Change in near-term target

The previous version of this section treated a **macroscopic \(N = 10^6\) atom ensemble** as the primary experiment. That is no longer the appropriate near-term target.

Recent review of the screening model indicates that the Gaussian screening factor used in Section 04 may suppress the effective coupling for a macroscopic \(^{87}\)Rb ensemble by an amount as small as \(lpha_{	ext{screen}} \sim 10^{-43}\), which is radically inconsistent with the heuristic \(10^{-4}\) to \(10^{-2}\) range used in earlier order-of-magnitude estimates. Until that discrepancy is resolved, a macroscopic neutral-atom protocol cannot be defended as a quantitatively motivated primary experiment.

The revised near-term target is therefore a **50–100 qubit NISQ-scale experiment**, where entanglement structure is programmable, state verification is more direct, and the interpretation of any screening factor is less likely to be confounded by uncontrolled bulk-ensemble averaging.

## 5.3 Recommended platform class

The most appropriate near-term implementation is a programmable NISQ platform in which entanglement depth, geometry, and decoherence channels can be controlled explicitly. Candidate platforms include neutral-atom arrays, trapped ions, or superconducting-qubit devices, provided the protocol can compare a high-entanglement branch against a matched low-entanglement branch under otherwise equivalent timing and control conditions.

This section does **not** assume that current NISQ devices can already detect the target effect. The point of the revised protocol is that they provide a cleaner and more interpretable regime for constraining the theory while the macroscopic-screening problem remains unresolved.

## 5.4 Signal statement after OP4 review

The previous version of Section 05 quoted a specific acceleration sensitivity mapping, including a tentative value

\[ \delta |	ilde{\kappa}| pprox 3.7 	imes 10^{-13} \]

and treated that value as if it were a stable experimental forecast. That statement must be removed.

The OP4 review established that the radial behavior of the predicted correction depends on the explicit source profile through the enclosed-source relation

\[ \Delta a(R) = rac{\kappa}{R^2} M_{	ext{ent}}(<R) \]

rather than through a universally valid \(1/R\) expression. A bounded source profile yields an exterior \(1/R^2\) scaling, whereas a \(1/R\) correction requires an extended profile such as \(ho_{	ext{ent}}(r) \propto 1/r^2\). Because the source profile and the screening behavior are both unsettled, the signal magnitude should now be stated as **indeterminate pending resolution of \(lpha_{	ext{screen}}\)** and of the final radial source model.

## 5.5 Measurement logic

A near-term NISQ implementation should be organized around a differential protocol:

- **Branch A:** prepare a 50–100 qubit state with maximal or near-maximal multipartite entanglement consistent with device capabilities.
- **Branch B:** prepare a matched reference state with the same qubit count, control sequence, and gross energy budget, but with entanglement intentionally suppressed or destroyed.
- **Readout:** compare the entanglement-conditioned phase, acceleration proxy, or equivalent interferometric observable across repeated trials.
- **Control checks:** interleave randomized compilation, device-bias reversals where available, and explicit entanglement-witness measurements to verify that the two branches differ in entanglement structure rather than in uncontrolled hardware drift.

The exact observable will depend on hardware platform. The essential requirement is that the protocol preserve a sharp comparison between entangled and minimally entangled states while holding conventional systematics as fixed as possible.

## 5.6 Systematic considerations

The dominant systematic question is no longer merely classical accelerometer sensitivity. It is now the interpretability of the effective source term in the presence of screening, finite device geometry, and state-preparation imperfections.

Key systematics for the revised program are:

| Systematic | Why it matters | Mitigation |
|-----------|----------------|-----------|
| Imperfect state preparation | Can mimic reduced entanglement-dependent signal | Verify entanglement depth or witness before/after acquisition |
| Decoherence drift | Changes branch contrast over time | Randomized branch order; short calibration cycles |
| Geometry-dependent coupling assumptions | Affects mapping from theory to predicted signal | Simulate each platform with explicit source profile assumptions |
| Platform-specific cross-talk | Can create false branch asymmetries | Symmetrize control pulses and include null reference circuits |
| Ambiguous screening regime | Prevents trustworthy signal forecasts | Treat signal size as indeterminate until \(lpha_{	ext{screen}}\) is derived or bounded in-regime |

## 5.7 What remains unchanged

The **falsification criterion** from Section 06 should remain intact. A null result, provided it is obtained in a regime where the source model and screening assumptions are explicitly stated and the device sensitivity is validated, still constrains or falsifies the entanglement–gravity coupling hypothesis.

What changes here is not the logic of falsification, but the claimed readiness of the experimental platform. The manuscript should no longer present a million-atom \(^{87}\)Rb ensemble as the default primary test, and it should no longer quote a determinate sensitivity-to-\(	ilde{\kappa}\) mapping until the screening and source-profile issues are resolved.

---

*Next: Section 06 — The falsification criterion*
