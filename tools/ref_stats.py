"""Reference figures for the AEP dashboard, computed independently of the page's JavaScript.

Reads AEP_hourly.csv from the raw GitHub URL with the standard library only and writes
tools/ref_stats.json, which tools/test_and_build.js compares against the dashboard's own
aggregate() function. Re-run only when the data or the definitions change.

Usage: python -I -X utf8 tools/ref_stats.py [output.json]
"""
import csv
import datetime
import io
import json
import os
import sys
import urllib.request

URL = "https://raw.githubusercontent.com/acatlin/hourly_energy_consumption/main/AEP_hourly.csv"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_stats.json")

raw = urllib.request.urlopen(URL, timeout=120).read().decode("utf-8")
rows = list(csv.reader(io.StringIO(raw)))[1:]

n = len(rows)
total = 0.0
mx = (-1.0, "")
mn = (1e18, "")
hour_weekday = [[0.0, 0] for _ in range(24)]
hour_weekend = [[0.0, 0] for _ in range(24)]
month = [[0.0, 0] for _ in range(13)]
dow = [[0.0, 0] for _ in range(7)]
summer = [0.0, 0]
winter = [0.0, 0]
nonpositive = 0

for ts, value in rows:
    v = float(value)
    y, m, d, h = int(ts[0:4]), int(ts[5:7]), int(ts[8:10]), int(ts[11:13])
    weekday = datetime.date(y, m, d).weekday()  # Monday = 0 ... Sunday = 6
    total += v
    if v <= 0:
        nonpositive += 1
    if v > mx[0]:
        mx = (v, ts)
    if v < mn[0]:
        mn = (v, ts)
    bucket = hour_weekend if weekday >= 5 else hour_weekday
    bucket[h][0] += v
    bucket[h][1] += 1
    month[m][0] += v
    month[m][1] += 1
    dow[weekday][0] += v
    dow[weekday][1] += 1
    if m in (6, 7, 8):
        summer[0] += v
        summer[1] += 1
    if m in (12, 1, 2):
        winter[0] += v
        winter[1] += 1


def mean(pair):
    return pair[0] / pair[1] if pair[1] else None


out = {
    "rows": n,
    "dup_timestamps": n - len({r[0] for r in rows}),
    "nonpositive": nonpositive,
    "first": min(r[0] for r in rows),
    "last": max(r[0] for r in rows),
    "avg": total / n,
    "max": mx,
    "min": mn,
    "summer_avg": mean(summer),
    "winter_avg": mean(winter),
    "summer_n": summer[1],
    "winter_n": winter[1],
    "hour_weekday": [mean(p) for p in hour_weekday],
    "hour_weekend": [mean(p) for p in hour_weekend],
    "weekday_n": sum(p[1] for p in hour_weekday),
    "weekend_n": sum(p[1] for p in hour_weekend),
    "month": {i: mean(month[i]) for i in range(1, 13)},
    "dow": {DAYS[i]: mean(dow[i]) for i in range(7)},
}

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)

print(f"rows={n} dups={out['dup_timestamps']} nonpositive={nonpositive} range={out['first']}..{out['last']}")
print(f"avg={out['avg']:.1f} max={mx} min={mn}")
print(f"summer={out['summer_avg']:.1f} winter={out['winter_avg']:.1f} summer/winter-1={(out['summer_avg'] / out['winter_avg'] - 1) * 100:.2f}%")
print(f"wrote {out_path}")
