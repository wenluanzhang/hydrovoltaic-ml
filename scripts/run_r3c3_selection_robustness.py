"""Reviewer 3, Comment 3: resistance-reporting selection and robustness.

This revision-only script reads the canonical phase-2 CSV and completed R1C2
artifacts. It never modifies the dataset, R1C2, or production Figure 3 files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import shap
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import StratifiedShuffleSplit, cross_validate, train_test_split

from run_r1c2_common112 import (
    FEATURES_MODEL_A,
    FEATURES_MODEL_B,
    R_COL,
    STRATIFY_COL,
    TARGET,
    build_pipeline,
    display_feature_name,
    split_fingerprint,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hydrovoltaic_dataset_phase2_input_utf8.csv"
R1C2_DIR = PROJECT_ROOT / "results" / "revision" / "R1C2"
OUT_DIR = PROJECT_ROOT / "results" / "revision" / "R3C3"

ROW_ID_COL = "canonical_row_index"
R_RAW_COL = "internal_resistance_Mohm"
MASTER_SEED = 20260818
SUBSAMPLE_REPETITIONS = 300
SUBSAMPLE_SIZE = 90  # round(0.80 * 112), selected stratified without replacement
SUBSAMPLE_CV_SPLITS = 5
TEST_SIZE = 0.20
SHAP_REPETITIONS = 50

SELECTION_CATEGORICAL_VARIABLES = [
    "mechanism_simple",
    "structure_class",
    "ion_type",
    "inorganic_electrolyte_present",
    "material_class",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_hash(row_ids: pd.Series | np.ndarray | list[int]) -> str:
    return hashlib.sha256(",".join(map(str, row_ids)).encode("utf-8")).hexdigest()


def validate_canonical_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.copy()
    df[ROW_ID_COL] = df.index.astype(int)
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df[R_COL] = pd.to_numeric(df[R_COL], errors="coerce")
    df[R_RAW_COL] = pd.to_numeric(df[R_RAW_COL], errors="coerce")
    reported = df.loc[
        np.isfinite(df[TARGET]) & np.isfinite(df[R_COL]) & (df[R_RAW_COL] > 0)
    ].copy()
    missing = df.loc[~df[ROW_ID_COL].isin(reported[ROW_ID_COL])].copy()
    if len(df) != 159 or len(reported) != 112 or len(missing) != 47:
        raise RuntimeError(
            f"Expected 159 total / 112 R-reported / 47 R-missing; got "
            f"{len(df)} / {len(reported)} / {len(missing)}."
        )
    if reported[R_COL].isna().any() or reported[R_RAW_COL].isna().any():
        raise RuntimeError("R-reported group unexpectedly contains a missing resistance value.")
    return reported, missing


def cramer_v(table: pd.DataFrame) -> float:
    chi2, _, _, _ = stats.chi2_contingency(table, correction=False)
    n = table.to_numpy().sum()
    if n == 0:
        return np.nan
    phi2 = chi2 / n
    r, k = table.shape
    denominator = min(k - 1, r - 1)
    return float(np.sqrt(phi2 / denominator)) if denominator else np.nan


def categorical_test(df: pd.DataFrame, variable: str) -> dict[str, object]:
    categories = df[variable].astype("string").fillna("Missing")
    table = pd.crosstab(categories, df["resistance_availability"])
    chi2, chi_p, dof, expected = stats.chi2_contingency(table, correction=False)
    sparse_cells = int((expected < 5).sum())
    minimum_expected = float(expected.min())
    result: dict[str, object] = {
        "variable": variable,
        "n": int(table.to_numpy().sum()),
        "n_categories": int(table.shape[0]),
        "test": "Chi-square",
        "statistic": float(chi2),
        "degrees_of_freedom": int(dof),
        "p_value": float(chi_p),
        "effect_size": "Cramer's V",
        "effect_size_value": cramer_v(table),
        "minimum_expected_count": minimum_expected,
        "n_expected_cells_lt_5": sparse_cells,
        "approximation_note": "Chi-square approximation used; no sparse expected cells." if sparse_cells == 0 else (
            "Chi-square approximation retained for an RxC table with sparse expected cells; "
            "Fisher's exact test is not available for general RxC tables in this workflow."
        ),
        "contingency_table_json": json.dumps(table.to_dict(), sort_keys=True),
    }
    if table.shape == (2, 2) and sparse_cells > 0:
        odds_ratio, fisher_p = stats.fisher_exact(table.to_numpy())
        result.update(
            {
                "test": "Fisher's exact",
                "statistic": float(odds_ratio),
                "degrees_of_freedom": np.nan,
                "p_value": float(fisher_p),
                "approximation_note": "Two-by-two sparse table; Fisher's exact test used.",
            }
        )
    return result


def make_subsample(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    splitter = StratifiedShuffleSplit(n_splits=1, train_size=SUBSAMPLE_SIZE, random_state=seed)
    positions = np.arange(len(df))
    train_idx, _ = next(splitter.split(positions, df[STRATIFY_COL]))
    return df.iloc[train_idx].copy()


def make_rep_splits(strata: pd.Series, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    splitter = StratifiedShuffleSplit(
        n_splits=SUBSAMPLE_CV_SPLITS,
        test_size=TEST_SIZE,
        random_state=seed,
    )
    positions = np.arange(len(strata))
    return list(splitter.split(positions, strata))


def evaluate_elastic_net(df: pd.DataFrame, features: list[str], splits: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    model = ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42, max_iter=10000)
    pipe = build_pipeline(df, features, model, scale_numeric=True)
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


def run_delta_r2_subsampling(observed: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for repetition in range(1, SUBSAMPLE_REPETITIONS + 1):
        seed = MASTER_SEED + repetition
        sample = make_subsample(observed, seed)
        splits = make_rep_splits(sample[STRATIFY_COL], seed)
        scores_a = evaluate_elastic_net(sample, FEATURES_MODEL_A, splits)
        scores_b = evaluate_elastic_net(sample, FEATURES_MODEL_B, splits)
        rows.append(
            {
                "repetition": repetition,
                "subsample_seed": seed,
                "n_rows": len(sample),
                "subsample_row_ids_sha256": row_hash(sample[ROW_ID_COL].tolist()),
                "cv_n_splits": SUBSAMPLE_CV_SPLITS,
                "cv_split_fingerprint": split_fingerprint(splits),
                "model_family": "Elastic Net",
                "model_A_r2_mean": scores_a.mean(),
                "model_A_r2_std": scores_a.std(),
                "model_B_r2_mean": scores_b.mean(),
                "model_B_r2_std": scores_b.std(),
                "delta_r2_mean": (scores_b - scores_a).mean(),
                "delta_r2_std": (scores_b - scores_a).std(),
                "all_split_deltas_positive": bool(np.all((scores_b - scores_a) > 0)),
            }
        )
    return pd.DataFrame(rows)


def shap_repeat(sample: pd.DataFrame, seed: int) -> dict[str, object]:
    model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
    pipe = build_pipeline(sample, FEATURES_MODEL_B, model, scale_numeric=False)
    x_train, x_test, y_train, _ = train_test_split(
        sample[FEATURES_MODEL_B],
        sample[TARGET],
        test_size=TEST_SIZE,
        random_state=seed,
        stratify=sample[STRATIFY_COL],
    )
    pipe.fit(x_train, y_train)
    preprocessor = pipe.named_steps["preprocessor"]
    encoded = preprocessor.transform(x_test)
    feature_names = preprocessor.get_feature_names_out()
    values = shap.TreeExplainer(pipe.named_steps["model"]).shap_values(encoded)
    importance = pd.DataFrame(
        {
            "descriptor": [display_feature_name(name) for name in feature_names],
            "mean_abs_shap": np.mean(np.abs(values), axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False, kind="stable").reset_index(drop=True)
    importance["rank"] = np.arange(1, len(importance) + 1)
    log_r = importance.loc[importance["descriptor"] == "log(R)"].iloc[0]
    second = importance.iloc[1]
    return {
        "logR_rank": int(log_r["rank"]),
        "logR_mean_abs_shap": float(log_r["mean_abs_shap"]),
        "second_descriptor": str(second["descriptor"]),
        "second_mean_abs_shap": float(second["mean_abs_shap"]),
        "logR_to_second_ratio": float(log_r["mean_abs_shap"] / second["mean_abs_shap"]),
    }


def run_shap_subsampling(observed: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for repetition in range(1, SHAP_REPETITIONS + 1):
        seed = MASTER_SEED + repetition
        sample = make_subsample(observed, seed)
        row = {
            "repetition": repetition,
            "subsample_seed": seed,
            "n_rows": len(sample),
            "subsample_row_ids_sha256": row_hash(sample[ROW_ID_COL].tolist()),
            "model_family": "Random Forest",
            "n_estimators": 300,
            "holdout_test_size": TEST_SIZE,
            "holdout_random_state": seed,
        }
        row.update(shap_repeat(sample, seed))
        rows.append(row)
    return pd.DataFrame(rows)


def generate_candidate_figure(
    groups: pd.DataFrame,
    power_availability: pd.DataFrame,
    deltas: pd.DataFrame,
    shap_results: pd.DataFrame,
    target_test: pd.DataFrame,
) -> None:
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.linewidth": 1.0,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.dpi": 600,
        }
    )
    colors = {"reported": "#009E73", "missing": "#8C8C8C", "orange": "#D55E00", "black": "#000000"}
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.4))

    ax = axes[0, 0]
    labels = ["R reported\n(n=112)", "R missing\n(n=47)"]
    values = [
        groups.loc[groups["resistance_availability"] == "R reported", TARGET].to_numpy(),
        groups.loc[groups["resistance_availability"] == "R missing", TARGET].to_numpy(),
    ]
    box = ax.boxplot(values, tick_labels=labels, patch_artist=True, widths=0.55, showfliers=False)
    for patch, color in zip(box["boxes"], [colors["reported"], colors["missing"]]):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)
    rng = np.random.default_rng(MASTER_SEED)
    for index, value in enumerate(values, start=1):
        ax.scatter(rng.normal(index, 0.045, len(value)), value, s=10, color=colors["black"], alpha=0.35, linewidths=0)
    p = target_test.loc[0, "p_value"]
    ax.set_ylabel(r"log($P_{est}$)")
    ax.set_title("Target distribution by R availability")
    ax.text(0.03, 0.96, f"Mann–Whitney p = {p:.3g}", transform=ax.transAxes, va="top")

    ax = axes[0, 1]
    ordered = power_availability.set_index("resistance_availability").loc[["R reported", "R missing"]]
    proportions = ordered["reported_power_density_fraction"].to_numpy() * 100
    ax.bar(labels, proportions, color=[colors["reported"], colors["missing"]], edgecolor=colors["black"], linewidth=0.5)
    for i, value in enumerate(proportions):
        ax.text(i, value + 2, f"{value:.1f}%", ha="center", va="bottom")
    ax.set_ylim(0, 110)
    ax.set_ylabel("Reported power density available (%)")
    ax.set_title("Reporting-completeness check")

    ax = axes[1, 0]
    ax.hist(deltas["delta_r2_mean"], bins=18, color=colors["reported"], edgecolor="white")
    ax.axvline(0, linestyle="--", color=colors["black"], linewidth=1)
    ax.axvline(deltas["delta_r2_mean"].median(), color=colors["orange"], linewidth=1.5)
    ax.set_xlabel(r"Subsample $\Delta R^2_{CV}$ (Model B − Model A)")
    ax.set_ylabel("Repetitions")
    ax.set_title("Repeated 80% observed-R subsampling")

    ax = axes[1, 1]
    labels_d = ["log(R) rank 1", "log(R) top 3"]
    values_d = [
        100 * (shap_results["logR_rank"] == 1).mean(),
        100 * (shap_results["logR_rank"] <= 3).mean(),
    ]
    ax.bar(labels_d, values_d, color=[colors["reported"], colors["orange"]], edgecolor=colors["black"], linewidth=0.5)
    for i, value in enumerate(values_d):
        ax.text(i, value + 2, f"{value:.0f}%", ha="center", va="bottom")
    ax.set_ylim(0, 110)
    ax.set_ylabel("SHAP robustness (%)")
    ax.set_title("Repeated SHAP-rank stability")
    ax.tick_params(axis="x", labelsize=7.5)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_color(colors["black"])
            spine.set_linewidth(1.0)
        ax.tick_params(direction="out", width=1.0, length=3)
    fig.subplots_adjust(left=0.12, right=0.985, bottom=0.12, top=0.88, wspace=0.30, hspace=0.55)
    for panel_label, ax in zip("ABCD", axes.flat):
        bounds = ax.get_position()
        fig.text(
            bounds.x0,
            bounds.y1 + 0.045,
            panel_label,
            ha="left",
            va="bottom",
            fontsize=10.5,
            fontweight="bold",
        )
    for suffix, kwargs in (("pdf", {}), ("svg", {}), ("png", {"dpi": 600})):
        fig.savefig(OUT_DIR / f"Fig_S6_R3C3_selection_and_robustness.{suffix}", bbox_inches="tight", pad_inches=0.03, **kwargs)
    plt.close(fig)


def regenerate_candidate_figure_only() -> None:
    """Redraw Fig. S6 from validated saved inputs without rerunning analysis."""
    metadata = json.loads((OUT_DIR / "analysis_metadata.json").read_text(encoding="utf-8"))
    if sha256(DATA_PATH) != metadata["dataset_sha256_after"]:
        raise RuntimeError("Canonical dataset checksum does not match the validated R3C3 figure inputs.")
    dataset = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    reported, missing = validate_canonical_data(dataset)
    groups = pd.concat(
        [
            reported.assign(resistance_availability="R reported"),
            missing.assign(resistance_availability="R missing"),
        ],
        ignore_index=True,
    )
    generate_candidate_figure(
        groups,
        pd.read_csv(OUT_DIR / "reported_power_availability_test.csv", encoding="utf-8-sig"),
        pd.read_csv(OUT_DIR / "subsampling_deltaR2_results.csv", encoding="utf-8-sig"),
        pd.read_csv(OUT_DIR / "subsampling_SHAP_results.csv", encoding="utf-8-sig"),
        pd.read_csv(OUT_DIR / "resistance_availability_target_comparison.csv", encoding="utf-8-sig"),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset_hash_before = sha256(DATA_PATH)
    r1c2_hashes = {
        path.name: sha256(path)
        for path in [
            R1C2_DIR / "modelA_modelB_common112.csv",
            R1C2_DIR / "shap_importance_common112.csv",
            R1C2_DIR / "analysis_metadata.json",
        ]
    }
    dataset = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    reported, missing = validate_canonical_data(dataset)

    groups = pd.concat(
        [
            reported.assign(resistance_availability="R reported"),
            missing.assign(resistance_availability="R missing"),
        ],
        ignore_index=True,
    )
    group_ids = groups[[ROW_ID_COL, "paper_doi", "resistance_availability", R_RAW_COL, R_COL]].sort_values(ROW_ID_COL)
    group_ids.to_csv(OUT_DIR / "resistance_availability_row_ids.csv", index=False, encoding="utf-8-sig")

    target_summary = (
        groups.groupby("resistance_availability", sort=False)[TARGET]
        .agg(n="count", median="median", mean="mean", std="std")
        .reset_index()
    )
    target_summary.to_csv(OUT_DIR / "resistance_availability_group_summary.csv", index=False, encoding="utf-8-sig")
    reported_target = reported[TARGET].to_numpy()
    missing_target = missing[TARGET].to_numpy()
    u_stat, p_value = stats.mannwhitneyu(reported_target, missing_target, alternative="two-sided", method="auto")
    rank_biserial = (2 * u_stat / (len(reported_target) * len(missing_target))) - 1
    target_test = pd.DataFrame(
        [
            {
                "variable": TARGET,
                "R_reported_n": len(reported_target),
                "R_missing_n": len(missing_target),
                "test": "Mann-Whitney U (two-sided)",
                "statistic": u_stat,
                "p_value": p_value,
                "effect_size": "rank-biserial correlation (R reported minus R missing)",
                "effect_size_value": rank_biserial,
            }
        ]
    )
    target_test.to_csv(OUT_DIR / "resistance_availability_target_comparison.csv", index=False, encoding="utf-8-sig")

    categorical_rows = [categorical_test(groups, variable) for variable in SELECTION_CATEGORICAL_VARIABLES]
    categorical_tests = pd.DataFrame(categorical_rows)
    categorical_tests.to_csv(OUT_DIR / "resistance_availability_categorical_tests.csv", index=False, encoding="utf-8-sig")

    groups["reported_power_density_available"] = pd.to_numeric(groups["power_density_uW_cm2"], errors="coerce").gt(0)
    availability_table = pd.crosstab(groups["reported_power_density_available"], groups["resistance_availability"])
    availability_test = categorical_test(groups, "reported_power_density_available")
    power_availability = (
        groups.groupby("resistance_availability", sort=False)["reported_power_density_available"]
        .agg(group_n="count", reported_power_density_n="sum", reported_power_density_fraction="mean")
        .reset_index()
    )
    availability_details = pd.DataFrame([availability_test]).rename(columns={"n": "test_total_n"})
    reported_power_test = power_availability.merge(
        availability_details.drop(columns=["contingency_table_json"]), how="cross"
    )
    reported_power_test["contingency_table_json"] = json.dumps(availability_table.to_dict(), sort_keys=True)
    reported_power_test.to_csv(OUT_DIR / "reported_power_availability_test.csv", index=False, encoding="utf-8-sig")

    deltas = run_delta_r2_subsampling(reported)
    deltas.to_csv(OUT_DIR / "subsampling_deltaR2_results.csv", index=False, encoding="utf-8-sig")
    delta_summary = pd.DataFrame(
        [
            {
                "n_repetitions": len(deltas),
                "subsample_n": SUBSAMPLE_SIZE,
                "model_family": "Elastic Net",
                "delta_r2_median": deltas["delta_r2_mean"].median(),
                "delta_r2_mean": deltas["delta_r2_mean"].mean(),
                "delta_r2_iqr": deltas["delta_r2_mean"].quantile(0.75) - deltas["delta_r2_mean"].quantile(0.25),
                "delta_r2_p05": deltas["delta_r2_mean"].quantile(0.05),
                "delta_r2_p95": deltas["delta_r2_mean"].quantile(0.95),
                "fraction_delta_r2_gt_0": (deltas["delta_r2_mean"] > 0).mean(),
                "fraction_all_cv_split_deltas_gt_0": deltas["all_split_deltas_positive"].mean(),
            }
        ]
    )
    delta_summary.to_csv(OUT_DIR / "subsampling_deltaR2_summary.csv", index=False, encoding="utf-8-sig")

    shap_results = run_shap_subsampling(reported)
    shap_results.to_csv(OUT_DIR / "subsampling_SHAP_results.csv", index=False, encoding="utf-8-sig")
    shap_summary = pd.DataFrame(
        [
            {
                "n_repetitions": len(shap_results),
                "subsample_n": SUBSAMPLE_SIZE,
                "model_family": "Random Forest",
                "fraction_logR_rank_1": (shap_results["logR_rank"] == 1).mean(),
                "fraction_logR_top_3": (shap_results["logR_rank"] <= 3).mean(),
                "logR_mean_abs_shap_median": shap_results["logR_mean_abs_shap"].median(),
                "logR_mean_abs_shap_iqr": shap_results["logR_mean_abs_shap"].quantile(0.75) - shap_results["logR_mean_abs_shap"].quantile(0.25),
                "logR_mean_abs_shap_p05": shap_results["logR_mean_abs_shap"].quantile(0.05),
                "logR_mean_abs_shap_p95": shap_results["logR_mean_abs_shap"].quantile(0.95),
                "logR_to_second_ratio_median": shap_results["logR_to_second_ratio"].median(),
                "logR_to_second_ratio_iqr": shap_results["logR_to_second_ratio"].quantile(0.75) - shap_results["logR_to_second_ratio"].quantile(0.25),
            }
        ]
    )
    shap_summary.to_csv(OUT_DIR / "subsampling_SHAP_summary.csv", index=False, encoding="utf-8-sig")

    generate_candidate_figure(groups, reported_power_test, deltas, shap_results, target_test)
    dataset_hash_after = sha256(DATA_PATH)
    if dataset_hash_before != dataset_hash_after:
        raise RuntimeError("Canonical dataset checksum changed during R3C3 analysis.")
    metadata = {
        "dataset_path": str(DATA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "dataset_sha256_before": dataset_hash_before,
        "dataset_sha256_after": dataset_hash_after,
        "n_total": len(dataset),
        "n_R_reported": len(reported),
        "n_R_missing": len(missing),
        "group_row_id_method": "zero-based canonical CSV row index stored in resistance_availability_row_ids.csv",
        "R_reported_row_ids_sha256": row_hash(reported[ROW_ID_COL].tolist()),
        "R_missing_row_ids_sha256": row_hash(missing[ROW_ID_COL].tolist()),
        "resistance_imputation": "none",
        "selection_variables": [TARGET, *SELECTION_CATEGORICAL_VARIABLES, "reported_power_density_available"],
        "target_test": "Mann-Whitney U (two-sided), with rank-biserial correlation",
        "categorical_test_policy": "Fisher's exact for sparse 2x2 tables; chi-square otherwise, with sparse RxC approximation flags recorded.",
        "reporting_completeness": "reported_power_density_available only; no arbitrary global reporting-quality score was constructed.",
        "subsampling": {
            "master_seed": MASTER_SEED,
            "repetitions": SUBSAMPLE_REPETITIONS,
            "subsample_size": SUBSAMPLE_SIZE,
            "sampling": "StratifiedShuffleSplit train_size=90, stratified by mechanism_simple, without replacement",
            "model_family": "Elastic Net from validated R1C2 Model A/B comparison",
            "model_settings": "ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42, max_iter=10000)",
            "descriptor_sets": "Validated R1C2 Model A and Model B; Model B adds observed log(R) only.",
            "validation": "5 StratifiedShuffleSplit 80/20 folds per repetition; Model A and Model B use identical folds within each repetition.",
        },
        "shap_robustness": {
            "repetitions": SHAP_REPETITIONS,
            "model_family": "Random Forest",
            "method": "Validated R1C2 SHAP method: RandomForestRegressor(n_estimators=300), stratified 80/20 holdout, TreeExplainer on transformed held-out predictors.",
        },
        "R1C2_read_only_hashes": r1c2_hashes,
        "candidate_figure": "Fig_S6_R3C3_selection_and_robustness.pdf/svg/png",
    }
    (OUT_DIR / "analysis_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"R-reported={len(reported)}, R-missing={len(missing)}, total={len(dataset)}")
    print(f"Delta R2 median={delta_summary.loc[0, 'delta_r2_median']:.6f}")
    print(f"SHAP rank-1 fraction={shap_summary.loc[0, 'fraction_logR_rank_1']:.3f}")
    print(f"Outputs: {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--figure-only",
        action="store_true",
        help="Redraw the candidate figure from validated saved results without rerunning analysis.",
    )
    args = parser.parse_args()
    if args.figure_only:
        regenerate_candidate_figure_only()
    else:
        main()
