## Project Context Update – Phase 1 Modeling (Clean Version)

### Date

2026-04-17

---

## 1. Dataset Status

The curated hydrovoltaic dataset contains ~180–220 samples after cleaning, with the following key preprocessing steps:

* Removal of active electrode systems (e.g., Cu/C, Zn/Al, Ag/C), which behave as galvanic cells rather than hydrovoltaic devices.
* Exclusion of pulse-output data to ensure consistency in current density interpretation.
* Manual correction and simplification of dominant mechanism labels.
* Preservation of raw categorical strings (e.g., polyelectrolyte types) alongside structured binary features.

The dataset is characterized by:

* High heterogeneity (cross-paper data)
* Small sample size
* Mixed mechanisms (streaming vs ion-gradient systems)

---

## 2. Target Engineering

A derived target was introduced:

* Estimated power density:

  P ≈ Voc × Jsc / 4

* Log-transformed target:

  log_estimated_power_density

Key observation:

* This derived target is significantly more learnable than Voc alone.
* Combining voltage and current reduces noise and better reflects device performance.

---

## 3. Phase 1 Modeling Summary

### Model progression:

* **V1–V2**: Baseline descriptors → poor performance for Voc prediction
* **V3**: Switching to log_estimated_power_density → major improvement
* **V4**: Adding ion_type → modest but meaningful improvement
* **V5**: Adding device_structure → negligible improvement
* **V6 (ongoing)**: Testing asymmetry decomposition

Typical performance:

* R² ≈ 0.2–0.25 (train/test)
* Stable under ShuffleSplit CV

Interpretation:

* This performance level is reasonable given literature-derived, heterogeneous data.

---

## 4. Core Scientific Findings (Phase 1)

### 4.1 Mechanism dominance

The dominant mechanism is the primary determinant of performance:

* Ion-gradient systems consistently outperform streaming systems
* Distribution shifts are observed across the entire performance range

Conclusion:

* Mechanism-level descriptors outweigh most material-level features

---

### 4.2 Ion transport effects

The introduction of `ion_type` reveals:

* "other_cation" systems correlate with higher performance
* Strong coupling between ion type and mechanism

Interpretation:

* Ion environment plays a key role in governing device output

---

### 4.3 Polyelectrolyte effect (re-evaluated)

Initial hypothesis:

* Polyelectrolytes may significantly enhance performance

Findings:

* Weak global effect
* Minor or conditional influence within ion-gradient systems
* No clear effect within salt-dominated subsets

Conclusion:

* Polyelectrolyte is not a primary driver
* Its apparent importance is partially confounded by mechanism and ion environment

---

### 4.4 Device structure (geometry vs mechanism)

Observation:

* Sandwich structures show higher average performance than in-plane systems (grouped statistics)

However:

* Device structure does not appear in SHAP or feature importance
* Minimal impact on R²

Conclusion:

* Device structure is a **derived / proxy variable**
* Its effect is explained by deeper variables:

  * structure_class
  * ion transport pathway
  * mechanism

---

### 4.5 Emerging hierarchy of variables

The data suggests a hierarchical control structure:

1. **Dominant mechanism** (primary driver)
2. **Ion environment (ion_type)**
3. **Material structure (porosity, ionic groups)**
4. **Secondary features (polyelectrolyte, device geometry)**

---

## 5. Methodological Insights

* Cross-paper datasets exhibit strong noise and limited generalizability
* Standard K-fold CV is unstable; ShuffleSplit is more appropriate
* Feature importance must be interpreted alongside grouped statistical analysis
* Many apparent correlations are explained away after conditioning on mechanism

---

## 6. Current Focus (Transition Stage)

Current work is transitioning from:

* Feature addition (V1–V5)

to:

* **Feature disentanglement and mechanism diagnosis**

Ongoing investigations:

* Decomposition of asymmetry_origin into:

  * environmental gradient
  * chemical asymmetry
  * electrode asymmetry

* Decomposition of ion_origin into:

  * intrinsic (material)
  * electrolyte-driven
  * water-derived

Goal:

* Identify variables that remain predictive within fixed mechanism regimes

---

## 7. Next Steps (Phase 1 → Phase 2 Bridge)

Before entering Phase 2 (multi-model comparison), remaining tasks:

* Evaluate asymmetry-related features (Model V6)
* Assess whether asymmetry provides independent signal beyond mechanism
* Test ion_origin with and without mechanism features (confounding check)

---

## 8. Strategic Direction

This project is evolving toward:

> A mechanism-oriented ML study rather than a pure predictive model

Key objective:

* Disentangle hydrovoltaic mechanisms using heterogeneous literature data
* Identify robust, model-independent physical drivers of performance

---

## 9. Key Insight (Phase 1)

> Many commonly assumed important features (e.g., polyelectrolyte, device structure) do not independently control performance.

Instead:

> Performance is governed primarily by ion transport regime and underlying mechanism, with other variables acting as secondary or proxy descriptors.

---

# Phase 1 Final Summary (Model V7)

## Date
2026-04-20

---

## 1. Objective

The goal of Phase 1 was to construct a curated hydrovoltaic dataset and identify robust predictors of device performance using machine learning.

The focus evolved from exploratory modeling to a mechanism-oriented analysis framework.

---

## 2. Dataset Status

After cleaning, the dataset contains ~150–200 samples.

Key preprocessing decisions:

- Removal of active electrode systems (galvanic cell behavior)
- Exclusion of pulse-output data
- Simplification of mechanism labels into `mechanism_simple`
- Feature restructuring (asymmetry, ion origin, polyelectrolyte)

The dataset remains:

- Small-scale
- Heterogeneous (cross-paper)
- Mechanism-mixed

---

## 3. Target Engineering

The target variable is defined as:

P ≈ Voc × Jsc / 4

and transformed as:

log_estimated_power_density

Key outcome:

- This target significantly improves model learnability compared to Voc alone
- It better reflects overall device performance

---

## 4. Validation Upgrade (Model V7)

Model V7 introduces a more robust evaluation framework:

- StratifiedShuffleSplit (by mechanism)
- 50 repeated splits
- Reporting:
  - mean CV R²
  - std
  - min / max
- Distribution-based evaluation (boxplots)

Key observation:

- Model performance is highly sensitive to data splitting
- Variance is large due to dataset heterogeneity

---

## 5. Feature Diagnosis

### 5.1 Primary drivers

Consistently important variables:

- mechanism_simple
- ion_type
- structure_class

These variables define the dominant physical regime.

---

### 5.2 Internal resistance

The variable:

log_internal_resistance_Mohm

shows:

- Strong improvement in predictive performance
- Reduced variance in cross-validation

Interpretation:

- Acts as an integrated descriptor of transport limitation
- Physically coupled to current and power output
- Not explicitly part of the target formula, but indirectly embedded

Note:

- Should be interpreted as a performance-related descriptor, not a purely independent variable

---

### 5.3 Proxy variables

Variables such as:

- device_structure

show:

- Weak improvement in mean R²
- Increased variance

Interpretation:

- Represent underlying mechanism or geometry indirectly
- Do not provide independent predictive power

---

### 5.4 Unstable / noisy variables

Variables such as:

- asymmetry_origin (decomposed)
- ion_origin (decomposed)

show:

- No improvement in performance
- Increased instability

Conclusion:

- Current definitions are not robust
- These variables are excluded from the main model

---

## 6. Final Model Definitions

### Model A — Mechanistic baseline

Features:
- mechanism_simple
- ion_type
- structure_class
- core material/device descriptors

Purpose:
- Capture fundamental physical drivers
- Enable interpretability

---

### Model B — Augmented model

Features:
- Model A + log_internal_resistance_Mohm

Purpose:
- Improve predictive performance
- Incorporate device-level transport information

---

## 7. Key Scientific Insight

Hydrovoltaic performance is primarily governed by:

1. Ion transport mechanism
2. Ionic environment
3. Material structure

Many commonly assumed variables (e.g., device geometry, asymmetry labels)
do not independently control performance, but instead act as proxy descriptors.

---

## 8. Conclusion

Phase 1 establishes:

- A curated hydrovoltaic dataset
- A robust validation framework (Model V7)
- A minimal and physically interpretable feature set

This provides a solid foundation for Phase 2:

→ multi-model comparison and further performance optimization