"""Reviewer 1 Comment 6: sparse hybrid structure-category sensitivity.

This is an exploratory, revision-only analysis.  It preserves the canonical
159-record CSV and all production Figure 2/3/5/6 outputs, writing only to
``results/revision/R1C6``.  The two literature-derived sparse hybrid labels are
not merged or recoded; their five records are excluded only for this
sensitivity calculation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler

from run_r1c2_common112 import (
    ABLATION_BLOCKS,
    FEATURES_MODEL_A,
    FEATURES_MODEL_B,
    RANDOM_STATE,
    TARGET,
    build_pipeline,
    display_feature_name,
    evaluate_cv,
    make_default_models,
    make_splits,
    split_fingerprint,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hydrovoltaic_dataset_phase2_input_utf8.csv"
OUT_DIR = PROJECT_ROOT / "results" / "revision" / "R1C6"
R1C2_DIR = PROJECT_ROOT / "results" / "revision" / "R1C2"
FIG5_DIR = PROJECT_ROOT / "results" / "figure5_R_origin"
FIG6_DIR = PROJECT_ROOT / "results" / "figure6_virtual_design"

R_COL = "log_internal_resistance_Mohm"
ROW_ID_COL = "canonical_row_index"
STRATIFY_COL = "mechanism_simple"
TEST_SIZE = 0.20
COMMON_CV_SPLITS = 50
SPARSE_CATEGORIES = ["hydrogel + porous", "hydrogel + film"]
ROBUST_STRUCTURES = ["porous", "film", "hydrogel"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_onehot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # pragma: no cover - scikit-learn compatibility
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def group_summary(df: pd.DataFrame, group_col: str, value_col: str, order: list[str]) -> pd.DataFrame:
    summary = (
        df.dropna(subset=[group_col, value_col])
        .groupby(group_col)[value_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reindex(order)
        .reset_index()
    )
    return summary


def explicit_descriptor_analysis(observed: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Repeat Figure 6's observed-R descriptor model without sparse hybrids."""
    model_df = observed.copy()
    model_df["log_P_est"] = pd.to_numeric(model_df[TARGET], errors="coerce")
    model_df["log_R"] = pd.to_numeric(model_df[R_COL], errors="coerce")
    model_df["structure_clean"] = (
        model_df["structure_class"].astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    )
    model_df["ion_type_clean"] = (
        model_df["ion_type"].astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    )
    model_df["inorganic_electrolyte_present_clean"] = pd.to_numeric(
        model_df["inorganic_electrolyte_present"], errors="coerce"
    )
    model_df["mechanism_clean"] = (
        model_df["mechanism_simple"].astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    )
    model_df = model_df.dropna(subset=["log_P_est", "log_R"]).copy()

    numeric_features = ["log_R", "inorganic_electrolyte_present_clean"]
    categorical_features = ["structure_clean", "ion_type_clean", "mechanism_clean"]
    features = numeric_features + categorical_features
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", make_onehot_encoder())]), categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )
    def elastic(max_iter: int) -> ElasticNetCV:
        return ElasticNetCV(
            l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9], alphas=np.logspace(-4, 1, 80),
            cv=5, random_state=RANDOM_STATE, max_iter=max_iter,
        )
    linear = Pipeline([("preprocess", preprocessor), ("model", elastic(20000))])
    polynomial = Pipeline([
        ("preprocess", preprocessor), ("poly", PolynomialFeatures(degree=2, include_bias=False)), ("model", elastic(30000))
    ])
    X, y = model_df[features], model_df["log_P_est"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    rows = []
    for name, model in [("Linear Elastic Net descriptor", linear), ("Polynomial Elastic Net descriptor", polynomial)]:
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        scores = cross_validate(
            model, X, y, cv=cv,
            scoring=("r2", "neg_root_mean_squared_error", "neg_mean_absolute_error"),
            return_train_score=False,
        )
        rows.append({
            "model": name, "n_rows": len(model_df),
            "train_R2": r2_score(y_train, model.predict(X_train)), "test_R2": r2_score(y_test, prediction),
            "test_RMSE": mean_squared_error(y_test, prediction) ** 0.5, "test_MAE": mean_absolute_error(y_test, prediction),
            "cv_R2_mean": scores["test_r2"].mean(), "cv_R2_std": scores["test_r2"].std(),
            "cv_RMSE_mean": -scores["test_neg_root_mean_squared_error"].mean(), "cv_RMSE_std": scores["test_neg_root_mean_squared_error"].std(),
            "cv_MAE_mean": -scores["test_neg_mean_absolute_error"].mean(), "cv_MAE_std": scores["test_neg_mean_absolute_error"].std(),
        })
    linear.fit(X, y)
    fitted_preprocessor = linear.named_steps["preprocess"]
    fitted_model = linear.named_steps["model"]
    coefficients = pd.DataFrame({
        "feature": fitted_preprocessor.get_feature_names_out(), "coefficient": fitted_model.coef_
    })
    coefficients["abs_coefficient"] = coefficients["coefficient"].abs()
    coefficients = coefficients.sort_values("abs_coefficient", ascending=False, kind="stable").reset_index(drop=True)

    reference = {
        "structure_clean": model_df["structure_clean"].mode().iloc[0],
        "ion_type_clean": model_df["ion_type_clean"].mode().iloc[0],
        "inorganic_electrolyte_present_clean": model_df["inorganic_electrolyte_present_clean"].mode().iloc[0],
        "mechanism_clean": model_df["mechanism_clean"].mode().iloc[0],
    }
    candidate_rows = []
    for structure in ROBUST_STRUCTURES:
        for ion in [ion for ion in ["proton", "other_cation", "anion"] if ion in set(model_df["ion_type_clean"])]:
            for inorg in [v for v in [0, 1] if v in set(model_df["inorganic_electrolyte_present_clean"].dropna())]:
                for log_r in [-2.0, -1.0, 0.0, 1.0]:
                    virtual = pd.DataFrame([{
                        "log_R": log_r, "inorganic_electrolyte_present_clean": inorg,
                        "structure_clean": structure, "ion_type_clean": ion,
                        "mechanism_clean": reference["mechanism_clean"],
                    }])[features]
                    candidate_rows.append({
                        "structure_clean": structure, "ion_type_clean": ion,
                        "inorganic_electrolyte_present_clean": inorg, "log_R": log_r,
                        "R_regime": "low_R" if log_r <= -1 else "high_R",
                        "predicted_log_P_est": linear.predict(virtual)[0],
                    })
    candidates = pd.DataFrame(candidate_rows).sort_values("predicted_log_P_est", ascending=False, kind="stable").reset_index(drop=True)
    candidates.insert(0, "rank", np.arange(1, len(candidates) + 1))
    return coefficients, pd.DataFrame(rows), candidates


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    dataset[ROW_ID_COL] = dataset.index.astype(int)
    original_hash = sha256(DATA_PATH)
    sparse_mask = dataset["structure_class"].isin(SPARSE_CATEGORIES)
    sparse = dataset.loc[sparse_mask].copy()
    retained = dataset.loc[~sparse_mask].copy()
    if len(dataset) != 159 or len(sparse) != 5 or len(retained) != 154:
        raise RuntimeError("Unexpected full/sparse/retained record counts.")
    if sparse["structure_class"].value_counts().to_dict() != {"hydrogel + porous": 4, "hydrogel + film": 1}:
        raise RuntimeError("Sparse-category labels/counts differ from the reviewer-defined scope.")
    if not dataset.loc[sparse_mask, "structure_class"].equals(sparse["structure_class"]):
        raise RuntimeError("Structure labels changed during sparse-record selection.")
    sparse.to_csv(OUT_DIR / "sparse_structure_records.csv", index=False, encoding="utf-8-sig")
    retained[[ROW_ID_COL, "paper_doi", "structure_class"]].to_csv(
        OUT_DIR / "retained_record_identifiers.csv", index=False, encoding="utf-8-sig"
    )

    retained[TARGET] = pd.to_numeric(retained[TARGET], errors="coerce")
    retained[R_COL] = pd.to_numeric(retained[R_COL], errors="coerce")
    structure_performance = group_summary(retained, "structure_class", TARGET, ROBUST_STRUCTURES)
    structure_performance = structure_performance.rename(columns={
        "count": "n", "mean": "mean_log_P_est", "median": "median_log_P_est", "std": "std_log_P_est",
        "min": "min_log_P_est", "max": "max_log_P_est",
    })
    structure_performance.to_csv(OUT_DIR / "structure_performance_sensitivity.csv", index=False, encoding="utf-8-sig")

    observed = retained.loc[np.isfinite(retained[TARGET]) & np.isfinite(retained[R_COL])].copy()
    if len(observed) != 107:
        raise RuntimeError(f"Expected 107 retained observed-R records; found {len(observed)}.")
    observed[[ROW_ID_COL, "paper_doi", "structure_class", TARGET, R_COL]].to_csv(
        OUT_DIR / "retained_observed_R_record_identifiers.csv", index=False, encoding="utf-8-sig"
    )
    structure_r = group_summary(observed, "structure_class", R_COL, ROBUST_STRUCTURES)
    structure_r = structure_r.rename(columns={
        "count": "n", "mean": "mean_log_R", "median": "median_log_R", "std": "std_log_R",
        "min": "min_log_R", "max": "max_log_R",
    })
    structure_r.to_csv(OUT_DIR / "structure_R_sensitivity.csv", index=False, encoding="utf-8-sig")
    arrays = [observed.loc[observed["structure_class"] == group, R_COL].to_numpy() for group in ROBUST_STRUCTURES]
    statistic, p_value = stats.kruskal(*arrays)
    pd.DataFrame([{
        "comparison": "structure class", "test": "Kruskal-Wallis", "statistic": statistic, "p_value": p_value,
        "groups": "; ".join(ROBUST_STRUCTURES), "n_total": len(observed),
    }]).to_csv(OUT_DIR / "structure_R_statistical_test.csv", index=False, encoding="utf-8-sig")

    common_splits = make_splits(observed[STRATIFY_COL], COMMON_CV_SPLITS)
    common_fingerprint = split_fingerprint(common_splits)
    model_rows = []
    for name, (model, scale_numeric) in make_default_models().items():
        score_a = evaluate_cv(observed, FEATURES_MODEL_A, model, scale_numeric, common_splits)
        score_b = evaluate_cv(observed, FEATURES_MODEL_B, model, scale_numeric, common_splits)
        model_rows.append({
            "model": name, "n_rows": len(observed), "cv_n_splits": COMMON_CV_SPLITS,
            "cv_split_fingerprint": common_fingerprint, "model_A_cv_r2_mean": score_a.mean(),
            "model_A_cv_r2_std": score_a.std(), "model_B_cv_r2_mean": score_b.mean(),
            "model_B_cv_r2_std": score_b.std(), "delta_B_minus_A_mean": (score_b - score_a).mean(),
            "delta_B_minus_A_std": (score_b - score_a).std(),
        })
    model_ab = pd.DataFrame(model_rows)
    model_ab.to_csv(OUT_DIR / "modelA_modelB_sensitivity.csv", index=False, encoding="utf-8-sig")

    from sklearn.ensemble import RandomForestRegressor
    ablation_model = RandomForestRegressor(n_estimators=300, max_depth=10, min_samples_split=2, min_samples_leaf=1, random_state=RANDOM_STATE, n_jobs=-1)
    full_scores = evaluate_cv(observed, FEATURES_MODEL_B, ablation_model, False, common_splits)
    ablation_rows = [{"removed_block": "Full model", "n_rows": len(observed), "cv_n_splits": COMMON_CV_SPLITS, "cv_split_fingerprint": common_fingerprint, "r2_mean": full_scores.mean(), "r2_std": full_scores.std(), "delta_vs_full_model": 0.0}]
    for label, removed in ABLATION_BLOCKS.items():
        scores = evaluate_cv(observed, [f for f in FEATURES_MODEL_B if f not in removed], ablation_model, False, common_splits)
        ablation_rows.append({"removed_block": label, "n_rows": len(observed), "cv_n_splits": COMMON_CV_SPLITS, "cv_split_fingerprint": common_fingerprint, "r2_mean": scores.mean(), "r2_std": scores.std(), "delta_vs_full_model": scores.mean() - full_scores.mean()})
    ablation = pd.DataFrame(ablation_rows)
    ablation.to_csv(OUT_DIR / "feature_block_ablation_sensitivity.csv", index=False, encoding="utf-8-sig")

    shap_model = RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    shap_pipe = build_pipeline(observed, FEATURES_MODEL_B, shap_model, False)
    X_train, X_test, y_train, _ = train_test_split(observed[FEATURES_MODEL_B], observed[TARGET], test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=observed[STRATIFY_COL])
    shap_pipe.fit(X_train, y_train)
    transformed = shap_pipe.named_steps["preprocessor"].transform(X_test)
    names = shap_pipe.named_steps["preprocessor"].get_feature_names_out()
    shap_values = shap.TreeExplainer(shap_pipe.named_steps["model"]).shap_values(transformed)
    shap_df = pd.DataFrame({"descriptor": [display_feature_name(name) for name in names], "encoded_feature": names, "mean_abs_shap": np.mean(np.abs(shap_values), axis=0)}).sort_values("mean_abs_shap", ascending=False, kind="stable").reset_index(drop=True)
    shap_df.insert(0, "rank", np.arange(1, len(shap_df) + 1))
    shap_df["n_rows_observed_R"] = len(observed)
    shap_df["holdout_random_state"] = RANDOM_STATE
    shap_df.to_csv(OUT_DIR / "SHAP_sensitivity.csv", index=False, encoding="utf-8-sig")

    coefficients, descriptor_performance, candidates = explicit_descriptor_analysis(observed)
    coefficients.to_csv(OUT_DIR / "explicit_descriptor_model_sensitivity.csv", index=False, encoding="utf-8-sig")
    descriptor_performance.to_csv(OUT_DIR / "explicit_descriptor_model_performance_sensitivity.csv", index=False, encoding="utf-8-sig")
    candidates.to_csv(OUT_DIR / "virtual_design_sensitivity.csv", index=False, encoding="utf-8-sig")

    baseline_model_ab = pd.read_csv(R1C2_DIR / "modelA_modelB_common112.csv", encoding="utf-8-sig")
    baseline_ablation = pd.read_csv(R1C2_DIR / "feature_block_ablation_common112.csv", encoding="utf-8-sig")
    baseline_shap = pd.read_csv(R1C2_DIR / "shap_importance_common112.csv", encoding="utf-8-sig")
    baseline_r = pd.read_csv(FIG5_DIR / "fig5C_structure_class_summary.csv", encoding="utf-8-sig")
    baseline_descriptor = pd.read_csv(FIG6_DIR / "fig6B_linear_vs_polynomial_model_comparison.csv", encoding="utf-8-sig")
    metadata = {
        "purpose": "Revision-only sensitivity analysis excluding the five sparse hybrid structure records; no production result is overwritten.",
        "canonical_dataset_path": str(DATA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "canonical_dataset_sha256_before_and_after": original_hash,
        "canonical_dataset_modified": False,
        "sparse_categories_excluded_without_merging": SPARSE_CATEGORIES,
        "n_full_dataset": len(dataset), "n_excluded_sparse_hybrid": len(sparse), "n_retained_full_dataset": len(retained),
        "n_observed_R_retained": len(observed),
        "excluded_row_indices": sparse[ROW_ID_COL].astype(int).tolist(),
        "retained_row_index_sha256": hashlib.sha256(",".join(map(str, retained[ROW_ID_COL].astype(int))).encode()).hexdigest(),
        "target": TARGET, "resistance_feature": R_COL,
        "model_A_features": FEATURES_MODEL_A, "model_B_features": FEATURES_MODEL_B,
        "model_A_model_B_validation": "StratifiedShuffleSplit(n_splits=50, test_size=0.2, random_state=42)",
        "model_A_model_B_split_fingerprint": common_fingerprint,
        "ablation_validation": "StratifiedShuffleSplit(n_splits=50, test_size=0.2, random_state=42)",
        "SHAP_method": "RandomForestRegressor(n_estimators=300, random_state=42), stratified 80/20 holdout, TreeExplainer on transformed held-out data",
        "explicit_descriptor_model": "Figure 6 Linear/Polynomial ElasticNetCV pipelines, 80/20 split random_state=42 and shuffled KFold(5, random_state=42); virtual candidates limited to porous, film, hydrogel.",
        "structure_R_test": "Kruskal-Wallis across porous, film, hydrogel; same test family as existing Figure 5 structure comparison.",
        "existing_output_usage_audit": {
            "Fig_2_and_Table_S3": "descriptive category display/counts and structure-performance visualization",
            "Fig_3_Model_A_B_ablation_SHAP_and_Tables_S5_S6": "model learning and inference; structure_class enters Model A/B and ablation, and its one-hot features may enter SHAP",
            "Fig_5_and_Table_S7": "observed-R structure group summary and Kruskal-Wallis statistical inference",
            "Fig_6_and_Table_S8": "explicit descriptor-model learning/coefficients and virtual-design candidate generation",
        },
        "production_comparison_sources": {
            "common112_modelA_modelB": str((R1C2_DIR / "modelA_modelB_common112.csv").relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "common112_ablation": str((R1C2_DIR / "feature_block_ablation_common112.csv").relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "common112_shap": str((R1C2_DIR / "shap_importance_common112.csv").relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "figure5_structure": str((FIG5_DIR / "fig5C_structure_class_summary.csv").relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "figure6_performance": str((FIG6_DIR / "fig6B_linear_vs_polynomial_model_comparison.csv").relative_to(PROJECT_ROOT)).replace("\\", "/"),
        },
        "baseline_rows_loaded": {"modelA_modelB": len(baseline_model_ab), "ablation": len(baseline_ablation), "shap": len(baseline_shap), "structure_R": len(baseline_r), "descriptor_performance": len(baseline_descriptor)},
    }
    (OUT_DIR / "analysis_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved R1C6 sensitivity outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
