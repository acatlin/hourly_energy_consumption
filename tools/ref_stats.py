"""Reference figures for the AEP dashboard, computed independently of the page's JavaScript.

Reads AEP_hourly.csv from the raw GitHub URL with pandas and writes tools/ref_stats.json,
which tools/test_and_build.js compares against the dashboard's own aggregate() function.
Re-run only when the data or the definitions change.

Setup: python -m venv .venv && .venv\\Scripts\\python -m pip install -r tools/requirements.txt
Usage: .venv\\Scripts\\python -I -X utf8 tools/ref_stats.py [output.json]
"""
import json
import os
import sys

import pandas as pd

URL = "https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/AEP_hourly.csv"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SUMMER_MONTHS = [6, 7, 8]
WINTER_MONTHS = [12, 1, 2]

out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_stats.json")

df = pd.read_csv(URL).rename(columns={"AEP_MW": "mw"})
when = pd.to_datetime(df["Datetime"])
df["hour"] = when.dt.hour
df["month"] = when.dt.month
df["dow"] = when.dt.dayofweek  # Monday = 0 ... Sunday = 6
df["weekend"] = df["dow"] >= 5

peak = df.loc[df["mw"].idxmax()]
low = df.loc[df["mw"].idxmin()]
in_summer = df["month"].isin(SUMMER_MONTHS)
in_winter = df["month"].isin(WINTER_MONTHS)
by_hour = df.groupby(["weekend", "hour"])["mw"].mean().unstack("weekend")  # 24 rows, columns False/True
by_month = df.groupby("month")["mw"].mean()
by_dow = df.groupby("dow")["mw"].mean()

out = {
    "rows": len(df),
    "dup_timestamps": int(df["Datetime"].duplicated().sum()),
    "nonpositive": int((df["mw"] <= 0).sum()),
    "first": df["Datetime"].min(),
    "last": df["Datetime"].max(),
    "avg": df["mw"].mean(),
    "max": [float(peak["mw"]), peak["Datetime"]],
    "min": [float(low["mw"]), low["Datetime"]],
    "summer_avg": df.loc[in_summer, "mw"].mean(),
    "winter_avg": df.loc[in_winter, "mw"].mean(),
    "summer_n": int(in_summer.sum()),
    "winter_n": int(in_winter.sum()),
    "hour_weekday": by_hour[False].tolist(),
    "hour_weekend": by_hour[True].tolist(),
    "weekday_n": int((~df["weekend"]).sum()),
    "weekend_n": int(df["weekend"].sum()),
    "month": {int(m): v for m, v in by_month.items()},
    "dow": {DAYS[d]: v for d, v in by_dow.items()},
}

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)

print(f"rows={out['rows']} dups={out['dup_timestamps']} nonpositive={out['nonpositive']} range={out['first']}..{out['last']}")
print(f"avg={out['avg']:.1f} max={out['max']} min={out['min']}")
print(f"summer={out['summer_avg']:.1f} winter={out['winter_avg']:.1f} summer/winter-1={(out['summer_avg'] / out['winter_avg'] - 1) * 100:.2f}%")
print(f"wrote {out_path}")
