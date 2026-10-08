"""Central configuration: paths, study thresholds, instrument constants, plotting labels.

Everything that is an assumption rather than a measurement lives here so it can be
reviewed and changed in one place.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_META = ROOT / "data" / "metadata"
RESULTS = ROOT / "results"
FIG_DIR = RESULTS / "figures"
TABLE_DIR = RESULTS / "tables"

# --- Study target thresholds -------------------------------------------------------
# These are the pass/fail limits used in the original thesis. The thesis does not cite a
# specific standard for them, so they are treated here as *study targets*, not as
# API specifications.
TARGET_FILTRATE_ML = 15.0       # filtrate must be <= this (mL, 30 min)
TARGET_CAKE_32ND = 2.0          # cake must be <= this (1/32 inch)

# --- Illustrative reading tolerances ------------------------------------------------
# NOT instrument specifications (none were recorded). They are round-number assumptions
# used only to show how sensitive pass/fail verdicts are to small reading differences.
TOL_FILTRATE_ML = 0.5
TOL_CAKE_32ND = 0.5

# --- Viscometer constants -----------------------------------------------------------
# Standard R1-B1 rotor-bob geometry with F1 torsion spring. The thesis does not record
# the instrument model, so shear stress / shear rate values are indicative only.
SHEAR_RATE_PER_RPM = 1.703      # 1/s per rpm
STRESS_PER_DIAL = 1.0678        # lb/100 ft2 per dial degree

# --- Reference doses used to define the blend labels -------------------------------
# Blend "75-25" = 75 % of the 1 g polymer reference dose + 25 % of the 2 g TiO2 dose.
REFERENCE_DOSE_G = {"polymer": 1.0, "TiO2": 2.0}

# --- Plot order, labels and colours --------------------------------------------------
# Order walks from the CMC reference, through the CMC blends, to TiO2, then through the
# PACR blends to the PACR reference.
SAMPLE_ORDER = ["CMC", "CT_75-25", "CT_50-50", "CT_25-75", "TiO2",
                "PT_25-75", "PT_50-50", "PT_75-25", "PACR"]

LABELS = {
    "CMC": "CMC 1 g",
    "CT_75-25": "CMC 0.75 g + TiO$_2$ 0.5 g",
    "CT_50-50": "CMC 0.5 g + TiO$_2$ 1 g",
    "CT_25-75": "CMC 0.25 g + TiO$_2$ 1.5 g",
    "TiO2": "TiO$_2$ 2 g",
    "PT_25-75": "PACR 0.25 g + TiO$_2$ 1.5 g",
    "PT_50-50": "PACR 0.5 g + TiO$_2$ 1 g",
    "PT_75-25": "PACR 0.75 g + TiO$_2$ 0.5 g",
    "PACR": "PACR 1 g",
}
PLAIN_LABELS = {k: v.replace("$_2$", "2") for k, v in LABELS.items()}

# Colour-blind-safe (Okabe-Ito) family colours
COLOURS = {"CMC": "#0072B2", "TiO2": "#009E73", "PACR": "#D55E00"}


def family(sample: str) -> str:
    """Return 'CMC', 'TiO2' or 'PACR' - the polymer family a sample belongs to."""
    if sample == "TiO2":
        return "TiO2"
    if sample.startswith("CT") or sample == "CMC":
        return "CMC"
    return "PACR"


def is_blend(sample: str) -> bool:
    return sample.startswith("CT_") or sample.startswith("PT_")


# --- Known discrepancies in the source thesis -----------------------------------------
# Documented in docs/data_corrections.md. The integrity tests expect exactly these.
KNOWN_REPORT_DISCREPANCIES = {
    "PT_50-50": "Thesis Table 4.4 prints PV 10 / YP 46; Table 4.3 (theta600 = 76, theta300 = 56) gives PV 20 / YP 36.",
}
