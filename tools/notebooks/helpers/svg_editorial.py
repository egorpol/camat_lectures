"""Export local score/scan context for the SVG editorial exercise.

No provider requests. Source pixels stay in the student's existing work project.
"""

import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops
import verovio

SVG_MEI_NS = "http://www.music-encoding.org/ns/mei"
SVG_NS = "http://www.w3.org/2000/svg"
SVG_XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
SVG_M = "{" + SVG_MEI_NS + "}"
SVG_EXTRA_ATTRIBUTES = [
    "measure@n", "staff@n", "layer@n", "note@pname", "note@oct", "note@dur",
    "note@dots", "note@accid", "note@accid.ges", "note@stem.dir", "chord@dur",
    "chord@dots", "accid@accid", "slur@startid", "slur@endid", "slur@staff",
    "slur@curvedir", "dynam@startid", "dynam@tstamp", "dynam@staff", "dynam@place",
]


def svg_file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def svg_raster(svg_text, width=1900):
    """Use librsvg if installed; CairoSVG is the optional Python fallback."""
    executable = shutil.which("rsvg-convert")
    if executable:
        result = subprocess.run([executable, "-w", str(width), "-b", "white"],
                                input=svg_text.encode(), capture_output=True, check=True, timeout=60)
        return result.stdout, "rsvg-convert"
    try:
        import cairosvg
    except ImportError as error:
        raise ImportError("Rendering PNG needs rsvg-convert or CairoSVG (python -m pip install cairosvg); CairoSVG also needs system Cairo.") from error
    return cairosvg.svg2png(bytestring=svg_text.encode(), output_width=width,
                           background_color="white"), "CairoSVG " + cairosvg.__version__


def svg_render_selection(mei, first_position, last_position, enriched=False):
    toolkit = verovio.toolkit()
    options = {"header": "none", "footer": "none", "breaks": "none", "pageWidth": 2400,
               "pageHeight": 10000, "adjustPageHeight": True, "scale": 60,
               "svgViewBox": True, "xmlIdSeed": 1}
    if enriched:
        options["svgAdditionalAttribute"] = SVG_EXTRA_ATTRIBUTES
    toolkit.setOptions(options)
    if not toolkit.loadData(Path(mei).read_text()):
        raise ValueError("Verovio could not load the MEI")
    if not toolkit.select({"measureRange": f"{first_position}-{last_position}"}):
        raise ValueError("Verovio could not select the passage")
    toolkit.redoLayout()
    if toolkit.getPageCount() != 1:
        raise ValueError("Use a smaller passage for this one-system packet")
    return toolkit.renderToSVG(1), {"verovio": toolkit.getVersion(), "options": options}


def svg_editorial_prompt(condition):
    extras = {
        "A": "No SVG source is supplied in this condition.",
        "B": "Also read score.svg as SVG SOURCE TEXT. Its element IDs/classes address the current MEI; retain glyph definitions when inspecting it.",
        "C": "Also read score-enriched.svg as SVG SOURCE TEXT. Its data-* attributes copy current encoded values, which may be wrong or inherited from a containing chord/key; they are not evidence from the print.",
    }
    return '''Compare source-system.png (IMSLP 51556, printed p.8, first system)
with engraving.png (our current Schumann Op.68 No.10 encoding). Read context.xml,
a READ-ONLY fragment with scoreDef and MEI labels 1–5; it is not a complete MEI.
The pickup is label 1; labels 2 and 3 are the first two full bars.

Focus ONLY on the slur phrases beginning in that pickup and those two full bars.
Identify up to two missing or differently attached printed slurs. For each:
state what you see in the source, the staff, start/end notes and existing MEI
IDs, the corresponding current-engraving discrepancy, and any uncertainty.
If you cannot inspect an attachment or distinguish an endpoint, say so.
Do not infer the source reading from a familiar edition or the current metadata.
Use only the supplied task files; do not consult answer keys, other editions or the web.

Then propose the smallest MEI 5.1 insertion/correction and an explanation for
editorial review. Preserve all existing pitches, rhythms, voices, IDs, metadata,
facsimile links and source breaks. Do not change SVG paths as the edition.
Keep source reading, encoding decision and engraving/renderer problem separate.
Do not invent validation results or human approval.

Return: observations with evidence -> exact targets/uncertainties -> minimal
candidate patch -> what the human should compare after rendering.
''' + "\n" + extras[condition] + "\n"


def export_svg_editorial_packet(mei_path, output, first_label="1", last_label="5"):
    mei = Path(mei_path).resolve()
    output = Path(output).resolve()
    input_hash = svg_file_hash(mei)
    root = ET.parse(mei).getroot()
    measures = root.findall("m:music/m:body//m:measure", {"m": SVG_MEI_NS})
    labels = [measure.get("n") for measure in measures]
    if len(set(labels)) != len(labels):
        raise ValueError("This single-movement exercise needs unique MEI measure labels")
    first, last = labels.index(first_label), labels.index(last_label)
    if first > last:
        raise ValueError("Passage end precedes its start")
    selected = measures[first:last + 1]
    if not selected or any(not m.get(SVG_XML_ID) for m in selected):
        raise ValueError("Selected measures need existing IDs")
    by_id = {e.get(SVG_XML_ID): e for e in root.iter() if e.get(SVG_XML_ID)}
    parents = {child: parent for parent in root.iter() for child in parent}
    zones = [by_id[m.get("facs", "").removeprefix("#")] for m in selected]
    surfaces = {parents[zone] for zone in zones}
    if len(surfaces) != 1:
        raise ValueError("Use one printed system/page for this exercise")
    surface = next(iter(surfaces))
    graphic = surface.find(SVG_M + "graphic")
    image_path = (mei.parent / graphic.get("target")).resolve()
    image_hash = svg_file_hash(image_path)
    identity = {"input_mei_sha256": input_hash, "source_image_sha256": image_hash,
                "labels": labels[first:last + 1], "packet_format": 1}
    if output.exists():
        manifest = json.loads((output / "manifest.json").read_text())
        if manifest["identity"] != identity:
            raise FileExistsError("Existing packet describes a different input; choose a new attempt folder")
        for filename, expected in manifest["files_sha256"].items():
            if svg_file_hash(output / filename) != expected:
                raise FileExistsError(f"Preserving modified packet file: {filename}")
        return manifest

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".svg-packet-", dir=output.parent) as temporary:
        stage = Path(temporary)
        ordinary, normal_info = svg_render_selection(mei, first + 1, last + 1)
        enriched, enriched_info = svg_render_selection(mei, first + 1, last + 1, True)
        (stage / "score.svg").write_text(ordinary)
        (stage / "score-enriched.svg").write_text(enriched)
        normal_root = ET.fromstring(ordinary)
        enriched_root = ET.fromstring(enriched)
        expected_ids = [m.get(SVG_XML_ID) for m in selected]
        def measure_ids(svg):
            return [e.get("id") for e in svg.iter()
                    if "measure" in e.get("class", "").split()]
        if measure_ids(normal_root) != expected_ids or measure_ids(enriched_root) != expected_ids:
            raise AssertionError("Rendered selection does not match MEI measures, including the pickup")
        rendered_ids = {e.get("id") for e in normal_root.iter() if e.get("id")}
        mapping = []
        for measure in selected:
            for event in measure.iter():
                if event.tag not in {SVG_M + tag for tag in ("note", "chord", "rest", "slur", "dynam", "tempo")}:
                    continue
                event_id = event.get(SVG_XML_ID)
                mapping.append({"mei_id": event_id, "measure": measure.get("n"),
                                "element": event.tag.split("}")[-1],
                                "encoded_attributes": dict(event.attrib),
                                "present_in_default_svg": event_id in rendered_ids})
                if event_id and event_id not in rendered_ids:
                    raise AssertionError(f"Expected event missing from rendered SVG: {event_id}")
        (stage / "element-map.json").write_text(json.dumps(mapping, indent=2) + "\n")
        context = ET.Element("score-context", {"purpose": "read-only MEI fragment; not a valid standalone MEI"})
        score_def = root.find("m:music/m:body//m:scoreDef", {"m": SVG_MEI_NS})
        if score_def is None:
            raise ValueError("Expected initial scoreDef for this Schumann passage")
        context.append(copy.deepcopy(score_def))
        for measure in selected:
            context.append(copy.deepcopy(measure))
        (stage / "context.xml").write_bytes(ET.tostring(context, encoding="utf-8", xml_declaration=True))
        png, renderer = svg_raster(ordinary)
        enriched_png, _ = svg_raster(enriched)
        before_pixels = Image.open(io.BytesIO(png)).convert("RGB")
        after_pixels = Image.open(io.BytesIO(enriched_png)).convert("RGB")
        same_pixels = before_pixels.size == after_pixels.size and ImageChops.difference(before_pixels, after_pixels).getbbox() is None
        if not same_pixels:
            raise AssertionError("Added data attributes unexpectedly changed the rendered appearance")
        (stage / "engraving.png").write_bytes(png)
        with Image.open(image_path) as image:
            crop = (max(0, min(int(z.get("ulx")) for z in zones) - 125),
                    max(0, min(int(z.get("uly")) for z in zones) - 64),
                    min(image.width, max(int(z.get("lrx")) for z in zones) + 125),
                    min(image.height, max(int(z.get("lry")) for z in zones) + 64))
            image.crop(crop).save(stage / "source-system.png")
        for condition in "ABC":
            (stage / f"prompt-{condition}.md").write_text(svg_editorial_prompt(condition))
        record = {"status": "not_run", "condition": "", "model_id": "", "extension_and_version": "",
                  "actual_input_transport": "unknown: record source text / raster preview / both",
                  "input_mei_sha256": input_hash, "manifest": "manifest.json",
                  "prompt_file": "", "response_file": "", "patch_file": "", "elapsed_seconds": None,
                  "usage_or_quota_observation": "", "found_phrase_divisions": "not_reviewed",
                  "correct_staff_and_endpoint_ids": "not_reviewed", "unexpected_changes": [],
                  "schema_reference_resource_checks": "not_run", "render_check": "not_run",
                  "human_source_review": "not_reviewed", "reviewer": "", "decision_and_corrections": ""}
        (stage / "record-template.json").write_text(json.dumps(record, indent=2) + "\n")
        manifest = {"prepared_on": "2026-10-26", "identity": identity,
                    "input_mei": str(mei), "source_image": str(image_path),
                    "source": "IMSLP 51556, original/excerpt/printed pages 8/1/8",
                    "source_crop_pixels": list(crop), "source_crop_basis": "union of linked measure zones plus context margin; review before use",
                    "measures_in_svg": expected_ids, "events_mapped": len(mapping),
                    "ordinary": normal_info, "enriched": enriched_info,
                    "png_renderer": renderer, "normal_and_enriched_pixels_identical": same_pixels,
                    "glyph_definitions_retained": normal_root.find("{" + SVG_NS + "}defs") is not None,
                    "source_human_review": "not_asserted", "provider_calls": 0,
                    "files_sha256": {p.name: svg_file_hash(p) for p in sorted(stage.iterdir())}}
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        stage.rename(output)
    if svg_file_hash(mei) != input_hash or svg_file_hash(image_path) != image_hash:
        raise AssertionError("Input changed during packet generation")
    return manifest
