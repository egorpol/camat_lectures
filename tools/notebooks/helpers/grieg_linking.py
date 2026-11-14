"""Grieg's Vöglein, from the PDF to a linked MEI file: source, pages, boxes, links, check."""

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

from IPython.display import HTML, Image, display

MEI_NS = "http://www.music-encoding.org/ns/mei"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
INPUTS_ZIP = "grieg-edition-inputs.zip"
SYSTEM_COLOURS = [(20, 90, 210), (170, 70, 10), (0, 125, 85), (140, 40, 150), (20, 115, 155)]


def _find(name, start=None):
    start = Path(start or Path.cwd()).resolve()
    for folder in (start, *start.parents):
        for candidate in (folder / name, folder / "notebooks" / name,
                          folder / "sessions/03-linking-and-editing/notebooks" / name):
            if candidate.is_file():
                return candidate
    return None


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _keep_or_write(path, data):
    """Write a file once; never replace a file that differs."""
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"{path} is already there and differs from the course file. "
                                  "Move it away, or choose a new PROJECT folder, and run the cell again.")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data)


def _bars(labels):
    labels = list(labels)
    return f"bars {labels[0]}–{labels[-1]}" if len(labels) > 1 else f"bar {labels[0]}"


def _short(path, project):
    try:
        return Path(path).resolve().relative_to(Path(project).resolve().parent)
    except ValueError:
        return Path(path)


# --- 1. The inputs, the working file and the volume ---------------------------

def load_inputs(project):
    """Unpack the course files once and make the working file work.mei."""
    project = Path(project).resolve()
    bundle = _find(INPUTS_ZIP)
    if bundle is None:
        raise FileNotFoundError(f"Put {INPUTS_ZIP} in the same folder as this notebook "
                                "(get_notebooks.py does this), then run this cell again.")
    with zipfile.ZipFile(bundle) as archive:
        expected = json.loads(archive.read("manifest.json"))["files_sha256"]
        files = {name: archive.read(name) for name in expected}
    for name, data in files.items():
        if hashlib.sha256(data).hexdigest() != expected[name]:
            raise ValueError(f"{name} in {bundle.name} is damaged. Download the ZIP again with get_notebooks.py.")
    settings = json.loads(files["settings.json"])
    inputs = project / "inputs"
    for name, data in files.items():
        if name != "manifest.json":
            _keep_or_write(inputs / name, data)
    work = project / "edition/mei/work.mei"
    if not work.exists():
        _keep_or_write(work, files[settings["mei"]])
        made = "Made your working file, a copy of the encoding:"
    else:
        made = "Your working file is already there. It is kept as it is:"
    context = {"project": project, "inputs": inputs, "settings": settings,
               "sources": json.loads(files["sources.json"]), "mei": inputs / settings["mei"], "work": work,
               "saved_boxes": {name.split("/")[1][:-5]: data for name, data in files.items() if name.startswith("boxes/")},
               "volume": project / "sources" / settings["volume_filename"],
               "excerpt": project / "sources" / settings["excerpt_filename"],
               "pages_json": project / "edition/pages/pages.json",
               "alignment": project / "edition/alignment.json"}
    print("The encoding, unchanged:", _short(context["mei"], project))
    print(made, _short(work, project))
    return context


def get_volume(context, allow_download=True):
    """Download the Peters volume from IMSLP once, and check that it is the course's file."""
    witness, volume = context["sources"]["printed_witness"], context["volume"]
    if volume.exists():
        if sha256_of(volume) != witness["sha256"]:
            raise ValueError(f"{volume.name} is not the scan the course uses. Move it away and run the cell again.")
        print("The volume is already there:", _short(volume, context["project"]))
    else:
        if not allow_download:
            raise FileNotFoundError(f"Copy the PDF here: {volume}")
        request = urllib.request.Request(witness["download_url"], headers={"User-Agent": "camat-grieg-seminar"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read(witness["bytes"] + 1)
        except OSError as problem:
            raise RuntimeError(f"Could not download the volume from IMSLP ({problem}). Check the internet connection "
                               f"and run the cell again, or copy the PDF from the USB stick to: {volume}") from None
        if len(data) != witness["bytes"] or hashlib.sha256(data).hexdigest() != witness["sha256"]:
            raise ValueError("The download is not the scan the course uses. Run the cell again later.")
        _keep_or_write(volume, data)
        print("Downloaded:", _short(volume, context["project"]))
    print(f"  {witness['bytes'] / 1e6:.1f} MB, {witness['page_count']} pages; "
          f"fingerprint (SHA-256) {witness['sha256'][:12]}…, the same as ours ✓")


# --- 2. Our two pages ----------------------------------------------------------

def cut_pages(context):
    """Copy PDF pages 9 and 10 of the volume into a PDF of their own; the volume stays unchanged."""
    import pypdf
    settings, record = context["settings"], context["sources"]["classroom_pdf"]
    if pypdf.__version__ != settings["pypdf_version"]:
        raise RuntimeError(f"This notebook needs pypdf {settings['pypdf_version']}, but {pypdf.__version__} is installed. "
                           "Run the first cell, restart the kernel, and run the notebook again.")
    volume, excerpt = context["volume"], context["excerpt"]
    before = sha256_of(volume)
    reader = pypdf.PdfReader(volume)
    writer, memory = pypdf.PdfWriter(), io.BytesIO()
    for number in settings["volume_pdf_pages"]:
        writer.add_page(reader.pages[number - 1])
    writer.add_metadata(record["pdf_metadata"])
    writer.write(memory)
    data = memory.getvalue()
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("The two-page PDF differs from ours. Ask your teacher.")
    _keep_or_write(excerpt, data)
    if sha256_of(volume) != before or len(pypdf.PdfReader(excerpt).pages) != 2:
        raise ValueError("Something went wrong while copying the pages. Ask your teacher.")
    print("Our two pages:", _short(excerpt, context["project"]))
    print(f"\n{'In the volume':<16}{'In our PDF':<13}Printed page")
    for mapping in record["page_mapping"]:
        print(f"PDF page {mapping['original_pdf_page']:<7}PDF page {mapping['excerpt_pdf_page']:<4}{mapping['printed_page']}")
    print("\nThe volume is unchanged ✓")


# --- 3. The pages as images ------------------------------------------------------

def draw_pages(context):
    """Draw both pages as PNG images at 300 dpi; CAMAT writes pages.json beside them."""
    from camat.pdf_facsimile import check_poppler, render_pdf_pages
    check_poppler()
    manifest = render_pdf_pages(context["excerpt"], context["pages_json"].parent, dpi=context["settings"]["dpi"])
    if manifest["pdf_sha256"] != context["sources"]["classroom_pdf"]["sha256"]:
        raise ValueError("The images do not come from our two-page PDF. Run the cells of parts 1 and 2 again.")
    for page in manifest["pages"]:
        if [page["width"], page["height"]] != context["settings"]["image_pixels"]:
            raise ValueError(f"{page['image']} is {page['width']} × {page['height']} pixels; we expected "
                             f"{' × '.join(map(str, context['settings']['image_pixels']))}. Ask your teacher.")
        print(f"PDF page {page['pdf_page_number']}: {_short(context['pages_json'].parent / page['image'], context['project'])}, "
              f"{page['width']} × {page['height']} pixels")
    print("CAMAT's record of the images:", _short(context["pages_json"], context["project"]))
    (context["pages_json"].parent / "boxes").mkdir(exist_ok=True)


def _manifest(context):
    if not context["pages_json"].is_file():
        raise FileNotFoundError("The page images are not there yet: run the cell of part 3 first.")
    return json.loads(context["pages_json"].read_text())


def _page(context, number):
    return next(page for page in _manifest(context)["pages"] if page["pdf_page_number"] == number)


def _picture(context, page, width):
    from PIL import Image as PILImage
    with PILImage.open(context["pages_json"].parent / page["image"]) as source:
        picture = source.convert("RGB")
    picture.thumbnail((width, width * 2))
    return picture


def _show_picture(picture):
    buffer = io.BytesIO()
    picture.save(buffer, format="PNG")
    display(Image(data=buffer.getvalue()))


def show_pages(context, width=560):
    """Both pages side by side, small."""
    from PIL import Image as PILImage
    pictures = [_picture(context, page, width) for page in _manifest(context)["pages"]]
    sheet = PILImage.new("RGB", (sum(p.width for p in pictures) + 20, max(p.height for p in pictures)), "white")
    sheet.paste(pictures[0], (0, 0))
    sheet.paste(pictures[1], (pictures[0].width + 20, 0))
    _show_picture(sheet)


# --- 4 and 5. Describe a page -----------------------------------------------------

def _systems(page):
    return [s["measures"] if isinstance(s, dict) else s for s in page.get("systems", [])]


def _sequence(layout):
    sequence = []
    for number in sorted(layout):
        for system in layout[number].get("systems", []):
            sequence.extend(system[1:] if sequence and system[0] == sequence[-1] else system)
    return sequence


def describe_page(context, line, number, save=True):
    """Check one page's line against the MEI file and save it in pages.json.

    CAMAT checks a whole movement. While the other page is not described yet, a page
    passes if its bars are an unbroken run of the MEI's bars, in order.
    """
    from camat.pdf_facsimile import apply_page_layout, check_page_layout, parse_page_layout
    ours = context["settings"]["layout"][number - 1]
    if not (line or "").strip():
        line = ours
        print(f"You have not written the line yet, so the notebook uses ours:\n    {ours}\n")
    try:
        layout = parse_page_layout(line, page_count=2)
    except ValueError as problem:
        print(f"CAMAT cannot read the line: {problem}\nNothing was saved.")
        return
    if set(layout) != {number}:
        print(f"This line describes PDF page {', '.join(map(str, layout))}; this cell is for PDF page {number}. "
              f"Start the line with {number} |. Nothing was saved.")
        return
    # The other page, as far as it is described already.
    for page in _manifest(context)["pages"]:
        if page["pdf_page_number"] != number and page["role"] == "music":
            layout[page["pdf_page_number"]] = {"role": "music", "printed_page": page.get("printed_page"),
                                               "systems": _systems(page)}
    rest = []
    try:
        check_page_layout(layout, context["work"])
    except ValueError as problem:
        details = getattr(problem, "details", {})
        bars, sequence = details.get("bars", []), _sequence(layout)
        starts = [i for i, bar in enumerate(bars) if sequence and bar == sequence[0]]
        unbroken = bool(starts) and bars[starts[0]:starts[0] + len(sequence)] == sequence
        if len(layout) == 2 or getattr(problem, "code", None) != "bars" or details.get("extra") or not unbroken:
            print(f"{problem}\nNothing was saved. Compare the line with the page, correct it and run the cell again.")
            return
        rest = details["missing"]
    if not save:
        print("CAMAT accepts this line (not saved).")
        return
    apply_page_layout(context["pages_json"], layout)
    page = layout[number]
    print(f"✓ Saved: PDF page {number} is printed page {page['printed_page']}, with {len(page['systems'])} systems.")
    for index, labels in enumerate(page["systems"], 1):
        print(f"    system {index}: {_bars(labels)} ({len(labels)} bars)")
    if rest:
        print(f"CAMAT checked the bars against the MEI file: none missing in between, in the right order.\n"
              f"Not described yet: {_bars(rest)}, on the other page.")
    else:
        print("CAMAT checked both pages against the MEI file: all its bars, each once, in the right order.")


# --- Boxes ---------------------------------------------------------------------

def box_file(context, number):
    return context["pages_json"].parent / "boxes" / f"{_page(context, number)['page_id']}.json"


def box_prompt(context, number):
    """A prompt for a chat model that can read images."""
    page = _page(context, number)
    counts = ", ".join(str(len(s)) for s in _systems(page)) or "?"
    image = context["pages_json"].parent / page["image"]
    print("1. In the chat, attach this image:", _short(image, context["project"]))
    print("2. Copy the prompt between the lines into the chat:\n")
    print("-" * 70)
    print(f"""The attached image is a page of printed piano music, {page['width']} pixels wide and
{page['height']} pixels high. It has {len(_systems(page)) or 'several'} systems of two staves each; from top to
bottom they have {counts} bars. Find every bar and give it a box from the barline
where it begins (or the start of the system) to the barline where it ends,
covering both staves. A short bar before or after a repeat sign is a bar too.

Answer only with JSON in this form, nothing else. Coordinates are pixels of the
full image: x from the left edge, y from the top edge. ulx, uly is the upper
left corner of a box, lrx, lry the lower right corner.

{{"measures": [{{"ulx": 100, "uly": 200, "lrx": 300, "lry": 400}}, ...]}}""")
    print("-" * 70)
    print(f"\n3. Save the answer (only the JSON) as: {_short(box_file(context, number), context['project'])}")


def _box_source(context, path, page):
    """Where a box file comes from. The detector's run record comes first: for the same
    pixels the detector can answer with exactly the bytes of the saved file."""
    data = path.read_bytes()
    run = path.with_suffix(".run.json")
    if run.is_file():
        edited = json.loads(run.read_text()).get("response_sha256") != hashlib.sha256(data).hexdigest()
        return "the detector's answer" + (", edited since" if edited else "")
    if data == context["saved_boxes"].get(page["page_id"]):
        return "the boxes we saved for the course"
    return "your own file (for example the chat's answer)"


def find_boxes(context, number, send=False):
    """Use the box file of a page: the chat's answer, the detector's answer, or the saved boxes."""
    from camat.pdf_facsimile import detect_measure_boxes
    page = _page(context, number)
    if page["role"] != "music":
        print(f"Describe PDF page {number} first (the cell above), then run this cell again.")
        return
    path = box_file(context, number)
    saved = context["saved_boxes"][page["page_id"]]
    if send:
        if path.exists() and _box_source(context, path, page) != "the boxes we saved for the course":
            print(f"There is already a box file for this page, {_box_source(context, path, page)}:\n"
                  f"    {_short(path, context['project'])}\nIt is kept. To send the page again, delete or rename "
                  "that file, then run this cell again.")
        else:
            # The detector gets every described page without a box file, so check the other page first.
            others = [p for p in _manifest(context)["pages"] if p["role"] == "music" and p["page_id"] != page["page_id"]
                      and not (path.parent / f"{p['page_id']}.json").exists()]
            if others:
                print(f"PDF page {others[0]['pdf_page_number']} is described but has no boxes yet: "
                      "run its box cell first. Nothing was sent.")
                return
            path.unlink(missing_ok=True)  # the saved boxes give way to the detector's answer
            print(f"Sending PDF page {number} to the Edirom measure detector (measure-detector.edirom.de) …")
            try:
                detect_measure_boxes(context["pages_json"], allow_upload=True)
            except Exception as problem:  # network, server or answer
                print(f"The detector did not answer ({problem}).\nRun the cell again in a minute, or use the "
                      "saved boxes: set SEND_TO_DETECTOR = False and run the cell again.")
                return
    elif not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(saved)
        print("There is no box file for this page yet, so the notebook uses the boxes we saved for the course.\n"
              "To find them yourself, use the chat or the detector (see above) and run this cell again.\n")
    print(f"Boxes for PDF page {number}: {_box_source(context, path, page)}")
    print(f"    {_short(path, context['project'])}")
    _report(context, page, path)


def _read_boxes(page, path):
    """(systems, problem): CAMAT's grouping of the boxes into systems, or what is wrong with the file."""
    from camat.pdf_facsimile import group_measure_boxes_into_systems
    if not path.is_file():
        return None, f"There is no box file yet: {path.name}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as problem:
        return None, (f"{path.name} cannot be read as JSON: line {problem.lineno}, column {problem.colno}: {problem.msg}. "
                      "Often a comma or a bracket is missing, or text from the chat came along. Fix it and save.")
    try:
        return group_measure_boxes_into_systems(payload, page), None
    except (ValueError, KeyError, TypeError) as problem:
        return None, f"{path.name}: {problem}. Fix it and save."


def _report(context, page, path):
    systems, problem = _read_boxes(page, path)
    if problem:
        print("✗", problem)
        return
    needed = _systems(page)
    print(f"    {sum(map(len, systems))} boxes in {len(systems)} rows; the page has {len(needed)} systems "
          f"with {sum(map(len, needed))} bars.")


# --- The live box overlay -----------------------------------------------------------

_watchers = {}


def _overlay(context, number, base):
    """(status as HTML, PNG bytes): the page with the boxes of its box file, numbered with their bars."""
    from PIL import ImageDraw, ImageFont
    page = _page(context, number)
    path = box_file(context, number)
    scale = base.width / page["width"]
    needed = _systems(page)
    systems, problem = _read_boxes(page, path)
    picture = base.copy()
    lines = []
    if problem:
        lines.append(f"<b style='color:#b91c1c'>✗ {problem}</b>")
    else:
        draw = ImageDraw.Draw(picture, "RGBA")
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        except OSError:
            font = ImageFont.load_default(22)
        for row, boxes in enumerate(systems):
            colour = SYSTEM_COLOURS[row % len(SYSTEM_COLOURS)]
            labels = needed[row] if row < len(needed) and len(needed[row]) == len(boxes) else None
            for index, box in enumerate(boxes):
                ulx, uly, lrx, lry = (round(v * scale) for v in box["bbox"])
                draw.rectangle([ulx, uly, lrx, lry], fill=(*colour, 22), outline=(*colour, 235), width=3)
                label = labels[index] if labels else f"{row + 1}.{index + 1}?"
                corner = (ulx + 6, lry - 6)
                left, top, right, bottom = draw.textbbox(corner, label, font=font, anchor="lb")
                draw.rectangle([left - 3, top - 2, right + 3, bottom + 2], fill=(255, 255, 255, 225))
                draw.text(corner, label, font=font, fill=(*colour, 255), anchor="lb")
        for row in range(max(len(systems), len(needed))):
            have = len(systems[row]) if row < len(systems) else 0
            if row < len(needed):
                fits = have == len(needed[row])
                lines.append(f"<span style='color:{'#047857' if fits else '#b91c1c'}'>{'✓' if fits else '✗'} "
                             f"system {row + 1}: {have} boxes for {_bars(needed[row])} ({len(needed[row])} bars)</span>")
            else:
                lines.append(f"<span style='color:#b91c1c'>✗ row {row + 1}: {have} boxes, but the page has "
                             f"only {len(needed)} systems</span>")
        if [len(s) for s in systems] == [len(s) for s in needed]:
            lines.append("<b>The counts fit. Now look: does each number sit on its bar, in both staves?</b>")
        else:
            lines.append("<b>A label like 2.3? is the 3rd box of a row whose count does not fit.</b>")
    lines.append(f"<span style='color:#6b7280'>{path.name} · drawn at {time.strftime('%H:%M:%S')}</span>")
    buffer = io.BytesIO()
    picture.save(buffer, format="PNG")
    return "<br>".join(lines), buffer.getvalue()


class BoxOverlay:
    """The page with its numbered boxes, drawn again each time the box file or pages.json is saved."""

    def __init__(self, context, number, width=900, interval=1.0):
        import ipywidgets as widgets
        self.context, self.number = context, number
        self.path = box_file(context, number)
        self.base = _picture(context, _page(context, number), width)
        self.status = widgets.HTML()
        self.image = widgets.Image(format="png", layout=widgets.Layout(width=f"{width}px", max_width="100%"))
        self.box = widgets.VBox([self.status, self.image])
        self.interval, self.callback, self.seen = interval, None, None

    def _stamp(self):
        stamps = []
        for path in (self.path, self.context["pages_json"]):
            try:
                stat = path.stat()
                stamps.append((stat.st_mtime_ns, stat.st_size))
            except OSError:
                stamps.append(None)
        return tuple(stamps)

    def draw(self):
        self.seen = self._stamp()
        self.status.value, self.image.value = _overlay(self.context, self.number, self.base)

    def _poll(self):
        if self._stamp() != self.seen:
            try:
                self.draw()
            except Exception as problem:  # keep watching while the file is half written
                self.status.value = f"<b style='color:#b91c1c'>Could not draw: {problem}</b>"

    def start(self):
        from tornado.ioloop import PeriodicCallback
        self.draw()
        self.callback = PeriodicCallback(self._poll, int(self.interval * 1000))
        self.callback.start()
        return self

    def stop(self):
        if self.callback is not None:
            self.callback.stop()
            self.callback = None
            self.status.value += "<br><i>Stopped watching the file.</i>"


def watch_boxes(context, number):
    """Show the live box overlay for one page; it redraws when the box file is saved."""
    page = _page(context, number)
    if page["role"] != "music":
        print(f"Describe PDF page {number} first, then run this cell again.")
        return None
    old = _watchers.pop(page["page_id"], None)
    if old is not None:
        old.stop()
    try:
        overlay = BoxOverlay(context, number).start()
    except ImportError:
        print("The live picture needs ipywidgets, so this picture does not follow the file. "
              "Run this cell again after each change. The boxes as they are now:")
        status, png = _overlay(context, number, _picture(context, page, 900))
        display(HTML(status))
        display(Image(data=png))
        return None
    _watchers[page["page_id"]] = overlay
    display(overlay.box)
    return overlay


def stop_watching():
    for overlay in list(_watchers.values()):
        overlay.stop()
    _watchers.clear()


def list_boxes(context, number):
    """Each bar with the position of its box in the file and its four numbers."""
    page = _page(context, number)
    path = box_file(context, number)
    systems, problem = _read_boxes(page, path)
    if problem:
        print("✗", problem)
        return
    needed = _systems(page)
    print(f"{path.name}: bar, box number in the file (counted from 1), and its four numbers (left, top, right, bottom)")
    for row, boxes in enumerate(systems):
        labels = needed[row] if row < len(needed) and len(needed[row]) == len(boxes) else None
        print(f"System {row + 1}")
        for index, box in enumerate(boxes):
            bar = f"bar {labels[index]}" if labels else f"{row + 1}.{index + 1}?"
            print(f"    {bar:<9} box {box['box_index'] + 1:>2}: {tuple(box['bbox'])}")


# --- 6. Align, review, link ------------------------------------------------------------

def align_pages(context, width=560):
    """Pair the boxes with the bars, system by system, and draw CAMAT's overlays of both pages."""
    from camat.pdf_facsimile import build_measure_alignment, check_page_layout, draw_alignment_overlays
    from PIL import Image as PILImage
    manifest = _manifest(context)
    layout = {p["pdf_page_number"]: {"role": "music", "systems": _systems(p)}
              for p in manifest["pages"] if p["role"] == "music"}
    if len(layout) != 2:
        print("Describe both pages first (parts 4 and 5), then run this cell again.")
        return False
    try:
        check_page_layout(layout, context["work"])
    except ValueError as problem:
        print(f"The two page lines do not fit the MEI file:\n{problem}\nCorrect the line in part 4 or 5 and run it again.")
        return False
    missing = [p["pdf_page_number"] for p in manifest["pages"] if not box_file(context, p["pdf_page_number"]).exists()]
    if missing:
        print(f"PDF page {missing[0]} has no box file yet: run its box cell (part 4 or 5), then this cell.")
        return False
    try:
        alignment = build_measure_alignment(context["pages_json"], output=context["alignment"])
    except ValueError as problem:
        context["alignment"].unlink(missing_ok=True)
        print("CAMAT did not pair the boxes with the bars: in some systems the number of boxes and bars differs.\n"
              f"{problem}\n(actual = boxes found, expected = bars in the description.) Fix the boxes, "
              "check them in the live picture, and run this cell again.")
        return False
    data = json.loads(alignment.read_text())
    print(f"✓ CAMAT paired {len(data['regions'])} boxes with {len(data['regions'])} bars on {len(data['pages'])} pages.")
    outputs = draw_alignment_overlays(alignment, context["project"] / "edition/overlays")
    pictures = []
    for output in outputs:
        with PILImage.open(output) as picture:
            picture = picture.convert("RGB")
            picture.thumbnail((width, width * 2))
            pictures.append(picture)
    sheet = PILImage.new("RGB", (sum(p.width for p in pictures) + 20, max(p.height for p in pictures)), "white")
    sheet.paste(pictures[0], (0, 0))
    sheet.paste(pictures[1], (pictures[0].width + 20, 0))
    _show_picture(sheet)
    print("Full size:", ", ".join(str(_short(output, context["project"])) for output in outputs))
    return True


def record_review(context, names):
    from camat.pdf_facsimile import approve_alignment_review
    if not context["alignment"].is_file():
        print("Run the cell above first, until it shows ✓.")
        return
    if not (names or "").strip():
        print("Write your names after REVIEWED_BY = and run the cell again. Without them the links can still be made, "
              "but CAMAT records both pages as unreviewed.")
        return
    approve_alignment_review(context["alignment"], names)
    review = json.loads(context["alignment"].read_text())["review"]
    for page_id, entry in review.items():
        print(f"✓ {page_id}: reviewed by {entry['reviewer']} on {entry['date']}")


def _music(root):
    """The music of a file without the links: to check that linking changed nothing else."""
    ns = f"{{{MEI_NS}}}"
    body = root.find(f"{ns}music/{ns}body")

    def walk(element):
        if element.tag in {ns + "pb", ns + "sb"}:
            return None
        attributes = {k: v for k, v in element.attrib.items() if k != "facs"}
        if element.tag == ns + "mdiv":
            attributes.pop("n", None)  # linking numbers the one movement n="1"
        return (element.tag, sorted(attributes.items()), (element.text or "").strip(),
                [value for child in element if (value := walk(child)) is not None])
    return walk(body)


def _linked_text(context, text):
    """(text, report, breaks): an MEI text with this edition's links, made beside work.mei
    so that the path to the page images is right for files in edition/mei and edition/checkpoints."""
    from camat.pdf_facsimile import integrate_pdf_facsimile, number_single_mdiv, write_page_breaks
    handle = tempfile.NamedTemporaryFile(prefix=".linking-", suffix=".mei", dir=context["work"].parent, delete=False)
    handle.close()
    candidate = Path(handle.name)
    try:
        candidate.write_text(number_single_mdiv(text), encoding="utf-8")
        report = integrate_pdf_facsimile(candidate, context["pages_json"], context["alignment"], candidate)
        breaks = write_page_breaks(candidate, context["pages_json"], candidate)
        return candidate.read_text(encoding="utf-8"), report, breaks
    finally:
        candidate.unlink(missing_ok=True)


def _replace(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(prefix=".saving-", suffix=".mei", dir=path.parent, delete=False)
    handle.close()
    Path(handle.name).write_text(text, encoding="utf-8")
    os.replace(handle.name, path)


def link_work(context):
    """Add the links to work.mei, keeping a copy of it as it was before.

    The unchanged encoding gets the same links, as edition/checkpoints/before-editing.mei:
    block 2 compares work.mei with it, so that its list of changes shows only your edits.
    """
    project, work = context["project"], context["work"]
    if not context["alignment"].is_file():
        print("Run the cell that pairs the boxes with the bars first, until it shows ✓.")
        return
    try:
        root = ET.parse(work).getroot()
    except ET.ParseError as error:
        line, column = error.position
        print(f"{work.name} cannot be read as XML: the problem is at line {line}, column {column}.\n"
              "Fix it in the editor first (Ctrl+Z, on a Mac Cmd+Z, undoes your last change), save, "
              "and run this cell again. Nothing was changed.")
        return
    text = work.read_text(encoding="utf-8")
    try:
        linked, report, breaks = _linked_text(context, text)
        baseline, _, _ = _linked_text(context, context["mei"].read_text(encoding="utf-8"))
    except ValueError as problem:
        print(f"The links were not added: {problem}\nNothing was changed.")
        return
    if _music(ET.fromstring(linked.encode("utf-8"))) != _music(root):
        print(f"Linking would change more than the links in {work.name}; nothing was saved. Ask your teacher.")
        return
    backup = project / "edition/checkpoints/work-before-linking.mei"
    if not backup.exists():
        _keep_or_write(backup, text.encode("utf-8"))
    _replace(work, linked)
    _replace(project / "edition/checkpoints/before-editing.mei", baseline)
    if "<facsimile" in text:
        print(f"✓ Updated the links in your working file, for the boxes as they are now: {_short(work, project)}")
    else:
        print(f"✓ Added the links to your working file: {_short(work, project)}")
    print(f"  {report['measures_linked']} bars point to their boxes on {report['surfaces']} pages; "
          f"{breaks['pb']} page breaks and {breaks['sb']} system breaks follow the print.")
    if report.get("unreviewed_pages"):
        print(f"  Not reviewed yet: {', '.join(report['unreviewed_pages'])} (write your names in the cell above).")
    print("  The music is unchanged: only the links are new.")
    print(f"  The file as it was before the links: {_short(backup, project)}")


# --- 7. Follow one link ---------------------------------------------------------------------

def _line_of(lines, text, start=0):
    for number in range(start, len(lines)):
        if text in lines[number]:
            return number
    return None


def follow_link(context, bar, width=900):
    """The chain from <measure n="bar"> to its zone, page and image, with the line numbers of work.mei."""
    work = context["work"]
    lines = work.read_text(encoding="utf-8").split("\n")
    root = ET.parse(work).getroot()
    music = root.find(f"{{{MEI_NS}}}music")
    measure = next((m for m in music.iter(f"{{{MEI_NS}}}measure") if m.get("n") == str(bar)), None)
    if measure is None:
        print(f"There is no <measure n=\"{bar}\"> in the music. Choose a bar from 1 to 39.")
        return
    if not measure.get("facs"):
        print(f"Bar {bar} has no link yet (no facs). Run the cell of part 6 first.")
        return
    zone_id = measure.get("facs").lstrip("#")
    zone = surface = None
    for candidate_surface in music.iter(f"{{{MEI_NS}}}surface"):
        for candidate_zone in candidate_surface.iter(f"{{{MEI_NS}}}zone"):
            if candidate_zone.get(XML_ID) == zone_id:
                zone, surface = candidate_zone, candidate_surface
    graphic = surface.find(f"{{{MEI_NS}}}graphic")
    start = _line_of(lines, "<music")
    steps = [("the bar", _line_of(lines, f'xml:id="{measure.get(XML_ID)}"', start), "facs points to the zone"),
             ("the zone", _line_of(lines, f'xml:id="{zone_id}"', start), "the box: ulx, uly (upper left), lrx, lry (lower right)"),
             ("its page", _line_of(lines, f'xml:id="{surface.get(XML_ID)}"', start), "the <surface> holding the zone"),
             ("the image", _line_of(lines, f'target="{graphic.get("target")}"', start), "the image file, seen from work.mei")]
    for name, number, note in steps:
        print(f"{name:<10} line {number + 1:>4}: {lines[number].strip()}")
        print(f"{'':<21}↑ {note}")
    box = [int(float(zone.get(k))) for k in ("ulx", "uly", "lrx", "lry")]
    image = (work.parent / graphic.get("target")).resolve()
    from PIL import Image as PILImage, ImageDraw
    with PILImage.open(image) as source:
        picture = source.convert("RGB")
    margin = 120
    region = (max(0, box[0] - margin), max(0, box[1] - margin),
              min(picture.width, box[2] + margin), min(picture.height, box[3] + margin))
    draw = ImageDraw.Draw(picture, "RGBA")
    draw.rectangle(box, fill=(200, 30, 30, 25), outline=(200, 30, 30, 240), width=8)
    crop = picture.crop(region)
    crop.thumbnail((width, width))
    print(f"\nThe box ({', '.join(map(str, box))}) on {image.name}:")
    _show_picture(crop)


# --- 8. The check -----------------------------------------------------------------------

def _validate(path, folder):
    subprocess.run([sys.executable, "-m", "camat.mei_validation", str(path), "--output-dir", str(folder), "--verovio"],
                   text=True, capture_output=True, timeout=300)
    findings = Path(folder) / "findings.json"
    return json.loads(findings.read_text()) if findings.is_file() else None


def _finding_key(finding):
    # Line numbers move when lines are added, and Verovio names elements without an xml:id
    # with new random IDs on each run, so neither is compared.
    message = finding.get("message", "")
    if finding.get("check") == "verovio_log" and " with @xml:id " in message:
        message = message.split(" with @xml:id ")[0] + " " + message.split(" has ", 1)[-1]
    return tuple(finding.get(k) for k in ("severity", "check", "element", "xml_id", "measure_n", "staff_n", "layer_n")) + (message,)


def check_links(context):
    """Check work.mei with CAMAT's MEI checker; show only what is new since before the links."""
    project, work = context["project"], context["work"]
    if "<facsimile" not in work.read_text(encoding="utf-8"):
        print(f"{work.name} has no links yet. Run the cell of part 6 until it shows ✓, then this cell.")
        return
    backup = project / "edition/checkpoints/work-before-linking.mei"
    now = _validate(work, project / "edition/validation-linked")
    then = _validate(backup, project / "edition/validation-before-linking")
    if now is None or then is None:
        print("The checker did not run. Run the cell again; if it still fails, ask your teacher.")
        return
    known = {}
    for finding in then:
        known[_finding_key(finding)] = known.get(_finding_key(finding), 0) + 1
    new = []
    for finding in now:
        key = _finding_key(finding)
        if known.get(key):
            known[key] -= 1
        else:
            new.append(finding)
    print(f"Checked {work.name} against the MEI rules (schema), its links and the page images, and with Verovio.")
    if not new:
        print("✓ No new problems: every bar points to a zone in the file, and the file finds both page images.")
        print(f"  (The encoding already had {len(then)} remarks before the links; they are not shown here.)")
        return
    for finding in new:
        where = f" (bar {finding['measure_n']})" if finding.get("measure_n") else ""
        mark = "✗" if finding["severity"] == "error" else "!"
        print(f"  {mark} line {finding.get('line') or '?'}{where}: {finding['message']}")
    if any(finding["severity"] == "error" for finding in new):
        print("Fix the lines marked ✗, save, and run this cell again.")
    print(f"The full report is in {_short(project / 'edition/validation-linked', project)}.")
