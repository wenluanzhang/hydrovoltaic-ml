# Revision repository audit

Audit scope: repository contents and the submitted `docs/MANUSCRIPT.pdf` and
`docs/Supplementary_Material.pdf`. No notebooks, data, figures, or manuscript
files were changed. Paths below are repository-relative.

## 1. Repository overview

This is a notebook-led research repository rather than a packaged pipeline. Its
work is organised in three chronological layers:

| Layer | Main files | Apparent role |
|---|---|---|
| Raw curation and early exploration | `data/raw/hydrovoltaic_data.xlsx`; `notebooks/01_data_cleaning.ipynb` through `notebooks/03_modeling_v7_validation.ipynb` | Literature-record curation, target engineering, early model versions, then construction of the phase-2 input. |
| Phase-2 analysis | `notebooks/04_modeling_phase2_models.ipynb` through `notebooks/11_physics_aware_R_descriptor.ipynb` | Fixed-dataset model comparison, robustness, SHAP/visual diagnostics, resistance analysis, explicit descriptors, and virtual design. |
| Manuscript production | `notebooks/12_figure1_dataset_overview.ipynb` through `notebooks/22_supporting_figures.ipynb` | Exported main and supporting figure panels, numerical cross-checks, and supporting tables. |

Key repository assets are:

- Raw data: `data/raw/hydrovoltaic_data.xlsx`, whose sheets are
  `HV_MEG_Dataset` (219 records), `excluded` (50 records),
  `controlled_vocabulary`, and `Data_Dictionary`.
- Canonical processed data: `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv`.
- Duplicate phase-2 working copy: `notebooks/hydrovoltaic_dataset_phase2_input_utf8.csv`.
  Both contain 159 rows and 52 columns; their byte hashes differ because their
  column ordering differs. This duplication is a revision risk.
- Earlier clean datasets: `notebooks/hydrovoltaic_clean.csv` (183 rows, 46
  columns) and `notebooks/hydrovoltaic_clean_phase1.csv` (183 rows, 50
  columns). These precede the final scope-screened phase-2 dataset.
- Analysis result files: `results/*.csv` and `results/*.json`, plus the
  figure-specific `results/figure*/` directories and
  `results/supporting_materials/`.
- Exported figures: final per-panel PNG/PDF/SVG files under
  `results/figure1_dataset_overview/final_panels/` through
  `results/figure6_virtual_design/final_panels/`, combined SI figures under
  `results/supporting_materials/figures/`, and legacy files in `figures/` and
  `figures/figure4/`.
- Manuscript-related files: `docs/MANUSCRIPT.pdf`,
  `docs/Supplementary_Material.pdf`, and historical project-context notes
  `docs/project_context.md`, `docs/project_context_v2.md`,
  `docs/project_context_v3.md`, and
  `docs/project_context_Phase 2_After Model Comparison.md`.

Notebooks 01--11 are the analytical record; 12--22 are the current
manuscript-production layer. The checked-in HTML exports for 01--19 are useful
for inspecting historical outputs, but should not be treated as a re-executable
source of truth. Notebooks 01--03, 06--11, 19, and the legacy standalone
`results/09_*`, `results/10_*`, `results/11_*`, `figures/`, and
`figure_references/` artifacts are exploratory/superseded where an equivalent
phase-2 or manuscript-production artifact exists.

## 2. Primary source-of-truth notebooks and datasets

The best-supported current source of truth is
`data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv`, not the 183-row
phase-1 CSVs. It is the file explicitly loaded by
`notebooks/04_modeling_phase2_models.ipynb`,
`notebooks/08_internal_resistance_analysis.ipynb`,
`notebooks/09_design_and_descriptor.ipynb`,
`notebooks/10_virtual_design.ipynb`, and
`notebooks/11_physics_aware_R_descriptor.ipynb`. It is also the dataset
selected by the saved execution of `notebooks/22_supporting_figures.ipynb`.

The canonical dataset contains 159 rows, with all 159 records having positive
`voc_V`, `jsc_uA_cm2`, `estimated_power_density_uW_cm2`, and
`log_estimated_power_density`; it has 108 positive
`power_density_uW_cm2` values and 112 positive `internal_resistance_Mohm`
values. These counts agree with the manuscript and Supplementary Table S3.

Current manuscript result control is distributed as follows:

- Dataset construction: `notebooks/01_data_cleaning.ipynb` (raw workbook to
  183-row clean CSV) and, critically,
  `notebooks/03_modeling_v7_validation.ipynb` (makes
  `mechanism_simple`, `log_internal_resistance_Mohm`, and
  `has_internal_resistance`, then writes the phase-2 input). The latter writes
  a notebook-local copy; the provenance of the processed copy should be
  preserved before a full rerun.
- Main ML calculations: `notebooks/04_modeling_phase2_models.ipynb` and
  `notebooks/05_modeling_phase2_robustness.ipynb`.
- Main figures: `notebooks/12_figure1_dataset_overview.ipynb` through
  `notebooks/17_figure6_virtual_design.ipynb`; final per-panel exports are the
  strongest figure assets.
- Supporting items: `notebooks/21_supporting_tables.ipynb` and
  `notebooks/22_supporting_figures.ipynb`.
- Numerical manuscript cross-check: `notebooks/18_paper_numbers_summary.ipynb`
  and `results/paper_numbers/`.

`scripts/draw_figure_1a.py` is the programmatic source for
`figures/fig_1a_redrawn.svg` and `.png`. The notebook headers for Figures 1--3
explicitly state that final multi-panel assembly is performed in Adobe
Illustrator; the submitted PDF therefore represents a manual assembly step
beyond the per-panel exports.

## 3. Main-figure generation map

| Submitted figure | Code/data provenance | Saved outputs and assembly status |
|---|---|---|
| Fig. 1 | Panel A: `scripts/draw_figure_1a.py`, which writes `figures/fig_1a_redrawn.svg` and `.png`. Panels B/C: `notebooks/12_figure1_dataset_overview.ipynb`, analysis cells 8--18 and final-production cells 23--28, from notebook-local `hydrovoltaic_dataset_phase2_input_utf8.csv`. The notebook's historical labels are `fig1C` (composition/target) and `fig1D` (completeness), whereas the submitted manuscript calls them B and C. | Data: `results/figure1_dataset_overview/fig1C_*` and `fig1D_reporting_completeness.csv`; panels: `results/figure1_dataset_overview/final_panels/fig1C_final_dataset_composition_and_target_distribution.*` and `fig1D_final_reporting_completeness.*`. Panel A is programmatic; final Fig. 1 assembly is explicitly Adobe Illustrator/manual. |
| Fig. 2 | `notebooks/13_figure2_dataset_structure.ipynb`: cells 5, 8, 11, 14, 19--27 prepare mechanism, structure, ion, and association data; cells 28--34 export final panels. Input is the notebook-local phase-2 copy. | `results/figure2_dataset_structure/fig2A_*` through `fig2D_*`; final panels in `results/figure2_dataset_structure/final_panels/`. Per panels are programmatic (fixed jitter seed 42); final manuscript assembly is not programmatically captured. |
| Fig. 3 | `notebooks/14_figure3_model_comparison.ipynb`, cells 5, 8, 11, and 14 define the four plotting tables; cells 19 and 23--27 export them. Underlying calculations are principally in `notebooks/04_modeling_phase2_models.ipynb` and `05_modeling_phase2_robustness.ipynb`. | `results/figure3_model_comparison/fig3A_tuned_model_comparison.csv`, `fig3B_modelA_modelB_descriptor_augmentation.csv`, `fig3C_feature_block_ablation.csv`, and `fig3D_SHAP_descriptor_importance.csv`, plus final panels. The Figure 3 notebook hard-codes displayed numerical arrays, so the panel production itself is programmatic but not a direct recomputation. Manual final assembly is stated. |
| Fig. 4 | `notebooks/15_figure4_resistance_regimes.ipynb`: cells 3--6 select/load a candidate phase-2 CSV and form `fig4_df`; cells 7--17 prepare raw/binned/regime/R-descriptor panels; final-production cells load the CSV outputs. Physics-aware comparison is sourced from `notebooks/11_physics_aware_R_descriptor.ipynb`; cell 15 says the initial display values are hard-coded for the draft. | `results/figure4_resistance_regimes/fig4A_logR_vs_logPest_raw.csv`, binned trend, regime raw/summary, and `fig4D_*comparison.csv`; final panels in its `final_panels/`. Panels are programmatic from exported data; Fig. 4C is a conceptual rule schematic and its submitted assembly is uncertain. |
| Fig. 5 | `notebooks/16_figure5_R_origin.ipynb` uses the observed-R subset and produces electrolyte, ion, structure, and statistical-test summaries; upstream analysis is `notebooks/08_internal_resistance_analysis.ipynb`. | `results/figure5_R_origin/fig5_raw_observed_R_data.csv`, `fig5A_*summary.csv`, `fig5B_*summary.csv`, `fig5C_*summary.csv`, and `fig5_statistical_tests.csv`; final panels in `final_panels/`. Programmatic panels; original Fig. 5D is identified in the notebook as conceptual and is not represented by a final panel export. |
| Fig. 6 | `notebooks/17_figure6_virtual_design.ipynb`: cells 6--13 prepare the observed-R descriptor dataset, linear/polynomial models, and coefficients; cells 16--20 create virtual grids/candidates; cells 26 onward redraw final panels from CSV. Earlier parallel work is in `notebooks/09_design_and_descriptor.ipynb` and `10_virtual_design.ipynb`. | `results/figure6_virtual_design/fig6A_*`, `fig6B_*`, `fig6C_*`, `fig6D_*`, and `fig6_test_set_predictions.csv`; final panels in `final_panels/`. The panels are programmatic; the final manuscript composition is not captured as code. |

## 4. Supporting-figure generation map

All submitted Fig. S1--S5 pages are generated by
`notebooks/22_supporting_figures.ipynb`; its Cell 1 defines paths and Cell 2
defines `save_combined_figure`, which saves PDF, SVG, and PNG. The saved
supplement visually matches the Fig. S1 generated artifact and annotation
content (108 points, `r = 0.96`, median displayed as 0.00).

| Submitted figure | Notebook section/cells and inputs | Final saved path / assembly |
|---|---|---|
| Fig. S1 | Cells 6--10 locate the canonical processed phase-2 dataset; Cell 10 creates `figS1_df`, `figS1_both_power`, and `figS1_vj`; Cell 11 draws A--D. | Row data: `results/supporting_materials/figures/Fig_S1/Fig_S1_target_construction_plotting_data.csv`; figure: `Fig_S1_target_construction_reported_power_consistency.{pdf,svg,png}` in the same directory. Fully programmatic within the notebook. |
| Fig. S2 | Cell 12. It uses `results/figure3_model_comparison/` files where available but its displayed validation/target-sensitivity values are explicitly entered as small `DataFrame` literals, described as summaries from Notebook 05. | `results/supporting_materials/figures/Fig_S2/Fig_S2_model_validation_robustness_diagnostics.*` and `Fig_S2_model_performance_descriptor_contribution.*`, with `Fig_S2A/B/C_*summary.csv`. Programmatic layout, but partly manually transcribed values. |
| Fig. S3 | Cell 13, from `results/figure4_resistance_regimes/fig4A_logR_vs_logPest_raw.csv`; it drops missing `log_R`/`log_P_est`, sweeps thresholds, and uses shuffled 5-fold CV with seed 42. | `results/supporting_materials/figures/Fig_S3/Fig_S3_threshold_sensitivity_data.csv` and `Fig_S3_R_regime_threshold_sensitivity.*`. Fully programmatic from the saved Figure 4 raw output. |
| Fig. S4 | Cells 14--15, from the selected canonical dataset. It derives `log_R` if absent, then uses observed-R rows with ion type, structure, and electrolyte fields. | `results/supporting_materials/figures/Fig_S4/Fig_S4_extended_R_origin_plotting_data.csv`, companion summaries, and `Fig_S4_extended_internal_resistance_origin_analysis.*`. Fully programmatic. |
| Fig. S5 | Cells 16--17, primarily from `results/figure6_virtual_design/fig6C_regime_aware_virtual_design.csv`. | `results/supporting_materials/figures/Fig_S5/Fig_S5_full_virtual_design_landscape_data.csv`, companion heatmap/range CSVs, and `Fig_S5_full_virtual_design_landscape.*`. Fully programmatic from saved virtual-design output. |

The support-table counterpart is `notebooks/21_supporting_tables.ipynb`, which
collects result CSVs into the individual table CSV files and
`results/supporting_materials/tables/Supporting_Tables_S1_to_S8.xlsx`.

## 5. Dataset and subset map

| Dataset/subset | Exact file and construction | Where used |
|---|---|---|
| Final 159 records | `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv` (159 x 52). Its engineered target is `estimated_power_density_uW_cm2 = voc_V * jsc_uA_cm2 / 4` and `log_estimated_power_density = log10(P_est)`. The upstream write is `notebooks/03_modeling_v7_validation.ipynb`, Cell 29, after `df_v7 = df_clean.dropna(subset=["log_estimated_power_density", "mechanism_simple"])`; the full 159 already have both required electrical inputs. | Primary current analysis and SI source. |
| Reported-power subset, n=108 | In the canonical data, `power_density_uW_cm2` is positive for 108 records. Fig. S1 Cell 10 first makes `log_P_reported = log10(P_reported_uW_cm2)` only where positive, then makes `figS1_both_power = figS1_df.dropna(subset=["log_P_est", "log_P_reported"])`. | Fig. S1A/B. No model is trained on this subset as the primary target. |
| Observed-resistance subset, n=112 | In the canonical data, `internal_resistance_Mohm` and `log_internal_resistance_Mohm` are non-null for 112 records. Figure 4 Cell 6 drops missing `log_R`/`log_P_est`; Figure 5 uses the observed-R subset; `notebooks/11_physics_aware_R_descriptor.ipynb` Cell 8 creates `df_phys_R = df_phys.dropna(subset=[TARGET, R_COL])`. | Resistance figures/tests and Model B/explicit descriptor analyses. |

Filtering is repeated independently across notebooks. The phase-2 benchmark uses all
159 rows after dropping only target and `mechanism_simple` (both complete in the
canonical data) and then imputes numeric values by median and categorical values
by most frequent category inside the preprocessing pipeline. Thus missing
resistance in its all-record Model B is imputed, not automatically excluded.
In contrast, fair internal-R comparisons and resistance-specific analyses drop
missing resistance and use 112 rows. This difference must be stated precisely in
any reviewer response.

Competing versions exist: the 183-row phase-1 CSVs use
`internal_resistance_MΩ`, whereas phase 2 uses
`internal_resistance_Mohm`; the latter field is still in units of MOhm as stated
in the manuscript/Table S1. The phase-2 duplicate in `notebooks/` also differs
in column order. Rows are additionally dropped by feature completeness in some
early notebooks: for example `01_data_cleaning.ipynb` Model V5 and the Phase-1
helper select features plus target and call `.dropna()`. These earlier outputs
must not be mixed with submitted phase-2 results.

## 6. Machine-learning analysis map

| Analysis | Notebook(s), dataset, and missing-data/validation logic | Traceable outputs |
|---|---|---|
| Model-family comparison: Elastic Net, SVR, RF, XGBoost | `notebooks/04_modeling_phase2_models.ipynb`, Cells 7--17 and 36--40, canonical 159-record data. Target/mechanism rows are retained; pipeline median-imputes numeric fields and most-frequent-imputes categorical fields; 50 `StratifiedShuffleSplit` splits and a stratified 80/20 holdout use seed 42. | Detailed phase-2 summaries and tuned parameters in `results/phase2_*` / `phase2_tuned_best_params.*`; manuscript display values are copied into `results/figure3_model_comparison/fig3A_tuned_model_comparison.csv`. |
| Model A versus Model B | Same notebook. Model A is the categorical/mechanistic baseline; Model B adds `log_internal_resistance_Mohm`. Because Model B is pipeline-imputed in the all-record benchmark, it is not the same operation as an observed-R-only comparison. `03_modeling_v7_validation.ipynb`, Cell 16, also has a fair observed-R same-subset check. | `fig3B_modelA_modelB_descriptor_augmentation.csv`; Table S5A. |
| Feature-block ablation and robustness | `notebooks/05_modeling_phase2_robustness.ipynb`, Sections 1--5: repeated stratified splitting, paper-DOI grouped validation, ablation, target sensitivity, mechanism subgroup models. | `results/ablation_summary.csv`, `phase2_*subgroup_results.csv`, and Figure/SI summaries. Fig. S2 Cell 12 manually enters selected values, so its displayed values require a direct check against Notebook 05/result tables. |
| SHAP/interpretation | `notebooks/04_modeling_phase2_models.ipynb`, Cells 21--24 (RF Model B) and `notebooks/07_visualization_support.ipynb`, Sections 07.2--07.3. The latter refits transformed RF/XGB on all X before SHAP/PDP. | Figure 3 displayed ranking in `fig3D_SHAP_descriptor_importance.csv`; Table S6. The figure notebook hard-codes the ranking values. |
| Resistance-regime analysis | `notebooks/11_physics_aware_R_descriptor.ipynb`, Cells 8 and 24--28, and `notebooks/15_figure4_resistance_regimes.ipynb`. Observed-R rows only; threshold is `log(R) <= -1` low-R and `> -1` high-R. | `results/11_R_regime_performance_summary.csv`, `results/figure4_resistance_regimes/fig4A_*`, `fig4B_*`, and Table S7C. |
| Internal-resistance model/tests | `notebooks/08_internal_resistance_analysis.ipynb`, cells 5--25; observed-R subset, RF with 50 `ShuffleSplit` resamples (seed 42), SHAP, Mann--Whitney and Kruskal--Wallis tests. `notebooks/16_figure5_R_origin.ipynb` packages the submitted group summaries/tests. | `results/figure5_R_origin/fig5_*summary.csv`, `fig5_statistical_tests.csv`, and Table S7A/B. |
| Explicit descriptor model | `notebooks/17_figure6_virtual_design.ipynb`, Cells 6--13; 112-row observed-R modeling table, with numeric median and categorical most-frequent imputation in the final Figure 6 pipeline. Linear Elastic Net uses 80/20 split and shuffled 5-fold CV, seed 42. The predecessor is `notebooks/09_design_and_descriptor.ipynb`. | `fig6A_linear_descriptor_coefficients_{raw,plot}.csv`; Table S8A. |
| Linear versus polynomial model | `notebooks/17_figure6_virtual_design.ipynb`, Cells 9--11; both fitted to the same observed-R descriptor table, 80/20 split and shuffled KFold(5), seed 42. | `fig6B_linear_vs_polynomial_model_comparison.csv`; Table S8B. |
| Virtual-design screening | `notebooks/17_figure6_virtual_design.ipynb`, Cells 16--20. The final fitted linear model predicts a defined virtual grid (structures, ion types, electrolyte states, and log-R values); it is not an experimental prediction set. `notebooks/10_virtual_design.ipynb` is the predecessor/self-contained re-fit. | `fig6C_*`, `fig6D_*`, `fig6_test_set_predictions.csv`; Table S8C. |

## 7. Reproducibility assessment

The current submission is reproducible at the level of its retained final CSV
outputs and final panel exports, but it is not yet a one-command, clean-room
reproduction. Strengths are: an identified 159-record final dataset; explicit
random seeds in the principal phase-2 notebooks; result CSVs backing nearly all
panels/tables; and saved Fig. S1 row-level plotting data.

The practical reproduction sequence is: establish the canonical phase-2 CSV,
verify the associated result CSVs, run targeted production notebooks from the
`notebooks/` working directory, then perform the documented Illustrator
assembly. Re-running upstream notebooks 01--11 risks overwriting results and
changing historical notebook state; it is not required for a narrow revision.

The submitted PDFs and current final results are mutually consistent for the
audited counts and Fig. S1 appearance. Figure 3 is less directly reproducible
from its figure notebook because its values are literal arrays rather than
loaded analysis outputs; a reviewer-driven numerical change should begin at the
upstream result calculation, not by editing plotted constants.

## 8. Revision-risk assessment

| Risk | Rating | Evidence and revision implication |
|---|---|---|
| Competing 159-row CSV copies and two 183-row phase-1 CSVs | High | `data/processed/` is canonical, but notebooks 12--15 often load the notebook-local duplicate or select the first available candidate. A revision can silently use the wrong version. |
| Hard-coded/manually transcribed manuscript values | High | `14_figure3_model_comparison.ipynb` defines Figure 3 tables as literals; Figure 4 Cell 15 says physics-aware values are hard-coded for the draft; Fig. S2 Cell 12 has literal validation values. Trace back to upstream analysis before changing any number. |
| Manual Illustrator assembly after panel export | High | Figure 1--3 production headers explicitly state it; other final panels are separate files. The published composite cannot be recreated exactly by a single script and has an extra handoff/label risk. |
| Notebook execution-order dependence | High | Many production cells depend on in-memory data frames made in earlier cells, and several paths assume execution from `notebooks/`. Re-running isolated later cells can fail or use stale kernel state. |
| Missing-data treatment changes the analysis population | High | All-record Model B median-imputes resistance, but resistance-specific/Figure 4--6 analyses use the 112 observed-R rows. Earlier Phase-1 models may `.dropna()` feature rows. State the population for every revised claim. |
| Stale HTML outputs and superseded exploratory work | Moderate | HTML notebooks preserve historical results; the 01--11 series and legacy 09--11 result files overlap later production work. Timestamps alone cannot resolve authority. |
| Path portability | Moderate | Most current paths are relative, but saved notebook outputs include absolute Windows paths, and several notebooks search candidate filenames/paths in priority order. No current source code hard-coded absolute path was found in the core production logic. |
| Feature/column-definition drift | Moderate | Phase 1 uses `internal_resistance_MΩ`; phase 2 uses `internal_resistance_Mohm`; both denote MOhm. `mechanism_simple` and resistance indicators are engineered in Notebook 03. Do not combine them without explicit conversion/provenance. |
| Incomplete package/environment lock | Moderate | No requirements/lockfile was found. scikit-learn and xgboost behavior, OneHotEncoder API, SHAP output, fonts, and rendering can vary by environment. |
| Seeds and validation protocols | Moderate | Principal phase-2 analysis uses seed 42, but different notebooks use different schemes (50 stratified shuffles, 5-fold KFold, Grouped CV, early ShuffleSplit). Reported values must retain the original protocol. |
| Fig. S1 terminology overstates the data field | Moderate | The data column is generic `power_density_uW_cm2`; Fig. S1 D and caption call it reported maximum power density. The repository does not retain a field verifying that every value is a measured Pmax. |

## 9. Fig. S1 / Reviewer 1 Comment 1 audit

Fig. S1 is generated entirely in `notebooks/22_supporting_figures.ipynb`:

1. Cells 6--8 scan candidate CSVs and select
   `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv` in the saved
   execution.
2. Cell 9 identifies `voc_V`, `jsc_uA_cm2`, `power_density_uW_cm2`,
   `estimated_power_density_uW_cm2`, and
   `log_estimated_power_density` by name.
3. Cell 10 makes `figS1_df` with the following concrete columns:
   `Voc_V`, `Jsc_uA_cm2`, `P_reported_uW_cm2`, `P_est_uW_cm2`, `log_P_est`,
   `log_P_reported`, `log_Voc`, `log_Jsc`, `mechanism`, `structure`, `ion`, and
   `delta_logP_est_minus_reported`.
4. It uses the stored `estimated_power_density_uW_cm2` when available; otherwise
   it computes `Voc_V * Jsc_uA_cm2 / 4`. It uses stored
   `log_estimated_power_density` when available; otherwise it computes a
   base-10 log of positive P_est. It always computes `log_P_reported` for
   positive reported values and
   `delta_logP_est_minus_reported = log_P_est - log_P_reported`.
5. It creates `figS1_both_power` by dropping missing `log_P_est` and
   `log_P_reported`. This is exactly the 108-record reported-power subset.
   It saves the entire row-level plotting data to
   `results/supporting_materials/figures/Fig_S1/Fig_S1_target_construction_plotting_data.csv`.
6. Cell 11 draws Fig. S1A from `x = log_P_reported` and `y = log_P_est`, adds a
   one-to-one line, and computes Pearson correlation via
   `np.corrcoef(x, y)[0, 1]`. The annotation is generated directly as
   `n = ...` and `r = ...`. The saved row data give n=108 and Pearson
   r=0.959187..., displayed as 0.96.
7. Cell 11 draws Fig. S1B from
   `delta_logP_est_minus_reported`, adds a dashed zero line and a solid median
   line, and computes `median_delta = np.nanmedian(delta)`. Its only
   data-driven text annotation is `median = ...`; saved data give a median of
   0.0001375, displayed as 0.00.

Thus the repository already contains reported power density, estimated power
density, both logarithms, Pearson correlation (at plotting time), and Delta
log(P). It does **not** currently calculate or save Spearman rank correlation,
log-space MAE, log-space RMSE, or either within-tolerance fraction. The existing
row-level CSV is sufficient to calculate all of them without changing the
source data.

The least disruptive insertion point is immediately after `figS1_both_power`
is created in Cell 10 (or at the start of Cell 11). Compute, from its two log
columns: `spearmanr`, `np.median(delta)`,
`np.mean(np.abs(delta))`, `np.sqrt(np.mean(delta**2))`, and the means of
`abs(delta) <= 0.5` and `abs(delta) <= 1.0`. Store a one-row statistics
DataFrame alongside the existing plotting CSV. Then derive both annotation
strings from that DataFrame: Fig. S1A can add Pearson and Spearman statistics;
Fig. S1B can add median, MAE/RMSE, and the two tolerance fractions. No model
fitting, data curation, or figure redesign is necessary.

The underlying dataset supports the wording **"experimentally reported power
density"** or **"reported power-density values"**. It does not support the
stronger universal claim that all 108 are experimentally reported *maximum*
power density: the raw/canonical column is `power_density_uW_cm2`, Table S1
defines it as reported power density from the original study, and no field
records Pmax/load-curve/reporting-definition provenance. The current Fig. S1D
label and supplement caption's "reported maximum power density" should be
treated as a terminology issue to resolve during the R1C1 revision, not as a
fact established by the stored data.

## 10. Minimal recommended implementation path for R1C1

1. Work only from `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv`
   and preserve its current hash/copy before editing any notebook.
2. Modify `notebooks/22_supporting_figures.ipynb`, Cell 10/11 only. Use the
   existing `figS1_both_power` subset and `delta_logP_est_minus_reported`; do
   not refit ML models or regenerate unrelated figures.
3. Add programmatic Spearman, median Delta log(P), log-space MAE/RMSE, and
   ±0.5/±1.0 log-unit fractions. Export a compact Fig. S1 statistics CSV next
   to `Fig_S1_target_construction_plotting_data.csv` so the revised annotation
   values are traceable.
4. Update Fig. S1A and B annotations directly from those computed statistics,
   regenerate only
   `results/supporting_materials/figures/Fig_S1/Fig_S1_target_construction_reported_power_consistency.{pdf,svg,png}`,
   and visually compare the revised PDF page with the existing SI layout.
5. Use neutral terminology in the revised SI text/caption unless original-study
   power definitions are separately curated: "reported power density" rather
   than universal "reported Pmax". Any broad manuscript wording should be
   checked against the same data-definition constraint.

### Final terminal summary

- **Revision readiness:** ready for a targeted, reviewer-driven revision using
  retained outputs, but not ready for an unguarded full-pipeline rerun.
- **Main source-of-truth dataset:**
  `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv` (159 records).
- **Main result notebooks:** 03 (phase-2 input), 04--05 (ML/robustness), 11
  (resistance descriptor), 12--17 (main figures), 21--22 (supporting
  materials), and 18 (numerical cross-check).
- **High-risk concerns:** duplicate dataset versions, hard-coded display values,
  manual final figure assembly, execution-order dependence, and different
  missing-resistance populations.
- **Modify first for R1C1:** `notebooks/22_supporting_figures.ipynb` Cells
  10--11; its direct inputs/outputs are the canonical dataset and
  `results/supporting_materials/figures/Fig_S1/`.
