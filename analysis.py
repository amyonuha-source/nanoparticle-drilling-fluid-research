"""Reproducible analysis. Run from the repository root:  python -m src.analysis

Reads data/raw + data/metadata, writes tables to results/tables and an integrity report.
"""
import numpy as np
import pandas as pd
from scipy import stats

from . import config as C
from .data import (load_filtration, load_density, load_ph, load_reported_pv_yp_gel,
                   load_formulations, rheology_wide)
from .rheology import (plastic_viscosity, yield_point, fit_herschel_bulkley, hysteresis)


def derived_rheology() -> pd.DataFrame:
    """PV/YP recomputed from raw dials, compared with the thesis table, plus HB fit."""
    up, down, avg = rheology_wide("up"), rheology_wide("down"), rheology_wide("avg_reported")
    rep = load_reported_pv_yp_gel().set_index("sample")
    rows = []
    for s in C.SAMPLE_ORDER:
        pv = plastic_viscosity(avg.loc[s, 600], avg.loc[s, 300])
        yp = yield_point(avg.loc[s, 300], pv)
        hb = fit_herschel_bulkley(avg.columns.values, avg.loc[s].values)
        rows.append({
            "sample": s,
            "pv_cP": pv, "yp_lb100ft2": yp,
            "pv_reported": rep.loc[s, "plastic_viscosity_cP"],
            "yp_reported": rep.loc[s, "yield_point_lb_100ft2"],
            "matches_thesis_table": bool(pv == rep.loc[s, "plastic_viscosity_cP"]
                                         and yp == rep.loc[s, "yield_point_lb_100ft2"]),
            "gel_10s": rep.loc[s, "gel_10sec"], "gel_10min": rep.loc[s, "gel_10min"],
            "hb_tau0_lb100ft2": hb["tau0"], "hb_tau0_se": hb["tau0_se"],
            "hb_K": hb["K"], "hb_n": hb["n"], "hb_n_se": hb["n_se"],
            "hb_r2": hb["r2"],
            "hysteresis_mean_up_minus_down": hysteresis(up.loc[s].values, down.loc[s].values),
            "hysteresis_at_3rpm": up.loc[s, 3] - down.loc[s, 3],
        })
    return pd.DataFrame(rows)


def threshold_sensitivity() -> pd.DataFrame:
    """How robust is each 'meets both study targets' verdict to small reading tolerances?"""
    f = load_filtration()
    out = []
    for _, r in f.iterrows():
        fl, ck = r["filtrate_ml"], r["mud_cake_32nd_in"]
        nominal = fl <= C.TARGET_FILTRATE_ML and ck <= C.TARGET_CAKE_32ND
        robust = (fl + C.TOL_FILTRATE_ML <= C.TARGET_FILTRATE_ML
                  and ck + C.TOL_CAKE_32ND <= C.TARGET_CAKE_32ND)
        possible = (fl - C.TOL_FILTRATE_ML <= C.TARGET_FILTRATE_ML
                    and ck - C.TOL_CAKE_32ND <= C.TARGET_CAKE_32ND)
        verdict = ("passes under every tolerance case" if robust else
                   "nominal pass, but fails if readings are at the unfavourable end" if nominal else
                   "nominal fail, but could pass at the favourable end" if possible else
                   "fails under every tolerance case")
        out.append({"sample": r["sample"], "filtrate_ml": fl, "cake_32nd": ck,
                    "nominal_pass_both": nominal, "robust_pass_both": robust,
                    "possible_pass_both": possible, "verdict": verdict})
    return pd.DataFrame(out)


def blend_interaction() -> pd.DataFrame:
    """Observed blend response vs the straight 'replacement line' between its two endpoints.

    x = fraction of the TiO2 reference dose (0 = polymer only, 1 = TiO2 only). The
    replacement line is the response expected if the two additives simply traded off
    linearly. Deviations above tolerance are candidate interactions, but total additive
    mass also rises across blends (1.25-1.75 g vs 1 g polymer), so loading and
    interaction cannot be separated with this dataset.
    """
    f = load_filtration().set_index("sample")
    form = load_formulations().set_index("sample")
    rows = []
    for series, pol in (("CMC", "CMC"), ("PACR", "PACR")):
        blends = [s for s in C.SAMPLE_ORDER if C.is_blend(s) and C.family(s) == series]
        for s in blends:
            x = form.loc[s, "tio2_dose_fraction"]
            for metric, tol in (("filtrate_ml", C.TOL_FILTRATE_ML), ("mud_cake_32nd_in", C.TOL_CAKE_32ND)):
                pred = (1 - x) * f.loc[pol, metric] + x * f.loc["TiO2", metric]
                obs = f.loc[s, metric]
                rows.append({"series": series, "sample": s, "tio2_dose_fraction": x,
                             "metric": metric, "observed": obs,
                             "replacement_line": round(pred, 3),
                             "deviation": round(obs - pred, 3),
                             "exceeds_illustrative_tolerance": abs(obs - pred) > tol})
    return pd.DataFrame(rows)


def correlations() -> pd.DataFrame:
    """Fluid-loss correlations with other properties (n = 9, descriptive only)."""
    f, d = load_filtration(), load_density()
    dr = derived_rheology()
    df = pd.DataFrame({"filtrate_ml": f["filtrate_ml"], "cake_32nd": f["mud_cake_32nd_in"],
                       "pv_cP": dr["pv_cP"], "yp_lb100ft2": dr["yp_lb100ft2"],
                       "gel_10s": dr["gel_10s"], "gel_10min": dr["gel_10min"],
                       "density_ppg": d["density_ppg"]})
    rows = []
    for col in df.columns[1:]:
        pr, pp = stats.pearsonr(df["filtrate_ml"], df[col])
        sr, sp = stats.spearmanr(df["filtrate_ml"], df[col])
        rows.append({"variable_vs_filtrate": col, "n": len(df), "pearson_r": pr,
                     "pearson_p": pp, "spearman_rho": sr, "spearman_p": sp})
    return pd.DataFrame(rows)


def integrity_report(dr: pd.DataFrame) -> str:
    """Plain-text report of every consistency check."""
    lines = ["DATA INTEGRITY REPORT", "=" * 60]
    up, down, avg = rheology_wide("up"), rheology_wide("down"), rheology_wide("avg_reported")
    diff = (avg - (up + down) / 2).abs()
    lines.append(f"Averages vs mean(up, down): max |difference| = {diff.values.max():.2f} dial units "
                 f"(rounding tolerance 0.5) -> {'OK' if diff.values.max() <= 0.5 else 'CHECK'}")
    bad = dr[~dr["matches_thesis_table"]]
    lines.append("")
    lines.append("PV / YP recomputed from raw dial readings vs thesis Table 4.4:")
    for _, r in dr.iterrows():
        flag = "OK" if r["matches_thesis_table"] else "MISMATCH"
        lines.append(f"  {r['sample']:9s} recomputed PV {r['pv_cP']:.0f} / YP {r['yp_lb100ft2']:.0f}   "
                     f"thesis PV {r['pv_reported']:.0f} / YP {r['yp_reported']:.0f}   {flag}")
    expected = set(C.KNOWN_REPORT_DISCREPANCIES)
    found = set(bad["sample"])
    lines.append("")
    lines.append(f"Known documented discrepancies: {sorted(expected)}")
    lines.append(f"Discrepancies found now:        {sorted(found)}")
    lines.append("Status: " + ("matches documentation" if expected == found else "UNDOCUMENTED CHANGE - investigate"))
    return "\n".join(lines)


def main() -> None:
    C.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    dr = derived_rheology()
    dr.round(4).to_csv(C.TABLE_DIR / "derived_rheology.csv", index=False)
    threshold_sensitivity().to_csv(C.TABLE_DIR / "filtration_threshold_sensitivity.csv", index=False)
    blend_interaction().to_csv(C.TABLE_DIR / "blend_vs_replacement_line.csv", index=False)
    correlations().round(4).to_csv(C.TABLE_DIR / "fluid_loss_correlations.csv", index=False)
    (C.TABLE_DIR / "integrity_report.txt").write_text(integrity_report(dr) + "\n", encoding="utf-8")
    print(integrity_report(dr))
    print(f"\nTables written to {C.TABLE_DIR}")


if __name__ == "__main__":
    main()
