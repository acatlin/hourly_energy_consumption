#!/usr/bin/env node
// Tests the dashboard's compute block and builds the artifact body.
//
// 1. Extracts aggregate() from aep_dashboard.html (between the @@compute markers),
//    runs it on AEP_hourly.csv and compares every figure with tools/ref_stats.json.
// 2. Writes the page without its HTML skeleton (head markers + body) to build/, which is
//    the file to publish as a claude.ai artifact (the Artifact tool adds its own skeleton).
//
// Usage: node tools/test_and_build.js [html] [csv] [ref.json] [out.html]
// Exit code 1 when any check fails.

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const htmlPath = process.argv[2] || path.join(root, "aep_dashboard.html");
const csvPath = process.argv[3] || path.join(root, "AEP_hourly.csv");
const refPath = process.argv[4] || path.join(__dirname, "ref_stats.json");
const outPath = process.argv[5] || path.join(root, "build", "aep_dashboard.artifact.html");

const html = fs.readFileSync(htmlPath, "utf8");
const block = html.split("/* @@compute:begin */")[1].split("/* @@compute:end */")[0];
const aggregate = new Function(block + "\nreturn aggregate;")();

const t0 = Date.now();
const stats = aggregate(fs.readFileSync(csvPath, "utf8"));
const ms = Date.now() - t0;
const ref = JSON.parse(fs.readFileSync(refPath, "utf8"));

const close = (a, b) => Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b));
const checks = [];
const eq = (name, a, b) => checks.push([name, typeof b === "number" ? close(a, b) : a === b, a, b]);

eq("rows", stats.rows, ref.rows);
eq("avg", stats.avg, ref.avg);
eq("max", stats.max, ref.max[0]);
eq("maxT", stats.maxT, ref.max[1]);
eq("min", stats.min, ref.min[0]);
eq("minT", stats.minT, ref.min[1]);
eq("first", stats.first, ref.first);
eq("last", stats.last, ref.last);
eq("summerAvg", stats.summerAvg, ref.summer_avg);
eq("winterAvg", stats.winterAvg, ref.winter_avg);
eq("summerN", stats.summerN, ref.summer_n);
eq("winterN", stats.winterN, ref.winter_n);
eq("weekdayN", stats.weekdayN, ref.weekday_n);
eq("weekendN", stats.weekendN, ref.weekend_n);
for (let h = 0; h < 24; h++) {
  eq("hourWeekday[" + h + "]", stats.hourWeekday[h], ref.hour_weekday[h]);
  eq("hourWeekend[" + h + "]", stats.hourWeekend[h], ref.hour_weekend[h]);
}
for (let m = 1; m <= 12; m++) eq("month[" + m + "]", stats.month[m - 1], ref.month[String(m)]);
["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].forEach((d, i) => eq("dow[" + d + "]", stats.dow[i], ref.dow[d]));
eq("monthN sum", stats.monthN.reduce((a, b) => a + b, 0), ref.rows);
eq("dowN sum", stats.dowN.reduce((a, b) => a + b, 0), ref.rows);

const failed = checks.filter((c) => !c[1]);
console.log(`${checks.length - failed.length}/${checks.length} checks passed; aggregate() took ${ms} ms`);
failed.forEach((c) => console.log("FAIL", c[0], "got", c[2], "expected", c[3]));

const head = html.split("<!-- @@head:begin -->")[1].split("<!-- @@head:end -->")[0];
const body = html.split("<body>")[1].split("</body>")[0];
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, head.trim() + "\n" + body.trim() + "\n");
console.log("artifact body written:", path.relative(root, outPath), fs.statSync(outPath).size, "bytes");

process.exit(failed.length ? 1 : 0);
