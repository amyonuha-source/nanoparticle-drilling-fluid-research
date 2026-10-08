"""Figure generation. Run from the repository root:  python -m src.figures"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.lines import Line2D
import numpy as np

from . import config as C
from .analysis import derived_rheology
from .data import (load_filtration, load_density, load_ph, load_formulations, rheology_wide)
from .rheology import herschel_bulkley, fit_herschel_bulkley

plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 11, "figure.dpi": 100,
    "savefig.dpi": 200, "savefig.bbox": "tight", "axes.axisbelow": True,
})
FOOT = "Data: final-year project, FUTO Petroleum Engineering (2025). Single test per formulation; no replicates."
FOOT_SHORT = "Single test per formulation; no replicates."


def _save(fig, name):
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = C.FIG_DIR / name
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def fig_filtration():
    f = load_filtration().set_index("sample")
    y = {s: i for i, s in enumerate(C.SAMPLE_ORDER)}
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.2), sharey=True)
    specs = [
        ("filtrate_ml", "Filtrate after 30 min (mL)", C.TARGET_FILTRATE_ML, C.TOL_FILTRATE_ML, (12, 17.2), "target \u2264 15 mL"),
        ("mud_cake_32nd_in", "Filter-cake thickness (1/32 in)", C.TARGET_CAKE_32ND, C.TOL_CAKE_32ND, (0, 5), "target \u2264 2/32 in"),
    ]
    for ax, (col, xl, target, tol, xlim, tlabel) in zip(axes, specs):
        ax.axvspan(xlim[0], target, color="#E8F5E9", zorder=0)
        ax.axvline(target, color="#2E7D32", lw=1.2, ls="--", zorder=1)
        ax.text(target, -0.85, tlabel, ha="center", va="bottom", color="#2E7D32", fontsize=9, fontweight="bold",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
        for s in C.SAMPLE_ORDER:
            v = f.loc[s, col]
            colr = C.COLOURS[C.family(s)]
            blend = C.is_blend(s)
            ax.errorbar(v, y[s], xerr=tol, fmt="none", ecolor="#9E9E9E", elinewidth=1.4, capsize=3, zorder=2)
            ax.scatter(v, y[s], s=95, zorder=3, facecolor="white" if blend else colr,
                       edgecolor=colr, linewidth=2)
            ax.text(v + tol + 0.08 * (xlim[1] - xlim[0]) / 5, y[s], f"{v:g}", va="center", fontsize=9)
        ax.set_xlim(*xlim)
        ax.set_xlabel(xl)
        ax.grid(axis="x", color="#EEEEEE")
        for yy in (0.5, 3.5, 4.5, 7.5):
            ax.axhline(yy, color="#CFD8DC", lw=0.8, zorder=0)
    axes[0].set_yticks(range(len(C.SAMPLE_ORDER)))
    axes[0].set_yticklabels([C.LABELS[s] for s in C.SAMPLE_ORDER])
    axes[0].set_ylim(len(C.SAMPLE_ORDER) - 0.4, -1.2)
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C.COLOURS["CMC"], markersize=9, label="CMC (1 g reference)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C.COLOURS["TiO2"], markersize=9, label="TiO$_2$ (2 g reference)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C.COLOURS["PACR"], markersize=9, label="PACR (1 g reference)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", markeredgecolor="#555", markeredgewidth=2, markersize=9, label="hollow = blend (polymer colour)"),
        Line2D([0], [0], color="#9E9E9E", lw=1.6, label="\u00b1 illustrative reading tolerance"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.02), fontsize=9)
    fig.suptitle("Filtration performance of nine water-based mud formulations", fontsize=13, fontweight="bold", y=1.0)
    fig.text(0.5, 0.945, "API low-pressure test (100 psi, 30 min). Error bars: \u00b10.5 mL and \u00b10.5/32 in are illustrative assumptions, not instrument specifications. "
             "TiO$_2$ and CMC are indistinguishable at that tolerance.",
             ha="center", fontsize=8.5, color="#555")
    fig.text(0.5, -0.07, FOOT, ha="center", fontsize=8, color="#777")
    fig.tight_layout(rect=(0, 0.03, 1, 0.93))
    _save(fig, "fig1_filtration_vs_study_targets.png")


def _blend_cmap(series):
    """Perceptual map for TiO2 dose fraction (0 = polymer only, 1 = TiO2 only)."""
    return plt.get_cmap("viridis")


def fig_rheogram():
    up, down, avg = rheology_wide("up"), rheology_wide("down"), rheology_wide("avg_reported")
    rpm = avg.columns.values.astype(float)
    gamma = rpm * C.SHEAR_RATE_PER_RPM
    form = load_formulations().set_index("sample")
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 5.2), sharex=True, sharey=True)

    ax = axes[0]
    for s in ("CMC", "PACR", "TiO2"):
        col = C.COLOURS[C.family(s)]
        ax.plot(gamma, up.loc[s].values * C.STRESS_PER_DIAL, "o-", color=col, ms=4, lw=1.6, label=f"{C.LABELS[s]} \u2013 up")
        ax.plot(gamma, down.loc[s].values * C.STRESS_PER_DIAL, "s--", color=col, ms=4, lw=1.2, alpha=0.8, label=f"{C.LABELS[s]} \u2013 down")
    ax.set_title("A  Single additives: up vs down ramp")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")

    for ax, series, letter in ((axes[1], "CMC", "B"), (axes[2], "PACR", "C")):
        cmap = _blend_cmap(series)
        members = [series if series == "CMC" else "PACR"] + [s for s in C.SAMPLE_ORDER if C.is_blend(s) and C.family(s) == series] + ["TiO2"]
        members = sorted(set(members), key=lambda s: form.loc[s, "tio2_dose_fraction"])
        gg = np.logspace(np.log10(gamma.min()), np.log10(gamma.max()), 100)
        for s in members:
            x = form.loc[s, "tio2_dose_fraction"]
            colr = cmap(0.92 * x)
            hb = fit_herschel_bulkley(rpm, avg.loc[s].values)
            ax.plot(gg, herschel_bulkley(gg, hb["tau0"], hb["K"], hb["n"]), "-", color=colr, lw=1.6)
            ax.plot(gamma, avg.loc[s].values * C.STRESS_PER_DIAL, "o", color=colr, ms=4.5, label=f"{C.LABELS[s]}  (n = {hb['n']:.2f})")
        ax.set_title(f"{letter}  {series} \u2192 TiO$_2$ replacement series")
        ax.legend(fontsize=7.5, frameon=False, loc="upper left", title="colour = TiO$_2$ dose fraction (purple 0 \u2192 yellow 1)\nmarkers: mean of up/down ramps; lines: Herschel\u2013Bulkley fit", title_fontsize=7.5)

    for ax in axes:
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("Shear rate (s$^{-1}$)  [rpm \u00d7 1.703]")
        ax.grid(True, which="both", color="#EEEEEE")
    axes[0].set_ylabel("Shear stress (lb/100 ft$^2$)  [dial \u00d7 1.0678]")
    fig.suptitle("Flow curves from the 8-speed viscometer data", fontsize=13, fontweight="bold")
    fig.text(0.5, -0.02, "Viscometer geometry assumed standard R1\u2013B1 / F1 spring (model not recorded in the source), so absolute stress and shear-rate values are indicative. "
             "Within-figure comparisons are unaffected.", ha="center", fontsize=8, color="#777")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _save(fig, "fig2_flow_curves.png")


def fig_thixotropy():
    dr = derived_rheology().set_index("sample")
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ys = np.arange(len(C.SAMPLE_ORDER))
    vals = [dr.loc[s, "hysteresis_mean_up_minus_down"] for s in C.SAMPLE_ORDER]
    cols = [C.COLOURS[C.family(s)] for s in C.SAMPLE_ORDER]
    bars = ax.barh(ys, vals, color=cols, edgecolor=cols, linewidth=1.5)
    for b, s in zip(bars, C.SAMPLE_ORDER):
        if C.is_blend(s):
            b.set_facecolor("white")
    for i, v in enumerate(vals):
        ax.text(v + 0.15, i, f"{v:.1f}", va="center", fontsize=9)
    ax.set_yticks(ys); ax.set_yticklabels([C.LABELS[s] for s in C.SAMPLE_ORDER])
    ax.invert_yaxis()
    ax.set_xlabel("Mean (up-ramp \u2212 down-ramp) dial reading, all 8 speeds")
    ax.set_title("Ramp hysteresis (a simple indicator of structure breakdown)")
    ax.grid(axis="x", color="#EEEEEE")
    fig.text(0.5, -0.04, "Hollow bars = blends. Depends on ramp timing and sequence, so valid for comparing these samples with each other only.\n" + FOOT,
             ha="center", fontsize=8, color="#777")
    _save(fig, "fig3_ramp_hysteresis.png")


def fig_blend_response():
    f = load_filtration().set_index("sample")
    form = load_formulations().set_index("sample")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    specs = [("filtrate_ml", "Filtrate after 30 min (mL)", C.TARGET_FILTRATE_ML, C.TOL_FILTRATE_ML),
             ("mud_cake_32nd_in", "Filter-cake thickness (1/32 in)", C.TARGET_CAKE_32ND, C.TOL_CAKE_32ND)]
    for ax, (col, yl, target, tol) in zip(axes, specs):
        ax.axhline(target, color="#2E7D32", ls=":", lw=1.2)
        ax.text(0.01, target, " study target", color="#2E7D32", fontsize=8, va="bottom")
        for series, pol in (("CMC", "CMC"), ("PACR", "PACR")):
            members = [pol] + [s for s in C.SAMPLE_ORDER if C.is_blend(s) and C.family(s) == series] + ["TiO2"]
            members = sorted(set(members), key=lambda s: form.loc[s, "tio2_dose_fraction"])
            xs = [form.loc[s, "tio2_dose_fraction"] for s in members]
            ys = [f.loc[s, col] for s in members]
            colr = C.COLOURS[series]
            ax.plot([0, 1], [f.loc[pol, col], f.loc["TiO2", col]], "--", color=colr, lw=1.3, alpha=0.8)
            ax.fill_between([0, 1], [f.loc[pol, col] - tol] * 1 + [f.loc["TiO2", col] - tol],
                            [f.loc[pol, col] + tol] * 1 + [f.loc["TiO2", col] + tol], color=colr, alpha=0.10, lw=0)
            ax.plot(xs, ys, "o-", color=colr, lw=1.8, ms=7, label=f"{series} \u2192 TiO$_2$ (observed)")
        ax.set_xlabel("Fraction of the 2 g TiO$_2$ reference dose  (0 = polymer only, 1 = TiO$_2$ only)")
        ax.set_ylabel(yl)
        ax.grid(color="#EEEEEE")
    h, l = axes[0].get_legend_handles_labels()
    h.append(Line2D([0], [0], color="#777", ls="--", lw=1.3)); l.append("replacement line \u00b1 illustrative tolerance")
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01), fontsize=9)
    axes[0].set_title("Fluid loss vs blend composition")
    axes[1].set_title("Cake thickness vs blend composition")
    fig.suptitle("Every blend sits above the straight replacement line", fontsize=13, fontweight="bold")
    fig.text(0.5, -0.09, "Dashed line = response expected if the two additives simply traded off linearly. Total additive mass rises from 1 g to 1.25\u20131.75 g across blends, so loading and interaction effects cannot be separated with this dataset. " + FOOT_SHORT,
             ha="center", fontsize=8, color="#777")
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    _save(fig, "fig4_blend_response.png")


def fig_matrix():
    f, d, p = load_filtration(), load_density(), load_ph()
    dr = derived_rheology()
    tab = {
        "Filtrate\n(mL)": f["filtrate_ml"].values,
        "Cake\n(1/32 in)": f["mud_cake_32nd_in"].values,
        "PV\n(cP)": dr["pv_cP"].values,
        "YP\n(lb/100ft$^2$)": dr["yp_lb100ft2"].values,
        "Gel 10 s": dr["gel_10s"].values,
        "Gel 10 min": dr["gel_10min"].values,
        "Density\n(ppg)": d["density_ppg"].values,
        "Filtrate pH\n(litmus)": p["filtrate_ph"].values,
    }
    cols = list(tab)
    M = np.array([tab[c] for c in cols], dtype=float).T
    norm = (M - M.min(0)) / (M.max(0) - M.min(0))
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1.15, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            txt = f"{v:.2f}" if cols[j].startswith("Density") else (f"{v:g}")
            ax.text(j, i, txt, ha="center", va="center", fontsize=9.5, color="white" if norm[i, j] > 0.6 else "#222")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=9)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(C.SAMPLE_ORDER)))
    ax.set_yticklabels([C.LABELS[s] for s in C.SAMPLE_ORDER])
    for lab, s in zip(ax.get_yticklabels(), C.SAMPLE_ORDER):
        lab.set_color(C.COLOURS[C.family(s)]); lab.set_fontweight("bold" if not C.is_blend(s) else "normal")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("All measured properties at a glance", pad=38, fontsize=13)
    fig.text(0.5, 0.01, "Shading = position within each column (min to max). It is NOT a quality score: a higher PV or gel strength is not 'better' or 'worse' without a design target.\n"
             "PV and YP are recomputed from the raw dial readings (PACR 0.5 g + TiO$_2$ 1 g differs from the thesis table; see docs/data_corrections.md). pH by litmus paper (\u00b10.5\u20131 unit). " + FOOT_SHORT, ha="center", fontsize=8, color="#777")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save(fig, "fig5_property_matrix.png")


def main():
    fig_filtration(); fig_rheogram(); fig_thixotropy(); fig_blend_response(); fig_matrix()


if __name__ == "__main__":
    main()
