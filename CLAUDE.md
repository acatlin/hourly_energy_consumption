# Hourly energy consumption

PJM hourly load CSVs plus an interactive dashboard, `aep_dashboard.html`, whose zone menu covers the twelve per-zone files.

## Data access

Code loads data files by their raw GitHub URL, `https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/<file>`, so notebooks and pages run anywhere without a checkout. The README lists every file and URL.

## Dashboard

- One standalone HTML file, no framework; charts are inline SVG built by the page's own script. GitHub Pages serves it from `main` at https://acatlin.github.io/hourly_energy_consumption/, and a push to `main` deploys. The file keeps its AEP name; `?zone=<CODE>` opens it on another zone.
- It is also a claude.ai artifact: https://claude.ai/artifact/UUQySQvgfQT2kLAZKKpKyz. The artifact sandbox blocks fetches to outside hosts, so the page tries the raw URL first and falls back to `<ZONE>_hourly.csv` published next to it. Republish by passing that URL, with `build/aep_dashboard.artifact.html` as the page and `files` mapping every per-zone CSV to itself (`{"AEP_hourly.csv": "AEP_hourly.csv", ...}` for all twelve codes in the zones block, about 29 MB in one publish).
- Three marker pairs structure the file and the tools depend on them: `<!-- @@head:begin -->` to `<!-- @@head:end -->` around the title, fonts and styles; `/* @@zones:begin */` to `/* @@zones:end */` around `ZONES`, the list of per-zone files with their menu order and wording; and `/* @@compute:begin */` to `/* @@compute:end */` around `aggregate()`, the only function that reads the data. New data logic goes inside the compute block; new styles go inside the head markers; a new zone is one entry in the zones block plus its CSV in the repo and in `tools/ref_stats.py`.
- Color follows the entity across charts: weekday blue, weekend orange, above-average month coral, other months quiet gray. The `:root` tokens passed the dataviz skill's color-vision validator in both themes; add a hue through that validator and define it for light and dark.

## Test and build

Run `node tools/test_and_build.js` after any change to the compute block, the zones block or the page structure. It runs `aggregate()` on every `<ZONE>_hourly.csv` in the repo and checks the figures against `tools/ref_stats.json` (84 per zone, keyed by zone code), checks that the zones block, the JSON and the per-zone files name the same zones, and writes the artifact body to `build/`.

The reference figures come from `tools/ref_stats.py`, which downloads all twelve files from their raw URLs and uses pandas from the repo's git-ignored `.venv` (`python -m venv .venv`, then install `tools/requirements.txt` into it). Run it as `.venv\Scripts\python -I -X utf8 tools/ref_stats.py`: a plain `pip install` on this machine lands in the user site-packages, which `python -I` skips, and the venv's packages stay visible under `-I`. It encodes the same definitions as the compute block: summer is June to August, winter December to February, weekend Saturday and Sunday, and a month is above average when its mean exceeds the overall hourly mean. A definition change edits both files, then regenerates the JSON and re-runs the test.
