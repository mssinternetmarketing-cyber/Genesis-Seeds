# Experimental Data Standards
## Format Specification for Incoming Experimental Results

**Folder:** `06_EXPERIMENTAL_DATA/`  
**Status:** Infrastructure document — no data yet; defines the format for when data arrives  
**Purpose:** Ensure that when real experimental results come in, they are stored in a format that allows immediate comparison with theoretical predictions and honest falsification assessment.

---

## 1. WHAT THIS FOLDER WILL CONTAIN

When real experiments are performed testing the κ̃ coupling, this folder will contain:
- Raw acceleration measurement data (differential Δa between coherent and decohered arms)
- Entropy verification data (entanglement witness results confirming entanglement depth)
- SPAM calibration data (per experiment run)
- Shot-scaling data (entropy vs. ν for Paper B validation)
- Upper bound tables (as experiments set increasingly stringent bounds)

Until real data exists, this folder contains only this standards document.

---

## 2. DATA FILE FORMAT STANDARDS

### 2.1 Raw Acceleration Data

Filename: `DeltaA_[platform]_[date]_[run_number].csv`

Example: `DeltaA_Rb87_BEC_20270315_run042.csv`

Required columns:

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| run_id | integer | — | Unique run identifier |
| timestamp | ISO8601 | — | UTC timestamp of measurement |
| N_atoms | integer | — | Atom number in coherent arm |
| entanglement_depth | integer | — | Verified entanglement depth (from witness) |
| T_coherence | float | s | Measured coherence time |
| delta_a_measured | float | m/s² | Differential acceleration measurement |
| delta_a_uncertainty | float | m/s² | 1-sigma statistical uncertainty |
| delta_a_systematic | float | m/s² | Estimated systematic error |
| kappa_tilde_bound | float | — | Upper bound on |κ̃| from this run |
| entanglement_verified | boolean | — | TRUE if witness confirms entanglement |
| notes | string | — | Any anomalies or issues with this run |

### 2.2 Entropy Scaling Data (Paper B validation)

Filename: `EntropyScaling_[platform]_[n_qubits]_[date].csv`

Required columns:

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| n_qubits | integer | — | Qubit count |
| nu_shots | integer | — | Number of measurement shots |
| S_vN_raw | float | bits | Raw entropy estimate |
| S_vN_corrected | float | bits | SPAM-corrected entropy estimate |
| S_vN_theoretical | float | bits | Theoretical entropy (for known state) |
| bias_estimated | float | bits | Estimated sampling bias (d-1)/(2ν) |
| SPAM_correction | float | bits | Applied SPAM correction |
| state_type | string | — | "GHZ", "product", "thermal", etc. |

---

## 3. FALSIFICATION ASSESSMENT PROTOCOL

When a sufficient dataset exists to evaluate the falsification criterion, the following assessment should be performed and documented:

**Step 1:** Confirm conditions F1–F5 are met (see Section 6 of Paper A):
- [ ] F1: N_entangled ≥ 10⁶ verified
- [ ] F2: Sensitivity ≤ 10⁻⁶ Pa confirmed
- [ ] F3: ≥ 1000 independent runs completed
- [ ] F4: ≥ 3 platforms with null results
- [ ] F5: No anomalous signal at F2 sensitivity

**Step 2:** Compute the combined upper bound on |κ̃| from all runs.

**Step 3:** Compare to theoretical prediction range: |κ̃_eff| ∈ [2.5×10⁻⁵, 2.5×10⁻³] (provisional).

**Step 4:** Issue assessment:
- If signal detected at predicted level: "Hypothesis supported at [confidence] — proceed to detailed characterization"
- If null result above F2 threshold: "Hypothesis NOT falsified — improve sensitivity and repeat"
- If null result below F2 threshold meeting F1–F5: "Hypothesis FALSIFIED for laboratory-scale relevance"

---

## 4. VERSIONING REQUIREMENT

Every data file committed to this folder must have an associated `metadata_[filename].json` with:
- Hash of the data file (SHA256)
- Analysis code version that processed the raw data
- Name of experimenter and institution
- Calibration file reference
- Date of analysis

This ensures reproducibility and prevents silent data modification.

---

## 5. WHAT A POSITIVE RESULT REQUIRES

If any run shows Δa significantly above noise, the following protocol must be completed before claiming detection:

1. **Blind analysis:** Reanalyze data with systematic offsets applied blindly, then unblinnd
2. **Independent replication:** At least one independent group must reproduce the result
3. **Platform independence check:** Signal must appear on at least 2 platforms
4. **Entanglement verification:** Witness measurements confirming entanglement depth must accompany the run showing the signal
5. **Theory comparison:** Measured κ̃ must be compared to prediction from Section 02 with explicit statement of which assumptions were required to make the comparison

A single anomalous run without all five checks is noise, not a discovery.
