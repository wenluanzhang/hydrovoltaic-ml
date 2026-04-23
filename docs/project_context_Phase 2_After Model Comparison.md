# Hydrovoltaic ML Project — Phase 2 Context (Model Comparison Completed)

## 1. Project Objective

This project aims to establish a machine learning framework for hydrovoltaic systems based on a curated dataset (~150–200 samples), with the goal of:

- Identifying key descriptors governing device performance
- Evaluating the predictive capability of mechanistic vs augmented feature sets
- Providing physically meaningful interpretation rather than purely predictive models

---

## 2. Dataset Status (Frozen for Phase 2)

The dataset used in Phase 2 is fixed and derived from Phase 1 validation:

- ~159 samples after cleaning
- Target:
  - `log_estimated_power_density` (primary)
- Key features:
  - Mechanistic descriptors (`mechanism_simple`, etc.)
  - Ion-related features (`ion_type`)
  - Structural features (`structure_class`)
  - Derived descriptor:
    - `log_internal_resistance_Mohm`

- Grouping variable:
  - `paper_doi` (used for grouped validation)

This dataset is treated as **frozen** for all subsequent Phase 2 analyses.

---

## 3. Phase 2 — Layer 1: Model Family Comparison (Completed)

### Models tested

- ElasticNet (linear baseline)
- Random Forest (main nonlinear model)
- SVR (kernel-based model)
- XGBoost (boosting model)

### Key Findings

- Model B (augmented features) consistently outperforms Model A (mechanistic-only)
- ElasticNet performs best under default settings
- Random Forest achieves comparable performance and is selected as the primary model
- XGBoost is highly sensitive to hyperparameters:
  - Poor performance under default settings
  - Significant improvement after tuning

### Important Insight

Despite different model structures:

- All tuned models converge to similar performance (~0.25 R²)

This indicates:

> Predictive performance is primarily constrained by dataset size and heterogeneity, rather than model capacity.

---

## 4. Hyperparameter Sensitivity (Completed)

- Random Forest and XGBoost were tuned using limited grid search
- Moderate improvement observed (especially for XGBoost)
- No change in overall conclusions

Interpretation:

> Hyperparameter tuning improves performance but does not alter the fundamental trends.

---

## 5. Current Position in Paper Structure

The project now has:

- ✔ Layer 1: Model comparison (completed)

Next:

- ⏳ Layer 2: Robustness analysis (in progress)
- ⏳ Layer 3: Interpretability and mechanism analysis (planned)

---

## 6. Next Steps (Phase 2 Continuation)

### Immediate tasks (Notebook 05)

- Repeated ShuffleSplit R² distribution
- Target ablation:
  - `Voc`, `log_Jsc`, `log_power`
- Additional feature ablation (optional refinement)

### Later tasks (Notebook 06)

- SHAP analysis (main interpretability section)
- Feature importance consolidation
- Mechanism-level interpretation

---

## 7. Key Scientific Direction

The focus of the project is shifting from:

> "Which model performs best?"

to:

> "What governs hydrovoltaic performance, and how robust are these conclusions?"

---

## 8. Important Notes

- Avoid over-emphasis on model tuning or leaderboard-style comparison
- Emphasize:
  - cross-model consistency
  - robustness
  - physical interpretability

- Dataset limitations (small size, heterogeneity) are not weaknesses,
  but key context for interpreting model performance

---