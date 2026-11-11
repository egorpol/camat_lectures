"""Live editing of the Schumann MEI file: working copy, print excerpt, change report, check."""

import copy
import difflib
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

from IPython.display import Image, display

MEI_NS = "http://www.music-encoding.org/ns/mei"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ET.register_namespace("", MEI_NS)
INPUTS_ZIP = "schumann-edition-inputs.zip"
TASK_ELEMENTS = {"dynam", "tempo", "slur", "annot"}  # what the tasks in this notebook add
IMSLP_PAGE = "https://imslp.org/wiki/Special:ImagefromIndex/51556"


def _name(element):
    return element.tag.split("}")[-1]


def bar_name(n):
    """MEI numbers the pickup as measure 1; musicians call the next bar bar 1."""
    if n == "1":
        return "the pickup"
    return f"bar {int(n) - 1}" if n and n.isdigit() else f"measure {n}"


def _count(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def _pitch(note):
    accidental = {"f": "♭", "s": "♯", "n": "", "ff": "𝄫", "ss": "𝄪"}
    sign = accidental.get(note.get("accid") or note.get("accid.ges") or "n", "")
    return f"{note.get('pname', '?').upper()}{sign}{note.get('oct', '')}"


# --- The working file -------------------------------------------------------

def _find_inputs_zip(start=None):
    start = Path(start or Path.cwd()).resolve()
    for folder in (start, *start.parents):
        for candidate in (folder / INPUTS_ZIP, folder / "notebooks" / INPUTS_ZIP,
                          folder / "sessions/02-building-an-edition/notebooks" / INPUTS_ZIP):
            if candidate.is_file():
                return candidate
    return None


def _starter_bytes(project):
    bundle = _find_inputs_zip()
    if bundle:
        with zipfile.ZipFile(bundle) as archive:
            data = archive.read("starter.mei")
            expected = json.loads(archive.read("manifest.json"))["files_sha256"]["starter.mei"]
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"starter.mei in {bundle} is damaged. Download the ZIP again with get_notebooks.py.")
        return data
    unpacked = sorted((project / "inputs").glob("*/starter.mei"))
    if unpacked:
        return unpacked[-1].read_bytes()
    raise FileNotFoundError(f"Put {INPUTS_ZIP} in the same folder as this notebook "
                            "(get_notebooks.py does this), then run this cell again.")


def _write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data)


def prepare_work_file(project):
    """Return (work, before). Creates each file once and never overwrites one."""
    project = Path(project).resolve()
    work = project / "edition/mei/work.mei"
    before = project / "edition/checkpoints/before-editing.mei"
    linked = project / "edition/checkpoints/linked-before-editing.mei"
    if not before.exists():
        if linked.exists():
            before = linked  # the linking notebook ran first: keep its page links
        else:
            _write_new(before, _starter_bytes(project))
    if work.exists():
        print("Your working file is already there. It is kept as it is:")
    else:
        _write_new(work, before.read_bytes())
        print("Copied the starting file to your working file:")
    print("  ", work.relative_to(project.parent))
    print("The file as it was before editing (do not edit this one):")
    print("  ", before.relative_to(project.parent))
    return work, before


# --- The print --------------------------------------------------------------

def show_print(project, width=1000):
    """Show the first two systems of page 8, from 02_pdf_preparation's page image."""
    image = Path(project) / "edition/pages/page-0001.png"
    if not image.is_file():
        print("The page image is not there yet. 02_pdf_preparation.ipynb makes it (session 2, part 3):\n"
              "run that notebook to the end, then run this cell again.\n"
              f"Until then, look at page 8 of the scan on IMSLP: {IMSLP_PAGE}")
        return
    from PIL import Image as PILImage
    with PILImage.open(image) as page:
        w, h = page.size
        # Systems 1 and 2 of the 300 dpi page (4167 x 5617 pixels), without the title.
        crop = page.crop((round(w * 0.036), round(h * 0.100), round(w * 0.962), round(h * 0.410)))
        crop.thumbnail((width, width))
        buffer = io.BytesIO()
        crop.convert("RGB").save(buffer, format="PNG")
    display(Image(data=buffer.getvalue()))


# --- Reading the file -------------------------------------------------------

def _read(path):
    """Parse an MEI file; on an XML error print what to do and return None."""
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as error:
        line, column = error.position
        print(f"{Path(path).name} cannot be read as XML: the problem is at line {line}, column {column}.\n"
              "Usually a tag is not closed, or a < or a quotation mark is missing, at or just before that line.\n"
              "Undo your last change in the editor (Ctrl+Z, on a Mac Cmd+Z), save, and run this cell again.")
        return None


def _measures(root):
    """Map every element inside a measure to that measure."""
    owner = {}
    for measure in root.iter(f"{{{MEI_NS}}}measure"):
        for element in measure.iter():
            owner[element] = measure
    return owner


def measure_xml(root, n):
    """The XML text of measure @n, as in the file."""
    for measure in root.iter(f"{{{MEI_NS}}}measure"):
        if measure.get("n") == str(n):
            excerpt = copy.deepcopy(measure)
            excerpt.tail = None
            lines = ET.tostring(excerpt, encoding="unicode").replace(f' xmlns="{MEI_NS}"', "").split("\n")
            indent = min((len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()), default=0)
            return "\n".join([lines[0]] + [line[indent:] for line in lines[1:]])
    raise ValueError(f"No measure n=\"{n}\" in the file.")


def slur_prompt(work):
    root = _read(work)
    if root is None:
        return ""
    return f'''I am editing an MEI file (MEI 5.1) of Schumann, Album für die Jugend, Op. 68 No. 10.
Add the slur printed in the left hand (staff 2). It starts on the C3 of the pickup,
measure n="1", and ends on the last note of the next measure, n="2", an F3.
It curves above the notes.

Add one <slur> element inside the pickup measure, after its <staff> elements, with
startid and endid pointing to the xml:id of the two notes (with a # in front),
staff="2", curvedir="above" and xml:id="seminar-slur-pickup". Change nothing else.

Here are the two measures from the file:

{measure_xml(root, 1)}
{measure_xml(root, 2)}
'''


# --- What changed -----------------------------------------------------------

def _key(element):
    attributes = tuple(sorted((k, v) for k, v in element.attrib.items() if k != XML_ID))
    return _name(element), element.get(XML_ID), attributes, (element.text or "").strip()


def _describe(element, by_id, owner):
    """One line for an element: its name, text, notes it points to, other attributes."""
    name = _name(element)
    parts = [f"<{name}>"]
    if name == "note":
        parts.append(_pitch(element))
    text = " ".join("".join(element.itertext()).split())
    if text:
        parts.append(f'"{text[:60]}"')
    if element.get(XML_ID):
        parts.append(f"(xml:id {element.get(XML_ID)})")
    children = list(element)
    if name in ("beam", "tuplet") and children:
        kinds = sorted({_name(child) for child in children})
        ids = ", ".join(child.get(XML_ID) for child in children if child.get(XML_ID))
        parts.append(f"around {_count(len(children), kinds[0] if len(kinds) == 1 else 'element')}"
                     + (f" ({ids})" if ids else ""))
    details = []
    for attribute in ("startid", "endid"):
        target = (element.get(attribute) or "").lstrip("#")
        if target:
            word = "from" if attribute == "startid" else "to"
            note = by_id.get(target)
            if note is None:
                details.append(f"{word} #{target} (no element in the file has this xml:id!)")
            else:
                where = bar_name(owner[note].get("n")) if note in owner else "outside the bars"
                pitch = _pitch(note) if _name(note) == "note" else f"<{_name(note)}>"
                details.append(f"{word} {pitch} in {where}")
    for attribute, value in sorted(element.attrib.items()):
        if attribute not in (XML_ID, "startid", "endid") and "}" not in attribute:
            details.append(f'{attribute}="{value}"')
    return " ".join(parts) + (": " + ", ".join(details) if details else "")


def show_changes(before, work):
    """Print, in plain words, what changed in work.mei since the file before editing.

    Spaces and line breaks are not counted. This never stops the notebook.
    """
    old, new = _read(before), _read(work)
    if old is None or new is None:
        return
    old_elements, new_elements = list(old.iter()), list(new.iter())
    old_owner, new_owner = _measures(old), _measures(new)
    new_ids = {}
    duplicates = set()
    for element in new_elements:
        if element.get(XML_ID):
            if element.get(XML_ID) in new_ids:
                duplicates.add(element.get(XML_ID))
            new_ids[element.get(XML_ID)] = element
    old_ids = {e.get(XML_ID): e for e in old_elements if e.get(XML_ID)}

    changes = []  # (where, sign, text, asked_for)
    matcher = difflib.SequenceMatcher(None, [_key(e) for e in old_elements],
                                      [_key(e) for e in new_elements], autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        removed, added = old_elements[i1:i2], new_elements[j1:j2]
        same_id = {e.get(XML_ID) for e in removed if e.get(XML_ID)} & {e.get(XML_ID) for e in added}
        for element in added:
            where = new_owner.get(element)
            where = bar_name(where.get("n")) if where is not None else "outside the bars"
            if element.get(XML_ID) in same_id:
                was = next(e for e in removed if e.get(XML_ID) == element.get(XML_ID))
                diffs = [f'{a}: "{was.get(a)}" → "{element.get(a)}"' for a in sorted(set(was.attrib) | set(element.attrib))
                         if was.get(a) != element.get(a)]
                if (was.text or "").strip() != (element.text or "").strip():
                    diffs.append(f'text: "{(was.text or "").strip()}" → "{(element.text or "").strip()}"')
                label = f"<{_name(element)}> {element.get(XML_ID)}"
                if _name(element) == "note":
                    label += f" ({_pitch(was)} → {_pitch(element)})" if _pitch(was) != _pitch(element) else f" ({_pitch(element)})"
                changes.append((where, "~", f"changed {label}: " + "; ".join(diffs), False))
            elif not any(element in parent for parent in added if parent is not element):
                asked = _name(element) in TASK_ELEMENTS and element.get(XML_ID) not in old_ids
                changes.append((where, "+", "new " + _describe(element, new_ids, new_owner), asked))
        for element in removed:
            if element.get(XML_ID) in same_id or any(element in parent for parent in removed if parent is not element):
                continue
            where = old_owner.get(element)
            where = bar_name(where.get("n")) if where is not None else "outside the bars"
            changes.append((where, "-", "removed " + _describe(element, old_ids, old_owner), False))

    if not changes:
        print(f"No changes yet: {Path(work).name} is the same as before editing (spaces and line breaks are not counted).")
        return
    print(f"Changes in {Path(work).name} since before editing (spaces and line breaks are not counted):")
    places = []
    for where, *_ in changes:
        if where not in places:
            places.append(where)
    for where in places:
        print(f"\n{where[0].upper() + where[1:]}")
        for _, sign, text, asked in (c for c in changes if c[0] == where):
            print(f"  {sign} {text}" + ("" if asked else "   ← not part of the tasks"))
    problems = [f"xml:id {i} is used more than once" for i in sorted(duplicates)]
    for element in new_elements:
        for attribute in ("startid", "endid", "plist"):
            for token in (element.get(attribute) or "").split():
                if token.startswith("#") and token[1:] not in new_ids:
                    problems.append(f"<{_name(element)}> {attribute} points to {token}, but no element has that xml:id")
    others = [text for _, sign, text, asked in changes if not asked]
    if others:
        print(f"\n{_count(len(others), 'change')} {'was' if len(others) == 1 else 'were'} not part of the tasks. "
              "Look at each one in the print: keep it if the print shows it, otherwise undo it in the editor.")
    if problems:
        print("\nTo fix:")
        for problem in problems:
            print("  ✗", problem)


# --- Checking the file ------------------------------------------------------

def _validate(path, folder):
    result = subprocess.run([sys.executable, "-m", "camat.mei_validation", str(path),
                             "--output-dir", str(folder), "--verovio"],
                            text=True, capture_output=True, timeout=300)
    findings_file = Path(folder) / "findings.json"
    if not findings_file.is_file():
        print("The checker did not run:")
        print(result.stderr[-2000:])
        return None
    return json.loads(findings_file.read_text())


def _finding_key(finding):
    # Line numbers move when lines are added, so they are not part of the comparison.
    return tuple(finding.get(k) for k in ("severity", "check", "element", "xml_id", "measure_n", "staff_n", "layer_n", "message"))


def check_file(work, before, project):
    """Run CAMAT's MEI checker on work.mei and report what is new since before editing."""
    if _read(work) is None:
        return
    project = Path(project)
    now = _validate(work, project / "edition/validation-editing")
    then = _validate(before, project / "edition/validation-before-editing")
    if now is None or then is None:
        return
    known = {_finding_key(f) for f in then}
    new = [f for f in now if _finding_key(f) not in known]
    errors = [f for f in new if f["severity"] == "error"]
    print(f"Checked {Path(work).name} against the MEI rules (schema) and with Verovio.")
    if not new:
        print(f"✓ No new problems. (The file before editing already had {_count(len(then), 'remark')}; they are not shown.)")
        return
    if not errors:
        print("✓ The file follows the MEI rules.")
    for finding in new:
        where = bar_name(finding["measure_n"]) if finding.get("measure_n") else "outside the bars"
        mark = "✗" if finding["severity"] == "error" else "!"
        print(f"  {mark} line {finding.get('line') or '?'} ({where}): {finding['message']}")
    if errors:
        print("Fix the lines marked ✗, save, and run this cell again.")
    print(f"The full report is in {(project / 'edition/validation-editing').relative_to(project.parent)}.")
