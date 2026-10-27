"""Portable helpers for the Schumann OMR reference notebook (standard library)."""

from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def prepare_schumann_image(pdf, destination, *, allow_download=False):
    """Fetch/check the frozen witness and render its eighth PDF page locally.

    Poppler's pdftoppm must be installed separately. Source media never enter
    the recorded notebook bundle. PNG bytes may differ across Poppler versions.
    """
    import urllib.request
    pdf, destination = Path(pdf).resolve(), Path(destination).resolve()
    expected = "893ab03c376724a9f4474497130eb2d8510ba9d71f05bb270c8f6000b731e289"
    url = "https://s9.imslp.org/files/imglnks/usimg/0/0a/IMSLP51556-PMLP02707-RS67.pdf"
    if not pdf.exists():
        if not allow_download:
            raise FileNotFoundError("Set allow_download=True or supply the frozen IMSLP PDF.")
        pdf.parent.mkdir(parents=True, exist_ok=True)
        temporary = pdf.with_suffix(".download")
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as out:
            shutil.copyfileobj(response, out)
        if file_sha256(temporary) != expected:
            temporary.unlink()
            raise ValueError("The downloaded PDF differs from the frozen witness.")
        temporary.replace(pdf)
    if file_sha256(pdf) != expected:
        raise ValueError("Wrong witness PDF: SHA-256 differs.")
    destination.mkdir(parents=True, exist_ok=False)
    command = ["pdftoppm", "-f", "8", "-l", "8", "-r", "300", "-png", "-singlefile",
               str(pdf), str(destination / "schumann-page")]
    result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
    from PIL import Image
    page = destination / "schumann-page.png"
    with Image.open(page) as image:
        if image.size != (4167, 5617):
            raise ValueError(f"Recheck crop coordinates for changed image dimensions: {image.size}")
        image.crop((100, 500, 4000, 2280)).save(destination / "schumann-two-systems.png")
    version = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True, check=True)
    save_json(destination / "preparation.json", {
        "pdf_sha256": expected, "source_url": url, "original_pdf_page": 8, "printed_page": 8,
        "dpi": 300, "pixels": [4167, 5617], "command": command,
        "poppler_version": version.stdout + version.stderr, "render_messages": result.stderr,
        "page_sha256": file_sha256(page), "crop_pixels_left_top_right_bottom": [100, 500, 4000, 2280],
        "crop_sha256": file_sha256(destination / "schumann-two-systems.png"), "resampling": "None",
    })
    return page, destination / "schumann-two-systems.png"


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_omr(engine, engine_python, image, destination, timeout=1200):
    """Run an installed recogniser in isolation and preserve its raw export/log.

    destination must be new. The recogniser can write diagnostics beside its
    input, so the image and any generated images are kept under local/.
    A process failure is recorded as a result, not silently repaired.
    """
    if engine not in {"homr", "oemer"}:
        raise ValueError("Supported engine names: homr, oemer")
    # Resolving a venv's Python symlink would select the base interpreter and
    # discard the isolated environment's packages.
    engine_python, image = Path(engine_python).absolute(), Path(image).resolve()
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    work = destination / "local"
    work.mkdir()
    input_image = work / "schumann-page.png"
    shutil.copyfile(image, input_image)
    module = "homr.main" if engine == "homr" else "oemer.ete"
    command = [str(engine_python), "-c", f"from {module} import main; main()", str(input_image)]
    env = dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", MKL_NUM_THREADS="2",
               CUDA_VISIBLE_DEVICES="", MPLCONFIGDIR=str(work / "mplconfig"),
               XDG_CACHE_HOME=str(work / "cache"))
    environment = subprocess.run(
        [str(engine_python), "-c", "import importlib.metadata as m,json,sys; "
         "print(json.dumps({'python':sys.version,'packages':dict(sorted((d.metadata['Name'],d.version) "
         "for d in m.distributions() if d.metadata.get('Name')))}))"],
        text=True, capture_output=True, check=True, env=env,
    )
    environment_info = json.loads(environment.stdout)
    if engine not in {name.lower() for name in environment_info["packages"]}:
        raise RuntimeError(f"{engine} is not installed in {engine_python}")
    metadata = {"engine": engine, "started_utc": datetime.now(timezone.utc).isoformat(),
                "input_sha256": file_sha256(input_image), "command": command,
                "hardware": "CPU; CUDA_VISIBLE_DEVICES is empty",
                "environment": environment_info,
                "status": "running", "corrections": "None: raw recogniser output is preserved."}
    save_json(destination / "run.json", metadata)
    start = time.monotonic()
    with (destination / "run.log").open("w", encoding="utf-8") as log:
        try:
            result = subprocess.run(command, cwd=work, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=timeout)
            metadata.update(returncode=result.returncode,
                            status="completed" if result.returncode == 0 else "failed")
        except subprocess.TimeoutExpired:
            metadata.update(returncode=None, status="timeout")
    metadata["elapsed_seconds_including_first_run_downloads"] = round(time.monotonic() - start, 3)
    exports = sorted(work.glob("*.musicxml")) + sorted(work.glob("*.xml"))
    metadata["exports_found"] = [p.name for p in exports]
    if len(exports) == 1:
        output = destination / "raw.musicxml"
        shutil.copyfile(exports[0], output)
        metadata["output"] = {"file": output.name, "sha256": file_sha256(output), "bytes": output.stat().st_size}
    package = subprocess.run(
        [str(engine_python), "-c", f"import importlib.util; print(importlib.util.find_spec('{engine}').submodule_search_locations[0])"],
        text=True, capture_output=True, check=True, env=env,
    )
    package_root = Path(package.stdout.strip())
    weights = sorted(p for p in package_root.rglob("*") if p.is_file() and p.suffix in {".onnx", ".h5", ".safetensors"})
    metadata["downloaded_model_files"] = [
        {"file": str(p.relative_to(package_root)), "sha256": file_sha256(p), "bytes": p.stat().st_size}
        for p in weights
    ]
    save_json(destination / "run.json", metadata)
    return metadata


def convert_omr_to_mei(raw_xml, destination, python=sys.executable):
    """Convert a copy with CAMAT; a native importer failure cannot kill Jupyter."""
    raw_xml, destination = Path(raw_xml).resolve(), Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    command = [str(python), "-m", "camat.conversion", "--source", str(raw_xml),
               "--output-dir", str(destination), "--mei-version", "5.1"]
    with (destination / "conversion.log").open("w", encoding="utf-8") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    mei_files = sorted(destination.glob("*.mei"))
    record = {"command": command, "returncode": result.returncode,
              "status": "completed" if result.returncode == 0 and mei_files else "failed",
              "input_sha256": file_sha256(raw_xml),
              "outputs": [{"file": p.name, "sha256": file_sha256(p)} for p in mei_files]}
    save_json(destination / "conversion-run.json", record)
    return record


def musicxml_summary(path):
    """Structural inspection, not an accuracy metric; measures counted per part."""
    root = ET.parse(path).getroot()
    if root.tag != "score-partwise":
        raise ValueError("This inspector expects uncompressed partwise MusicXML")
    parts = []
    for part in root.findall("part"):
        measures = part.findall("measure")
        parts.append({"part": part.get("id"), "measures": len(measures),
                      "labels": [m.get("number") for m in measures],
                      "pitched_note_elements": len(part.findall(".//note/pitch")),
                      "rest_elements": len(part.findall(".//note/rest")),
                      "staff_values": sorted({e.text for e in part.findall(".//note/staff") if e.text}),
                      "voice_values": sorted({e.text for e in part.findall(".//note/voice") if e.text})})
    return {"file": Path(path).name, "parts": parts,
            "dynamics": len(root.findall(".//dynamics")),
            "slur_endpoints": len(root.findall(".//slur")),
            "written_words": [e.text for e in root.findall(".//direction-type/words") if e.text]}


def chord_after_rest_locations(path):
    """Locate pitched chord members attached to a preceding rest, for inspection.

    This is one specific structural warning, not a complete MusicXML validator.
    """
    root, found = ET.parse(path).getroot(), []
    for part in root.findall("part"):
        for measure in part.findall("measure"):
            leader = None
            for i, item in enumerate(measure):
                if item.tag != "note":
                    if item.tag in {"backup", "forward"}:
                        leader = None
                    continue
                if item.find("chord") is None:
                    leader = item
                elif leader is not None and leader.find("rest") is not None:
                    found.append({"part": part.get("id"), "measure_label": measure.get("number"),
                                  "child_index": i, "staff": item.findtext("staff", "1"),
                                  "voice": item.findtext("voice", "1")})
    return found


def musicxml_bar_notes(path, part_index=0, measure_index=0):
    """List a raw measure's events with onsets; indices are positions, not labels."""
    from fractions import Fraction
    root = ET.parse(path).getroot()
    part = root.findall("part")[part_index]
    division = 1
    for measure in part.findall("measure")[:measure_index + 1]:
        if measure.findtext("attributes/divisions"):
            division = int(measure.findtext("attributes/divisions"))
    measure = part.findall("measure")[measure_index]
    position, last_onset, events = Fraction(0), Fraction(0), []
    for item in measure:
        if item.tag in {"backup", "forward"}:
            delta = Fraction(int(item.findtext("duration", "0")), division)
            position += delta if item.tag == "forward" else -delta
        elif item.tag == "note":
            duration = Fraction(int(item.findtext("duration", "0")), division)
            is_chord = item.find("chord") is not None
            onset = last_onset if is_chord else position
            pitch = item.find("pitch")
            spelling = "rest" if pitch is None else (
                pitch.findtext("step", "?") + {"-2": "bb", "-1": "b", "0": "", "1": "#", "2": "##"}.get(pitch.findtext("alter", "0"), "?")
                + pitch.findtext("octave", "?"))
            events.append({"onset_quarters": str(onset), "duration_quarters": str(duration),
                           "pitch": spelling, "staff": item.findtext("staff", "1"),
                           "voice": item.findtext("voice", "1"), "chord": is_chord})
            if not is_chord:
                last_onset = onset
                position += duration
    return {"label": measure.get("number"), "events": events}


def render_score_to_svg(score, destination, python=sys.executable):
    """Run Verovio in a separate process and keep its exact warnings."""
    score, destination = Path(score).resolve(), Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    code = """from pathlib import Path
import sys,verovio,json
t=verovio.toolkit()
t.setOptions({'pageWidth':2100,'pageHeight':2970,'scale':40,'adjustPageHeight':True,'breaks':'auto','footer':'none','header':'none'})
if not t.loadFile(sys.argv[1]): raise SystemExit(2)
out=Path(sys.argv[2])
for page in range(1,t.getPageCount()+1): (out/f'page-{page}.svg').write_text(t.renderToSVG(page))
print(json.dumps({'verovio':t.getVersion(),'pages':t.getPageCount()}))
"""
    result = subprocess.run([str(python), "-c", code, str(score), str(destination)],
                            text=True, capture_output=True, timeout=120)
    (destination / "render.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    return {"returncode": result.returncode, "pages": sorted(destination.glob("page-*.svg")),
            "messages": result.stdout + result.stderr}
