"""Data loading. Raw CSVs are never modified in place; all derived values are computed."""
import pandas as pd

from .config import DATA_RAW, DATA_META, SAMPLE_ORDER


def _ordered(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index("sample").loc[SAMPLE_ORDER].reset_index()
    return df


def load_filtration() -> pd.DataFrame:
    return _ordered(pd.read_csv(DATA_RAW / "filtration.csv"))


def load_density() -> pd.DataFrame:
    return _ordered(pd.read_csv(DATA_RAW / "density.csv"))


def load_ph() -> pd.DataFrame:
    return _ordered(pd.read_csv(DATA_RAW / "ph.csv"))


def load_reported_pv_yp_gel() -> pd.DataFrame:
    return _ordered(pd.read_csv(DATA_RAW / "pv_yp_gel_reported.csv"))


def load_formulations() -> pd.DataFrame:
    return _ordered(pd.read_csv(DATA_META / "formulations.csv"))


def load_rheology_long() -> pd.DataFrame:
    """Long table: sample, ramp (up/down/avg_reported), rpm, dial_reading."""
    return pd.read_csv(DATA_RAW / "rheology_8speed.csv")


def rheology_wide(ramp: str) -> pd.DataFrame:
    """One row per sample, one column per rpm, for the chosen ramp."""
    long = load_rheology_long()
    sub = long[long["ramp"] == ramp]
    wide = sub.pivot(index="sample", columns="rpm", values="dial_reading")
    return wide.loc[SAMPLE_ORDER]
