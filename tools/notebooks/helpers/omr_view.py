"""What the OMR notebook shows: the recorded results, the scan, one bar in words."""

from pathlib import Path
import json
import re
import shutil
import subprocess
import urllib.request

from IPython.display import display, HTML, Image

OMR_WORK = Path.cwd() / "schumann_omr_work"
# The same file and folder as in 02_pdf_preparation, so the scan is downloaded once.
SCAN_PDF = Path.cwd() / "schumann_edition_work/sources/imslp-51556-schumann-op68.pdf"
# The first two systems of page 8 (pickup and bars 1–8) at 150 dpi: half of the
# 300 dpi crop (100, 500, 4000, 2280) that HOMR read.
TWO_SYSTEMS = ["-r", "150", "-x", "50", "-y", "250", "-W", "1950", "-H", "890"]
OMR_LENGTHS = {"1/4": "sixteenth", "1/2": "eighth", "3/4": "dotted eighth", "1": "quarter",
               "3/2": "dotted quarter", "2": "half", "3": "dotted half", "4": "whole"}
OMR_STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def load_schumann_recordings():
    """Unpack the recordings ZIP next to the notebook and check every file."""
    folder = unpack_schumann_recordings(find_schumann_recordings(),
                                        OMR_WORK / f"recorded-{SCHUMANN_RECORDINGS_SHA256[:8]}")
    manifest = json.loads((folder / "manifest.json").read_text())
    for relative, expected in manifest["files_sha256"].items():
        if file_sha256(folder / relative) != expected:
            raise ValueError(f"{relative} in {folder} has changed. Delete that folder and run the cell again.")
    print("OMR results loaded:", len(manifest["files_sha256"]), "files in", folder)
    return folder


def get_schumann_scan(recorded):
    """Download IMSLP 51556 once and check that it is the course's copy."""
    source = json.loads((recorded / "source.json").read_text())
    if not SCAN_PDF.exists():
        print("Downloading the scan from IMSLP (9 MB) ...")
        SCAN_PDF.parent.mkdir(parents=True, exist_ok=True)
        temporary = SCAN_PDF.with_suffix(".download")
        request = urllib.request.Request(source["source_url"], headers={"User-Agent": "camat-schumann-seminar"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as out:
                shutil.copyfileobj(response, out)
        except OSError as problem:
            raise RuntimeError(f"Could not download the scan from IMSLP ({problem}). Check the internet "
                               f"connection and run the cell again, or put a copy of the file here: {SCAN_PDF}") from None
        if file_sha256(temporary) != source["pdf_sha256"]:
            temporary.unlink()
            raise ValueError("The download is not the scan the course uses. Run the cell again later.")
        temporary.replace(SCAN_PDF)
    elif file_sha256(SCAN_PDF) != source["pdf_sha256"]:
        raise ValueError(f"{SCAN_PDF} is not the scan the course uses. Move it away and run the cell again.")
    return SCAN_PDF


def show_schumann_scan(recorded, width=900):
    pdf = get_schumann_scan(recorded)
    image = OMR_WORK / "scan-two-systems.png"
    if not image.exists():
        if not shutil.which("pdftoppm"):
            raise RuntimeError("Poppler's pdftoppm is missing: select the seminar kernel (setup page, step 7).")
        OMR_WORK.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-f", "8", "-l", "8", *TWO_SYSTEMS, "-png", "-singlefile",
                        str(pdf), str(image.with_suffix(""))], check=True, capture_output=True, timeout=120)
    display(Image(filename=str(image), width=width))


# The score on a white background (readable in dark themes), without Verovio's
# bar numbers: they count the pickup as bar 1, and the print has none.
def show_omr_score(svg_file):
    svg = Path(svg_file).read_text(encoding="utf-8")
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r'<g [^>]*class="mNum[^"]*"[^>]*>.*?</g>', "", svg, flags=re.S)
    display(HTML(f'<div style="background:white; padding:4px; overflow-x:auto">{svg}</div>'))


def _omr_event(pitches, duration):
    if not pitches:
        return f"rest {OMR_LENGTHS.get(duration, duration + ' quarter notes')}"
    def height(name):
        return 12 * int(name[-1]) + OMR_STEPS[name[0]] + name.count("♯") - name.count("♭") - 2 * name.count("𝄫")
    chord = "+".join(sorted(pitches, key=height))
    return f"{chord} {OMR_LENGTHS.get(duration, duration + ' quarter notes')}"


def read_bar(recorded, bar, run="homr-two-systems"):
    """Print one bar of an OMR result in words. bar: "pickup", or 1, 2, ... as musicians count."""
    raw = recorded / run / "raw.musicxml"
    index = 0 if str(bar).lower() == "pickup" else int(bar)
    count = musicxml_summary(raw)["parts"][0]["measures"]
    if not 0 <= index < count:
        print(f"This result has the pickup and bars 1–{count - 1}.")
        return
    found = musicxml_bar_notes(raw, measure_index=index)
    print("Pickup" if index == 0 else f"Bar {index}", "as HOMR read it" if run.startswith("homr") else "")
    for staff, name in (("1", "treble"), ("2", "bass")):
        events = []
        for event in found["events"]:
            if event["staff"] != staff:
                continue
            pitch = event["pitch"].replace("bb", "𝄫").replace("b", "♭").replace("#", "♯")
            if event["chord"] and events:
                events[-1][0].append(pitch)
            else:
                events.append(([] if pitch == "rest" else [pitch], event["duration_quarters"]))
        print(f"  {name + ':':8}", ", ".join(_omr_event(p, d) for p, d in events))
