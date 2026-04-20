# Hydrovoltaic ML Project Context

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Dataset Construction](#2-dataset-construction)
- [3. Target Engineering](#3-target-engineering)
- [4. Phase 1 Modeling Evolution](#4-phase-1-modeling-evolution)
- [5. Model V7 — Validation Upgrade](#5-model-v7--validation-upgrade)
- [6. Feature Diagnosis](#6-feature-diagnosis)
- [7. Final Model Definitions](#7-final-model-definitions)
- [8. Key Scientific Insights](#8-key-scientific-insights)
- [9. Limitations](#9-limitations)
- [10. Next Steps (Phase 2)](#10-next-steps-phase-2)

---

## 1. Project Overview

This project aims to apply machine learning to hydrovoltaic devices, with a focus on:

- Understanding physical mechanisms governing performance
- Identifying robust predictors across heterogeneous literature data
- Building a curated dataset for future reuse

Unlike purely predictive ML studies, this project emphasizes:

> **Mechanism-oriented modeling and feature interpretability**

---

## 2. Dataset Construction

### 2.1 Data Source

- Extracted from published hydrovoltaic literature
- Cross-paper dataset with heterogeneous experimental conditions

### 2.2 Cleaning Strategy

Key filtering steps:

- Removed active electrode systems (e.g., Cu/C, Zn/Al)
  - These behave as galvanic cells rather than hydrovoltaic devices
- Removed pulse-output data
  - Ensures consistency in current density interpretation
- Standardized mechanism labels

### 2.3 Dataset Characteristics

- Sample size: ~150–200
- High heterogeneity
- Mixed mechanisms:
  - ion-gradient systems
  - streaming systems

---

## 3. Target Engineering

### 3.1 Original Issue

- Voc alone is not sufficient to describe performance
- Jsc and Voc are often reported separately

### 3.2 Derived Target

Estimated power density:

P ≈ Voc × Jsc / 4

Log-transformed target:

log_estimated_power_density

### 3.3 Key Outcome

- Significantly improved model learnability
- Reduced noise compared to using Voc alone
- Better representation of overall device performance

---

## 4. Phase 1 Modeling Evolution

### 4.1 Early Models (V1–V2)

- Basic descriptors
- Poor predictive performance

### 4.2 Target Upgrade (V3)

- Switched to power density
- Major improvement

### 4.3 Feature Expansion (V4–V5)

- Added ion_type, device_structure
- Limited improvement

### 4.4 Transition

Shift from:

> “adding more features”

to:

> **feature diagnosis and mechanism understanding**

---

## 5. Model V7 — Validation Upgrade

### 5.1 Motivation

Earlier models suffered from:

- Limited cross-validation (few splits)
- High variance in R²
- Potential instability due to data heterogeneity

---

### 5.2 Method

Model V7 introduces:

- StratifiedShuffleSplit (by mechanism)
- 50 repeated splits
- Metrics:
  - mean R²
  - std
  - min / max
- Distribution-based evaluation (boxplots)

---

### 5.3 Key Observation

- Model performance strongly depends on data split
- Large variance reflects dataset heterogeneity
- Typical performance:

R² ≈ 0.1–0.2

---

## 6. Feature Diagnosis

### 6.1 Primary Drivers (Independent Variables)

Consistently important:

- mechanism_simple
- ion_type
- structure_class

These define the dominant physical regime.

---

### 6.2 Internal Resistance

Feature:

log_internal_resistance_Mohm

Findings:

- Significant improvement in predictive performance
- Reduced cross-validation variance

Interpretation:

- Represents integrated transport limitation
- Strongly coupled to current output
- Not explicitly part of target, but indirectly embedded

Conclusion:

> **A performance-related integrated descriptor**

---

### 6.3 Proxy Variables

Example:

- device_structure

Observations:

- Slight improvement in mean R²
- Increased variance

Interpretation:

- Reflects underlying mechanism or geometry
- Does not provide independent predictive power

---

### 6.4 Unstable / Noisy Variables

Examples:

- asymmetry-related features
- ion_origin-related features

Observations:

- No improvement in performance
- Increased instability

Conclusion:

- Definitions are not robust
- Excluded from main modeling

---

## 7. Final Model Definitions

### 7.1 Model A — Mechanistic Baseline

Features:

- mechanism_simple
- ion_type
- structure_class
- core material descriptors

Purpose:

- Capture fundamental physical drivers
- Maintain interpretability

---

### 7.2 Model B — Augmented Model

Features:

- Model A + log_internal_resistance_Mohm

Purpose:

- Improve predictive performance
- Incorporate device-level transport information

---

## 8. Key Scientific Insights

Hydrovoltaic performance is primarily governed by:

1. Ion transport mechanism
2. Ionic environment
3. Material structure

Key finding:

> Many commonly assumed variables (e.g., device geometry, asymmetry)
> act as proxy variables rather than independent drivers.

---

## 9. Limitations

- Small dataset size
- Cross-paper variability
- Missing or inconsistent measurements (e.g., internal resistance)
- Mechanism labeling uncertainty

---

## 10. Next Steps (Phase 2)

Phase 2 will focus on:

### 10.1 Multi-model comparison

- Random Forest
- XGBoost
- SVR
- Linear models (Lasso / Elastic Net)

---

### 10.2 Model robustness

- Compare performance across models
- Evaluate consistency of feature importance

---

### 10.3 Mechanism-aware modeling

- Potential separation of models by mechanism
- Within-mechanism feature analysis

---

### 10.4 Paper preparation

- Figures:
  - model comparison
  - SHAP analysis
  - feature importance
- Writing:
  - Methods
  - Results
  - Discussion

---

# End of Phase 1