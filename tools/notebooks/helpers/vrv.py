# Verovio in a separate Python process.
#
# Some broken inputs crash Verovio 6.3 instead of giving an error (tested
# 2026-10-14): ABC without X: or K:, kern with too few columns. In a notebook
# a crash kills the kernel, and all your variables are gone. So Verovio runs
# in a child process: if it crashes, only the child dies. The child's error
# output is Verovio's log, which Jupyter would otherwise not show.

import json
import math
import os
import subprocess
import sys

from IPython.display import HTML, display

VEROVIO_VERSION = "6.3.0"

_CHILD = r'''
import json, sys
import verovio
job = json.loads(sys.stdin.read())
tk = verovio.toolkit()
tk.setOptions(job["options"])
out = {"ok": bool(tk.loadData(job["text"])), "version": tk.getVersion()}
if out["ok"]:
    out["svg"] = [tk.renderToSVG(p) for p in range(1, tk.getPageCount() + 1)] if job["svg"] else []
    out["mei"] = tk.getMEI()
    out["timemap"] = tk.renderToTimemap({"includeMeasures": True, "includeRests": True})
sys.stdout.write("\n@@RESULT@@\n" + json.dumps(out))
'''


# Load text in one format and return what the demos need (as on the web page).
# width: target width in pixels; Verovio lays the music out to fit it.
def read_score(fmt, text, width=800, scale=40, header="auto", svg=True):
    checked = precheck(fmt, text)
    result = {"ok": False, "errors": checked["errors"], "warnings": checked["warnings"],
              "log": "", "svg": [], "mei": "", "timemap": [], "notes": []}
    if result["errors"]:
        return result
    options = {
        "inputFrom": fmt, "scale": scale, "pageWidth": max(600, math.floor(width * 100 / scale + 0.5)),
        "adjustPageHeight": True, "pageMarginTop": 30, "pageMarginBottom": 30,
        "pageMarginLeft": 30, "pageMarginRight": 30, "header": header, "footer": "none",
    }
    child = subprocess.run(
        [sys.executable, "-c", _CHILD],
        input=json.dumps({"text": text, "options": options, "svg": svg}),
        capture_output=True, text=True, encoding="utf-8", timeout=300,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    result["log"] = child.stderr.strip()
    if child.returncode < 0:
        result["errors"].append(
            f"Verovio crashed on this text (signal {-child.returncode}). This happens with some broken "
            "input that Verovio does not report as an error. Undo your last change and try again.")
        return result
    if child.returncode > 0 or "\n@@RESULT@@\n" not in child.stdout:
        result["errors"].append("The Verovio process failed; see the log below. Did the install cell run?")
        return result
    out = json.loads(child.stdout.rsplit("\n@@RESULT@@\n", 1)[1])
    if not out["ok"]:
        result["errors"].append(f"Verovio could not read this text as {fmt}.")
        return result
    result.update(ok=True, version=out["version"], svg=out["svg"], mei=out["mei"], timemap=out["timemap"])
    result["notes"] = notes_from_timemap(result["timemap"], pitches_from_mei(result["mei"]))
    result["meter"] = meter_from_mei(result["mei"])
    result["fifths"] = fifths_from_mei(result["mei"])
    return result


# The score on a white background (readable in dark themes), then the messages.
def show(result):
    for page in result["svg"]:
        display(HTML(f'<div style="background:white; padding:4px; overflow-x:auto">{page}</div>'))
    for text in result["errors"]:
        print("Error:", text)
    for text in result["warnings"]:
        print("Warning:", text)
    for line in result["log"].splitlines():
        if line.strip():
            print("Verovio:", line)


def render(fmt, text, **options):
    result = read_score(fmt, text, **options)
    show(result)
    return result
