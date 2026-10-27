"""Preserve completed Schumann OMR runs without source images or model weights.

Usage: python tools/collect_schumann_omr.py /path/to/runtime
The runtime contains runs/{homr-fullpage-v1,homr-two-systems-v1,
oemer-fullpage-v1,oemer-fullpage-v2,oemer-fullpage-v3} and verify-input/.
Collect only after all subprocesses have completed. A new output folder is
required; existing recordings/edits are never overwritten.
"""

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent / "notebooks/helpers"))
from omr import file_sha256, musicxml_summary, render_score_to_svg, save_json

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/02-building-an-edition"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("--output", type=Path, default=SESSION / "teacher/references/omr-schumann")
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    mapping = {"homr-fullpage": "homr-fullpage-v1", "homr-two-systems": "homr-two-systems-v1",
               "oemer-default": "oemer-fullpage-v1", "oemer-legacy-cpu": "oemer-fullpage-v2",
               "oemer-cpu": "oemer-fullpage-v3"}
    for name, original in mapping.items():
        source, dest = args.runtime / "runs" / original, out / name
        dest.mkdir()
        record = json.loads((source / "run.json").read_text())
        assert record["status"] != "running", original
        shutil.copyfile(source / "run.json", dest / "run.json")
        original_log = (source / "run.log").read_bytes()
        (dest / "run-original.log.gz").write_bytes(gzip.compress(original_log, mtime=0))
        text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", original_log.decode("utf-8", errors="replace"))
        lines = [line for line in text.splitlines()
                 if not re.match(r"(?:1st|2nd)_(?:model\.onnx|weights\.h5):", line)]
        (dest / "run.log").write_text("# Reading copy: download-progress updates and ANSI colour removed.\n"
                                      "# Exact original: run-original.log.gz (outside the embedded notebook bundle).\n"
                                      + "\n".join(lines) + "\n")
        save_json(dest / "log-provenance.json", {"original_sha256": hashlib.sha256(original_log).hexdigest(),
                  "original_bytes": len(original_log), "original_gzip_sha256": file_sha256(dest / "run-original.log.gz"),
                  "reading_copy_sha256": file_sha256(dest / "run.log"),
                  "transformation": "Remove CR-separated download progress lines and ANSI colour; prepend notice."})
        packages = record["environment"]["packages"]
        (dest / "requirements.txt").write_text("# Complete recorded environment; Python 3.11/Linux. Install with uv pip --no-deps.\n"
                                               + "\n".join(f"{n}=={v}" for n, v in sorted(packages.items())) + "\n")
        if (source / "raw.musicxml").exists():
            shutil.copyfile(source / "raw.musicxml", dest / "raw.musicxml")
            assert file_sha256(dest / "raw.musicxml") == record["output"]["sha256"]
            save_json(dest / "structure.json", musicxml_summary(dest / "raw.musicxml"))
        for subfolder in ("converted", "rendered"):
            if (source / subfolder).exists():
                shutil.copytree(source / subfolder, dest / subfolder)
    shutil.copyfile(args.runtime / "verify-input/preparation.json", out / "source.json")
    shutil.copyfile(SESSION / "sources/sources.json", out / "source-catalogue.json")
    reference = out / "reference"
    reference.mkdir()
    shutil.copyfile(SESSION / "examples/schumann/LICENSE", reference / "LICENSE")
    shutil.copyfile(SESSION / "examples/schumann/starter.mei", reference / "starter-whole-piece.mei")
    # Select the teaching starter's first nine measures for the comparison;
    # there are no body slurs/control events to leave dangling at the cut.
    ns = {"m": "http://www.music-encoding.org/ns/mei"}
    ET.register_namespace("", ns["m"])
    tree = ET.parse(reference / "starter-whole-piece.mei")
    body = tree.getroot().find("m:music/m:body", ns)
    parents = {child: parent for parent in body.iter() for child in parent}
    measures = body.findall(".//m:measure", ns)
    assert [m.get("n") for m in measures[:9]] == list(map(str, range(1, 10)))
    for measure in measures[9:]:
        parents[measure].remove(measure)
    for element in list(body.iter()):
        if element.tag in {f"{{{ns['m']}}}sb", f"{{{ns['m']}}}pb"}:
            parents[element].remove(element)
    excerpt = reference / "starter-first-nine.mei"
    tree.write(excerpt, encoding="utf-8", xml_declaration=True)
    preview = render_score_to_svg(excerpt, reference / "rendered")
    assert preview["returncode"] == 0, preview
    validation = json.loads((SESSION / "teacher/schumann/validation/run.json").read_text())
    save_json(out / "conversion-environment.json", {
        "camat": validation["camat"], "python": validation["python"],
        "dependency_versions": validation["dependency_versions"],
        "rendering": "Separate lecture Python 3.11 environment, Verovio 6.3.0-425dd7b; full-page failure and crop success.",
        "limit": "Editable CAMAT checkout, not a clean installation of the PyPI 0.2.8 release."})
    save_json(reference / "derivation.json", {
        "basis": "Prepared teaching starter, derived from Maja Hartwig / MEI Sample Collection.",
        "upstream_revision": "e4a3c4dece588ae0bdb13e5cf956340dcd99b447",
        "whole_piece_sha256": file_sha256(reference / "starter-whole-piece.mei"),
        "selection": "Keep only body measures labelled 1–9; omit layout breaks; preserve header credits.",
        "expression": "Deliberately absent; not an OMR output and not a complete gold standard.",
        "source_based_pitch_corrections": json.loads((SESSION / "teacher/schumann/changes.json").read_text())["source_based_pitch_corrections"]})
    (out / "README.md").write_text("""# Schumann OMR recordings — 24 October 2026

Use the [executed reference notebook](02_schumann_omr_recorded.ipynb) to inspect
the results. The portable [student notebook](../../notebooks/02_schumann_omr.ipynb)
loads these recordings from the separate `schumann-omr-recordings.zip` data file.
Keep the ZIP beside a downloaded notebook for offline review; `get_notebooks.py`
copies both files. There is no encoded data blob in the notebook.
Its optional cells prepare the source and run fresh recognition/conversion.

Two HOMR 0.7.0 CPU examples: whole page and first two systems. OeMeR 0.1.8
records the initial GPU-runtime failure, an older CPU-runtime load failure,
and the CPU 1.20.1 attempt. Read each run.json for its actual outcome.
These are selected case studies, not an accuracy or speed ranking.

Raw MusicXML exports are untouched. converted/ contains CAMAT outputs/reports;
rendered/ contains engravings and exact renderer diagnostics. reference/ holds
the deliberately reduced teaching MEI, its first-nine-measure selection and
the upstream license. The print governs musical decisions. The comparison
found two A3 → F3 discrepancies in the reused MEI; the teaching files now
record those corrections. No complete note-level gold standard is claimed.

run.log is a reading copy with download progress and ANSI colour removed.
run-original.log.gz preserves the exact original; log-provenance.json records
both identities. Original compressed logs are omitted from the portable bundle.
run.json records command, timestamp, elapsed time, package versions, input/output
hashes and model hashes. Timings include first-run downloads where applicable.
requirements.txt freezes each complete environment, installed with --no-deps.
For OeMeR CPU this deliberately substitutes onnxruntime for its declared GPU
dependency; it is a tested local workaround, not a supported platform guarantee.

Source PDFs/images, diagnostic images and models are excluded. Fetch the scan
at runtime; see source.json and source-catalogue.json. Input was original PDF
p.8 / printed p.8 (300 dpi, 4167×5617); the HOMR crop is (100,500,4000,2280),
without resampling. Engine-internal resizing/preprocessing is additional.
The reference notebook does not embed scanned source images.

To reproduce the portable bundle after changing these files:
`python tools/pack_schumann_omr.py`, then `python tools/build_notebooks.py`
(from the repository root). Recording collection is in tools/collect_schumann_omr.py;
the notebook source is tools/notebooks/02_schumann_omr.py and the invocation,
preparation and inspection helpers are tools/notebooks/helpers/omr.py.
""", encoding="utf-8")
    manifest = {"recorded_on": "2026-10-24", "host": {"platform": platform.platform(), "machine": platform.machine()},
                "files_sha256": {p.relative_to(out).as_posix(): file_sha256(p) for p in sorted(out.rglob("*"))
                                 if p.is_file() and p.suffix != ".gz"}}
    save_json(out / "manifest.json", manifest)
    print("Collected", len(manifest["files_sha256"]), "files in", out)


if __name__ == "__main__":
    main()
