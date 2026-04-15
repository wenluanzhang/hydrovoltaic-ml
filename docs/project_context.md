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
