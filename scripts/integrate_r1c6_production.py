"""Integrate validated R1C6 outputs into the affected production CSV sources.

The script deliberately does not touch the canonical dataset, Figure 3, Tables
S4-S6, Figure 4, or any unrelated production artifact.  Plot/table notebooks
consume the CSVs written here to preserve their established visual style.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
R1C6 = ROOT / "results" / "revision" / "R1C6"
FIG5 = ROOT / "results" / "figure5_R_origin"
FIG6 = ROOT / "results" / "figure6_virtual_design"

ROBUST_CLEAN = {"porous", "film", "hydrogel"}


def coefficient_label(feature: str) -> str:
    label = feature.replace("num__", "").replace("cat__", "")
    label = label.replace("log_R", "log(R)")
    label = label.replace("inorganic_electrolyte_present_clean", "Inorganic electrolyte")
    label = label.replace("structure_clean_", "Structure: ")
    label = label.replace("ion_type_clean_", "Ion: ")
    label = label.replace("mechanism_clean_", "Mechanism: ")
    return label.replace("_", " ")


def main() -> None:
    structure_r = pd.read_csv(R1C6 / "structure_R_sensitivity.csv", encoding="utf-8-sig")
    fig5c = structure_r.rename(
        columns={
            "structure_class": "structure_class_clean",
            "n": "count",
            "mean_log_R": "mean",
            "median_log_R": "median",
            "std_log_R": "std",
            "min_log_R": "min",
            "max_log_R": "max",
        }
    )[["structure_class_clean", "count", "mean", "median", "std", "min", "max"]]
    if set(fig5c["structure_class_clean"]) != ROBUST_CLEAN:
        raise ValueError("R1C6 Figure 5C source does not contain exactly the robust structures.")
    fig5c.to_csv(FIG5 / "fig5C_structure_class_summary.csv", index=False, encoding="utf-8-sig")

    tests = pd.read_csv(FIG5 / "fig5_statistical_tests.csv", encoding="utf-8-sig")
    robust_test = pd.read_csv(R1C6 / "structure_R_statistical_test.csv", encoding="utf-8-sig").iloc[0]
    tests = tests.loc[tests["panel"] != "Fig5C"].copy()
    tests = pd.concat(
        [
            tests,
            pd.DataFrame(
                [
                    {
                        "panel": "Fig5C",
                        "comparison": "structure class",
                        "test": robust_test["test"],
                        "statistic": robust_test["statistic"],
                        "p_value": robust_test["p_value"],
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    tests.to_csv(FIG5 / "fig5_statistical_tests.csv", index=False, encoding="utf-8-sig")

    coefficients = pd.read_csv(R1C6 / "explicit_descriptor_model_sensitivity.csv", encoding="utf-8-sig")
    if coefficients["feature"].str.contains("hydrogel_+", regex=False).any():
        raise ValueError("Sparse hybrid coefficient present in validated R1C6 source.")
    coefficients.to_csv(FIG6 / "fig6A_linear_descriptor_coefficients_raw.csv", index=False, encoding="utf-8-sig")
    coefficient_plot = coefficients.loc[coefficients["abs_coefficient"] > 1e-8].copy()
    coefficient_plot["label"] = coefficient_plot["feature"].map(coefficient_label)
    coefficient_plot.to_csv(FIG6 / "fig6A_linear_descriptor_coefficients_plot.csv", index=False, encoding="utf-8-sig")

    model_performance = pd.read_csv(R1C6 / "explicit_descriptor_model_performance_sensitivity.csv", encoding="utf-8-sig")
    model_performance.to_csv(FIG6 / "fig6B_linear_vs_polynomial_model_comparison.csv", index=False, encoding="utf-8-sig")

    candidates = pd.read_csv(R1C6 / "virtual_design_sensitivity.csv", encoding="utf-8-sig")
    if not set(candidates["structure_clean"]).issubset(ROBUST_CLEAN):
        raise ValueError("Sparse hybrid virtual candidate present in validated R1C6 source.")
    candidates.to_csv(FIG6 / "fig6D_virtual_design_candidates_all.csv", index=False, encoding="utf-8-sig")
    candidates.head(10).to_csv(FIG6 / "fig6D_top_virtual_design_candidates.csv", index=False, encoding="utf-8-sig")

    fig6c = candidates.loc[
        (candidates["ion_type_clean"] == "other_cation")
        & (candidates["inorganic_electrolyte_present_clean"] == 1)
        & (candidates["log_R"].isin([-2.0, -1.0, 0.0]))
    ].copy()
    fig6c["structure_label"] = fig6c["structure_clean"].str.replace("_", " ", regex=False).str.title()
    fig6c["regime"] = fig6c["log_R"].map({-2.0: "Low-R", -1.0: "Threshold", 0.0: "High-R"})
    fig6c = fig6c[["structure_clean", "structure_label", "regime", "log_R", "predicted_log_P_est"]]
    fig6c = fig6c.sort_values(["structure_clean", "log_R"]).reset_index(drop=True)
    fig6c.to_csv(FIG6 / "fig6C_regime_aware_virtual_design.csv", index=False, encoding="utf-8-sig")
    fig6c.to_csv(FIG6 / "fig6C_virtual_design_map.csv", index=False, encoding="utf-8-sig")
    print("Integrated validated R1C6 production CSV sources.")


if __name__ == "__main__":
    main()
