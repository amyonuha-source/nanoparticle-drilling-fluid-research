# Data corrections and source-document discrepancies

Every number in `data/raw/` is transcribed from the final-year project report. While transcribing, the
values were cross-checked against each other. This file lists everything that did not reconcile, so a
reader can see exactly what was changed in the analysis and what was left alone.

**Policy:** raw files keep the thesis values. Corrections are made in code (and reported in
`results/tables/integrity_report.txt`), never by silently editing the raw data.

| # | Where in the report | What the report says | What the data show | How it is handled here |
|---|---|---|---|---|
| 1 | Table 4.4, row PACR-TiO2 50-50 | PV 10 cP, YP 46 lb/100 ft2 | Table 4.3 average ramp gives theta600 = 76 and theta300 = 56, so PV = 20 cP and YP = 36 lb/100 ft2 (the printed PV and YP still sum to theta300 = 56, which suggests the two values were swapped between columns or mis-split) | `data/raw/pv_yp_gel_reported.csv` keeps the printed values. All figures and tables use the recomputed 20 / 36. `tests/` fails if any *other* mismatch appears. |
| 2 | Section 4.2.3 (hybrid formulations), text | "CT 75-25 ... PV of 8 cP and YP of 14" | Those are the CT 25-75 values. CT 75-25 is PV 18, YP 26 | Text error only; tables are correct. Not used. |
| 3 | Table 3.7, column headers | "CT 72-25"; the last PT column is headed "PT 25-75" | The first is CT 75-25. The last PT column carries 0.75 g PACR + 0.5 g TiO2, i.e. PT 75-25 | Masses in `data/metadata/formulations.csv` follow section 3.2.3.1 and the column contents, not the headers. |
| 4 | Section 3.2.3.1 | "The five formulations tested were as follows", followed by nine samples | Nine formulations were tested | Nine used throughout. |
| 5 | Section 3.2.3.1 vs Table 3.6 | "distilled water" vs "deionized water" | Not resolved by the source | Documented as "distilled/deionized" until confirmed. |
| 6 | Abstract, Section 4.2.3 | TiO2 "minimal impact" on PV, YP and gel strength | No additive-free (bentonite-only) base mud was tested, so impact cannot be measured. Against CMC, TiO2 gives PV -21 %, YP -27 %, 10-min gel -49 % | README states the CMC comparison and says explicitly that no baseline exists. |
| 7 | Section 4.2.1, 4.2.2, 4.2.4 | "API standard" limits of 15 mL, 2/32 in, 8.5-9.5 ppg and pH 7.5-9.5 | No specific API document is cited for these limits | Treated as *study targets* in `src/config.py`. Add the exact citation if one exists. |
| 8 | Section 4.2.2, density | Values reported to 0.01 ppg | A standard mud balance reads to about 0.1 ppg (the reading resolution quoted in the source SIWES procedure), so differences below 0.1 ppg are not meaningful. PT 75-25 (9.05) differs from the others by 0.35 ppg and may be a reading or mixing artefact | Reported as measured; flagged as unexplained in the README. |
| 9 | Section 3.2.3.2, pH | pH by litmus paper, differences of 0.2-0.5 units interpreted | Litmus paper resolves roughly 0.5-1 pH unit | pH plotted but not interpreted beyond the range. |
| 10 | Section 3.2.2 | SEM, XRD, FTIR and EDX are described as methods | No micrographs, patterns, spectra or derived values appear in the report | The README does not claim characterization results and says none are included. |
