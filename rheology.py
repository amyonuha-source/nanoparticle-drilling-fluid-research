"""Rheology calculations from viscometer dial readings."""
import numpy as np
from scipy.optimize import curve_fit

from .config import SHEAR_RATE_PER_RPM, STRESS_PER_DIAL


def plastic_viscosity(theta600: float, theta300: float) -> float:
    """PV (cP) = theta600 - theta300."""
    return theta600 - theta300


def yield_point(theta300: float, pv: float) -> float:
    """YP (lb/100 ft2) = theta300 - PV."""
    return theta300 - pv


def herschel_bulkley(gamma, tau0, k, n):
    """tau = tau0 + K * gamma**n  (tau in lb/100 ft2, gamma in 1/s)."""
    return tau0 + k * np.power(gamma, n)


def fit_herschel_bulkley(rpm, dial):
    """Least-squares Herschel-Bulkley fit to an 8-speed ramp.

    Returns a dict with tau0, K, n, their standard errors, R2 and RMSE (lb/100 ft2).
    Eight points constrain three parameters only loosely - always read the standard
    errors alongside the values.
    """
    gamma = np.asarray(rpm, dtype=float) * SHEAR_RATE_PER_RPM
    tau = np.asarray(dial, dtype=float) * STRESS_PER_DIAL
    p0 = [max(0.8 * tau.min(), 0.1), 1.0, 0.5]
    popt, pcov = curve_fit(
        herschel_bulkley, gamma, tau, p0=p0,
        bounds=([0.0, 1e-6, 0.05], [np.inf, np.inf, 1.5]), maxfev=50000,
    )
    resid = tau - herschel_bulkley(gamma, *popt)
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((tau - tau.mean()) ** 2))
    se = np.sqrt(np.diag(pcov))
    return {
        "tau0": popt[0], "K": popt[1], "n": popt[2],
        "tau0_se": se[0], "K_se": se[1], "n_se": se[2],
        "r2": 1.0 - ss_res / ss_tot, "rmse": float(np.sqrt(ss_res / len(tau))),
    }


def hysteresis(up, down):
    """Mean (up - down) dial difference across all speeds.

    A positive value means the up-ramp reads higher than the down-ramp, which is a
    simple indicator of time-dependent (thixotropic) structure breakdown. It depends
    on the ramp sequence and timing, so use it for comparing samples measured the same way.
    """
    return float(np.mean(np.asarray(up, dtype=float) - np.asarray(down, dtype=float)))
