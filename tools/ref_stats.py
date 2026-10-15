"""Reference figures for the dashboard, computed independently of the page's JavaScript.

Reads every per-zone file (<ZONE>_hourly.csv) from its raw GitHub URL with pandas and writes
tools/ref_stats.json, keyed by zone code, which tools/test_and_build.js compares against the
dashboard's own aggregate() function. Re-run only when the data or the definitions change.

Setup: python -m venv .venv && .venv\\Scripts\\python -m pip install -r tools/requirements.txt
Usage: .venv\\Scripts\\python -I -X utf8 tools/ref_stats.py [output.json]
"""
import json
import os
import sys

import pandas as pd

BASE = "https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/"
ZONES = ["AEP", "COMED", "DAYTON", "DEOK", "DOM", "DUQ", "EKPC", "FE", "NI", "PJME", "PJMW", "PJM_Load"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SUMMER_MONTHS = [6, 7, 8]
WINTER_MONTHS = [12, 1, 2]


def figures(zone):
    """The dashboard's figures for one zone, from the raw CSV, with the same definitions as the compute block."""
    df = pd.read_csv(BASE + f"{zone}_hourly.csv").rename(columns={f"{zone}_MW": "mw"})
    when = pd.to_datetime(df["Datetime"])
    df["hour"] = when.dt.hour
    df["month"] = when.dt.month
    df["dow"] = when.dt.dayofweek  # Monday = 0 ... Sunday = 6
    df["weekend"] = df["dow"] >= 5

    # A reading below one fifth of the zone's median is a metering artifact, not load (the compute block
    # explains the threshold): it counts toward rows, dup_timestamps, first and last but toward no other figure.
    median = float(df["mw"].median())
    artifact = df["mw"] < 0.2 * median
    dropped = df[artifact].sort_values("Datetime")
    kept = df[~artifact]

    peak = kept.loc[kept["mw"].idxmax()]
    low = kept.loc[kept["mw"].idxmin()]
    in_summer = kept["month"].isin(SUMMER_MONTHS)
    in_winter = kept["month"].isin(WINTER_MONTHS)
    by_hour = kept.groupby(["weekend", "hour"])["mw"].mean().unstack("weekend")  # 24 rows, columns False/True
    by_month = kept.groupby("month")["mw"].mean()
    by_dow = kept.groupby("dow")["mw"].mean()

    return {
        "rows": len(df),
        "dup_timestamps": int(df["Datetime"].duplicated().sum()),
        "first": df["Datetime"].min(),
        "last": df["Datetime"].max(),
        "median": median,
        "excluded": [[float(v), t] for v, t in zip(dropped["mw"], dropped["Datetime"])],
        "avg": kept["mw"].mean(),
        "max": [float(peak["mw"]), peak["Datetime"]],
        "min": [float(low["mw"]), low["Datetime"]],
        "summer_avg": kept.loc[in_summer, "mw"].mean(),
        "winter_avg": kept.loc[in_winter, "mw"].mean(),
        "summer_n": int(in_summer.sum()),
        "winter_n": int(in_winter.sum()),
        "hour_weekday": by_hour[False].tolist(),
        "hour_weekend": by_hour[True].tolist(),
        "weekday_n": int((~kept["weekend"]).sum()),
        "weekend_n": int(kept["weekend"].sum()),
        "month": {int(m): v for m, v in by_month.items()},
        "dow": {DAYS[d]: v for d, v in by_dow.items()},
    }


out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_stats.json")

out = {}
for zone in ZONES:
    f = out[zone] = figures(zone)
    print(f"{zone}: rows={f['rows']} dups={f['dup_timestamps']} excluded={len(f['excluded'])} range={f['first']}..{f['last']}")
    print(f"  avg={f['avg']:.1f} max={f['max']} min={f['min']} summer/winter-1={(f['summer_avg'] / f['winter_avg'] - 1) * 100:.2f}%")

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)

print(f"wrote {out_path} ({len(out)} zones)")
