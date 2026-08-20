# Hydrovoltaic ML Major Revision — Final Consistency Audit

## Audit scope

- `MANUSCRIPT_R1.pdf` — revised main manuscript, 42 PDF pages.
- `Supplementary_Material_R1.pdf` — revised Supporting Information (SI), 27 PDF pages.
- `Response_letter.pdf` — response to Reviewers 1–3, 20 PDF pages.
- Audit performed: 2026-08-19 18:38:39 +08:00 (Asia/Shanghai).
- Method: page-by-page text and visual inspection of all three PDFs; cross-checks covered stated populations, numerical results, notation, terminology, causal strength, figures/tables, dataset scope, internal-resistance interpretation, $P_{est}$ interpretation, and every substantive reviewer comment.

## Executive summary

- MUST-FIX issues: **9**
- RECOMMENDED issues: **2**
- FORMAT-ONLY issues: **4**
- Overall numerical assessment: **The scientific revision is numerically coherent across the principal repeated results.** The canonical population sizes (159, 112, 47, 108, and 107), $P_{est}$ validation statistics, Model A/B changes, ablation results, SHAP values, threshold statistics, selection-bias tests, repeated-subsampling results, explicit-model coefficients, linear/polynomial performance, and leading virtual prediction agree wherever they are repeated. No direct numerical contradiction was found. This assessment is conditional on resolving the provenance of the 112 resistance values and documenting the currently undefined Fig. S2 and Table S7(D) protocols. The response letter's claimed five-record sparse-hybrid sensitivity analysis is not documented in either final PDF.

## MUST-FIX

### MUST-001 — Internal-resistance provenance conflicts with the 112-record “reported” population

- Status: UNVERIFIED
- Severity: MUST-FIX
- File: `Supplementary_Material_R1.pdf`; `MANUSCRIPT_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: SI p. 9, Table S1, `internal_resistance_Mohm`; manuscript pp. 13, 20–25, 26–36; response pp. 3, 7, 9–11, 16–18.
- Reviewer linkage: Reviewer 1 Comment 2; Reviewer 2 overall comment; Reviewer 3 Comment 3.
- Current wording/result: Table S1 defines internal resistance as “reported or estimated for the device,” while the manuscript and response repeatedly define the $n=112$ subset as records with “reported internal resistance”; response p. 3 further says the resistance was “experimentally reported.”
- Problem: The PDFs do not establish whether all 112 values were directly reported, whether some were estimated, or how any estimates were produced. This is a factual provenance contradiction, not a stylistic difference.
- Why it matters: The principal common-subset analysis, non-imputation claim, operating-state interpretation, and reviewer response all depend on the provenance of $R$. Calling estimated values “reported” would materially misdescribe the evidence.
- Recommended minimal correction: Verify the record-level provenance first. Then make Table S1, the population labels, and the response agree. If any values were estimated, identify the count and estimation protocol and revise “reported” claims accordingly; if all 112 were directly reported, remove “or estimated.” At the same time, define $R$ consistently as a reported operating-state/device-level quantity rather than a standardized dry-state intrinsic material property.
- Cross-document evidence: Manuscript p. 13 states “Internal resistance was reported for 112/159 records”; SI p. 4 states the 112 records are those “for which internal resistance was reported”; response p. 3 makes the same claim; SI Table S1 alone permits estimated values.
- Requires new analysis: NO — requires source/provenance verification and document correction, not a new scientific analysis.

#### Repository forensic finding

- Exact count: **112** of the 159 final records have a positive, non-missing `internal_resistance_MOhm` value; 47 are missing. The raw workbook contains 135 numeric values among 219 rows, of which 124 remain after the `continuous_output == 1` filter (183 rows), and the final selection retains 112.
- Pipeline trace: the 124 resistance values in `data/raw/hydrovoltaic_data.xlsx` (sheet `HV_MEG_Dataset`) pass unchanged into `notebooks/hydrovoltaic_clean.csv` and `notebooks/hydrovoltaic_clean_phase1.csv`; the 112 selected values then pass unchanged into `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv`. `notebooks/01_data_cleaning.ipynb` does not calculate or estimate resistance. `notebooks/03_modeling_v7_validation.ipynb` only computes `log_internal_resistance_Mohm = log10(internal_resistance_MOhm)` and the availability flag. The row-level comparisons found zero resistance mismatches, zero availability-flag mismatches, and only floating-point-roundoff differences in the stored logarithm.
- Source/curation provenance: **the repository cannot classify any of the 112 values as source-reported versus curator-estimated.** The workbook contains no resistance formulas, cell comments, populated record notes, source excerpts, or per-record provenance field. Its `Data_Dictionary` sheet defines resistance as “Numeric (MOhm) or NA” and notes “Often estimated or missing,” while the otherwise available `notes` field is blank. The ignored raw/processed files also have no Git history from which an earlier provenance annotation can be recovered.
- Therefore all 112 values are pipeline-traceable constants but remain **provenance-unestablished at the literature-extraction/curation boundary**. Determining which, if any, were estimated requires record-level checking against the source papers or an external curation record; it cannot be answered from this repository. This is why the status is `UNVERIFIED`, not `VERIFIED-OPEN` or `RESOLVED`.
- Supporting paths: `data/raw/hydrovoltaic_data.xlsx` (`HV_MEG_Dataset` and `Data_Dictionary` sheets); `notebooks/01_data_cleaning.ipynb`; `notebooks/hydrovoltaic_clean.csv`; `notebooks/hydrovoltaic_clean_phase1.csv`; `notebooks/03_modeling_v7_validation.ipynb`; `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv`.

### MUST-002 — Curator-harmonized mechanism categories are still repeatedly called “reported mechanism labels”

- Status: OPEN
- Severity: MUST-FIX
- File: `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript pp. 4–5, 13–19, 21–23, 32–33, 37; Fig. 2 caption (p. 19); SI pp. 1, 3, 10, 12, 22; Table S1 `mechanism_simple`; response pp. 13–14.
- Reviewer linkage: Reviewer 3 Comments 1 and 4; Reviewer 2 overall comment.
- Current wording/result: The revised methods disclose expert-guided harmonization and possible reassignment when original terminology and comparative behavior were inconsistent (manuscript p. 10; SI p. 1; response pp. 13–14). Elsewhere the variable remains “reported mechanism label”; SI Table S1 calls it a “Simplified literature-reported mechanism label” and says it is “Treated as reported label.”
- Problem: A category that may be curator-reassigned is not purely a reported author label. The current terminology gives two incompatible provenance descriptions for the same model variable.
- Why it matters: Mechanism-label weakness is a central conclusion, so the distinction between author-reported labels and curator-harmonized comparative descriptors affects interpretation and reviewer confidence.
- Recommended minimal correction: Use one provenance-accurate term, such as “curator-harmonized mechanism descriptor,” throughout analytical text, figure/table labels, and the response. Where original author wording is specifically discussed, reserve “reported mechanism” for that source-level wording. Update Table S1's definition and note.
- Cross-document evidence: Manuscript p. 10 explicitly says devices could be assigned to the category “judged to provide the most coherent description”; SI p. 1 says categories “contain curator judgment”; response p. 14 calls them “curator-harmonized mechanism categories”; manuscript Fig. 2 and SI Table S1 still present them as reported labels.
- Requires new analysis: NO.

### MUST-003 — Causal/control language remains stronger than the observational analysis and contradicts the response

- Status: OPEN
- Severity: MUST-FIX
- File: `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript title and Abstract p. 1; Introduction p. 5; Section 3.3 p. 18; Section 5 title and text pp. 26–28; Fig. 4 title/caption p. 28; Sections 6.1–6.3 pp. 29–31; Conclusions pp. 37–38; SI Table S1 p. 10; Fig. S4 title p. 24; response pp. 10–12.
- Reviewer linkage: Reviewer 2 overall comment; Reviewer 3 introductory concern and Comments 1, 3, and 4.
- Current wording/result: Examples include “Transport-Controlled Performance,” “transferable performance controls,” “dominant controlling factors,” “Resistance-Controlled Performance Regimes,” “possible controlling variable,” “regime-level controlling variable,” “controls performance regimes,” “Ionic and electrolyte control,” “Structural control,” “resistance variations in turn affect device performance,” “key controlling descriptor,” SI Table S1 “controlling R,” and Fig. S4 “internal-resistance origin analysis.”
- Problem: These formulations imply causal control, mediation, or physical origin. The PDFs elsewhere correctly describe a curated observational cross-literature analysis with omitted variables, heterogeneous conditions, selection effects, and descriptor associations. The response says the paper was narrowed to avoid a “universal controlling mechanism,” but the final manuscript retains that vocabulary in prominent locations.
- Why it matters: This directly reopens the reviewers' principal concern that statistical associations are being overinterpreted as fundamental mechanisms. $R$ is an integrated reported operating-state/device-level descriptor; low $R$ alone does not identify a microscopic mechanism or establish universal causality.
- Recommended minimal correction: Replace only the listed overclaims with association/importance/screening language. Examples: “transport-associated,” “performance associations,” “resistance-associated regimes,” “descriptor associated with,” and “extended internal-resistance association analysis.” Preserve genuinely physical, qualified statements such as high resistance being capable of limiting load delivery, but avoid asserting that the present analysis proves control, mediation, or origin.
- Cross-document evidence: Manuscript pp. 10–11 and SI pp. 1–2 expressly state that results are associations rather than causal estimates; response pp. 10–11 says resistance is not a unique microscopic mechanism or universal controlling mechanism. The listed title, headings, and conclusions conflict with those limitations.
- Requires new analysis: NO.

### MUST-004 — Abstract and Conclusions do not restrict the strongest resistance result to the R-reported subset

- Status: OPEN
- Severity: MUST-FIX
- File: `MANUSCRIPT_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Abstract p. 1, especially lines 14–18; Conclusions p. 37, especially lines 685–690; response pp. 10–11 and 17.
- Reviewer linkage: Reviewer 2 overall comment; Reviewer 3 Comment 3.
- Current wording/result: The Abstract says “Internal resistance emerged as the dominant individual descriptor” and gives the 6.4-fold SHAP comparison without identifying the $n=112$ R-reported subset. The Conclusions say “Internal resistance emerged as the key controlling descriptor” without the subset restriction.
- Problem: The strongest high-visibility conclusion reads as applying to the full 159-record dataset or the hydrovoltaic field generally, despite documented selection effects and the response's explicit restriction to the population with reported $R$.
- Why it matters: The analysis itself establishes robustness within the observed-R population, not representativeness across all 159 records or the full literature.
- Recommended minimal correction: Add a short explicit qualifier in both locations: “within the 112-record subset with reported internal resistance” (subject to resolving MUST-001), and retain the selection/representativeness limitation. Replace “controlling” in the Conclusion under MUST-003.
- Cross-document evidence: Manuscript p. 24 limits the conclusion to devices for which $R$ has been reported; response p. 11 says this was the intended revised framing; response p. 17 repeats the same restriction. The Abstract and Conclusions omit it.
- Requires new analysis: NO.

### MUST-005 — “Design rules” remain despite the response's descriptor-screening reframing

- Status: OPEN
- Severity: MUST-FIX
- File: `MANUSCRIPT_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript Section 2.3 p. 15; Section 7 pp. 32–35, especially pp. 32–34; Conclusions p. 38; response pp. 7, 11, and 18.
- Reviewer linkage: Reviewer 1 Comment 6; Reviewer 2 overall comment; Reviewer 3 Comment 4.
- Current wording/result: The manuscript retains “design-rule generation,” “unstable coefficients or design rules,” “transparent set of descriptor rules,” literature-derived “design rules,” “model-derived design rule,” and “extraction of physically interpretable design rules.”
- Problem: The response expressly reframes the virtual designs as “descriptor-level screening guidance” and says they are not experimentally validated recipes or causal design rules. The retained phrases create revision patchwork and overstate what the modest-performance, observational explicit model supports.
- Why it matters: Reviewers specifically questioned practical guidance and sparse categories. “Design rules” implies validated, transferable prescriptions beyond the presented evidence.
- Recommended minimal correction: Use the manuscript's already established terms “descriptor-level screening,” “screening trends,” or “descriptor states” for the authors' results. A cited external paper's title may retain “Design Rules,” but the present study should not adopt that label for its own outputs.
- Cross-document evidence: Manuscript pp. 34–36 correctly says the combinations are descriptor states, not validated recipes, while pp. 32–34 and 38 still call them design rules; response p. 11 explicitly rejects a stand-alone design rule framing.
- Requires new analysis: NO.

### MUST-006 — Claimed five-record sparse-hybrid sensitivity analysis is not documented

- Status: VERIFIED-OPEN
- Severity: MUST-FIX
- File: `Response_letter.pdf`; `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`
- Page / section / figure / table: Response pp. 7–8 and 18–19; manuscript Section 2.3 p. 15 (lines 280–282); SI Methods S3–S6 pp. 4–8; Tables S4–S8 pp. 14–20; Figs. S1–S6 pp. 21–26.
- Reviewer linkage: Reviewer 1 Comment 6; Reviewer 3 Comment 4.
- Current wording/result: The response says, “we performed a sensitivity analysis in which all five sparse-hybrid records were removed from the resistance-dependent machine-learning workflow,” and reports unchanged four-family augmentation, ablation, and SHAP conclusions. The manuscript only says their influence “was evaluated separately.” The SI gives no population, protocol, numerical result, table, or figure for this claimed rerun.
- Problem: A substantive response claim cannot be verified in the final manuscript or SI. The $n=107$ explicit model and virtual screen are documented, but those are not the claimed sensitivity reruns of the $n=112$ Fig. 3 analyses.
- Why it matters: This analysis is the response's direct evidence that rare hybrid records do not drive the central resistance conclusion.
- Recommended minimal correction: Document the already performed sensitivity analysis in the SI with its $n=107$ population, model/validation protocol, and compact numerical results for all four Model A/B comparisons, ablation, and SHAP rank; cross-reference it from the manuscript and response. If the analysis was not actually retained/performed, remove the response claim rather than implying documentation that does not exist.
- Cross-document evidence: SI S6 and Table S8 document only the separate explicit Elastic Net/virtual-design workflow; SI S3–S4 and Tables S4–S6 remain explicitly $n=112$. No SI item presents the sparse-hybrid-excluded Fig. 3 sensitivity results claimed in response p. 7.
- Requires new analysis: NO — the response says the analysis already exists; this is a documentation/claim-reconciliation issue.

#### Repository forensic finding

- The claimed reruns **do exist** and are the full sparse-category-excluded Fig. 3 sensitivity, not the separate explicit Elastic Net/virtual-design workflow. `scripts/run_r1c6_sparse_structure_sensitivity.py` removes the four `hydrogel + porous` rows and one `hydrogel + film` row (canonical row indices 123, 134, 137, 139, and 144), leaving 107 observed-R records. It imports the production Model A/B definitions and model helpers from `scripts/run_r1c2_common112.py`. `results/revision/R1C6/analysis_metadata.json` records the canonical-data hash, exclusions, feature sets, and protocols; `results/revision/R1C6/sparse_structure_records.csv` records the five excluded rows.
- Model A versus Model B used identical `StratifiedShuffleSplit(n_splits=50, test_size=0.2, random_state=42)` splits (fingerprint `7e2de3de11d9492ce61e8535a494d3c89f14d8f9ced3b3bb22e64ae7e1a19ca7`). Exact saved mean +/- SD CV $R^2$ values (A; B; B-A) are: Elastic Net `0.12514704250530678 +/- 0.21788323180765704`; `0.2538137894512198 +/- 0.2133738812827973`; `+0.12866674694591304 +/- 0.11515213585473609`. SVR `-0.16484028867259448 +/- 0.46255029862946184`; `0.005529756941640023 +/- 0.40886103786592837`; `+0.17037004561423444 +/- 0.2004758865887298`. Random Forest `0.02744861360791968 +/- 0.4142927098161099`; `0.14278614688477886 +/- 0.3054890323400291`; `+0.11533753327685917 +/- 0.28224481999652173`. XGBoost `-0.21476255627454977 +/- 0.6296683805603616`; `-0.029967853404819306 +/- 0.35011609900627305`; `+0.1847947028697304 +/- 0.4828590350438941`. Source: `results/revision/R1C6/modelA_modelB_sensitivity.csv`.
- Feature-block ablation used the same 50 splits. Exact saved mean +/- SD CV $R^2$ and change from the full model are: full `0.14578161654301114 +/- 0.3016624498255235`; remove internal resistance `0.0320234234597325 +/- 0.40959030529464563`, change `-0.11375819308327864`; remove structure `0.1290537799525689 +/- 0.30681935931210647`, change `-0.016727836590442247`; remove ion type `0.143660115042509 +/- 0.2972173447744393`, change `-0.0021215015005021376`; remove material class `0.08420352934969483 +/- 0.3223192499921583`, change `-0.06157808719331631`; remove mechanism labels `0.1535294271803008 +/- 0.3075286367029461`, change `+0.007747810637289659`. Source: `results/revision/R1C6/feature_block_ablation_sensitivity.csv`.
- The SHAP rerun used a 300-tree Random Forest, stratified 80/20 holdout, seed 42, and TreeExplainer on the held-out transformed data. `log(R)` remains rank 1 with exact mean absolute SHAP `0.44685884243476975`; the runner-up, other cation, is `0.13311401220355817`. The complete 80-feature ranking is in `results/revision/R1C6/SHAP_sensitivity.csv`.
- These outputs support the response-letter wording: Model B improves over Model A for all four families, removing resistance causes the largest ablation decline, and `log(R)` remains the top SHAP descriptor. The status remains open only because neither final PDF documents the retained analysis. `scripts/integrate_r1c6_production.py` integrates the separate Fig. 5/Fig. 6 sparse-category results and deliberately does not replace Fig. 3 or Tables S4-S6, explaining why these sensitivity files did not enter the PDFs.

### MUST-007 — Fig. S2 has no identifiable analysis population or model protocol

- Status: VERIFIED-OPEN
- Severity: MUST-FIX
- File: `Supplementary_Material_R1.pdf`
- Page / section / figure / table: SI p. 22, Fig. S2 and caption; potentially Methods S3–S4, pp. 4–6.
- Reviewer linkage: Reviewer 1 Comment 2; Reviewer 3 Comments 1, 3, and 4.
- Current wording/result: Fig. S2 reports random-split versus paper-grouped validation, target sensitivity, and mechanism-subgroup modeling, but the caption and methods do not identify the analysis population, model family/configuration, exact descriptor set, whether $\log(R)$ was included, or how missing $R$ was handled.
- Problem: The reader cannot determine whether Fig. S2 uses all 159 records with imputation, the common 112-record observed-R population, a no-$R$ model, or another legacy protocol. Its values therefore cannot be compared safely with Fig. 3 or the revised no-imputation claims.
- Why it matters: Missing-data treatment and common-population comparison were central reviewer concerns. An undefined robustness figure can appear to preserve the old workflow the response says was revised.
- Recommended minimal correction: Add a concise protocol statement to Methods S3/S4 and the Fig. S2 caption specifying $n$ for each panel/subgroup, model family, features/target, validation scheme, inclusion or exclusion of $\log(R)$, and missing-data handling. If the figure uses an old superseded workflow, relabel or remove it after verifying provenance.
- Cross-document evidence: Fig. 3 and Tables S4–S6 explicitly state $n=112$ and no $R$ imputation; Fig. S2 contains no parallel definition and is not numerically tied to those tables.
- Requires new analysis: NO — protocol/provenance documentation must be established first.

#### Repository forensic finding

- Fig. S2 belongs to the **original 159-record Model B workflow with imputed missing resistance**, not the revised 112-record no-imputation workflow and not a no-R model. The generating analysis is `notebooks/05_modeling_phase2_robustness.ipynb`; `notebooks/22_supporting_figures.ipynb` later hard-codes its rounded summaries to draw/export Fig. S2. The three exported tables are `results/supporting_materials/figures/Fig_S2/Fig_S2A_validation_strategy_summary.csv`, `Fig_S2B_target_sensitivity_summary.csv`, and `Fig_S2C_mechanism_subgroup_summary.csv` in that directory.
- Common model/proprocessing: every panel uses `RandomForestRegressor(n_estimators=300, max_depth=10, min_samples_split=2, min_samples_leaf=1, random_state=42, n_jobs=-1)` and Model B. Its 18 inputs are `material_class`, `structure_class`, `built_in_asymmetry`, `inorganic_electrolyte_present`, `polyelectrolyte_present`, `has_anionic`, `has_cationic`, `has_zwitterionic`, `mechanism_simple`, `water_interaction_mode`, `top_electrode`, `bottom_electrode`, `electrode_symmetry`, `metal_electrode`, `ionic_groups`, `ion_type`, `log_internal_resistance_Mohm`, and `has_internal_resistance`. Numeric missing values are median-imputed and categorical missing values are most-frequent-imputed before one-hot encoding. Consequently, the 47 missing `log(R)` values in the full population are imputed, while `has_internal_resistance` marks their absence.
- Panel A: $n=159$, target `log_estimated_power_density`. “Repeated random split” is mechanism-stratified `StratifiedShuffleSplit(n_splits=100, test_size=0.2, random_state=42)` and gives underlying `0.164450 +/- 0.178716` (exported/displayed `0.164 +/- 0.179`). “Grouped by paper” is `GroupKFold(n_splits=5)` using `paper_doi`, with no shuffle/seed, and gives `0.106480 +/- 0.197512` (exported `0.106 +/- 0.198`).
- Panel B: $n=159$, Model B and 50 mechanism-stratified 80/20 splits (`random_state=42`). Targets/results are `log_estimated_power_density`, `0.197305 +/- 0.154939` (exported `0.197 +/- 0.155`); raw `voc_V`, `-0.385838 +/- 0.607262` (exported `-0.386 +/- 0.607`); and natural-log-transformed `jsc_uA_cm2` after clipping at $10^{-9}$, `0.274758 +/- 0.146178` (exported `0.275 +/- 0.146`). No target values are missing.
- Panel C: target `log_estimated_power_density`; Model B is fit separately to the ion-gradient subgroup ($n=107$) and streaming subgroup ($n=52$). Each uses `StratifiedShuffleSplit(n_splits=50, test_size=0.2, random_state=42)` with a constant dummy stratum, so these are repeated random 80/20 splits. Results are `0.004680 +/- 0.247485` (exported `0.005 +/- 0.247`) and `-0.756644 +/- 0.529685` (exported `-0.757 +/- 0.530`), respectively. Missing `log(R)` is median-imputed within each subgroup and marked by the availability indicator.
- Scientific compatibility: the figure can be retained only as a clearly labeled, separately defined full-dataset/imputation sensitivity and must not be presented as direct evidence for the revised common-112 no-imputation workflow. If the intended role is instead to validate that revised workflow, it must be rerun; alternatively, documenting/reframing or removing the legacy figure requires no new computation. The status is `VERIFIED-OPEN` because provenance is resolved but the SI still lacks this essential protocol and qualification.

### MUST-008 — Table S7(D) presents unexplained R² values from an undefined model/protocol

- Status: RESOLVED-IN-REPO
- Severity: MUST-FIX
- File: `Supplementary_Material_R1.pdf`; `MANUSCRIPT_R1.pdf`
- Page / section / figure / table: SI p. 18, Table S7(D); SI Methods S5 p. 7; manuscript Fig. 3/Section 4 pp. 20–25.
- Reviewer linkage: Reviewer 1 Comments 2 and 4; Reviewer 3 Comment 3.
- Current wording/result: Table S7(D) reports CV $R^2$/test $R^2$ of 0.251254/0.428578 for “Raw log(R),” identical values for centered $\log(R)$, and 0.296935/0.518388 for an R-regime descriptor. No model family, feature set, population, train/test split, CV scheme, preprocessing, or random seed is stated.
- Problem: These values are substantially different from Fig. 3/Table S4 and Table S5, but the methodological reason cannot be determined from the PDFs. They may be legitimate results from a different protocol; the absence of definition makes them appear inconsistent and prevents reproduction.
- Why it matters: The audit must not treat different valid $R^2$ values as contradictory, but the document must provide enough information to distinguish protocols. Table S7(D) currently does not.
- Recommended minimal correction: Add a Table S7(D) note and matching S5 method paragraph defining population, response variable, complete feature set, model, split/CV protocol, preprocessing, and relationship to Fig. 3. If the panel is obsolete or not needed for the threshold argument, remove it rather than leave an unexplained model comparison.
- Cross-document evidence: Table S4 explicitly uses 112 records and 30 stratified shuffle splits; Table S5 uses 112 records and 50 identical splits; Table S7(D) has no corresponding protocol. Its differing values are therefore unresolved, not demonstrated numerical errors.
- Requires new analysis: NO.

#### Repository forensic finding

- The listed values are reproducible **legacy outputs** from the historical version of `notebooks/11_physics_aware_R_descriptor.ipynb` at Git commit `f50d026` (the notebook output and its then-written `results/11_physics_R_descriptor_model_comparison.csv`). They used all 159 records and `log_estimated_power_density` as target. The model was an `ElasticNetCV` pipeline with inner five-fold CV, `l1_ratio=[0.1,0.3,0.5,0.7,0.9,1.0]`, `alphas=logspace(-4,2,80)`, `max_iter=20000`, and `random_state=42`.
- Complete feature sets were: raw model = `log_internal_resistance_Mohm`, `structure_class`, `ion_type`, `mechanism_simple`; centered model = `logR_centered` plus the same three categorical fields; regime model = `R_regime` plus the same three categorical fields. Numeric values were median-filled then standardized; categorical values were filled with `unknown` then one-hot encoded with `drop="first"` and unknown-category tolerance. The 80/20 train/test split was unstratified with `random_state=42`; external CV was `KFold(n_splits=5, shuffle=True, random_state=42)`.
- Missing-R treatment is the decisive legacy defect. Raw `log(R)` was median-imputed; centered `log(R)` remained missing until it too was median-imputed (to the centered median). The regime code used `np.where(logR <= observed_median, "low_R", "high_R")`, which assigned all 47 missing-R records to `high_R`; the resulting groups were 56 low-R and 103 high-R. Thus each displayed model had $n=159$. The historical notebook's stored full-precision outputs are: raw CV $R^2=0.2512535267699536 +/- 0.09120404225219486$, test $R^2=0.42857762213842443$; centered CV $R^2=0.2512535267699537 +/- 0.09120404225219488$, test $R^2=0.42857762213842443$; regime CV $R^2=0.29693465299850785 +/- 0.1315840403282318$, test $R^2=0.5183880687963153$. Table S7(D) rounds these to the values under audit.
- `notebooks/15_figure4_resistance_regimes.ipynb` then hard-coded these rounded legacy values into `results/figure4_resistance_regimes/fig4D_R_descriptor_comparison.csv`; `notebooks/21_supporting_tables.ipynb` copied that file verbatim into `results/supporting_materials/tables/Table_S7D_R_descriptor_comparison.csv`. This explains why Table S7(D) persisted after its source analysis changed.
- Git commit `43fe24c` revised `notebooks/11_physics_aware_R_descriptor.ipynb` to keep missing regimes as missing, use the fixed Fig. 4 threshold `log(R)=-1`, and run all three formulations on the 112 observed-R records. The current saved `results/11_physics_R_descriptor_model_comparison.csv` consequently gives raw/centered CV `0.30475620413498383 +/- 0.14693906721539404`, test `0.3202843268100538`, and regime CV `0.3102820207766089 +/- 0.15531666226084082`, test `0.2023249785659702`. Table S7(D) was not refreshed from this corrected output.
- Purpose and relationship to Fig. 3: this was a small, interpretable Elastic Net comparison of alternative resistance formulations, not the four-family, 16-versus-17-descriptor Fig. 3 analysis. Its full-$n=159$ imputation, four-feature design, single random holdout, and five-fold KFold scheme explain the different $R^2$ values.
- Historical classification: **B — obsolete legacy output requiring removal or replacement.** The exact legacy numbers and protocol are verifiable, but they were superseded specifically to correct missing-R/regime handling. Retaining them merely with a method note would preserve a known misclassification of 47 missing-R records.

#### Production fix (2026-08-20)

- Disposition: **RETAINED + REPLACED.** The comparison remains scientifically coherent because it directly tests whether the interpretable resistance-model conclusion depends materially on representing resistance as raw continuous `log(R)`, centered continuous `log(R)`, or the coarse fixed-threshold regime descriptor. It is not presented as evidence that the regime descriptor is uniformly superior.
- `notebooks/11_physics_aware_R_descriptor.ipynb` was rerun successfully and is now the single analysis source for both S7(C) and S7(D). It uses the 112 records with observed `log_internal_resistance_Mohm`, excludes all 47 missing-R records before either analysis, uses `log(R)=-1` for the regime definition, and writes the new S7(C) canonical file `results/11_R_regime_performance_statistics.csv` plus the existing corrected S7(D) canonical file `results/11_physics_R_descriptor_model_comparison.csv`.
- S7(C) provenance was re-traced independently. `notebooks/15_figure4_resistance_regimes.ipynb` historically loaded a notebook-local phase-2 CSV, but that file and `data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv` parse to exactly identical 159-by-52 data despite byte-level encoding differences. A fresh calculation from the canonical processed file reproduces low-R $n=55$ and high-R $n=57$ and all published S7(C)/Fig. 4 statistics exactly; therefore no separate Fig. 4 inconsistency was found.
- The obsolete propagation path was removed: Notebook 15 no longer hard-codes the legacy 159-record S7(D) values, and `notebooks/21_supporting_tables.ipynb` no longer copies the historical Figure 4 CSV. Both now read the corrected Notebook 11 outputs. `scripts/refresh_table_s7_cd.py` independently validates the S7(C) result against the current processed data, validates $n=112$ for every S7(D) formulation, and refreshes only the affected Figure 4 and SI CSVs.
- Corrected S7(D) canonical results are raw/centered `log(R)`: CV $R^2=0.30475620413498383 +/- 0.14693906721539404$, test $R^2=0.3202843268100538$; R-regime: CV $R^2=0.3102820207766089 +/- 0.15531666226084082$, test $R^2=0.2023249785659702$. Every row has $n=112$.
- The complete current S7(C)/S7(D) protocol and source/output paths are recorded in `results/revision/Table_S7C_S7D_method_note.md`.
- Repository status: `RESOLVED-IN-REPO`. The current Word/SI PDF has not been regenerated and still displays the obsolete S7(D) values; final PDF replacement and visual/numerical verification remain pending.

### MUST-009 — Main-manuscript Supplementary Materials list omits Fig. S6

- Status: OPEN
- Severity: MUST-FIX
- File: `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript p. 39, Supplementary Materials list; SI p. 26, Fig. S6; response p. 17.
- Reviewer linkage: Reviewer 3 Comment 3.
- Current wording/result: The manuscript lists “Figs. S1 to S5,” while the revised SI contains Fig. S6 and the response calls it the new figure documenting resistance-data availability and robustness.
- Problem: The main manuscript's inventory is outdated.
- Why it matters: It makes a claimed reviewer-response addition look unfinished or absent.
- Recommended minimal correction: Change the list to “Figs. S1 to S6.”
- Cross-document evidence: SI p. 26 is explicitly Fig. S6; response p. 17 says the new analyses were added to Fig. S6; manuscript p. 39 stops at S5.
- Requires new analysis: NO.

## RECOMMENDED

### REC-001 — Data dictionary omits electrode descriptors used by the model and SHAP ranking

- Status: OPEN
- Severity: RECOMMENDED
- File: `Supplementary_Material_R1.pdf`; `MANUSCRIPT_R1.pdf`
- Page / section / figure / table: SI pp. 9–10, Table S1; SI p. 16, Table S6; manuscript pp. 9–10 and 21–23.
- Reviewer linkage: Reviewer 3 Comments 1 and 4.
- Current wording/result: Table S1 is presented as the data dictionary and descriptor encoding, but it does not list top- or bottom-electrode descriptors. Table S6 ranks “Top electrode: Cu,” “Bottom electrode: Cu,” “Top electrode: Au,” and “Bottom electrode: Au,” and the manuscript says electrode-material information was retained.
- Problem: The documented descriptor framework is incomplete relative to the features actually interpreted by SHAP.
- Why it matters: Readers cannot reconstruct the full baseline descriptor set or its encoding from the SI.
- Recommended minimal correction: Add concise Table S1 entries for the electrode-material fields and their missing-data/encoding treatment, or explicitly cross-reference the complete repository dictionary and enumerate the model feature groups in S3.
- Cross-document evidence: SI Table S6 includes four electrode-derived features in the top ten; SI Table S1 contains no electrode field; manuscript p. 10 says electrode-material information was retained.
- Requires new analysis: NO.

### REC-002 — Make the Fig. 4 population explicit in the standalone caption

- Status: OPEN
- Severity: RECOMMENDED
- File: `MANUSCRIPT_R1.pdf`
- Page / section / figure / table: Manuscript p. 28, Fig. 4 caption; Section 5 introduction p. 26 and Section 5.2 p. 27.
- Reviewer linkage: Reviewer 1 Comments 2 and 4; Reviewer 3 Comment 3.
- Current wording/result: The surrounding text defines the observed-R population as $n=112$ and gives the 55/57 regime split, but the Fig. 4 caption says only that devices have reported internal resistance and does not state $n=112$ or the panel-B group sizes.
- Problem: The figure is correct but not fully self-contained regarding population.
- Why it matters: Explicit population labeling helps prevent the resistance-regime result from being mistaken for a 159-record analysis.
- Recommended minimal correction: Add “$n=112$” to the caption and “low-R $n=55$; high-R $n=57$” for panel B.
- Cross-document evidence: Manuscript pp. 26–27 and SI Table S7(C) give the population and group counts; Fig. 4 uses that same population but omits the numbers from its caption.
- Requires new analysis: NO.

## FORMAT-ONLY

### FMT-001 — Cross-validation $R^2$ notation is not standardized

- Status: OPEN
- Severity: FORMAT-ONLY
- File: `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript pp. 21–25 and 34–36; SI Methods/Tables pp. 4–8 and 14–19; response pp. 3, 5, 7, and 17.
- Reviewer linkage: General numerical presentation.
- Current wording/result: The PDFs alternate among $R^2_{CV}$, “CV $R^2$,” “cross-validated $R^2$,” extracted headers such as `R2CV`, and $\Delta R^2$ without a CV qualifier for cross-validated changes.
- Problem: The same metric and its change are formatted multiple ways; $\Delta R^2$ can be mistaken for a held-out/test-$R^2$ change.
- Why it matters: Consistent notation makes the different model protocols easier to distinguish.
- Recommended minimal correction: Adopt one display convention, preferably $R^2_{CV}$ and $\Delta R^2_{CV}$, in analytical prose, captions, and publication-facing table headings. Literal dataset/result column names may remain unchanged when explicitly identified as such.
- Cross-document evidence: Main Section 4 uses typeset $R^2_{CV}$ but p. 24 uses “median $\Delta R^2$”; Table S5 uses $\Delta R^2_{CV}$; Table S8 uses “CV R²”; response often uses plain “Delta R2.”
- Requires new analysis: NO.

### FMT-002 — Mathematical minus signs are mixed with hyphens

- Status: OPEN
- Severity: FORMAT-ONLY
- File: `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript pp. 16–17, 27, 30, and 33–36; SI pp. 3, 7–8, 15, and 18–26; response pp. 2, 5, 15, and 17.
- Reviewer linkage: General numerical presentation.
- Current wording/result: Negative values and thresholds alternate between a mathematical minus (−) and a keyboard hyphen (-), including $\log(R)=-1$, medians, coefficients, and negative $R^2$ values.
- Problem: Mathematical sign typography is inconsistent.
- Why it matters: This is visible revision patchwork in equations, tables, and captions.
- Recommended minimal correction: Use the mathematical minus sign for numerical negatives and subtraction in publication text; retain hyphens only inside literal field/category names such as `low_R` or source-code-style labels.
- Cross-document evidence: The Fig. 4 caption uses “−1,” while nearby Section 5.2 text and several SI tables/captions use “-1”; main p. 17 uses hyphens for negative medians while equations elsewhere use minus glyphs.
- Requires new analysis: NO.

### FMT-003 — $V_{oc}$, $J_{sc}$, and $P_{est}$ symbol styling varies

- Status: OPEN
- Severity: FORMAT-ONLY
- File: `MANUSCRIPT_R1.pdf`; `Supplementary_Material_R1.pdf`; `Response_letter.pdf`
- Page / section / figure / table: Manuscript Abstract p. 1 and Sections 2.1–2.2 pp. 9–13; SI S2 p. 3, Table S1 pp. 9–10, Figs. S1–S2 pp. 21–22; response pp. 1–3 and 15–16.
- Reviewer linkage: Reviewer 1 Comment 1; Reviewer 3 Comment 2.
- Current wording/result: Mathematical prose/labels vary among $V_{OC}$/$V_{oc}$, $J_{SC}$/$J_{sc}$, and visually different `Pest`/$P_{est}$ forms.
- Problem: Mathematical notation is not fully uniform across the three documents.
- Why it matters: Uniform symbols make the standardized-proxy definition and validation easier to follow.
- Recommended minimal correction: Choose one manuscript convention (for example, $V_{oc}$, $J_{sc}$, and $P_{est}$) and apply it to mathematical prose, equations, axes, and captions. Do not alter literal dataset column names such as `voc_V`, `jsc_uA_cm2`, or `estimated_power_density_uW_cm2`.
- Cross-document evidence: Main Eq. (1) uses one subscript style, later prose uses another; the SI figure/table labels and response use additional plain-text variants. Dataset-column spellings are correctly treated as literal identifiers and are not themselves inconsistencies.
- Requires new analysis: NO.

### FMT-004 — Several SI tables wrap headers and numbers into ambiguous fragments

- Status: OPEN
- Severity: FORMAT-ONLY
- File: `Supplementary_Material_R1.pdf`
- Page / section / figure / table: SI pp. 17–20, especially Table S7(A) and Table S8(B); also raw publication-facing headings in Tables S7–S8.
- Reviewer linkage: General figure/table consistency.
- Current wording/result: Table S7(A) breaks signs and decimal digits over multiple lines (for example, negative means/minima and long decimals), and Table S8(B) breaks values and headers such as `n_rows`, `cv_R2_mean`, and test metrics across narrow cells. Table S7 uses raw internal column names in publication-facing headings.
- Problem: Some values can only be reconstructed by joining stacked fragments; signs are visually separated from numbers.
- Why it matters: This creates avoidable ambiguity in the numerical record even though the underlying values agree with the manuscript.
- Recommended minimal correction: Reformat the affected tables in landscape or with fewer columns/rounded precision; keep each signed number on one line and replace raw variable names with readable headings. Preserve the underlying values.
- Cross-document evidence: SI p. 17 visually splits Table S7(A) values such as negative means/minima; SI p. 19 similarly splits Table S8(B) numerical cells. The same rounded canonical values are readable in the manuscript prose.
- Requires new analysis: NO.

## Reviewer closure matrix

| Reviewer | Comment | Response claim | Main implemented? | SI implemented? | Numbers consistent? | Status | Related audit IDs |
|---|---|---|---|---|---|---|---|
| R1 | C1 — Validate $P_{est}$ against reported power density | Compared 108 records in log space; added Pearson/Spearman, bias/error, tolerance fractions; revised terminology and Fig. S1 | Yes, Section 2.2 | Yes, S2 and Fig. S1 | Yes | CLOSED | — |
| R1 | C2 — Common population and missing-$R$ handling | Re-ran Fig. 3 on the same 112 records; no $R$ imputation; identical splits for Model A/B | Yes, Section 4 and Fig. 3 | Yes, S3–S4 and Tables S4–S6 | Yes | CLOSED for Fig. 3; Fig. S2 remains undefined | MUST-001, MUST-007 |
| R1 | C3 — Add Song et al. and clarify osmotic-system exclusion | Added citation and expanded physical exclusion rationale | Yes, Section 2.1 and Ref. 30 | Scope criteria present in S1/Table S2 | N/A | CLOSED | — |
| R1 | C4 — Justify $R=0.1$ MΩ threshold | Tested 42 thresholds; exact $\log(R)=-1$ included; boundary not optimized | Yes, Section 5.2/Fig. 4 | Yes, S5, Table S7(C), Fig. S3 | Yes | CLOSED | REC-002 |
| R1 | C5 — Add Zhou et al. for structural resistance discussion | Added citation while keeping osmotic systems outside dataset scope | Yes, Section 6.2 and Ref. 32 | Scope limitation remains consistent | N/A | CLOSED | — |
| R1 | C6 — Sparse hybrid categories | Retained descriptively; excluded from inference/virtual screening; claimed separate five-record Fig. 3 sensitivity | Partly: exclusions are documented; sensitivity only asserted | Partly: 107-record explicit model is documented; claimed Fig. 3 sensitivity is absent | Documented values are consistent; claimed sensitivity has no values | OPEN | MUST-005, MUST-006 |
| R2 | Overall — Wet/operating-state $R$, electrolyte coupling, causal limits, practical value | Reframed $R$ as reported operating-state/device-level; not intrinsic or unique mechanism; narrowed to screening guidance and R-reported subset | Partly: limitations appear, but prominent causal/control/design-rule language and unqualified conclusions remain | Partly: causal caveats appear, but Table S1 provenance/wording and Fig. S4 title conflict | Repeated numbers consistent | OPEN | MUST-001, MUST-003, MUST-004, MUST-005 |
| R3 | C1 — Dataset construction, representativeness, heterogeneous conditions | Added curated/nonrepresentative scope, extraction/harmonization, omitted-variable limitations, revised Fig. 1 | Yes | Yes, S1 and Tables S1–S3 | Yes | PARTIAL — mechanism provenance wording and dictionary completeness remain | MUST-002, REC-001 |
| R3 | C2 — $P_{est}$ validity and nonlinear/time-dependent behavior | Validated 108 records; used “reported power density”; retained proxy limitations | Yes, Section 2.2 | Yes, S2/Fig. S1 | Yes | CLOSED | — |
| R3 | C3 — Resistance availability/selection bias | Compared 112 vs 47; added 300 subsamples and 50 SHAP reruns; narrowed population scope; added Fig. S6 | Yes, Section 4.5, except high-visibility summary qualifier | Yes, S4/Fig. S6 | Yes | PARTIAL | MUST-004, MUST-009 |
| R3 | C4 — Coarse descriptors and imbalance | Added omitted-variable/coarse-graining caveats; retained sparse categories descriptively; claimed sparse-hybrid sensitivity | Partly | Partly: exclusions documented; claimed sensitivity absent; electrode features missing from dictionary | Documented values consistent | OPEN | MUST-002, MUST-005, MUST-006, REC-001 |

## Numerical consistency ledger

| Quantity / analysis | Canonical final value | Main-manuscript location | SI location | Response-letter location | Consistency status |
|---|---|---|---|---|---|
| Full curated dataset | $n=159$ | pp. 7, 13 | S1 pp. 1–2; Table S3 p. 12 | pp. 3, 7, 13–14, 16 | Consistent |
| Reported-$R$ subset | $n=112$ (provenance wording unresolved) | pp. 13, 20, 24–26 | S3–S4 pp. 4–5; Tables S3–S6; Fig. S6 | pp. 3, 7, 10, 16–17 | Numerically consistent; factual provenance open (MUST-001) |
| R-missing subset | $n=47$ | p. 24 | S4 p. 5; Fig. S6 p. 26 | p. 16 | Consistent; $112+47=159$ |
| $P_{est}$ validation subset | $n=108$ | pp. 12–13 | S2 p. 3; Table S3 p. 12; Fig. S1 p. 21 | pp. 2, 15 | Consistent |
| Sparse-structure-excluded explicit-model subset | $n=107$ | pp. 30–36 | S5–S6 pp. 7–8; Table S8 pp. 19–20; Fig. S5 p. 25 | pp. 7, 18 | Consistent; $84+13+10=107$ and $112-5=107$ |
| $P_{est}$ validation — Pearson | $r=0.959$ | p. 12 | S2 p. 3; Fig. S1 p. 21 | pp. 2, 15 | Consistent; plot annotation rounds to 0.96 |
| $P_{est}$ validation — Spearman | $\rho=0.957$ | p. 12 | S2 p. 3; Fig. S1 p. 21 | pp. 2, 15 | Consistent; plot annotation rounds to 0.96 |
| $P_{est}$ validation — median $\Delta\log(P)$ | $1.37\times10^{-4}$ | p. 12 | S2 p. 3; Fig. S1 p. 21 | pp. 2, 15 | Consistent; plot/caption describe rounded 0.00/approximately zero |
| $P_{est}$ validation — MAE | 0.276 log units | p. 12 | S2 p. 3; Fig. S1 p. 21 | pp. 2, 15 | Consistent; plot annotation rounds to 0.28 |
| $P_{est}$ validation — RMSE | 0.373 log units | p. 12 | S2 p. 3; Fig. S1 p. 21 | pp. 2, 15 | Consistent; plot annotation rounds to 0.37 |
| $P_{est}$ validation — within $\pm0.5$ | 76.9% | p. 12 | S2 p. 3 | pp. 2, 15 | Consistent |
| $P_{est}$ validation — within $\pm1.0$ | 98.1% | p. 12 | S2 p. 3 | pp. 2, 15 | Consistent |
| Tuned model-family $R^2_{CV}$ means | Elastic Net 0.203; SVR 0.187; Random Forest 0.179; XGBoost 0.143 | p. 21; Fig. 3A p. 25 | Table S4 p. 14 | Not separately stated | Consistent; Table S4 protocol is 30 splits |
| Model A/B $\Delta R^2_{CV}$ | Elastic Net $+0.107\pm0.118$; SVR $+0.187\pm0.143$; Random Forest $+0.068\pm0.202$; XGBoost $+0.130\pm0.306$ | p. 22; Fig. 3B p. 25 (means) | Table S5(A) p. 15 | pp. 3–4 (means) | Consistent; 50 identical splits, $n=112$ |
| Ablation $\Delta R^2_{CV}$ | Internal resistance −0.0618; material class −0.0538; structure −0.0216; ion type −0.0023; mechanism +0.0026 | pp. 22–23; Fig. 3C p. 25 | Table S5(B) p. 15 | p. 3 gives internal-resistance value; pp. 7/19 give ranking | Consistent |
| SHAP top values | $\log(R)$ 0.460; other cation 0.0719; top-electrode Cu 0.0519; biomass 0.0506; bottom-electrode Cu 0.0498; film 0.0490; top-electrode Au 0.0473; proton 0.0467; bottom-electrode Au 0.0407; polymer 0.0382 | p. 23 and Fig. 3D p. 25 give top values/ranking | Table S6 p. 16 | p. 3 gives top two and 6.4× ratio | Consistent; $0.460/0.0719\approx6.4$ |
| Resistance threshold | $R=0.1$ MΩ corresponds to $\log_{10}(R/\mathrm{M\Omega})=-1$; 42 thresholds tested; best mean regime-only CV near −1.15 | pp. 27–28 | S2 p. 3; S5 p. 7; Fig. S3 p. 23 | p. 5 | Consistent |
| Table S7(C) resistance regimes (new canonical) | Low-R: $n=55$, mean/median/SD $\log(P_{est})=0.413553/0.454845/0.957220$, mean/median $\log(R)=-1.807239/-1.721246$; high-R: $n=57$, corresponding values $-0.850091/-0.823906/1.243873$ and $0.425354/0.176091$ | p. 27 gives counts, medians, and $\approx1.28$ separation | Current Table S7(C) p. 18 agrees; canonical replacement source is `results/11_R_regime_performance_statistics.csv` | p. 5 | Fresh 112-record calculation; $\log(R)=-1$; no missing-R records; Fig. 4/manuscript numbers remain consistent |
| Fig. 5A electrolyte groups | Without inorganic electrolyte $n=71$, median $\log(R)=0.000$; with $n=41$, median −1.65758 (−1.658); Mann–Whitney $U=2218$, $p=4.10\times10^{-6}$ | p. 29; Fig. 5 p. 31 | Table S7(A–B) pp. 17–18 | Not numerically repeated | Consistent; totals 112 |
| Fig. 5B ion groups | Proton $n=62$, median 0.000; other cation $n=42$, median −1.63868 (−1.639); anion $n=8$, median −0.18362 (−0.184); $H=20.40773$, $p=3.70\times10^{-5}$ | p. 29; Fig. 5 p. 31 | Table S7(A–B) pp. 17–18 | Not numerically repeated | Consistent; totals 112 |
| Structure association | Porous $n=84$, median −0.22797 (−0.228); film $n=13$, median −1.000; hydrogel $n=10$, median −2.000; $H=8.543$; $p=0.014$ | p. 30; Fig. 5 p. 31 | S5 p. 7; Table S7(A–B) pp. 17–18 | p. 7 | Consistent; SI exact $H=8.5427$, $p=0.013963$ |
| Selection bias — target distribution | Mann–Whitney $p=0.0130$ (0.013); rank-biserial correlation 0.250 | p. 24 | S4 p. 5; Fig. S6 p. 26 | p. 16 | Consistent |
| Selection bias — power-density availability | R-reported 81.2%; R-missing 36.2%; $p=2.74\times10^{-8}$; Cramér's $V=0.441$ | p. 24 gives percentages | Fig. S6 p. 26 gives all statistics | p. 16 gives all statistics | Consistent |
| Repeated Model A/B subsampling | 300 repetitions; 90 records each; positive in 288/300 (96.0%); median $\Delta R^2_{CV}=+0.1269$ | p. 24 | S4 pp. 5–6; Fig. S6 p. 26 | p. 17 | Consistent |
| Repeated SHAP rank | 50 repetitions; $\log(R)$ ranked first in 50/50 | p. 24 | S4 pp. 5–6; Fig. S6 p. 26 | p. 17 | Consistent |
| Explicit-model coefficients ($n=107$) | $\log(R)$ −0.43943; film +0.369564; porous −0.29955; inorganic electrolyte +0.144788; other cation +0.143237; ion-gradient +0.10173; streaming −0.10171; anion −0.07409 | p. 33 and Fig. 6A p. 36 (rounded) | Table S8(A) p. 19 | Not separately stated | Consistent |
| Linear explicit-model performance | CV $R^2=0.172976\pm0.167158$ (0.173 ± 0.167); test $R^2=0.102012$ (0.102) | p. 34; Fig. 6B p. 36 | S6 p. 8; Table S8(B) p. 19 | Not separately stated | Consistent |
| Polynomial explicit-model performance | CV $R^2=0.158647\pm0.102194$ (0.159 ± 0.102); test $R^2=0.099229$ (0.099) | p. 34; Fig. 6B p. 36 | S6 p. 8; Table S8(B) p. 19 | Not separately stated | Consistent |
| Top virtual descriptor prediction | Film + other cation + inorganic electrolyte + $\log(R)=-2$: predicted $\log(P_{est})=1.089454$ (1.089) | p. 35; Fig. 6D p. 36 | Table S8(C) p. 20 | Not separately stated | Consistent |
| Table S7(D) R-descriptor formulations (new canonical) | Raw/centered $\log(R)$: $n=112$, CV 0.304756 ± 0.146939, test 0.320284; R-regime: $n=112$, CV 0.310282 ± 0.155317, test 0.202325 | No direct counterpart; distinct four-feature Elastic Net formulation check | Current Table S7(D) PDF still shows obsolete 159-record values; repository CSV replacement is corrected | Not stated | `RESOLVED-IN-REPO` under MUST-008; SI PDF regeneration/verification pending |

## Population map

| Population | Definition | Analyses using it | Why |
|---|---|---|---|
| $n=159$ | Full curated non-galvanic cross-literature comparison set | Fig. 1 composition/completeness; Fig. 2 descriptive mechanism/structure/ion distributions; target construction; full-dataset reporting summaries | $V_{oc}$, $J_{sc}$, $P_{est}$, and the principal categorical descriptors are available for all records; sparse categories are retained descriptively |
| $n=112$ | Records described as having reported internal resistance (provenance must be verified under MUST-001) | Fig. 3 model family, Model A/B, ablation, and SHAP; Fig. 4 resistance regimes; Fig. 5A electrolyte and Fig. 5B ion comparisons; selection/robustness base population | Ensures observed $R$ and no internal-resistance imputation; Model A/B use identical records |
| $n=108$ | Records with both $P_{est}$ and reported power density | $P_{est}$ validation and Fig. S1A/B/D | Supports proxy validation without calling reported values measured $P_{max}$ |
| $n=107$ | Observed-R records after excluding five sparse hybrid structures: hydrogel + porous (4) and hydrogel + film (1) | Fig. 5C three-class structure inference; explicit Elastic Net model; Fig. 6 and Fig. S5 virtual descriptor screening; Table S8 | Prevents one- and four-record structure categories from driving inferential/explicit-model coefficients or virtual screening |
| $n=47$ | Records with missing internal resistance | Comparison against the 112-record observed-R group in Fig. S6 | Quantifies resistance-reporting selection effects; not used for resistance-dependent inference |

## Final unresolved questions

1. Source-level provenance remains unavailable for all 112 non-missing resistance values: which records were directly reported versus curator-estimated, and what external source/curation evidence establishes that classification?
2. Will the verified sparse-hybrid-excluded Fig. 3 sensitivity outputs in `results/revision/R1C6/` be documented in the SI and cross-referenced from the manuscript/response?
3. Will Fig. S2 be explicitly retained as a legacy full-159, median-imputed Model B sensitivity (with the protocol and limitation disclosed), removed, or recomputed for the revised common-112 workflow?
4. Will the next SI Word/PDF regeneration correctly replace Table S7(D) with the repository's corrected 112-record output and include the documented protocol note?
