#!/usr/bin/env node
// Tests the dashboard's compute block on every zone and builds the artifact body.
//
// 1. Extracts the zone list (between the @@zones markers) and aggregate() (between the @@compute
//    markers) from aep_dashboard.html, runs aggregate() on every <ZONE>_hourly.csv in the data
//    directory and compares each figure with tools/ref_stats.json, which is keyed by zone code.
//    It also checks that the page, the reference file and the data directory name the same zones.
// 2. Writes the page without its HTML skeleton (head markers + body) to build/, which is
//    the file to publish as a claude.ai artifact (the Artifact tool adds its own skeleton).
//
// Usage: node tools/test_and_build.js [html] [data dir] [ref.json] [out.html]
// Exit code 1 when any check fails.

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const htmlPath = process.argv[2] || path.join(root, "aep_dashboard.html");
const dataDir = process.argv[3] || root;
const refPath = process.argv[4] || path.join(__dirname, "ref_stats.json");
const outPath = process.argv[5] || path.join(root, "build", "aep_dashboard.artifact.html");

const html = fs.readFileSync(htmlPath, "utf8");
const between = (start, end) => {
  const parts = html.split(start);
  if (parts.length !== 2 || !parts[1].includes(end)) throw new Error(`expected exactly one ${start} ... ${end} block in ${htmlPath}`);
  return parts[1].split(end)[0];
};
const ZONES = new Function(between("/* @@zones:begin */", "/* @@zones:end */") + "\nreturn ZONES;")();
const aggregate = new Function(between("/* @@compute:begin */", "/* @@compute:end */") + "\nreturn aggregate;")();
const ref = JSON.parse(fs.readFileSync(refPath, "utf8"));

const close = (a, b) => Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b));
const checks = [];
const eq = (name, a, b) => checks.push([name, typeof b === "number" ? close(a, b) : a === b, a, b]);

// The page's zone list, the reference figures and the per-zone files in the data directory must agree
const codes = ZONES.map((z) => z.code);
const sorted = (a) => a.slice().sort().join(",");
const filesOnDisk = fs.readdirSync(dataDir).filter((f) => /^[A-Za-z_]+_hourly\.csv$/.test(f)).map((f) => f.replace(/_hourly\.csv$/, ""));
eq("zone codes unique", new Set(codes).size, codes.length);
eq("zones block names every per-zone file", sorted(codes), sorted(filesOnDisk));
eq("reference figures cover the same zones", sorted(codes), sorted(Object.keys(ref)));
ZONES.forEach((z) => eq(`${z.code} has name, area and desc`, Boolean(z.name && z.area && z.desc), true));

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
let totalMs = 0;
for (const code of codes) {
  const r = ref[code];
  const csvPath = path.join(dataDir, `${code}_hourly.csv`);
  if (!r || !fs.existsSync(csvPath)) continue; // already reported by the zone-set checks above
  const t0 = Date.now();
  const stats = aggregate(fs.readFileSync(csvPath, "utf8"));
  totalMs += Date.now() - t0;
  const check = (name, a, b) => eq(`${code} ${name}`, a, b);

  check("rows", stats.rows, r.rows);
  check("dups", stats.dups, r.dup_timestamps);
  check("avg", stats.avg, r.avg);
  check("max", stats.max, r.max[0]);
  check("maxT", stats.maxT, r.max[1]);
  check("min", stats.min, r.min[0]);
  check("minT", stats.minT, r.min[1]);
  check("first", stats.first, r.first);
  check("last", stats.last, r.last);
  check("summerAvg", stats.summerAvg, r.summer_avg);
  check("winterAvg", stats.winterAvg, r.winter_avg);
  check("summerN", stats.summerN, r.summer_n);
  check("winterN", stats.winterN, r.winter_n);
  check("weekdayN", stats.weekdayN, r.weekday_n);
  check("weekendN", stats.weekendN, r.weekend_n);
  for (let h = 0; h < 24; h++) {
    check("hourWeekday[" + h + "]", stats.hourWeekday[h], r.hour_weekday[h]);
    check("hourWeekend[" + h + "]", stats.hourWeekend[h], r.hour_weekend[h]);
  }
  for (let m = 1; m <= 12; m++) check("month[" + m + "]", stats.month[m - 1], r.month[String(m)]);
  DAYS.forEach((d, i) => check("dow[" + d + "]", stats.dow[i], r.dow[d]));
  check("monthN sum", stats.monthN.reduce((a, b) => a + b, 0), r.rows);
  check("dowN sum", stats.dowN.reduce((a, b) => a + b, 0), r.rows);
}

const failed = checks.filter((c) => !c[1]);
console.log(`${checks.length - failed.length}/${checks.length} checks passed across ${codes.length} zones; aggregate() took ${totalMs} ms in total`);
failed.forEach((c) => console.log("FAIL", c[0], "got", c[2], "expected", c[3]));

const head = html.split("<!-- @@head:begin -->")[1].split("<!-- @@head:end -->")[0];
const body = html.split("<body>")[1].split("</body>")[0];
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, head.trim() + "\n" + body.trim() + "\n");
console.log("artifact body written:", path.relative(root, outPath), fs.statSync(outPath).size, "bytes");

process.exit(failed.length ? 1 : 0);
