"""Build the beginner SVG demo assets and the notebook's separate data ZIP.

Requires Verovio 6.3, Pillow and rsvg-convert. The browser and student notebook
use prepared local assets and need no renderer, network, API key or CAMAT project.
"""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from lxml import etree
import verovio

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/02-building-an-edition"
DEMO = SESSION / "examples/svg-introduction"
SOURCE = SESSION / "teacher/schumann/manual-entry-solution.mei"
M = "{http://www.music-encoding.org/ns/mei}"
ID = "{http://www.w3.org/XML/1998/namespace}id"

NOTE = '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 48 48">
  <ellipse cx="19" cy="35" rx="10" ry="6" transform="rotate(-18 19 35)"/>
  <line x1="28" y1="32" x2="28" y2="5" stroke="black" stroke-width="2"/>
</svg>
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    DEMO.mkdir(parents=True, exist_ok=True)
    source_bytes = SOURCE.read_bytes()
    tree = etree.fromstring(source_bytes)
    body = tree.find(M + "music/" + M + "body")
    measures = list(body.iter(M + "measure"))
    for measure in measures[1:]:
        measure.getparent().remove(measure)
    description = tree.find(M + "meiHead/" + M + "encodingDesc/" + M + "projectDesc")
    paragraph = etree.SubElement(description, M + "p")
    paragraph.text = ("SVG introduction: pickup-only teaching demonstration. The C3 variant retains the starter pitch; "
                      "the F3 variant is an artificial single-note change to demonstrate re-engraving, not an editorial correction. "
                      "Both preserve the existing note ID d1e60. No source scan is included.")
    variants = {}
    expected_signature = None
    for pitch in ("c", "f"):
        root = copy.deepcopy(tree)
        note, = root.xpath('//*[@xml:id="d1e60"]')
        note.set("pname", pitch)
        mei = etree.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
        (DEMO / f"pickup-{pitch}3.mei").write_bytes(mei)
        # Prove the prepared variants differ only at this note's pitch name.
        normalized = copy.deepcopy(root)
        normalized.xpath('//*[@xml:id="d1e60"]')[0].set("pname", "c")
        signature = etree.tostring(normalized, method="c14n")
        if expected_signature is None:
            expected_signature = signature
        assert signature == expected_signature
        record = {"name": pitch.upper() + "3", "mei_note": etree.tostring(note, encoding="unicode").strip()}
        for enriched in (False, True):
            toolkit = verovio.toolkit()
            options = {"header": "none", "footer": "none", "breaks": "none", "pageWidth": 1050,
                       "pageHeight": 3000, "adjustPageHeight": True, "adjustPageWidth": True,
                       "scale": 60, "svgViewBox": True, "xmlIdSeed": 1}
            if enriched:
                options["svgAdditionalAttribute"] = ["note@pname", "note@oct", "note@dur"]
            toolkit.setOptions(options)
            assert toolkit.loadData(mei.decode())
            svg = toolkit.renderToSVG(1)
            svg_root = etree.fromstring(svg.encode())
            group, = svg_root.xpath('//*[@id="d1e60"]')
            suffix = "-enriched" if enriched else ""
            filename = f"pickup-{pitch}3{suffix}.svg"
            (DEMO / filename).write_text(svg)
            record["enriched" if enriched else "plain"] = svg
            record["extra_attributes" if enriched else "attributes"] = dict(group.attrib)
        # Keep the visible snippet short; it is an exact note start tag with no
        # inherited namespace declarations, not a replacement MEI document.
        record["mei_note"] = '<note xml:id="d1e60" pname="' + pitch + '" oct="3" dur="8" stem.dir="up"/>'
        variants[pitch] = record
    (DEMO / "note-symbol.svg").write_text(NOTE)
    png = subprocess.run(["rsvg-convert", "-w", "32", "-h", "32", "-b", "white"],
                         input=NOTE.encode(), capture_output=True, check=True).stdout
    (DEMO / "note-32px.png").write_bytes(png)
    (DEMO / "score-data.js").write_text(
        "// Prepared with tools/build_svg_introduction.py; no live renderer or network is used.\n"
        "window.SVG_INTRO_SCORES = " + json.dumps(variants, ensure_ascii=False) + ";\n")
    (DEMO / "LICENSE").write_bytes((SESSION / "examples/schumann/LICENSE").read_bytes())
    files = [path for path in sorted(DEMO.iterdir()) if path.is_file() and path.name not in {"README.md", "manifest.json"}]
    manifest = {"prepared_on": "2026-10-26", "source": str(SOURCE.relative_to(ROOT)),
                "source_sha256": digest(source_bytes), "verovio": verovio.toolkit().getVersion(),
                "meaning": "Prepared teaching demonstrations; F3 is artificial, not a source correction",
                "note_id_preserved": "d1e60", "variants_differ_only_in_note_pname": True,
                "scan_images_included": False,
                "files_sha256": {path.name: digest(path.read_bytes()) for path in files}}
    (DEMO / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    bundle = SESSION / "notebooks/svg-introduction-assets.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files + [DEMO / "manifest.json"]:
            entry = zipfile.ZipInfo(path.name, date_time=(2026, 10, 26, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, path.read_bytes())
    assert SOURCE.read_bytes() == source_bytes
    print(f"Built {len(files)} local assets; ZIP {bundle.stat().st_size:,} bytes; source preserved.")


if __name__ == "__main__":
    main()
