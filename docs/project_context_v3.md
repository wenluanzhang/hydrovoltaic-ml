# Project Context: Hydrovoltaic Device Performance and Transport Analysis

This project aims to build a curated dataset and machine learning framework to understand the governing factors behind hydrovoltaic device performance, with a particular focus on evaporation-induced electricity systems.

Unlike many existing studies that rely on small, system-specific datasets, this work compiles a cross-literature dataset (~200 samples) with careful filtering to exclude systems dominated by galvanic or redox-driven effects. The resulting dataset emphasizes physically consistent hydrovoltaic mechanisms.

The core objective is not only to build predictive models, but to extract physically meaningful insights that connect device design, transport properties, and performance.

---

## Key Methodological Framework

The analysis is structured in three conceptual layers:

### Phase 1–2: Predictive Modeling

- Multiple machine learning models (ElasticNet, SVR, Random Forest, XGBoost) are applied to predict log(power density)
- Hyperparameter tuning and cross-validation are performed to ensure robustness
- Model performance reaches moderate predictive power (R² ≈ 0.2–0.3), consistent with small, heterogeneous materials datasets

Two modeling strategies are compared:

- **Model A (design-only features)**  
  → evaluates predictive power from structural and material descriptors

- **Model B (including internal resistance)**  
  → evaluates whether performance is governed by transport limitation

Results show that internal resistance is the dominant predictor of performance.

---

### Phase 3: Interpretability and Rule Extraction

- SHAP analysis identifies key features influencing performance
- Partial dependence plots reveal threshold behavior of internal resistance
- Decision tree–based rule extraction provides interpretable design regimes

A key finding is the existence of two regimes:

- Low-resistance regime → higher performance
- High-resistance regime → transport-limited performance

---

### Phase 4: Robustness and Validation

A comprehensive robustness analysis is conducted:

- Repeated ShuffleSplit cross-validation
- Grouped cross-validation (paper-level separation)
- Feature ablation and target ablation
- Subgroup modeling (mechanism-specific)

These analyses confirm that the main conclusions are stable and not artifacts of dataset composition.

---

### Phase 5: Visualization and Design Space Analysis

- SHAP summaries, PDP plots, and correlation analysis
- PCA-based design space visualization
- Distribution analysis across structure, ion type, and mechanism

Results show that:

- Performance varies continuously (no clear clustering)
- Mechanism labels do not define distinct regions in design space
- Internal resistance provides a clearer organization of the system

---

### Phase 6: Internal Resistance as a Central Descriptor

A key conceptual shift is made by treating internal resistance as a target variable:

- ML models are used to predict resistance from design features
- SHAP and statistical tests identify key factors influencing resistance
- Mann–Whitney tests confirm statistically significant effects

Key findings:

- Electrolyte presence strongly reduces resistance
- Porous structures tend to increase resistance (due to transport limitations)
- Ion type influences resistance, but no consistent ranking exists among specific cations
- Mechanism labels have minimal predictive power

---

## Core Insight

The study establishes a hierarchical relationship:

Design → Transport (internal resistance) → Performance

Internal resistance emerges as a physically meaningful, system-level descriptor that mediates the relationship between device design and performance.

---

## Contribution

This project contributes:

1. A curated hydrovoltaic dataset with improved physical consistency
2. A systematic ML + statistical framework for analyzing device performance
3. Identification of internal resistance as the key governing variable
4. Interpretable design rules for improving hydrovoltaic devices

The work bridges machine learning and physical interpretation, moving beyond prediction toward mechanism-aware understanding of hydrovoltaic systems.


# Paper Abstract
Hydrovoltaic devices generate electricity from water–solid interactions, but their governing design principles remain unclear due to heterogeneous systems. Here, we construct a curated dataset (~200 samples) and apply machine learning to identify key factors controlling performance.

We show that internal resistance is the dominant descriptor, revealing a transition between low-resistance, high-performance regimes and high-resistance, transport-limited regimes. Statistical analysis confirms that electrolyte presence significantly reduces resistance, while porous structures tend to increase it due to transport limitations. Ion-type effects are weaker and less consistent than electrolyte and structural factors.

These results establish a hierarchical relationship between design, transport, and performance, and provide physically interpretable guidelines for optimizing hydrovoltaic devices.