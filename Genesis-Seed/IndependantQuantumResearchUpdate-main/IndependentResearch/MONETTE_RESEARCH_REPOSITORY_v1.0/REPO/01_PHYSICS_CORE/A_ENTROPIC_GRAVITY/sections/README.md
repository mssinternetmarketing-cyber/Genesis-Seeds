# A_ENTROPIC_GRAVITY

**Repository:** Monette Research — Entropic Gravity & PEIG Framework  
**Parent:** `01_PHYSICS_CORE/`  
**Status:** Pre-submission draft — all Phase 2 corrections applied  
**Target journals:** Physical Review Letters, Nature Physics  
**Last Updated:** March 2026

---

## Purpose

This folder contains the complete physics paper on gravitational coupling to
entanglement entropy density. It is the primary peer-review-bound deliverable
of this research program. Every other folder in the repository either supports
this work (definitions, corrections) or extends it (PEIG framework, speculative
engineering).

---

## Sections

| File | Content | Phase 2 Issues Resolved |
|---|---|---|
| `sections/01_theory.tex` | Modified Einstein equation; full κ̃ derivation; screening factor; conservation tension | κ̃ = −1/4 reframed as estimate; screening variables defined; conservation discussed |
| `sections/02_dimensional_rigor.tex` | Complete unit verification; bit-to-entropy conversion table; correction of G_eff formula | Dimensional error in G_eff formula corrected and explained |
| `sections/03_extrapolation_boundary.tex` | Where Jacobson's framework ends; the lab-scale hypothesis; three motivations; response to reviewers | Honest framing of what is proven vs. hypothesized |
| `sections/04_experimental_protocol.tex` | Atom interferometry setup; Δa(R) derivation; sensitivity; 3-stage protocol | First derivation of Δa(R) formula in the entire corpus |
| `sections/05_falsification.tex` | Canonical falsification criterion; confirmation threshold; bounds table; decision tree | Unified three competing versions into one canonical statement |

---

## How to Compile

This folder is designed to be included in `master_paper.tex` at the root of
`A_ENTROPIC_GRAVITY/` using `\input{sections/01_theory}` etc. Compile with:

```bash
pdflatex master_paper.tex
bibtex master_paper
pdflatex master_paper.tex
pdflatex master_paper.tex
```

Or upload the full folder to **Overleaf** for browser-based compilation with
automatic dependency resolution.

---

## Key Results Summary

**Modified Einstein equation:**
$$G_{\mu\nu} = 8\pi G\,T_{\mu\nu} + \tilde{\kappa}\,\frac{c^4}{k_B\ln 2}\,S_{\text{ent}}\,g_{\mu\nu}$$

**Ideal coupling (under holographic Planck-scale regulator hypothesis):**
$$\tilde{\kappa} = -\frac{1}{4}$$

**Realistic range (with environmental screening):**
$$\tilde{\kappa} \in [-2.5\times10^{-3},\; -2.5\times10^{-5}]$$

**Experimental sensitivity:**
$$\delta|\tilde{\kappa}| = 3.7\times10^{-13}$$

**Falsification threshold:**
$$|\tilde{\kappa}| < 10^{-15} \text{ after 1000 runs on 2+ platforms at } \Delta p < 10^{-6}\text{ Pa}$$

---

## What Changed From Source Files

The most important changes from the original corpus documents:

1. **κ̃ = −1/4 is no longer called a "derivation."** It is a
   first-principles *estimate* under the holographic Planck-scale regulator
   hypothesis. The exact point where the hypothesis enters the calculation
   is marked with a framed box in `01_theory.tex`.

2. **The Δa(R) formula is now derived.** It was asserted without derivation
   across all source documents. `04_experimental_protocol.tex` provides the
   first derivation, starting from the linearized modified Poisson equation.

3. **The dimensional error in the emergent G formula is corrected.**
   `02_dimensional_rigor.tex` shows the error explicitly and explains why no
   simple dimensional-analysis formula can recover Newton's G from
   entanglement gradients without a full holographic UV completion.

4. **The three competing falsification statements are unified.** Five source
   files each stated slightly different falsification criteria. The canonical
   version in `05_falsification.tex` supersedes all of them.

5. **The conservation equation tension is acknowledged.** The modified
   Einstein equation implies that ordinary matter stress-energy is not
   independently conserved. This is now stated as a prediction of the
   framework, not swept under the rug.
