# Green-synthesized TiO₂ as a fluid-loss additive in water-based drilling mud

[![reproduce-and-test](https://github.com/amyonuha-source/nanoparticle-drilling-fluid-research/actions/workflows/ci.yml/badge.svg)](https://github.com/amyonuha-source/nanoparticle-drilling-fluid-research/actions)

Data and reproducible analysis for nine water-based mud formulations that compare **titanium dioxide nanoparticles
made from *Newbouldia laevis* leaf extract** against two conventional polymers, CMC and PACR, and against six CMC/PACR + TiO₂ blends.
From the final-year project, carried out in a team of three.
**My role:** I led the filtration-control testing across all formulations and controls.

![Filtration versus study targets](results/figures/fig1_filtration_vs_study_targets.png)

## What the data show

| Question | Finding | How firm is it? |
|---|---|---|
| Does TiO₂ (2 g) reduce fluid loss compared with CMC (1 g)? | 13.7 mL vs 14.5 mL (0.8 mL, 5.5 % lower) | **Indicative only.** One test each, no replicates; with a ±0.5 mL reading tolerance on each value the two error bars overlap. |
| Which formulation had the thinnest cake? | TiO₂: 2/32 in. CMC 2.5/32, PACR 4/32 (thickest) | Indicative; 0.5/32 in is below ruler resolution. |
| Does only TiO₂ meet the targets (≤ 15 mL **and** ≤ 2/32 in)? | Nominally yes. But CMC passes at the favourable end of the same tolerance, so the two cannot be separated. | See `results/tables/filtration_threshold_sensitivity.csv`. |
| Do blends help? | **No.** All six blends lose more fluid than both of their parent additives (14.8–16.1 mL), and sit 0.9–2.75 mL above the straight replacement line. | Consistent across all six blends. Total additive mass also rises in blends (1.25–1.75 g), so loading and interaction cannot be separated. |
| Is TiO₂ rheologically "inert"? | **No.** Against CMC it gives lower PV (11 vs 14 cP), YP (24 vs 33) and 10-min gel (20 vs 39). Herschel–Bulkley fits give a much lower yield stress (2.8 ± 1.9 vs 19.8 ± 1.2 lb/100 ft²) and a lower flow index n (0.39 ± 0.04 vs 0.60 ± 0.05). | Real in these data, but there is **no additive-free control**, so the effect relative to the base mud is unknown. The doses also differ (2 g vs 1 g). |
| Does fluid loss track rheology? | No detectable relationship (\|r\| ≤ 0.2 with PV, YP, gels, density, n = 9, none significant). | Descriptive only. |

Gel strength, pH and density are plotted in `results/figures/fig5_property_matrix.png`. The PT 75-25 density (9.05 ppg) is
0.35 ppg above the rest and is unexplained; litmus-paper pH resolves only about 0.5–1 unit.

![Flow curves](results/figures/fig2_flow_curves.png)

## A correction to the original report

Recomputing PV and YP from the raw 8-speed dial readings shows that the PACR + TiO₂ 50-50 values in the report's Table 4.4 are wrong:
**PV 20 cP / YP 36 lb/100 ft²**, not 10 / 46. Every other row reconciles. Details and nine further minor discrepancies are in
[`docs/data_corrections.md`](docs/data_corrections.md). The test suite fails if any new mismatch appears.

## Blend labels

"CT 75-25" means **75 % of the 1 g CMC reference dose + 25 % of the 2 g TiO₂ reference dose** (0.75 g + 0.5 g). These are not mass ratios.
The full table is in [`data/metadata/formulations.csv`](data/metadata/formulations.csv).

## Run it

```bash
git clone https://github.com/amyonuha-source/nanoparticle-drilling-fluid-research.git
cd nanoparticle-drilling-fluid-research
pip install -r requirements.txt
python -m src.analysis     # tables + integrity report -> results/tables/
python -m src.figures      # figures -> results/figures/
pip install -r requirements-dev.txt && python -m pytest -q
```

Python 3.10 or later. Everything in `results/` is regenerated from `data/` by those two commands.

## Repository layout

```text
data/raw/          measurements exactly as recorded (filtration, density, pH, 8-speed rheology, thesis PV/YP/gel)
data/metadata/     formulations.csv (masses, dose fractions) and data_dictionary.csv (units, instruments, sources)
src/               config.py (assumptions) · data.py · rheology.py · analysis.py · figures.py
tests/             data-integrity tests (also run in CI)
results/tables/    derived rheology, threshold sensitivity, replacement-line deviations, correlations, integrity report
results/figures/   fig1–fig5 (PNG)
docs/              methodology.md · data_corrections.md
```

## Limitations (read before citing any number)

- One test per formulation, no replicates, no uncertainty estimate from the experiment itself. The ±0.5 mL and ±0.5/32 in bands are **illustrative assumptions**.
- No additive-free (bentonite-only) control, so no result is expressed relative to the base mud.
- Doses are not matched between additives (TiO₂ 2 g vs CMC/PACR 1 g).
- Pass/fail limits (15 mL, 2/32 in) are the study's own targets; the report does not cite a specific API document for them.
- pH by litmus paper; density quoted to 0.01 ppg although a mud balance resolves about 0.1 ppg.
- Viscometer model and geometry were not recorded, so shear-stress and shear-rate conversions use standard R1–B1 / F1 constants and are indicative.
- Low-pressure, ambient-temperature filtration only. No HPHT, aging or contamination testing.
- Nanoparticle characterization (SEM, XRD, FTIR, EDX) is described in the project report's methods section, but no results from it are included here, so no claims are made about particle size, crystal phase or morphology.

## Cite

See [`CITATION.cff`](CITATION.cff). Code is MIT-licensed (see `LICENSE`).

**Author:** Chiamaka Onuh, Federal University of Technology, Owerri.
