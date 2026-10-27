"""Schumann witness preparation; notation/settings live in a separate ZIP."""

from pathlib import Path
import hashlib
import io
import json
import urllib.request
import xml.etree.ElementTree as ET
import zipfile


def pdf_file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def find_schumann_pdf_inputs(start=None):
    start = Path(start or Path.cwd()).resolve()
    name = "schumann-edition-inputs.zip"
    for folder in (start, *start.parents):
        for candidate in (folder / name, folder / "notebooks" / name,
                          folder / "sessions/02-building-an-edition/notebooks" / name):
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(f"Copy {name} beside this notebook, or run get_notebooks.py to get both files.")


def _preserve_or_write(path, data):
    """Keep existing matching inputs; never replace an edited or different file."""
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Preserving different file: {path}. Choose a new PROJECT folder.")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(data)


def _preserve_json(path, value):
    _preserve_or_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def load_schumann_pdf_inputs(bundle, project):
    """Unpack a checked copy of the starter, credits and preparation settings."""
    bundle, project = Path(bundle).resolve(), Path(project).resolve()
    required = {"starter.mei", "LICENSE", "sources.json", "settings.json"}
    with zipfile.ZipFile(bundle) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        if set(manifest["files_sha256"]) != required or set(archive.namelist()) != required | {"manifest.json"}:
            raise ValueError("Unexpected Schumann input bundle contents.")
        files = {name: archive.read(name) for name in required}
    for name, data in files.items():
        if hashlib.sha256(data).hexdigest() != manifest["files_sha256"][name]:
            raise ValueError(f"Input hash mismatch: {name}")
    folder = project / "inputs" / pdf_file_sha256(bundle)[:12]
    for name, data in files.items():
        _preserve_or_write(folder / name, data)
    return folder, json.loads(files["settings.json"]), json.loads(files["sources.json"])


def prepare_schumann_pdfs(project, settings, sources, *, local_original=None, allow_download=True):
    """Check the frozen volume, then extract original page 8 without changing it.

    pypdf is pinned because even a visually identical derivative can have
    different PDF bytes. CAMAT renders only this separately identified extract.
    """
    import pypdf
    if pypdf.__version__ != settings["pypdf_version"]:
        raise RuntimeError(f"This notebook needs pypdf {settings['pypdf_version']}, but {pypdf.__version__} is installed. "
                           "Run the first cell, restart the kernel, and run the notebook again.")
    folder = Path(project).resolve() / "sources"
    original = folder / settings["original_filename"]
    excerpt = folder / settings["excerpt_filename"]
    witness = sources["printed_witness"]
    expected_original = witness["sha256"]
    if original.exists():
        if pdf_file_sha256(original) != expected_original:
            raise ValueError(f"{original} is not the scan the course uses. Move it away and run the cell again.")
    else:
        if local_original is not None:
            data = Path(local_original).read_bytes()
        elif allow_download:
            request = urllib.request.Request(witness["download_url"], headers={"User-Agent": "camat-schumann-seminar"})
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    data = response.read(witness["bytes"] + 1)
            except OSError as problem:
                raise RuntimeError(f"Could not download the scan from IMSLP ({problem}). Check the internet "
                                   f"connection and run the cell again, or put a copy of the file here: {original}") from None
        else:
            raise FileNotFoundError("Supply LOCAL_ORIGINAL or enable ALLOW_SOURCE_DOWNLOAD.")
        if len(data) != witness["bytes"] or hashlib.sha256(data).hexdigest() != expected_original:
            raise ValueError("The download is not the scan the course uses. Run the cell again later.")
        _preserve_or_write(original, data)
    reader = pypdf.PdfReader(original)
    if len(reader.pages) != witness["page_count"]:
        raise ValueError("Unexpected original PDF page count.")
    page = reader.pages[settings["original_pdf_page"] - 1]
    writer, memory = pypdf.PdfWriter(), io.BytesIO()
    writer.add_page(page)
    writer.add_metadata(sources["classroom_pdf"]["pdf_metadata"])
    writer.write(memory)
    data = memory.getvalue()
    if hashlib.sha256(data).hexdigest() != sources["classroom_pdf"]["sha256"]:
        raise ValueError("Extracted PDF differs from the frozen one-page derivative; review the recipe.")
    _preserve_or_write(excerpt, data)
    reread = pypdf.PdfReader(excerpt)
    if len(reread.pages) != 1 or pdf_file_sha256(original) != expected_original:
        raise ValueError("Extraction integrity check failed.")
    record = {
        "original_pdf": str(original.relative_to(Path(project).resolve())),
        "original_sha256": expected_original, "original_page_count": len(reader.pages),
        "excerpt_pdf": str(excerpt.relative_to(Path(project).resolve())),
        "excerpt_sha256": pdf_file_sha256(excerpt), "excerpt_page_count": 1,
        "original_pdf_page": settings["original_pdf_page"], "excerpt_pdf_page": 1,
        "printed_page": settings["printed_page"], "pypdf": pypdf.__version__,
        "transformation": sources["classroom_pdf"]["transformation"],
        "pdf_metadata": sources["classroom_pdf"]["pdf_metadata"],
        "media_box_points": list(map(float, page.mediabox)),
        "crop_box_points": list(map(float, page.cropbox)), "rotation": page.rotation,
    }
    _preserve_json(folder / "page-mapping.json", record)
    return original, excerpt, record


def schumann_body_measures(mei_file):
    ns = {"m": "http://www.music-encoding.org/ns/mei"}
    body = ET.parse(mei_file).getroot().find("m:music/m:body", ns)
    if body is None:
        raise ValueError("No music/body found.")
    measures = body.findall(".//m:measure", ns)
    labels = [m.get("n") for m in measures]
    if labels != list(map(str, range(1, 22))):
        raise ValueError(f"This workshop expects the whole-piece carrier, labels 1–21. Found {labels}")
    return measures


def print_bar_table(mei_file, settings):
    """Bars as musicians count them, beside the MEI numbers, systems and IDs."""
    by_label = {m.get("n"): m for m in schumann_body_measures(mei_file)}
    print(f"{'Bar':<8}{'MEI n':<7}{'System':<8}xml:id")
    for system, labels in enumerate(settings["system_mei_labels"], 1):
        for label in labels:
            bar = "pickup" if label == "1" else str(int(label) - 1)
            print(f"{bar:<8}{label:<7}{system:<8}{by_label[label].get('{http://www.w3.org/XML/1998/namespace}id')}")


def save_schumann_page_checkpoint(project, mei_file, settings, pdf_record, pages_json):
    """Verify the technical map and save the handoff to the measure-box block."""
    project, pages_json = Path(project).resolve(), Path(pages_json).resolve()
    manifest = json.loads(pages_json.read_text())
    if manifest["page_count"] != 1 or manifest["dpi"] != 300:
        raise ValueError("Expected one rendered page at 300 dpi.")
    if manifest["pdf_sha256"] != pdf_record["excerpt_sha256"]:
        raise ValueError("Page images do not belong to the frozen excerpt PDF.")
    page = manifest["pages"][0]
    if page["role"] != "music" or page["printed_page"] != "8" or page["pdf_page_number"] != 1:
        raise ValueError("Check the excerpt-page/printed-page description.")
    systems = [s["measures"] if isinstance(s, dict) else s for s in page["systems"]]
    if systems != settings["system_mei_labels"]:
        raise ValueError("The systems in part 4 do not match the print. Compare where each system starts "
                         "with the image, correct the line in part 4, run that cell again, then this one.")
    if [page["width"], page["height"]] != settings["expected_image_pixels"]:
        raise ValueError("Image geometry differs; review before drawing boxes.")
    image = pages_json.parent / page["image"]
    if pdf_file_sha256(image) != page["sha256"]:
        raise ValueError("Page image changed after rendering.")
    by_label = {m.get("n"): m for m in schumann_body_measures(mei_file)}
    identifiers = [m.get("{http://www.w3.org/XML/1998/namespace}id") for m in by_label.values()]
    if None in identifiers or len(set(identifiers)) != len(identifiers):
        raise ValueError("Measure IDs must be present and unique before facsimile linking.")
    rows = []
    for number, labels in enumerate(systems, 1):
        for label in labels:
            rows.append({"mei_label": label, "measure_xml_id": by_label[label].get("{http://www.w3.org/XML/1998/namespace}id"),
                         "conventional_bar": "pickup" if label == "1" else str(int(label) - 1),
                         "system": number, "original_pdf_page": 8, "excerpt_pdf_page": 1, "printed_page": "8",
                         "core_editing_passage": label in settings["reviewed_mei_labels"]})
    _preserve_json(project / "edition/measure-page-map.json", rows)
    record = {"stage": "page preparation; measure boxes and facsimile links are not created yet",
              "mei_input": str(Path(mei_file).resolve().relative_to(project)), "mei_sha256": pdf_file_sha256(mei_file),
              "pages_json": str(pages_json.relative_to(project)), "pages_json_sha256": pdf_file_sha256(pages_json),
              "image_sha256": page["sha256"], "image_pixels": [page["width"], page["height"]],
              "renderer": manifest["renderer"], "original_to_excerpt_to_printed": [8, 1, "8"],
              "body_measures": len(rows), "systems": len(systems),
              "scope": settings["scope"], "next_step": "Review one measure box per MEI measure, then merge facsimile links."}
    _preserve_json(project / "page-preparation-checkpoint.json", record)
    return rows, record
