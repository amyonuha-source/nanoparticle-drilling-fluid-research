"""Integrity tests. Run with:  python -m pytest -q"""
import numpy as np

from src import config as C
from src.analysis import derived_rheology, threshold_sensitivity, blend_interaction
from src.data import (load_filtration, load_density, load_ph, load_formulations,
                      load_reported_pv_yp_gel, rheology_wide)


def test_all_nine_samples_in_every_table():
    for loader in (load_filtration, load_density, load_ph, load_formulations, load_reported_pv_yp_gel):
        assert list(loader()["sample"]) == C.SAMPLE_ORDER


def test_rheology_has_eight_speeds_for_each_ramp():
    for ramp in ("up", "down", "avg_reported"):
        wide = rheology_wide(ramp)
        assert list(wide.columns) == [3, 6, 30, 60, 100, 200, 300, 600]
        assert wide.shape[0] == 9
        assert not wide.isna().any().any()


def test_reported_average_matches_mean_of_up_and_down():
    up, down, avg = rheology_wide("up"), rheology_wide("down"), rheology_wide("avg_reported")
    assert (avg - (up + down) / 2).abs().values.max() <= 0.5 + 1e-9  # thesis rounds to whole numbers


def test_pv_yp_discrepancies_are_exactly_the_documented_ones():
    dr = derived_rheology()
    mismatched = set(dr.loc[~dr["matches_thesis_table"], "sample"])
    assert mismatched == set(C.KNOWN_REPORT_DISCREPANCIES)


def test_pt_5050_recomputed_values():
    dr = derived_rheology().set_index("sample")
    assert dr.loc["PT_50-50", "pv_cP"] == 20 and dr.loc["PT_50-50", "yp_lb100ft2"] == 36


def test_dose_fractions_follow_the_label_scheme():
    form = load_formulations().set_index("sample")
    for s in C.SAMPLE_ORDER:
        pol = form.loc[s, "cmc_g"] + form.loc[s, "pacr_g"]
        assert abs(form.loc[s, "polymer_dose_fraction"] - pol / C.REFERENCE_DOSE_G["polymer"]) < 1e-9
        assert abs(form.loc[s, "tio2_dose_fraction"] - form.loc[s, "tio2_g"] / C.REFERENCE_DOSE_G["TiO2"]) < 1e-9
    # blend label 'XX_75-25' means 75 % polymer dose, 25 % TiO2 dose
    assert form.loc["CT_75-25", "polymer_dose_fraction"] == 0.75
    assert form.loc["CT_75-25", "tio2_dose_fraction"] == 0.25


def test_nominal_tio2_pass_is_not_robust_to_tolerance():
    t = threshold_sensitivity().set_index("sample")
    assert t.loc["TiO2", "nominal_pass_both"] and not t.loc["TiO2", "robust_pass_both"]
    assert t.loc["CMC", "possible_pass_both"]  # CMC cannot be separated from TiO2 at this tolerance


def test_every_blend_is_above_the_replacement_line_for_filtrate():
    b = blend_interaction()
    fl = b[b["metric"] == "filtrate_ml"]
    assert (fl["deviation"] > 0).all() and len(fl) == 6


def test_fit_quality_is_reasonable():
    assert (derived_rheology()["hb_r2"] > 0.95).all()
