"""Reviewer 1 Comment 2: common observed-resistance subset analysis.

This standalone revision script preserves the submitted Figure 3 outputs and
writes all common-subset results to results/revision/R1C2/.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.metrics import r2_score
from sklearn.model_selection import StratifiedShuffleSplit, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hydrovoltaic_dataset_phase2_input_utf8.csv"
HISTORICAL_FIG3_DIR = PROJECT_ROOT / "results" / "figure3_model_comparison"
OUT_DIR = PROJECT_ROOT / "results" / "revision" / "R1C2"
FIGURE_DIR = OUT_DIR / "figures"

TARGET = "log_estimated_power_density"
R_COL = "log_internal_resistance_Mohm"
STRATIFY_COL = "mechanism_simple"
ROW_ID_COL = "canonical_row_index"
RANDOM_STATE = 42
TEST_SIZE = 0.20
COMMON_CV_SPLITS = 50
FIG3A_CV_SPLITS = 30

# Submitted Model A descriptors from notebooks/04_modeling_phase2_models.ipynb.
FEATURES_MODEL_A = [
    "material_class",
    "structure_class",
    "built_in_asymmetry",
    "inorganic_electrolyte_present",
    "polyelectrolyte_present",
    "has_anionic",
    "has_cationic",
    "has_zwitterionic",
    "mechanism_simple",
    "water_interaction_mode",
    "top_electrode",
    "bottom_electrode",
    "electrode_symmetry",
    "metal_electrode",
    "ionic_groups",
    "ion_type",
]

# In the submitted all-159 analysis, Model B added R and its missingness flag.
# Within the required observed-R subset, that flag is identically 1, so it is
# deliberately omitted: Model B differs from Model A by log(R) only.
FEATURES_MODEL_B = FEATURES_MODEL_A + [R_COL]

ABLATION_BLOCKS = {
    "Internal resistance": [R_COL],
    "Structure": ["structure_class"],
    "Ion type": ["ion_type"],
    "Material class": ["material_class"],
    "Mechanism labels": ["mechanism_simple"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_onehot_encoder() -> OneHotEncoder:
    """Use the current scikit-learn spelling while retaining a clear fallback."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # pragma: no cover - for older local environments
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def split_feature_types(df: pd.DataFrame, features: list[str]) -> tuple[list[str], list[str]]:
    categorical, numeric = [], []
    for feature in features:
        if pd.api.types.is_numeric_dtype(df[feature]):
            numeric.append(feature)
        else:
            categorical.append(feature)
    return categorical, numeric


def build_preprocessor(df: pd.DataFrame, features: list[str], scale_numeric: bool) -> ColumnTransformer:
    """Match submitted preprocessing while explicitly never imputing log(R)."""
    categorical, numeric = split_feature_types(df, features)
    other_numeric = [feature for feature in numeric if feature != R_COL]
    transformers: list[tuple[str, object, list[str]]] = []

    if categorical:
        transformers.append(
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", make_onehot_encoder()),
                    ]
                ),
                categorical,
            )
        )
    if other_numeric:
        numeric_steps: list[tuple[str, object]] = [("imputer", SimpleImputer(strategy="median"))]
        if scale_numeric:
            numeric_steps.append(("scaler", StandardScaler()))
        transformers.append(("num", Pipeline(steps=numeric_steps), other_numeric))
    if R_COL in features:
        # Observed-R filtering above guarantees this branch receives no missing R.
        resistance_transformer: object = StandardScaler() if scale_numeric else "passthrough"
        transformers.append(("resistance", resistance_transformer, [R_COL]))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_pipeline(df: pd.DataFrame, features: list[str], model: object, scale_numeric: bool) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(df, features, scale_numeric)),
            ("model", clone(model)),
        ]
    )


def split_fingerprint(splits: list[tuple[np.ndarray, np.ndarray]]) -> str:
    payload = "|".join(
        f"{','.join(map(str, train))}:{','.join(map(str, test))}" for train, test in splits
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_splits(strata: pd.Series, n_splits: int) -> list[tuple[np.ndarray, np.ndarray]]:
    splitter = StratifiedShuffleSplit(
        n_splits=n_splits,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )
    positions = np.arange(len(strata))
    return list(splitter.split(positions, strata))


def evaluate_cv(
    df: pd.DataFrame,
    features: list[str],
    model: object,
    scale_numeric: bool,
    splits: list[tuple[np.ndarray, np.ndarray]],
) -> np.ndarray:
    pipe = build_pipeline(df, features, model, scale_numeric)
    scores = cross_validate(
        pipe,
        df[features],
        df[TARGET],
        cv=splits,
        scoring="r2",
        n_jobs=1,
        return_train_score=False,
    )
    return scores["test_score"]


def display_feature_name(encoded_name: str) -> str:
    if encoded_name == f"resistance__{R_COL}":
        return "log(R)"
    if encoded_name.startswith("cat__"):
        name = encoded_name.removeprefix("cat__")
        replacements = {
            "ion_type_other_cation": "Other cation",
            "ion_type_proton": "Proton",
            "ion_type_anion": "Anion",
            "inorganic_electrolyte_present_1": "Inorganic electrolyte",
            "structure_class_porous": "Porous structure",
            "structure_class_film": "Film structure",
            "mechanism_simple_ion_gradient": "Ion-gradient label",
            "mechanism_simple_streaming": "Streaming label",
        }
        return replacements.get(name, name.replace("_", " ").title())
    return encoded_name.removeprefix("num__").replace("_", " ").title()


def make_default_models() -> dict[str, tuple[object, bool]]:
    return {
        "Elastic Net": (ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=RANDOM_STATE, max_iter=10000), True),
        "SVR": (SVR(kernel="rbf", C=10, epsilon=0.1), True),
        "Random Forest": (
            RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1),
            False,
        ),
        "XGBoost": (
            XGBRegressor(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                objective="reg:squarederror",
            ),
            False,
        ),
    }


def make_tuned_models() -> dict[str, tuple[object, bool]]:
    """Submitted Figure 3A settings saved in phase2_tuned_best_params.json."""
    return {
        "Elastic Net": (ElasticNet(alpha=0.1, l1_ratio=0.8, random_state=RANDOM_STATE, max_iter=10000), True),
        "SVR": (SVR(kernel="rbf", C=1, epsilon=0.01), True),
        "Random Forest": (
            RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=1,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            False,
        ),
        "XGBoost": (
            XGBRegressor(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.03,
                subsample=1.0,
                colsample_bytree=1.0,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                objective="reg:squarederror",
            ),
            False,
        ),
    }


def set_figure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.linewidth": 1.0,
            "axes.labelsize": 9.5,
            "axes.titlesize": 10,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 7.8,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.dpi": 600,
            "figure.dpi": 150,
            "axes.grid": False,
        }
    )


def format_axis(ax: plt.Axes) -> None:
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
        spine.set_color("#000000")
    ax.tick_params(direction="out", width=1.0, length=4, color="#000000", top=False, right=False)


def save_figure(fig: plt.Figure, stem: str) -> None:
    for extension, kwargs in (("pdf", {}), ("svg", {}), ("png", {"dpi": 600})):
        fig.savefig(FIGURE_DIR / f"{stem}.{extension}", bbox_inches="tight", pad_inches=0.03, **kwargs)
    plt.close(fig)


def generate_revision_panels(model_ab: pd.DataFrame, family: pd.DataFrame, ablation: pd.DataFrame, shap_df: pd.DataFrame) -> None:
    """Create revision copies of scientifically affected Fig. 3 panels from CSV data."""
    set_figure_style()
    colors = {"black": "#000000", "gray": "#8C8C8C", "light_gray": "#D0D0D0", "green": "#009E73", "red": "#D55E00"}

    fig, ax = plt.subplots(figsize=(3.35, 2.65))
    order = ["Elastic Net", "SVR", "Random Forest", "XGBoost"]
    data = family.set_index("model").loc[order].reset_index()
    x = np.arange(len(data))
    ax.errorbar(x, data["cv_r2_mean"], yerr=data["cv_r2_std"], fmt="o", color=colors["black"], ecolor=colors["gray"], elinewidth=1.0, capsize=3, markersize=4.5)
    ax.axhline(0, linestyle="--", linewidth=1.0, color=colors["light_gray"])
    ax.set_xticks(x)
    ax.set_xticklabels(data["model"], rotation=25, ha="right")
    ax.set_ylabel(r"$R^2_{\mathrm{CV}}$")
    ax.set_title("Tuned model-family comparison")
    format_axis(ax)
    plt.tight_layout()
    save_figure(fig, "fig3A_common112_tuned_model_comparison")

    fig, ax = plt.subplots(figsize=(3.65, 2.65))
    data = model_ab.set_index("model").loc[["Elastic Net", "Random Forest", "XGBoost", "SVR"]].reset_index()
    y = np.arange(len(data))
    for i, row in enumerate(data.itertuples()):
        ax.hlines(i, row.model_A_cv_r2_mean, row.model_B_cv_r2_mean, linewidth=1.4, color=colors["gray"])
        ax.plot(row.model_A_cv_r2_mean, i, "o", markersize=4.5, color="#BDBDBD", markeredgecolor=colors["black"], markeredgewidth=0.4)
        ax.plot(row.model_B_cv_r2_mean, i, "o", markersize=4.8, color=colors["green"], markeredgecolor=colors["black"], markeredgewidth=0.4)
    ax.axvline(0, linestyle="--", linewidth=1.0, color=colors["light_gray"])
    ax.set_yticks(y)
    ax.set_yticklabels(data["model"])
    ax.set_xlabel(r"$R^2_{\mathrm{CV}}$")
    ax.set_title(r"Descriptor augmentation on common $n=112$")
    format_axis(ax)
    plt.tight_layout()
    save_figure(fig, "fig3B_common112_descriptor_augmentation")

    fig, ax = plt.subplots(figsize=(3.65, 2.65))
    data = ablation[ablation["removed_block"] != "Full model"].sort_values("delta_vs_full_model")
    y = np.arange(len(data))
    colors_ablation = [colors["red"] if value < 0 else colors["gray"] for value in data["delta_vs_full_model"]]
    ax.barh(y, data["delta_vs_full_model"], color=colors_ablation, edgecolor=colors["black"], linewidth=0.4)
    ax.axvline(0, linestyle="--", linewidth=1.0, color=colors["light_gray"])
    ax.set_yticks(y)
    ax.set_yticklabels(data["removed_block"])
    ax.set_xlabel(r"$\Delta R^2_{\mathrm{CV}}$ vs full model")
    ax.set_title(r"Feature-block ablation on common $n=112$")
    format_axis(ax)
    plt.tight_layout()
    save_figure(fig, "fig3C_common112_feature_block_ablation")

    fig, ax = plt.subplots(figsize=(3.95, 3.05))
    data = (
        shap_df.nlargest(10, "mean_abs_shap")
        .sort_values("mean_abs_shap", ascending=True)
    )
    y = np.arange(len(data))
    for i, row in enumerate(data.itertuples()):
        color = colors["green"] if row.descriptor == "log(R)" else colors["gray"]
        ax.hlines(i, 0, row.mean_abs_shap, linewidth=1.9 if row.descriptor == "log(R)" else 1.15, color=color)
        ax.plot(row.mean_abs_shap, i, "o", markersize=5.2 if row.descriptor == "log(R)" else 4.0, color=color)
    ax.set_yticks(y)
    ax.set_yticklabels(data["descriptor"])
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title(r"SHAP descriptor importance (common $n=112$)")
    format_axis(ax)
    plt.tight_layout()
    save_figure(fig, "fig3D_common112_SHAP_descriptor_importance")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    dataset = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    dataset[ROW_ID_COL] = dataset.index.astype(int)
    dataset[TARGET] = pd.to_numeric(dataset[TARGET], errors="coerce")
    dataset[R_COL] = pd.to_numeric(dataset[R_COL], errors="coerce")
    observed = dataset.loc[np.isfinite(dataset[TARGET]) & np.isfinite(dataset[R_COL])].copy()
    if len(observed) != 112:
        raise RuntimeError(f"Expected 112 observed-resistance records; found {len(observed)}.")
    if observed[R_COL].isna().any():
        raise RuntimeError("Observed-resistance subset unexpectedly contains missing log(R).")
    if observed["has_internal_resistance"].nunique(dropna=False) != 1 or observed["has_internal_resistance"].iloc[0] != 1:
        raise RuntimeError("The internal-resistance availability flag is not constant in the observed subset.")

    missing_non_r = observed[FEATURES_MODEL_A].isna().sum()
    subset_summary = observed[[ROW_ID_COL, "paper_doi", STRATIFY_COL, TARGET, R_COL]].copy()
    subset_summary["has_missing_nonresistance_descriptor"] = observed[FEATURES_MODEL_A].isna().any(axis=1).to_numpy()
    subset_summary.to_csv(OUT_DIR / "subset_summary.csv", index=False, encoding="utf-8-sig")

    common_splits = make_splits(observed[STRATIFY_COL], COMMON_CV_SPLITS)
    common_split_hash = split_fingerprint(common_splits)
    default_models = make_default_models()
    model_ab_rows = []
    cv_scores_for_ab: dict[str, dict[str, np.ndarray]] = {}
    for name, (model, scale_numeric) in default_models.items():
        scores_a = evaluate_cv(observed, FEATURES_MODEL_A, model, scale_numeric, common_splits)
        scores_b = evaluate_cv(observed, FEATURES_MODEL_B, model, scale_numeric, common_splits)
        cv_scores_for_ab[name] = {"A": scores_a, "B": scores_b}
        split_table = pd.DataFrame({"split": np.arange(1, len(scores_a) + 1), "model_A_r2": scores_a, "model_B_r2": scores_b, "delta_B_minus_A": scores_b - scores_a})
        split_table.to_csv(OUT_DIR / f"modelA_modelB_common112_{name.lower().replace(' ', '_')}_splits.csv", index=False, encoding="utf-8-sig")
        model_ab_rows.append(
            {
                "model": name,
                "n_rows": len(observed),
                "cv_n_splits": COMMON_CV_SPLITS,
                "cv_split_fingerprint": common_split_hash,
                "model_A_cv_r2_mean": scores_a.mean(),
                "model_A_cv_r2_std": scores_a.std(),
                "model_B_cv_r2_mean": scores_b.mean(),
                "model_B_cv_r2_std": scores_b.std(),
                "delta_B_minus_A_mean": (scores_b - scores_a).mean(),
                "delta_B_minus_A_std": (scores_b - scores_a).std(),
            }
        )
    model_ab = pd.DataFrame(model_ab_rows)
    model_ab.to_csv(OUT_DIR / "modelA_modelB_common112.csv", index=False, encoding="utf-8-sig")

    # Fig. 3A was based on tuned Model B, so it requires a common-112 replacement.
    fig3a_splits = make_splits(observed[STRATIFY_COL], FIG3A_CV_SPLITS)
    family_rows = []
    for name, (model, scale_numeric) in make_tuned_models().items():
        scores = evaluate_cv(observed, FEATURES_MODEL_B, model, scale_numeric, fig3a_splits)
        family_rows.append(
            {
                "model": name,
                "descriptor_set": "Model_B_common112_observed_R",
                "n_rows": len(observed),
                "cv_n_splits": FIG3A_CV_SPLITS,
                "cv_split_fingerprint": split_fingerprint(fig3a_splits),
                "cv_r2_mean": scores.mean(),
                "cv_r2_std": scores.std(),
            }
        )
    family = pd.DataFrame(family_rows)
    family.to_csv(OUT_DIR / "model_family_common112.csv", index=False, encoding="utf-8-sig")

    # Submitted Fig. 3C used this separate 300-tree RF robustness configuration.
    ablation_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    full_scores = evaluate_cv(observed, FEATURES_MODEL_B, ablation_model, False, common_splits)
    ablation_rows = [
        {
            "removed_block": "Full model",
            "n_rows": len(observed),
            "cv_n_splits": COMMON_CV_SPLITS,
            "cv_split_fingerprint": common_split_hash,
            "r2_mean": full_scores.mean(),
            "r2_std": full_scores.std(),
            "delta_vs_full_model": 0.0,
        }
    ]
    for label, dropped_features in ABLATION_BLOCKS.items():
        features = [feature for feature in FEATURES_MODEL_B if feature not in dropped_features]
        scores = evaluate_cv(observed, features, ablation_model, False, common_splits)
        ablation_rows.append(
            {
                "removed_block": label,
                "n_rows": len(observed),
                "cv_n_splits": COMMON_CV_SPLITS,
                "cv_split_fingerprint": common_split_hash,
                "r2_mean": scores.mean(),
                "r2_std": scores.std(),
                "delta_vs_full_model": scores.mean() - full_scores.mean(),
            }
        )
    ablation = pd.DataFrame(ablation_rows)
    ablation.to_csv(OUT_DIR / "feature_block_ablation_common112.csv", index=False, encoding="utf-8-sig")

    # Submitted Fig. 3D methodology: Model-B default RF, stratified 80/20 holdout,
    # TreeExplainer on the transformed held-out predictor matrix.
    shap_model = RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    shap_pipe = build_pipeline(observed, FEATURES_MODEL_B, shap_model, False)
    X_train, X_test, y_train, _ = train_test_split(
        observed[FEATURES_MODEL_B],
        observed[TARGET],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=observed[STRATIFY_COL],
    )
    shap_pipe.fit(X_train, y_train)
    shap_preprocessor = shap_pipe.named_steps["preprocessor"]
    X_test_encoded = shap_preprocessor.transform(X_test)
    feature_names = shap_preprocessor.get_feature_names_out()
    shap_values = shap.TreeExplainer(shap_pipe.named_steps["model"]).shap_values(X_test_encoded)
    shap_importance = pd.DataFrame(
        {
            "descriptor": [display_feature_name(name) for name in feature_names],
            "encoded_feature": feature_names,
            "mean_abs_shap": np.mean(np.abs(shap_values), axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False, kind="stable").reset_index(drop=True)
    shap_importance.insert(0, "rank", np.arange(1, len(shap_importance) + 1))
    shap_importance["n_rows_observed_R"] = len(observed)
    shap_importance["holdout_random_state"] = RANDOM_STATE
    shap_importance.to_csv(OUT_DIR / "shap_importance_common112.csv", index=False, encoding="utf-8-sig")

    submitted_ab = pd.read_csv(HISTORICAL_FIG3_DIR / "fig3B_modelA_modelB_descriptor_augmentation.csv", encoding="utf-8-sig")
    submitted_family = pd.read_csv(HISTORICAL_FIG3_DIR / "fig3A_tuned_model_comparison.csv", encoding="utf-8-sig")
    submitted_ablation = pd.read_csv(HISTORICAL_FIG3_DIR / "fig3C_feature_block_ablation.csv", encoding="utf-8-sig")
    comparison = model_ab.merge(submitted_ab, on="model", how="left", suffixes=("_common112", "_submitted159"))
    comparison.to_csv(OUT_DIR / "submitted_vs_common112_modelA_modelB.csv", index=False, encoding="utf-8-sig")
    family.compare(submitted_family, keep_shape=True, keep_equal=False) if False else None
    pd.DataFrame(
        {
            "model": family["model"],
            "common112_cv_r2_mean": family["cv_r2_mean"],
            "common112_cv_r2_std": family["cv_r2_std"],
            "submitted159_cv_r2_mean": submitted_family.set_index("model").loc[family["model"], "cv_r2_mean"].to_numpy(),
            "submitted159_cv_r2_std": submitted_family.set_index("model").loc[family["model"], "cv_r2_std"].to_numpy(),
        }
    ).to_csv(OUT_DIR / "submitted_vs_common112_model_family.csv", index=False, encoding="utf-8-sig")
    ablation_compare = ablation.merge(submitted_ablation[["removed_block", "r2_mean", "r2_std", "delta_vs_baseline"]], on="removed_block", how="left", suffixes=("_common112", "_submitted159"))
    ablation_compare.to_csv(OUT_DIR / "submitted_vs_common112_ablation.csv", index=False, encoding="utf-8-sig")

    metadata = {
        "dataset_path": str(DATA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "dataset_sha256": sha256(DATA_PATH),
        "n_observed_resistance": int(len(observed)),
        "row_identification_method": "zero-based canonical CSV row index stored as canonical_row_index; paper_doi retained for source-study traceability",
        "row_index_sha256": hashlib.sha256(",".join(map(str, observed[ROW_ID_COL].tolist())).encode("utf-8")).hexdigest(),
        "target": TARGET,
        "resistance_feature": R_COL,
        "model_A_features": FEATURES_MODEL_A,
        "model_B_features": FEATURES_MODEL_B,
        "submitted_missingness_indicator": "has_internal_resistance omitted from common-112 Model B because it is constant 1 for all selected records; Model B therefore adds log(R) only.",
        "random_seed": RANDOM_STATE,
        "model_A_model_B_validation": f"StratifiedShuffleSplit(n_splits={COMMON_CV_SPLITS}, test_size={TEST_SIZE}, random_state={RANDOM_STATE})",
        "model_A_model_B_split_fingerprint": common_split_hash,
        "Fig3A_validation": f"StratifiedShuffleSplit(n_splits={FIG3A_CV_SPLITS}, test_size={TEST_SIZE}, random_state={RANDOM_STATE})",
        "ablation_validation": f"StratifiedShuffleSplit(n_splits={COMMON_CV_SPLITS}, test_size={TEST_SIZE}, random_state={RANDOM_STATE})",
        "SHAP_method": "RandomForestRegressor(n_estimators=300, random_state=42), stratified 80/20 holdout, shap.TreeExplainer on transformed held-out data",
        "missing_value_handling": {
            "internal_resistance": "No imputation. Rows without valid log_internal_resistance_Mohm are excluded before all analyses.",
            "other_numeric_descriptors": "SimpleImputer(strategy='median') within each training fold, matching submitted preprocessing.",
            "categorical_descriptors": "SimpleImputer(strategy='most_frequent') plus OneHotEncoder(handle_unknown='ignore') within each training fold, matching submitted preprocessing.",
            "observed_nonresistance_missing_counts": {key: int(value) for key, value in missing_non_r.items() if int(value) > 0},
        },
        "model_settings": {
            "Model_A_Model_B_default": "ElasticNet(alpha=0.1,l1_ratio=0.5); SVR(rbf,C=10,epsilon=0.1); RF(n_estimators=300); XGB(n_estimators=300,max_depth=4,learning_rate=0.05,subsample=0.8,colsample_bytree=0.8)",
            "Fig3A_tuned": "ElasticNet(alpha=0.1,l1_ratio=0.8); SVR(rbf,C=1,epsilon=0.01); RF(n_estimators=100,max_depth=5,min_samples_split=5,min_samples_leaf=1); XGB(n_estimators=100,max_depth=3,learning_rate=0.03,subsample=1.0,colsample_bytree=1.0)",
            "Ablation": "RandomForestRegressor(n_estimators=300,max_depth=10,min_samples_split=2,min_samples_leaf=1,random_state=42)",
        },
        "Fig3A_requires_revision": True,
        "Fig3A_reason": "Submitted Fig. 3A is a tuned Model-B comparison and therefore includes log(R) with all-159 preprocessing-based imputation; common-112 results are required for a resistance-importance argument.",
        "submitted_reference_files": [
            "results/figure3_model_comparison/fig3A_tuned_model_comparison.csv",
            "results/figure3_model_comparison/fig3B_modelA_modelB_descriptor_augmentation.csv",
            "results/figure3_model_comparison/fig3C_feature_block_ablation.csv",
            "results/figure3_model_comparison/fig3D_SHAP_descriptor_importance.csv",
        ],
        "SI_entries_requiring_update_if_adopted": {
            "Table_S4": "All four Fig. 3A model-family CV R2 mean/std entries, because Fig. 3A is Model B and now uses n=112 observed-R records.",
            "Table_S5A": "All four Model A vs Model B CV R2 and Delta entries.",
            "Table_S5B": "Full model and all five feature-block ablation entries.",
            "Table_S6": "Full SHAP descriptor ranking and the log(R)-to-second-feature ratio derived from it.",
        },
    }
    (OUT_DIR / "analysis_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    generate_revision_panels(model_ab, family, ablation, shap_importance)

    log_r = shap_importance.loc[shap_importance["descriptor"] == "log(R)"].iloc[0]
    second = shap_importance.iloc[1]
    print(f"Observed-resistance subset: n={len(observed)}")
    print(f"log(R): rank {int(log_r['rank'])}, mean |SHAP|={log_r['mean_abs_shap']:.6f}")
    print(f"Second-ranked: {second['descriptor']}, mean |SHAP|={second['mean_abs_shap']:.6f}")
    print(f"SHAP ratio: {log_r['mean_abs_shap'] / second['mean_abs_shap']:.6f}")
    print(f"Revision outputs: {OUT_DIR}")


if __name__ == "__main__":
    main()
