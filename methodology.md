# Methodology

Source: final-year project, Department of Petroleum Engineering, Federal University of Technology, Owerri
(February 2025). All values below are as recorded in that report; items it does not record are marked *not recorded*.

## Materials and mud preparation (per 350 mL batch)

| Component | Amount | Notes |
|---|---|---|
| Distilled / deionized water | 350 mL | the report uses both terms |
| Bentonite | 15 g | hydrated in a mud mixer for 10 min |
| Fluid-loss / viscosity additive | see `data/metadata/formulations.csv` | added after bentonite hydration |
| Barite | 10 g | added last for weighting |

Samples were sealed and aged 24 h at room temperature before testing. Batch size of 350 mL corresponds to
one laboratory barrel equivalent, so grams per batch are numerically pounds per barrel (ppb).

TiO2 was synthesized by a plant-mediated route using *Newbouldia laevis* extract (the report spells the species "laeve").

## Formulations and the blend-label scheme

Reference doses: CMC 1 g, PACR 1 g, TiO2 2 g. A blend label gives the fraction of each reference dose, so
**"75-25" means 75 % of the polymer reference dose + 25 % of the TiO2 reference dose** (for example
0.75 g CMC + 0.5 g TiO2). The labels are therefore not mass ratios, and total additive mass varies
(1.25 g, 1.5 g, 1.75 g across blends; 1 g for CMC and PACR; 2 g for TiO2).

## Tests

| Property | Method | Conditions |
|---|---|---|
| Filtrate and cake | API filter press (LPLT) | 350 mL mud, 100 psi differential, about 32 C (ambient), 30 min, filter paper; cake measured in 1/32 in |
| Density | Mud balance | one reading per sample |
| Rheology | 8-speed rotational viscometer | 600, 300, 200, 100, 60, 30, 6, 3 rpm; up-ramp and down-ramp recorded; instrument model *not recorded* |
| Gel strength | Same viscometer at 3 rpm | after 10 s and 10 min rest |
| pH | Litmus paper | filtrate and cake, approx. +/-0.5-1 unit |

One test per formulation. No replicates, no blank (additive-free) control.

## Calculations (all in `src/`)

- **PV (cP)** = theta600 - theta300 and **YP (lb/100 ft2)** = theta300 - PV, from the average ramp (`rheology.py`).
- **Herschel-Bulkley fit**: tau = tau0 + K * gamma^n over all eight speeds, with
  tau = 1.0678 x dial and gamma = 1.703 x rpm (standard R1-B1 / F1 constants; the actual instrument is not recorded).
  Standard errors come from the fit covariance. With eight points and three parameters the parameters are
  correlated; compare samples qualitatively.
- **Ramp hysteresis**: mean of (up-ramp dial - down-ramp dial) over the eight speeds. A positive value means
  the up-ramp reads higher. It depends on ramp timing and sequence.
- **Threshold sensitivity**: nominal pass uses the study targets (<= 15 mL, <= 2/32 in). The *robust* and *possible*
  cases shift both readings by +/-0.5 (mL and 1/32 in respectively). These tolerances are **assumptions**, not instrument
  specifications; change them in `src/config.py`.
- **Replacement line**: for each blend, the straight line between its polymer-only and TiO2-only endpoints, evaluated at the
  TiO2 dose fraction. It shows what a simple linear trade-off would predict. It cannot separate an interaction from the
  effect of higher total additive loading.

## What this dataset cannot support

- A statistical test of any difference between formulations (no replicates).
- The effect of any additive relative to the base mud (no bentonite-only control).
- A dose-matched comparison between TiO2 (2 g) and CMC (1 g).
- Any claim about nanoparticle size, phase or morphology (no characterization data in the repository).
- Behaviour at temperature or pressure above the test conditions (no HPHT data).
