# Hourly Energy Consumption (PJM)

Hourly electricity consumption, in megawatts (MW), for regions of the PJM Interconnection, a regional transmission organization serving parts of the eastern United States. The data spans April 1998 through August 2018. Each file covers one region and its own date range.

Source: PJM Interconnection, as packaged in the Kaggle dataset [Hourly Energy Consumption](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption).

## Dashboard

An interactive dashboard of the per-region series (key figures, hour-of-day, monthly and day-of-week patterns) is served from this repo by GitHub Pages at https://acatlin.github.io/hourly_energy_consumption/. The page is `aep_dashboard.html`; its zone menu covers all twelve regions, and `?zone=COMED` (any code from the table below) opens the page on that region. It fetches the selected `<REGION>_hourly.csv` from the raw URL listed below and computes every figure in the browser.

To work on it, run `node tools/test_and_build.js`. It runs the page's aggregation code on every per-region file, checks the figures against `tools/ref_stats.json` and writes a copy of the page without the HTML skeleton to `build/` for publishing elsewhere. `tools/ref_stats.py` regenerates the reference figures for every region from the raw CSVs with pandas. Set up once with `python -m venv .venv` and `.venv\Scripts\python -m pip install -r tools/requirements.txt`, then run `.venv\Scripts\python -I -X utf8 tools/ref_stats.py`.

## Data files

Each per-region file has two columns: `Datetime` (an hourly timestamp, with no time zone) and `<REGION>_MW`. Rows are not guaranteed to be in chronological order, so sort by `Datetime` after loading.

| File | Region | Rows | From | To | Size |
|------|--------|-----:|------|----|-----:|
| `AEP_hourly.csv` | American Electric Power | 121,273 | 2004-10-01 | 2018-08-03 | 3.4 MB |
| `COMED_hourly.csv` | Commonwealth Edison (Chicago area) | 66,497 | 2011-01-01 | 2018-08-03 | 1.8 MB |
| `DAYTON_hourly.csv` | Dayton Power and Light | 121,275 | 2004-10-01 | 2018-08-03 | 3.3 MB |
| `DEOK_hourly.csv` | Duke Energy Ohio/Kentucky | 57,739 | 2012-01-01 | 2018-08-03 | 1.6 MB |
| `DOM_hourly.csv` | Dominion Virginia Power | 116,189 | 2005-05-01 | 2018-08-03 | 3.2 MB |
| `DUQ_hourly.csv` | Duquesne Light (Pittsburgh area) | 119,068 | 2005-01-01 | 2018-08-03 | 3.2 MB |
| `EKPC_hourly.csv` | East Kentucky Power Cooperative | 45,334 | 2013-06-01 | 2018-08-03 | 1.2 MB |
| `FE_hourly.csv` | FirstEnergy | 62,874 | 2011-06-01 | 2018-08-03 | 1.7 MB |
| `NI_hourly.csv` | Northern Illinois Hub | 58,450 | 2004-05-01 | 2011-01-01 | 1.6 MB |
| `PJME_hourly.csv` | PJM East | 145,366 | 2002-01-01 | 2018-08-03 | 4.1 MB |
| `PJMW_hourly.csv` | PJM West | 143,206 | 2002-04-01 | 2018-08-03 | 3.9 MB |
| `PJM_Load_hourly.csv` | PJM total load (before the East/West split) | 32,896 | 1998-04-01 | 2002-01-01 | 0.9 MB |

Two combined files hold every region as a column in one wide table, with blanks where a region has no data for that hour:

| File | Columns | Rows | From | To | Size |
|------|---------|-----:|------|----|-----:|
| `pjm_hourly_est.csv` | `Datetime`, `AEP`, `COMED`, `DAYTON`, `DEOK`, `DOM`, `DUQ`, `EKPC`, `FE`, `NI`, `PJME`, `PJMW`, `PJM_Load` | 178,262 | 1998-04-01 | 2018-08-03 | 12.7 MB |
| `est_hourly.paruqet` | same table in Apache Parquet format | | | | 3.7 MB |

The misspelled `.paruqet` extension is preserved from the source dataset. The file is a valid Parquet file.

## Loading the data in code

Reference data files by their raw GitHub URL rather than a local path, so code runs the same anywhere:

```python
import pandas as pd

BASE = "https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/"

aep = (
    pd.read_csv(BASE + "AEP_hourly.csv", index_col="Datetime", parse_dates=True)
    .sort_index()
)

combined = pd.read_csv(BASE + "pjm_hourly_est.csv", index_col="Datetime", parse_dates=True)
```

Reading the Parquet file requires `pyarrow` or `fastparquet`:

```python
est = pd.read_parquet(BASE + "est_hourly.paruqet")
```

## Raw URLs

| File | Raw URL |
|------|---------|
| `AEP_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/AEP_hourly.csv |
| `COMED_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/COMED_hourly.csv |
| `DAYTON_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/DAYTON_hourly.csv |
| `DEOK_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/DEOK_hourly.csv |
| `DOM_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/DOM_hourly.csv |
| `DUQ_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/DUQ_hourly.csv |
| `EKPC_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/EKPC_hourly.csv |
| `FE_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/FE_hourly.csv |
| `NI_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/NI_hourly.csv |
| `PJME_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/PJME_hourly.csv |
| `PJMW_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/PJMW_hourly.csv |
| `PJM_Load_hourly.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/PJM_Load_hourly.csv |
| `pjm_hourly_est.csv` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/pjm_hourly_est.csv |
| `est_hourly.paruqet` | https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/est_hourly.paruqet |
