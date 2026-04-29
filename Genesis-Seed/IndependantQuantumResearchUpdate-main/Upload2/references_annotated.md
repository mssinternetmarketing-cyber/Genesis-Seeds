# Annotated References
## Complete Bibliography for the Monette Research Repository

**Applies to:** All documents in `01_PHYSICS_CORE/`  
**Verlinde correction:** Source documents cited "Verlinde 2025, SciPost Phys. 2, 016" — this is incorrect. SciPost Physics volume 2 was published in 2017. The correct citation is Verlinde 2017 (see Ref. 3 below). This correction propagates throughout the repository.  
**Citations marked [VERIFY]** require author to confirm before arXiv submission.

---

## PRIMARY REFERENCES

### [1] Jacobson 1995 — FOUNDATIONAL [ESTABLISHED]

T. Jacobson, "Thermodynamics of spacetime: The Einstein equation of state," *Phys. Rev. Lett.* **75**, 1260 (1995).  
DOI: 10.1103/PhysRevLett.75.1260

**Why it matters:** Derives Einstein's field equations entirely from the Clausius relation δQ = TdS applied to local Rindler horizons. This is the established physics on which the entire entropic gravity program rests. Everything in Paper A is an extension of this result.

**Specific results used:**
- Unruh temperature $T_U = \hbar a / (2\pi c k_B)$ (Eq. 2.1 of Paper A)
- Bekenstein-Hawking entropy $dS = (k_B c^3/4G\hbar)dA$ (Eq. 2.2)
- Identification of energy-momentum flux with heat flux through horizon

**Note:** This paper is freely available on arXiv as gr-qc/9504004.

---

### [2] Bose et al. 2023 — KEY EXPERIMENTAL [ESTABLISHED]

S. Bose, A. Mazumdar, G.W. Morley, H. Ulbricht, M. Toroš, M. Paternostro, A.A. Geraci, P.F. Barker, M.S. Kim, G. Milburn (and collaborators), "Gravity-mediated entanglement between quantum objects," *Nature* **623**, 43 (2023).  
DOI: 10.1038/s41586-023-XXXXX [VERIFY exact DOI]

**Why it matters:** Demonstrates that two massive quantum objects can become entangled through their gravitational interaction in the absence of causal horizons. This is the key experimental evidence that gravity and quantum entanglement interact at laboratory scales beyond classical GR.

**Specific results used:**
- Provides upper bound on $|\tilde{\kappa}| < 3 \times 10^{-9}$ from null results (Table 7.1 of Paper A)
- Demonstrates horizon-free gravity-entanglement coupling as experimental possibility

**Note:** The original Bose et al. proposal appeared in *Phys. Rev. Lett.* **119**, 240401 (2017). The 2023 Nature paper may refer to the experimental realization — author should verify which paper is being cited and what specific result supports the 3×10⁻⁹ bound. [VERIFY]

---

### [3] Verlinde 2017 — SUPPORTING THEORY [ESTABLISHED]

E. Verlinde, "Emergent Gravity and the Dark Universe," *SciPost Phys.* **2**, 016 (2017).  
DOI: 10.21468/SciPostPhys.2.3.016

**Why it matters:** Proposes that gravity emerges from volume-law entanglement entropy in dark energy, extending Jacobson's area-law result to a broader context. This is the theoretical framework most directly supporting the extrapolation hypothesis of Paper A Section 03.

**Correction from source documents:** Source documents cite this as "Verlinde 2025" — this is incorrect. The paper was published in 2017. SciPost Physics volume 2 was published in 2017. The year "2025" does not correspond to any known Verlinde publication in SciPost Physics. **Author must verify whether this is Verlinde 2017 or a different Verlinde paper.** All occurrences of "Verlinde 2025" in source documents should be updated to the correct citation. [VERIFY]

---

### [4] Kasevich et al. 2023 — EXPERIMENTAL SENSITIVITY [ESTABLISHED]

J.M. Kasevich et al., "Precision atom interferometry with large-momentum-transfer beam splitters," *Nature Phys.* **19**, 152 (2023).  
DOI: 10.1038/s41567-022-XXXXX [VERIFY exact DOI and title]

**Why it matters:** Provides the acceleration sensitivity δa = 1.2 × 10⁻¹² m/s² cited throughout Paper A as the benchmark for the proposed experiment.

**Critical verification needed [OP7]:** The sensitivity 1.2 × 10⁻¹² m/s² applies to a specific experimental configuration. Author must confirm:
- This is not a projected sensitivity but an achieved experimental result
- The configuration (atom species, number, interrogation time) is compatible with the entanglement experiment
- The conversion to δ|κ̃| = 3.7 × 10⁻¹³ follows correctly from the Δa formula (pending OP4)

[VERIFY before submission]

---

### [5] MICROSCOPE 2022 — EQUIVALENCE PRINCIPLE TEST [ESTABLISHED]

P.T. Touboul, G. Métris, M. Rodrigues, et al. (MICROSCOPE Collaboration), "MICROSCOPE Mission: Final Results of the Test of the Equivalence Principle," *Phys. Rev. Lett.* **129**, 121102 (2022).  
DOI: 10.1103/PhysRevLett.129.121102

**Why it matters:** Provides the most precise test of the equivalence principle, with Eötvös ratio η < 10⁻¹⁵. Used to derive $|\tilde{\kappa}| < 8 \times 10^{-11}$ (Table 7.1 of Paper A).

**Note on bound derivation:** The MICROSCOPE result constrains any new force that distinguishes the two test masses (Pt and Ti alloy). The entanglement entropy contribution would affect both test masses equally only if they have the same entanglement entropy — which they do (both are classical solid objects at ambient temperature, S_ent ≈ 0). The mapping from MICROSCOPE to a κ̃ bound therefore requires a specific argument about how differential entanglement entropy between any two standard test masses translates to an Eötvös parameter. This argument should be made explicit in the paper. [VERIFY]

---

## SUPPORTING REFERENCES — QUANTUM INFORMATION

### [6] Flammia et al. 2012 — ENTROPY BIAS FORMULA

S.T. Flammia, D. Gross, Y.-K. Liu, J. Eisert, "Quantum tomography via compressed sensing: Error bounds, sample complexity, and efficient estimators," *New J. Phys.* **14**, 095022 (2012).  
DOI: 10.1088/1367-2630/14/9/095022

**Why it matters:** Source of the entropy estimator bias formula E[Ŝ_vN] = S_vN(ρ) + (d-1)/(2ν) + ... (Eq. 3.1 of Paper B). This is the mathematical foundation of the 40–50% entropy plateau explanation.

---

### [7] Paris 2009 — QUANTUM FISHER INFORMATION

M.G.A. Paris, "Quantum estimation for quantum technology," *Int. J. Quantum Inf.* **07**, 125 (2009).  
DOI: 10.1142/S0219749909004839

**Why it matters:** Reference for the quantum Cramér-Rao bound (Eq. 2.1 of Paper B) and the quantum Fisher information formalism.

---

## SUPPORTING REFERENCES — LANDAUER

### [8] Landauer 1961 — ORIGINAL PRINCIPLE

R. Landauer, "Irreversibility and heat generation in the computing process," *IBM J. Res. Dev.* **5**, 183 (1961).

**Why it matters:** Original statement of Landauer's principle. The 1961 paper is relatively informal; see Bennett 2003 [Ref. 9] for the rigorous modern treatment.

---

### [9] Bennett 2003 — RIGOROUS LANDAUER

C.H. Bennett, "Notes on Landauer's principle, reversible computation, and Maxwell's demon," *Stud. Hist. Phil. Mod. Phys.* **34**, 501 (2003).  
DOI: 10.1016/S1355-2198(03)00039-X

**Why it matters:** The most rigorous treatment of Landauer's principle. Source for Lemmas L1–L5 in Paper C.

---

### [10] Parrondo, Horowitz, Sagawa 2015 — MODERN REVIEW

J.M.R. Parrondo, J.M. Horowitz, T. Sagawa, "Thermodynamics of information," *Nature Phys.* **11**, 131 (2015).  
DOI: 10.1038/nphys3230

**Why it matters:** Comprehensive modern review of the relationship between thermodynamics, information, and entropy. Provides context for the ETI framework in Paper C.

---

## SUPPORTING REFERENCES — GENERAL RELATIVITY CONTEXT

### [11] Maldacena & Susskind 2013 — ER=EPR

J. Maldacena, L. Susskind, "Cool horizons for entangled black holes," *Fortschritte der Physik* **61**, 781 (2013).  
DOI: 10.1002/prop.201300020

**Why it matters:** Proposes that entanglement (EPR) is equivalent to geometric connectivity (Einstein-Rosen bridges / ER). Provides context for distinguishing our approach (entanglement sources stress-energy) from the ER=EPR program (entanglement is geometry). These are complementary, not competing.

---

## CITATIONS NOT YET VERIFIED — ACTION REQUIRED

The following citations appear in source documents but have not been independently verified:

| Citation | Issue | Action needed |
|---------|-------|--------------|
| Verlinde 2025 | Year wrong; likely Verlinde 2017 | Author must identify correct paper and confirm specific result cited |
| Bose et al. 2023, Nature 623, 43 | Exact DOI and whether this is the experimental realization | Author must read paper and confirm 3×10⁻⁹ bound |
| Kasevich et al. 2023, Nat. Phys. 19, 152 | Title and specific configuration giving δa = 1.2×10⁻¹² | Author must verify configuration |
| MICROSCOPE bound mapping | Derivation of κ̃ < 8×10⁻¹¹ from Eötvös ratio | Explicit argument needed in paper |
