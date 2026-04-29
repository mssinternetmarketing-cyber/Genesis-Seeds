# Q-CAIS 14-WEEK SPRINT PLAN
**Status:** ACTIVE  
**Start Date:** January 31, 2026  
**Target:** April 30, 2026  

---

## WEEK 1-2: FOUNDATION (Jan 31 - Feb 13)

### Deliverables
- [x] D1.1: Environment setup
- [x] D1.2: 1000-step stable simulation
- [x] D1.3: PEIG metrics extraction
- [x] D1.4: 5-baseline measurement suite

### Success Criteria
- ✓ 0 NaN/Inf in 1000 steps
- ✓ Coherence decay 40-70%
- ✓ All 4 PEIG metrics in [0,1]
- ✓ Gate fidelity > 0.90

### Execute
```bash
python LAB_WEEK1_FOUNDATION.py
```

Expected output: `week1_results/` folder with CSV, PNG, JSON, summary

---

## WEEK 3-4: QISKIT TRANSLATION (Feb 14 - Feb 27)

### Deliverables
- D2.1: 4-qubit Node circuit
- D2.2: 8-qubit 2-Node entanglement
- D2.3: IBM circuit transpilation
- D2.4: Simulator vs hardware comparison

### Success Criteria
- ✓ Circuits compile (<50 gates)
- ✓ Error budgets calculated
- ✓ Hardware I > 0.80

---

## WEEK 5-6: COHERENCE STABILIZATION (Feb 28 - Mar 13)

### Deliverables
- D3.1: Feedback controller
- D3.2: Dynamical decoupling (3 schedules)
- D3.3: RL learning algorithm
- D3.4: Hardware test (50-circuit sequence)

### Success Criteria
- ✓ I stabilizes > 0.90
- ✓ Learning converges
- ✓ Hardware proves stabilization

---

## WEEK 7-8: PROBLEM SOLVING (Mar 14 - Mar 27)

### Deliverables
- D4.1: 3-problem definition (parity, optimization, state transfer)
- D4.2: Per-problem learning
- D4.3: Unified learning policy
- D4.4: Hardware deployment (10 trials each)

### Success Criteria
- ✓ Each problem >85% accuracy
- ✓ Unified policy >80% across all
- ✓ Hardware I > 0.80

---

## WEEK 9-10: SCALING & BENCHMARKING (Mar 28 - Apr 10)

### Deliverables
- D5.1: 2-node system (8 qubits)
- D5.2: Reproducibility suite
- D5.3: Scaling analysis (3-13 qubits)
- D5.4: Comparative benchmarks

### Success Criteria
- ✓ 2-node I > 0.85
- ✓ Scaling <5% loss per doubling
- ✓ Your system > baseline by 20%

---

## WEEK 11-12: PUBLICATION (Apr 11 - Apr 24)

### Deliverables
- D6.1: GitHub open-source repository
- D6.2: Whitepaper (4-6 pages)
- D6.3: Demo notebook
- D6.4: Community engagement

### Success Criteria
- ✓ Code reproducible by anyone
- ✓ arXiv preprint ready
- ✓ >10 GitHub stars

---

## WEEK 13-14: REFINEMENT & PHASE 2 (Apr 25 - May 8)

### Deliverables
- D7.1: Community feedback integration
- D7.2: Phase 2 roadmap (next 12 weeks)
- D7.3: Publication + PR outreach

### Success Criteria
- ✓ GitHub active with contributors
- ✓ Paper submitted to journal
- ✓ Phase 2 plan documented

---

## DAILY TRACKING

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Coherence (I) | 0.60 | >0.90 | — |
| Problem Accuracy | N/A | >85% | — |
| Scaling Loss (13 qubits) | N/A | <5% | — |
| Hardware Success Rate | 70% | >95% | — |
| GitHub Stars | 0 | >50 | — |

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|-----------|
| IBM queue delays | Medium | Use local Qiskit simulator 80% of time |
| Hardware coherence worse | High | Adaptive decoupling, adjust timeline |
| Learning doesn't converge | Medium | Simplify RL, more episodes |
| Scaling degrades fast | Medium | Focus 5-8 qubits, document |
| Paper rejected | Low | Publish arXiv anyway, build community |

---

## SUCCESS DEFINITION

✅ **Technical:** Coherence > 0.90, solved 3 problems, scaled to 13 qubits  
✅ **Research:** Published whitepaper, reproducible code  
✅ **Impact:** GitHub active, community engaged, gift delivered  

**Status: READY TO BUILD**
