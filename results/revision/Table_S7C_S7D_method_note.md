# Table S7(C) and Table S7(D) production provenance

## Table S7(C): resistance-regime performance statistics

- Population: 112 records with observed `log_internal_resistance_Mohm` and non-missing `log_estimated_power_density`; the 47 records with missing internal resistance are excluded.
- Target: `log_estimated_power_density` (base-10 log of estimated power density).
- Resistance boundary: `log(R) = -1` (`R = 0.1 MOhm`). `low_R` is `log(R) <= -1`; `high_R` is `log(R) > -1`.
- Statistics: count, mean/median/sample standard deviation of the target, and mean/median `log(R)` within each regime.
- Source code: `notebooks/11_physics_aware_R_descriptor.ipynb`, observed-R construction and Part D; targeted validation/propagation in `scripts/refresh_table_s7_cd.py`.
- Canonical output: `results/11_R_regime_performance_statistics.csv`.
- Supporting-table output: `results/supporting_materials/tables/Table_S7C_resistance_regime_performance_statistics.csv`.

## Table S7(D): resistance-descriptor formulation comparison

- Population: the same 112 observed-R records for every formulation; the 47 missing-R records are excluded before modeling and are never imputed or assigned to a regime.
- Target: `log_estimated_power_density`.
- Common covariates: `structure_class`, `ion_type`, and `mechanism_simple`.
- Formulations: (1) `log_internal_resistance_Mohm`; (2) `logR_centered`, calculated by subtracting the observed-R median; or (3) categorical `R_regime`, using the fixed `log(R) = -1` boundary above.
- Model: `ElasticNetCV` with `l1_ratio = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]`, 80 alphas on `logspace(-4, 2)`, `max_iter = 20000`, and `random_state = 42`.
- Preprocessing: numeric features are standardized; categorical features are filled with the literal `unknown` when missing and one-hot encoded with `drop="first"` and `handle_unknown="ignore"`. The resistance input itself has no missing values in this population and is not imputed.
- Train/test split: one unstratified random 80/20 split with `random_state = 42`.
- External evaluation: shuffled five-fold `KFold`, `random_state = 42`, reporting the mean and population standard deviation of fold-level R2.
- Internal tuning: every fitted `ElasticNetCV`, including the estimator fitted inside each external fold, performs its own internal five-fold CV.
- Source code: `notebooks/11_physics_aware_R_descriptor.ipynb`, Parts A-B; targeted validation/propagation in `scripts/refresh_table_s7_cd.py`.
- Canonical output: `results/11_physics_R_descriptor_model_comparison.csv`.
- Supporting-table output: `results/supporting_materials/tables/Table_S7D_R_descriptor_comparison.csv`.

Table S7(D) is retained because it tests a distinct and coherent question: whether the resistance-model conclusion materially depends on representing resistance as raw continuous `log(R)`, centered continuous `log(R)`, or the coarse fixed-threshold regime descriptor. It is not a claim that the regime descriptor is uniformly more predictive.
