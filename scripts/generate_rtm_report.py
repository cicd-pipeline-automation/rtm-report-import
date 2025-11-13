#!/usr/bin/env python3
import argparse, glob, os, xml.etree.ElementTree as ET
from datetime import datetime
from html import escape


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", required=True)
    p.add_argument("--output", "-o", required=True)
    p.add_argument("--title", "-t", default="RTM Automated Test Report")
    p.add_argument("--test-execution-key", "-e", default="")
    return p.parse_args()


def parse_reports(path):
    results, totals = [], {"passed":0, "failed":0, "skipped":0, "total":0}

    for f in glob.glob(os.path.join(path, "*.xml")):
        try:
            root = ET.parse(f).getroot()
        except:
            continue

        suites = [root] if root.tag == "testsuite" else root.findall("testsuite")

        for ts in suites:
            suite = ts.attrib.get("name", os.path.basename(f))
            for tc in ts.findall("testcase"):
                name = tc.attrib.get("name")
                cls = tc.attrib.get("classname", "")
                time = float(tc.attrib.get("time", "0") or 0)

                status = "passed"
                msg = ""

                if tc.find("failure") is not None:
                    status = "failed"
                    msg = (tc.find("failure").text or "").strip()
                elif tc.find("error") is not None:
                    status = "failed"
                    msg = (tc.find("error").text or "").strip()
                elif tc.find("skipped") is not None:
                    status = "skipped"

                results.append({
                    "suite": suite,
                    "classname": cls,
                    "name": name,
                    "time": time,
                    "status": status,
                    "message": msg
                })

                totals["total"] += 1
                totals[status] += 1

    return results, totals


def generate_html(title, results, totals, exec_key):
    p = totals["passed"]
    f = totals["failed"]
    s = totals["skipped"]
    t = totals["total"]

    generated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = ""
    for r in results:
        rows += f"""
        <tr>
            <td>{escape(r['suite'])}</td>
            <td>{escape(r['classname'])}</td>
            <td>{escape(r['name'])}</td>
            <td><span class='status-pill status-{r['status']}'>{r['status'].upper()}</span></td>
            <td>{r['time']:.3f}</td>
            <td>{escape(r['message'])}</td>
        </tr>
        """

    exec_html = f"<p><b>RTM Execution Key:</b> {exec_key}</p>" if exec_key else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{escape(title)}</title>

<style>
body{{{{font-family:Arial;margin:20px;background:#f4f4f6;}}}}
table{{{{width:100%;border-collapse:collapse;background:white;}}}}
th,td{{{{padding:8px;border-bottom:1px solid #eee;}}}}
th{{{{background:#f0f0f5;}}}}

.status-pill{{{{padding:3px 8px;border-radius:8px;color:white;}}}}
.status-passed{{{{background:#28a745;}}}}
.status-failed{{{{background:#dc3545;}}}}
.status-skipped{{{{background:#ffc107;color:#333;}}}}

.summary-card{{{{display:inline-block;padding:12px;background:white;margin-right:10px;
               border-radius:8px;box-shadow:0 0 4px #0001;}}}}

.chart-box{{{{width:350px;background:white;padding:10px;margin-top:20px;
            border-radius:8px;box-shadow:0 0 4px #0001;}}}}
</style>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>

<body>
<h1>{escape(title)}</h1>
<p>Generated: {generated}</p>
{exec_html}

<h2>Summary</h2>
<div class="summary-card">Total: <b>{t}</b></div>
<div class="summary-card" style="color:#28a745">Passed: <b>{p}</b></div>
<div class="summary-card" style="color:#dc3545">Failed: <b>{f}</b></div>
<div class="summary-card" style="color:#ffc107">Skipped: <b>{s}</b></div>

<h2>Charts</h2>
<div class="chart-box"><canvas id="pie"></canvas></div>
<div class="chart-box"><canvas id="bar"></canvas></div>

<h2>Details</h2>
<table>
<tr>
<th>Suite</th><th>Class</th><th>Name</th><th>Status</th><th>Time</th><th>Message</th>
</tr>
{rows}
</table>

<script>

new Chart(document.getElementById('pie'), {{{{
    type:'pie',
    data: {{{{
        labels:['Passed','Failed','Skipped'],
        datasets:[{{{{ data:[{p},{f},{s}], backgroundColor:['#28a745','#dc3545','#ffc107'] }}}}]
    }}}}
}});

new Chart(document.getElementById('bar'), {{{{
    type:'bar',
    data: {{{{
        labels:['Passed','Failed','Skipped'],
        datasets:[{{{{ label:'Tests', data:[{p},{f},{s}] }}}}]
    }}}},

    options: {{{{
        scales: {{{{
            y: {{{{ beginAtZero:true }}}}
        }}}}
    }}}}

}});

</script>

</body>
</html>
"""

    return html


def main():
    args = parse_args()
    results, totals = parse_reports(args.input)
    html = generate_html(args.title, results, totals, args.test_execution_key)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
