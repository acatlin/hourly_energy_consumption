# Hourly energy consumption

PJM hourly load CSVs plus an interactive dashboard for the AEP series, `aep_dashboard.html`.

## Data access

Code loads data files by their raw GitHub URL, `https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/<file>`, so notebooks and pages run anywhere without a checkout. The README lists every file and URL.

## Dashboard

- One standalone HTML file, no framework; charts are inline SVG built by the page's own script. GitHub Pages serves it from `main` at https://acatlin.github.io/hourly_energy_consumption/, and a push to `main` deploys.
- It is also a claude.ai artifact: https://claude.ai/artifact/UUQySQvgfQT2kLAZKKpKyz. The artifact sandbox blocks fetches to outside hosts, so the page tries the raw URL first and falls back to `AEP_hourly.csv` published next to it. Republish by passing that URL, with `build/aep_dashboard.artifact.html` as the page and `files: {"AEP_hourly.csv": "AEP_hourly.csv"}`.
- Two marker pairs structure the file and the tools depend on them: `<!-- @@head:begin -->` to `<!-- @@head:end -->` around the title, fonts and styles, and `/* @@compute:begin */` to `/* @@compute:end */` around `aggregate()`, the only function that reads the data. New data logic goes inside the compute block; new styles go inside the head markers.
- Color follows the entity across charts: weekday blue, weekend orange, above-average month coral, other months quiet gray. The `:root` tokens passed the dataviz skill's color-vision validator in both themes; add a hue through that validator and define it for light and dark.

## Test and build

Run `node tools/test_and_build.js` after any change to the compute block or the page structure. It checks `aggregate()` against `tools/ref_stats.json` (83 figures) and writes the artifact body to `build/`.

The reference figures come from `tools/ref_stats.py`, standard library only. It encodes the same definitions as the compute block: summer is June to August, winter December to February, weekend Saturday and Sunday, and a month is above average when its mean exceeds the overall hourly mean. A definition change edits both files, then regenerates the JSON and re-runs the test.
