# Project Context

## Goal

Use interpretable machine learning to understand structure–performance relationships in hydrovoltaic materials based on literature-derived data.

## Dataset

* ~219 data points collected from literature
* Active electrode-dominated systems removed
* Pulsed-output systems excluded for primary analysis
* Final dataset focuses on continuous-output systems (~180 samples)

## Key Decisions

### Output Mode Filtering

* Pulsed systems show extremely high and unstable current values
* Only continuous-output systems retained for main analysis to ensure physical comparability

### Feature Engineering

* Polyelectrolyte types converted into binary descriptors:

  * has_anionic
  * has_cationic
  * has_zwitterionic
* Raw chemical labels preserved separately for qualitative analysis

### Target Selection

* Primary target: voc_V (more complete and stable)
* Secondary target: log-transformed current density (log_jsc)

## Current Step

* Data cleaning and feature structuring completed
* Preparing dataset for modeling (feature selection and encoding)

## Notes / Observations

* Current density strongly affected by output mode (pulse vs continuous)
* Data distribution is highly skewed for current-related metrics
* Voltage appears more robust across studies

## Modeling Progress (Phase 1 → Phase 3)

### Dataset Status

* Clean hydrovoltaic dataset constructed (~180 samples)
* Active-electrode systems excluded
* Pulsed-output systems excluded; only continuous-output systems retained
* Final usable samples:

  * Voc: ~180
  * Jsc: ~159
  * Derived power metric: ~159

---

## Model V1: Baseline (Voc)

### Setup

* Target: Voc
* Features: high-level categorical descriptors (material_class, structure_class, electrolyte presence, mechanism, etc.)

### Result

* R² ≈ -1.31 (very poor performance)

### Interpretation

* High-level descriptors alone cannot explain variation in Voc
* Model fails to capture meaningful physical relationships

---

## Model V2: Refined Features (Voc)

### Setup

* Target: Voc
* Features:

  * Added electrode-related descriptors (top/bottom electrode, symmetry, metal electrode)
  * Added ionic information (ionic_groups, polyelectrolyte types)

### Result

* R² ≈ -0.20
* RMSE and MAE improved significantly

### Interpretation

* Feature refinement improves stability
* However, Voc remains weakly predictable
* Suggests mismatch between chosen target and feature set

---

## Target Redefinition

### Motivation

* Voc reflects electrostatic potential but not full device output
* Jsc is highly skewed and unstable across studies
* Reported power density is inconsistent and incomplete

### Strategy

Define a standardized derived target:

estimated_power_density = Voc × Jsc / 4

Then apply log transformation:

log_estimated_power_density = log10(estimated_power_density)

### Rationale

* Combines voltage and current into a single performance metric
* Ensures consistency across literature data
* Log transform reduces skewness and improves ML compatibility

---

## Model V3: Derived Power Target

### Setup

* Target: log_estimated_power_density
* Features: refined feature set from Model V2

### Result

* R² ≈ 0.19 (first positive R²)
* RMSE ≈ 1.21
* MAE ≈ 0.92

### Interpretation

* Model begins to capture meaningful structure–performance relationships
* Derived target significantly improves learnability
* Feature set is physically relevant but still incomplete

---

## Key Insights

1. Feature engineering alone is insufficient if target is not aligned with physical behavior
2. Target definition is critical for successful modeling in literature-based datasets
3. Derived power metric provides a more robust and informative learning objective
4. Electrode and ionic descriptors contribute useful signal
5. Current dataset supports interpretable ML, though predictive power remains moderate

---

## Next Steps

* Analyze feature importance (Random Forest)
* Apply SHAP for interpretability
* Identify dominant factors governing hydrovoltaic performance
* Consider adding quantitative descriptors if available (e.g., thickness, concentration)

---
