"""Grieg's Vöglein, block 2: the header and the printed marks, with the live score.

Pasted after grieg_linking.py in the same cell; it uses that file's functions.
"""

import copy
import datetime
import re
import difflib
import textwrap
from fractions import Fraction

MARKS = {"dynam", "tempo", "hairpin", "slur", "pedal", "dir", "fing", "octave"}
HEADER_TASKS = {"identifier", "change", "application"}
ET.register_namespace("", MEI_NS)  # measures shown without a namespace prefix


def _name(element):
    return element.tag.split("}")[-1]


def _text(element):
    """The words of an element and its children, with a space where they meet."""
    if element is None:
        return ""
    return re.sub(r" ([.,;:)])", r"\1", " ".join(" ".join(element.itertext()).split()))


def _pitch(note):
    sign = {"f": "♭", "s": "♯", "n": "", "ff": "𝄫", "ss": "𝄪"}.get(note.get("accid") or note.get("accid.ges") or "n", "")
    return f"{note.get('pname', '?').upper()}{sign}{note.get('oct', '')}"


def _read(path):
    """Parse an MEI file; on an XML error say what to do and return None."""
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as error:
        line, column = error.position
        print(f"{Path(path).name} cannot be read as XML: the problem is at line {line}, column {column}.\n"
              "Usually a tag is not closed, or a < or a quotation mark is missing, at or just before that line.\n"
              "Undo your last change in the editor (Ctrl+Z, on a Mac Cmd+Z), save, and run this cell again.")
        return None


def _nth_line(lines, text, n=1):
    """The line number (from 1) of the n-th line containing text."""
    found = [number for number, line in enumerate(lines, 1) if text in line]
    return found[n - 1] if len(found) >= n else None


# --- The edition and your system -------------------------------------------------

def open_edition(project):
    """Continue from 03_grieg_linking: the linked work.mei and the file before editing."""
    project = Path(project).resolve()
    work = project / "edition/mei/work.mei"
    before = project / "edition/checkpoints/before-editing.mei"
    if not (before.is_file() and work.is_file() and "<facsimile" in work.read_text(encoding="utf-8")):
        raise FileNotFoundError("This notebook continues from 03_grieg_linking.ipynb. Run that notebook to the end "
                                "first, in the same folder, then run this cell again.")
    context = load_inputs(project)
    context["before"] = before
    print("The file before editing (do not edit this one):", _short(before, project))
    return context


def choose_system(context, page, system):
    """Remember which system of which printed page this pair restores."""
    pages = {p.get("printed_page"): p for p in _manifest(context)["pages"]}
    if str(page) not in pages:
        print(f"Page {page} is not one of ours: write 42 or 43.")
        return
    systems = _systems(pages[str(page)])
    if not 1 <= int(system) <= len(systems):
        print(f"Page {page} has systems 1 to {len(systems)}.")
        return
    bars = systems[int(system) - 1]
    context["system"] = {"page": str(page), "number": int(system), "bars": bars}
    print(f"Your system: page {page}, system {system}, {_bars(bars)}.")


def _system(context):
    if "system" not in context:
        raise ValueError("Run the cell with PAGE and SYSTEM in part 2 first.")
    return context["system"]


def _boxes(context):
    """{bar: (image, (left, top, right, bottom))} from the links of the file before editing."""
    music = ET.parse(context["before"]).getroot().find(f"{{{MEI_NS}}}music")
    zones = {}
    for surface in music.iter(f"{{{MEI_NS}}}surface"):
        image = (context["before"].parent / surface.find(f"{{{MEI_NS}}}graphic").get("target")).resolve()
        for zone in surface.iter(f"{{{MEI_NS}}}zone"):
            zones[zone.get(XML_ID)] = (image, tuple(int(float(zone.get(k))) for k in ("ulx", "uly", "lrx", "lry")))
    return {m.get("n"): zones[m.get("facs").lstrip("#")]
            for m in music.iter(f"{{{MEI_NS}}}measure") if (m.get("facs") or "").lstrip("#") in zones}


def _crop(image, box, labels=(), width=1100, margin=40):
    from PIL import Image as PILImage, ImageDraw, ImageFont
    with PILImage.open(image) as source:
        picture = source.convert("RGB")
    draw = ImageDraw.Draw(picture, "RGBA")
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except OSError:
        font = ImageFont.load_default(44)
    for x, y, label in labels:
        left, top, right, bottom = draw.textbbox((x, y), label, font=font, anchor="lt")
        draw.rectangle([left - 6, top - 4, right + 6, bottom + 4], fill=(255, 255, 255, 230))
        draw.text((x, y), label, font=font, fill=(20, 90, 210, 255), anchor="lt")
    region = (max(0, box[0] - margin), max(0, box[1] - margin),
              min(picture.width, box[2] + margin), min(picture.height, box[3] + margin))
    crop = picture.crop(region)
    crop.thumbnail((width, width))
    _show_picture(crop)


def show_system(context):
    """Your system in the print, with its bar numbers."""
    bars = _system(context)["bars"]
    boxes = _boxes(context)
    image = boxes[bars[0]][0]
    union = (min(boxes[b][1][0] for b in bars), min(boxes[b][1][1] for b in bars),
             max(boxes[b][1][2] for b in bars), max(boxes[b][1][3] for b in bars))
    labels = [(boxes[b][1][0] + 30, union[1] + 10, f"bar {b}") for b in bars]
    _crop(image, union, labels)


# --- The header ----------------------------------------------------------------------

def _who(change, ids):
    names = [_text(e) for e in change.iter() if _name(e) in ("persName", "name", "corpName")]
    for pointer in (change.get("resp") or "").split():
        target = ids.get(pointer.lstrip("#"))
        if target is None:
            names.append(f"{pointer} (not in the file!)")
        else:
            names.append(_text(target.find(f"{{{MEI_NS}}}name")) if _name(target) == "application" else _text(target))
    return ", ".join(names) or "?"


def _what(change, ids):
    description = change.find(f"{{{MEI_NS}}}changeDesc")
    text = _text(description)
    for ref in description.iter(f"{{{MEI_NS}}}ref") if description is not None else []:
        target = (ref.get("target") or "").lstrip("#")
        if (ref.get("target") or "").startswith("#") and target not in ids:
            text += f" [the link #{target} points to nothing in the file]"
    return text


def _date(change):
    date = change.find(f"{{{MEI_NS}}}date")
    if date is None:
        return "?"
    return (date.get("isodate") or date.get("notafter") or date.get("notbefore") or _text(date) or "?")[:10]


def _address(identifier):
    """A web address without its http:// part, shortened, so that the output has no live link."""
    text = _text(identifier).split("://", 1)[-1]
    return text if len(text) <= 70 else text[:40] + "…" + text[-28:]


def show_header(context):
    """The header of work.mei in plain words, with the lines where to find it."""
    root = _read(context["work"])
    if root is None:
        return
    lines = context["work"].read_text(encoding="utf-8").split("\n")
    m = f"{{{MEI_NS}}}"
    head = root.find(f"{m}meiHead")
    ids = {e.get(XML_ID): e for e in root.iter() if e.get(XML_ID)}
    title_stmt = head.find(f"{m}fileDesc/{m}titleStmt")
    pub = head.find(f"{m}fileDesc/{m}pubStmt")
    print(f"The header: lines {_nth_line(lines, '<meiHead')}–{_nth_line(lines, '</meiHead')} of {context['work'].name}\n")
    title = title_stmt.find(f"{m}title")
    subtitle = title.find(f"{m}titlePart")
    print("Title:      ", (title.text or "").strip() + (f" ({_text(subtitle)})" if subtitle is not None else ""))
    print("Composer:   ", _text(title_stmt.find(f"{m}composer")))
    print("Encoded by: ", ", ".join(_text(p) for p in title_stmt.iter(f"{m}persName") if p.get("role") == "encoder"))
    print("Published:  ", _text(pub.find(f"{m}publisher")), _text(pub.find(f"{m}date")))
    print("Rights:     ", textwrap.shorten(_text(pub.find(f".//{m}useRestrict")), 90))
    manifestations = head.findall(f"{m}manifestationList/{m}manifestation")
    print(f"\nSources: {len(manifestations)} <manifestation>s")
    for number, source in enumerate(manifestations, 1):
        title = _text(source.find(f"{m}titleStmt/{m}title"))
        people = [f"{_text(p)} ({p.get('role')})" for p in source.find(f"{m}titleStmt").iter()
                  if _name(p) in ("persName", "corpName") and p.get("role") != "composer"]
        people += [_text(p) for p in source.iter(f"{m}corpName") if p not in source.find(f"{m}titleStmt").iter()]
        date = source.find(f".//{m}pubStmt/{m}date")
        plate = source.find(f".//{m}plateNum")
        print(f"  {number}. line {_nth_line(lines, '<manifestation>', number)}: {title}")
        print(f"     {', '.join(people)}" + (f"; {_text(date) or date.get('isodate')}" if date is not None else "")
              + (f"; plate {_text(plate)}" if plate is not None else ""))
        for identifier in source.findall(f"{m}identifier"):
            value = _address(identifier) if identifier.get("type") == "URI" else _text(identifier)
            print(f"     identifier ({identifier.get('type')}): {value}")
    changes = head.findall(f"{m}revisionDesc/{m}change")
    print(f"\nChanges: {len(changes)} <change>s, from line {_nth_line(lines, '<revisionDesc')}")
    for change in changes:
        what = textwrap.wrap(_what(change, ids), 64) or ["?"]
        print(f"  {change.get('n') or '?':>3}  {_date(change):<10}  {textwrap.shorten(_who(change, ids), 26):<26}  {what[0]}")
        for more in what[1:]:
            print(f"{'':45}{more}")


def header_lines(context, names):
    """The lines to add to the header, ready to paste, with where they go."""
    root = _read(context["work"])
    if root is None:
        return
    lines = context["work"].read_text(encoding="utf-8").split("\n")
    witness = context["sources"]["printed_witness"]
    system = _system(context)
    people = [n.strip() for n in names.replace(" and ", ",").split(",") if n.strip()] or ["Your name", "Your partner's name"]
    if not names.strip():
        print("(Write your names after NAMES = in the cell above and run both cells again; until then the lines say \"Your name\".)\n")
    print(f"1. The print we use. In the first <manifestation>, the Peters print, after its line\n"
          f"   <identifier type=\"URI\">… (line {_nth_line(lines, '<identifier type=\"URI\"')}), add:\n")
    print(f'        <identifier type="IMSLP">{witness["imslp_file_id"]}</identifier>')
    print(f'        <identifier type="SHA-256">{witness["sha256"]}</identifier>')
    changes = root.findall(f"{{{MEI_NS}}}meiHead/{{{MEI_NS}}}revisionDesc/{{{MEI_NS}}}change")
    number = max((int(c.get("n")) for c in changes if (c.get("n") or "").isdigit()), default=0) + 1
    persons = "\n".join(f"            <persName>{person}</persName>" for person in people)
    print(f"\n2. Your work. Before the line </revisionDesc> (line {_nth_line(lines, '</revisionDesc')}), add:\n")
    print(f"""      <change n="{number}">
        <respStmt>
{persons}
        </respStmt>
        <changeDesc>
          <p>Linked every bar to its box on pages 42–43 of the Peters print (IMSLP {witness['imslp_file_id']}) with CAMAT 0.2.8. Restored the printed marks of page {system['page']}, system {system['number']} ({_bars(system['bars'])}) from the print.</p>
        </changeDesc>
        <date isodate="{datetime.date.today().isoformat()}"/>
      </change>""")


def check_header(context):
    """Are the two header tasks done?"""
    root = _read(context["work"])
    if root is None:
        return
    m = f"{{{MEI_NS}}}"
    witness = context["sources"]["printed_witness"]
    peters = root.find(f"{m}meiHead/{m}manifestationList/{m}manifestation")
    values = [_text(i) for i in peters.findall(f"{m}identifier")]
    imslp = any(v.removeprefix("IMSLP") == str(witness["imslp_file_id"]) for v in values)
    sha = witness["sha256"] in values
    before = len(ET.parse(context["before"]).getroot().findall(f"{m}meiHead/{m}revisionDesc/{m}change"))
    changes = root.findall(f"{m}meiHead/{m}revisionDesc/{m}change")
    new = changes[before:]
    named = [c for c in new if any(_text(p) and "Your" not in _text(p) for p in c.iter(f"{m}persName"))]
    print(("✓" if imslp else "✗") + " The Peters print has the IMSLP file number 28165.")
    print(("✓" if sha else "✗") + " The Peters print has the fingerprint (SHA-256) of the scan.")
    if not new:
        print("✗ No new <change> yet.")
    elif not named:
        print("✗ The new <change> does not have your names yet.")
    else:
        print(f"✓ A new <change>, n=\"{new[-1].get('n')}\", by {_who(new[-1], {})}, dated {_date(new[-1])}.")
    if len(new) > 1:
        print(f"! {len(new)} new <change>s: one is enough for today's work.")


# --- The notes of your system --------------------------------------------------------

def _events(layer):
    """[(beat, element)] for the notes, chords and rests of a layer. A beat is an eighth (6/8),
    counted from 1 at the start of the bar: the number to write in tstamp."""
    events, position = [], Fraction(0)

    def walk(element, beam):
        nonlocal position
        if _name(element) in ("note", "chord", "rest", "space"):
            dur, dots = element.get("dur"), int(element.get("dots") or 0)
            length = Fraction(8, int(dur)) * (2 - Fraction(1, 2 ** dots)) if dur and dur.isdigit() else Fraction(0)
            events.append((1 + position, element, beam))
            position += 0 if element.get("grace") else length
            return
        for child in element:
            walk(child, element if _name(element) == "beam" else beam)
    walk(layer, None)
    return events


def _beat(value):
    whole, part = divmod(value, 1)
    return f"{int(whole)}" + ({Fraction(1, 4): "¼", Fraction(1, 2): "½", Fraction(3, 4): "¾"}.get(part, "") if part else "")


def show_notes(context):
    """The notes of your system, bar by bar and staff by staff: beat, pitch and xml:id."""
    root = _read(context["work"])
    if root is None:
        return
    bars = _system(context)["bars"]
    music = root.find(f"{{{MEI_NS}}}music")
    hands = {"1": "right hand (staff 1)", "2": "left hand (staff 2)"}
    for measure in music.iter(f"{{{MEI_NS}}}measure"):
        if measure.get("n") not in bars:
            continue
        print(f"Bar {measure.get('n')}   <measure n=\"{measure.get('n')}\" xml:id=\"{measure.get(XML_ID)}\">")
        for staff in measure.findall(f"{{{MEI_NS}}}staff"):
            print(f"  {hands.get(staff.get('n'), 'staff ' + staff.get('n'))}")
            for layer in staff.findall(f"{{{MEI_NS}}}layer"):
                events = _events(layer)
                index = 0
                while index < len(events):
                    beat, element, beam = events[index]
                    group = [element]
                    # Short beamed notes are shown on one line: their first and last are slur ends.
                    while (beam is not None and _name(element) == "note" and element.get("dur") in ("16", "32")
                           and index + 1 < len(events) and events[index + 1][2] is beam
                           and _name(events[index + 1][1]) == "note"):
                        index += 1
                        group.append(events[index][1])
                    if _name(element) == "rest":
                        print(f"    beat {_beat(beat):<4} rest")
                    elif _name(element) == "chord":
                        notes = element.findall(f"{{{MEI_NS}}}note")
                        print(f"    beat {_beat(beat):<4} {'+'.join(map(_pitch, notes)):<18} chord {element.get(XML_ID)} "
                              f"(notes {', '.join(n.get(XML_ID) for n in notes)})")
                    elif _name(element) == "note":
                        pitches = " ".join(_pitch(n) for n in group)
                        print(f"    beat {_beat(beat):<4} {pitches:<18} {' '.join(n.get(XML_ID) for n in group)}")
                    index += 1


def measure_xml(root, n):
    """The XML text of <measure n="n"> in the music, as in the file, without the MEI namespace."""
    for measure in root.find(f"{{{MEI_NS}}}music").iter(f"{{{MEI_NS}}}measure"):
        if measure.get("n") == str(n):
            excerpt = copy.deepcopy(measure)
            excerpt.tail = None
            lines = ET.tostring(excerpt, encoding="unicode").replace(f' xmlns="{MEI_NS}"', "").split("\n")
            indent = min((len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()), default=0)
            return "\n".join([lines[0]] + [line[indent:] for line in lines[1:]])
    raise ValueError(f"No measure n=\"{n}\" in the music.")


def slur_prompt(context):
    """A prompt for Copilot: the slurs of your system, with its bars from the file."""
    root = _read(context["work"])
    if root is None:
        return
    system = _system(context)
    measures = "\n".join(measure_xml(root, n) for n in system["bars"])
    print(f'''I am editing an MEI file (MEI 5.1) of Grieg, Vöglein (Little bird), Op. 43 No. 4.
Add the slurs printed in system {system['number']} of page {system['page']}, {_bars(system['bars'])}:

- REPLACE THIS LINE: for each slur, the xml:id of its first and last note, its staff (1 or 2),
  and whether it curves above or below the notes.

Add one <slur> element per slur, inside the measure where it starts, after its <staff>
elements, with startid and endid pointing to the xml:id of the two notes (with a # in
front), staff, curvedir and an xml:id that begins with "seminar-slur-". Change nothing else.

Here are the measures from the file:

{measures}''')


# --- What changed -------------------------------------------------------------------------

def _key(element):
    attributes = tuple(sorted((k, v) for k, v in element.attrib.items() if k != XML_ID))
    return _name(element), element.get(XML_ID), attributes, (element.text or "").strip()


def _places(root):
    """Map every element to where it is: a bar of the music, the header, or elsewhere."""
    m = f"{{{MEI_NS}}}"
    place = {element: "the header" for element in root.find(f"{m}meiHead").iter()}
    music = root.find(f"{m}music")
    for element in music.iter():
        place[element] = "the music, outside the bars"
    for measure in music.iter(f"{m}measure"):
        for element in measure.iter():
            place[element] = measure.get("n")
    return place


def _describe(element, by_id, place):
    """One line for an element: its name, text, notes it points to, other attributes."""
    name = _name(element)
    parts = [f"<{name}>"]
    if name == "note":
        parts.append(_pitch(element))
    text = _text(element)
    if text:
        parts.append(f'"{textwrap.shorten(text, 70)}"')
    if element.get(XML_ID):
        parts.append(f"(xml:id {element.get(XML_ID)})")
    details = []
    for attribute in ("startid", "endid"):
        target = (element.get(attribute) or "").lstrip("#")
        if target:
            word = "from" if attribute == "startid" else "to"
            note = by_id.get(target)
            if note is None:
                details.append(f"{word} #{target} (no element in the file has this xml:id!)")
            else:
                where = place.get(note, "?")
                where = f"bar {where}" if where.isdigit() else where
                pitch = _pitch(note) if _name(note) == "note" else f"<{_name(note)}>"
                details.append(f"{word} {pitch} in {where}")
    for attribute, value in sorted(element.attrib.items()):
        if attribute not in (XML_ID, "startid", "endid") and "}" not in attribute:
            details.append(f'{attribute}="{value}"')
    return " ".join(parts) + (": " + ", ".join(details) if details else "")


def _changes(context):
    """[(place, sign, text, note)] for the differences between the file before editing and work.mei."""
    old, new = _read(context["before"]), _read(context["work"])
    if old is None or new is None:
        return None, []
    bars = _system(context)["bars"] if "system" in context else None
    old_elements, new_elements = list(old.iter()), list(new.iter())
    old_place, new_place = _places(old), _places(new)
    old_ids = {e.get(XML_ID): e for e in old_elements if e.get(XML_ID)}
    new_ids, duplicates = {}, set()
    for element in new_elements:
        if element.get(XML_ID):
            if element.get(XML_ID) in new_ids:
                duplicates.add(element.get(XML_ID))
            new_ids[element.get(XML_ID)] = element

    def note(element, place, asked):
        if not asked:
            return "not part of the tasks"
        if place.isdigit() and bars and place not in bars:
            return "outside your system"
        return ""

    changes = []
    matcher = difflib.SequenceMatcher(None, [_key(e) for e in old_elements], [_key(e) for e in new_elements],
                                      autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        removed, added = old_elements[i1:i2], new_elements[j1:j2]
        same_id = {e.get(XML_ID) for e in removed if e.get(XML_ID)} & {e.get(XML_ID) for e in added}
        for element in added:
            place = new_place.get(element, "?")
            if element.get(XML_ID) in same_id:
                was = next(e for e in removed if e.get(XML_ID) == element.get(XML_ID))
                diffs = [f'{a}: "{was.get(a)}" → "{element.get(a)}"' for a in sorted(set(was.attrib) | set(element.attrib))
                         if was.get(a) != element.get(a)]
                if (was.text or "").strip() != (element.text or "").strip():
                    diffs.append(f'text: "{(was.text or "").strip()}" → "{(element.text or "").strip()}"')
                label = f"<{_name(element)}> {element.get(XML_ID)}"
                if _name(element) == "note" and _pitch(was) != _pitch(element):
                    label += f" ({_pitch(was)} → {_pitch(element)})"
                asked = _name(element) == "facsimile" and set(element.attrib) ^ set(was.attrib) <= {"decls"}
                changes.append((place, "~", f"changed {label}: " + "; ".join(diffs), note(element, place, asked)))
            elif not any(element in parent for parent in added if parent is not element):
                asked = (_name(element) in MARKS | HEADER_TASKS and element.get(XML_ID) not in old_ids
                         and (place == "the header") == (_name(element) in HEADER_TASKS))
                changes.append((place, "+", "new " + _describe(element, new_ids, new_place), note(element, place, asked)))
        for element in removed:
            if element.get(XML_ID) in same_id or any(element in parent for parent in removed if parent is not element):
                continue
            place = old_place.get(element, "?")
            changes.append((place, "-", "removed " + _describe(element, old_ids, old_place), "not part of the tasks"))
    problems = [f"xml:id {i} is used more than once" for i in sorted(duplicates)]
    for element in new_elements:
        for attribute in ("startid", "endid", "plist", "facs"):
            for token in (element.get(attribute) or "").split():
                if token.startswith("#") and token[1:] not in new_ids:
                    problems.append(f"<{_name(element)}> {attribute} points to {token}, but no element has that xml:id")
    return problems, changes


def show_changes(context):
    """What changed in work.mei since before editing, in plain words. Never stops the notebook."""
    problems, changes = _changes(context)
    if problems is None:
        return
    work = context["work"].name
    if not changes and not problems:
        print(f"No changes yet: {work} is the same as before editing (spaces and line breaks are not counted).")
        return
    print(f"Changes in {work} since before editing (spaces and line breaks are not counted):")
    places = []
    for place, *_ in changes:
        if place not in places:
            places.append(place)
    for place in places:
        print(f"\n{'Bar ' + place if place.isdigit() else place[0].upper() + place[1:]}")
        for _, sign, text, flag in (c for c in changes if c[0] == place):
            print(f"  {sign} {text}" + (f"   ← {flag}" if flag else ""))
    flagged = [c for c in changes if c[3]]
    if flagged:
        print(f"\n{len(flagged)} change{'s' if len(flagged) != 1 else ''} marked ←: look at each one in the print. "
              "Keep it if the print shows it and it belongs to your task; otherwise undo it in the editor.")
    if problems:
        print("\nTo fix:")
        for problem in problems:
            print("  ✗", problem)


# --- Check and review -----------------------------------------------------------------------

def check_file(context):
    """CAMAT's MEI checker on work.mei: what is new, and what is gone, since before editing."""
    if _read(context["work"]) is None:
        return
    project = context["project"]
    now = _validate(context["work"], project / "edition/validation-editing")
    then = _validate(context["before"], project / "edition/validation-before-editing")
    if now is None or then is None:
        print("The checker did not run. Run the cell again; if it still fails, ask your teacher.")
        return

    def count(findings):
        counts = {}
        for finding in findings:
            counts.setdefault(_finding_key(finding), []).append(finding)
        return counts
    old, current = count(then), count(now)
    new = [f for key, found in current.items() for f in found[len(old.get(key, [])):]]
    gone = [f for key, found in old.items() for f in found[len(current.get(key, [])):]]
    print(f"Checked {context['work'].name} against the MEI rules (schema), its links and the page images, and with Verovio.")
    if not new:
        print(f"✓ No new problems. (The file before editing had {len(then)} remarks; they are not shown.)")
    for finding in new:
        where = f"bar {finding['measure_n']}" if finding.get("measure_n") else "outside the bars"
        print(f"  {'✗' if finding['severity'] == 'error' else '!'} line {finding.get('line') or '?'} ({where}): {finding['message']}")
    if any(f["severity"] == "error" for f in new):
        print("Fix the lines marked ✗, save, and run this cell again.")
    if gone:
        print(f"\nGone since before editing ({len(gone)}):")
        for finding in gone:
            print(f"  ✓ {finding['message']}")
    print(f"The full report is in {_short(project / 'edition/validation-editing', project)}.")


def show_review(context, width=900):
    """For the reviewers: the new marks bar by bar, then the system in the print
    (and any other bar with changes, on its own)."""
    problems, changes = _changes(context)
    if problems is None:
        return
    bars = sorted({c[0] for c in changes if c[0].isdigit()}, key=int)
    others = [c for c in changes if not c[0].isdigit()]
    if not bars and not others:
        print("No changes to review yet.")
        return
    system = _system(context)
    for bar in bars:
        print(f"Bar {bar}")
        for _, sign, text, flag in (c for c in changes if c[0] == bar):
            print(f"  {sign} {text}" + (f"   ← {flag}" if flag else ""))
    if others:
        print(f"Elsewhere: {len(others)} change{'s' if len(others) != 1 else ''} (the header and so on), "
              "listed by show_changes.")
    if problems:
        print("To fix:", *problems, sep="\n  ✗ ")
    print(f"\nPage {system['page']}, system {system['number']}, in the print:")
    show_system(context)
    boxes = _boxes(context)
    for bar in (b for b in bars if b not in system["bars"]):
        print(f"Bar {bar}, outside the system, in the print:")
        _crop(*boxes[bar], width=width)


REVIEW_DECISIONS = ("accept", "correct", "unresolved")


def _sheet_entry(sign, text, flag):
    return [f"- `{sign} {text}`" + (f" ← {flag}" if flag else ""), "    - Decision:", "    - Why:"]


def _read_sheet(text):
    """{change: what the reviewers wrote after Decision:}, for the entries of a review sheet."""
    entries, current = {}, None
    for line in text.split("\n"):
        if line.startswith("## Unresolved"):
            break
        found = re.match(r"- `(.+)`", line)
        if found:
            current = found.group(1)
            entries[current] = ""
        elif current is not None and line.strip().lstrip("-* ").lower().startswith("decision:"):
            entries[current] = line.split(":", 1)[1].strip()
            current = None
    return entries


def review_sheet(context, names=""):
    """The peer-review sheet edition/reviews/page-P-system-S.md: one entry per change in the bars.
    Written once and then kept; run again, it counts the decisions and lists the changes not on it.
    One file per system, so that the pairs' sheets do not collide when session 4 combines them."""
    problems, changes = _changes(context)
    if problems is None:
        return
    project, system = context["project"], _system(context)
    sheet = project / f"edition/reviews/page-{system['page']}-system-{system['number']}.md"
    entries = sorted((c for c in changes if c[0].isdigit()), key=lambda c: int(c[0]))
    if problems:
        print("To fix first:", *problems, sep="\n  ✗ ")
        print()
    if not sheet.is_file():
        if not entries:
            print("No changes in the bars yet, so there is nothing to review.")
            return
        lines = [f"# Peer review: page {system['page']}, system {system['number']} ({_bars(system['bars'])})", "",
                 f"Restored by: {names.strip()}  ", "Reviewed by:  ",
                 f"Sheet written: {datetime.date.today().isoformat()}", "",
                 "Compare each change with the print. After *Decision* write accept, correct or unresolved, "
                 "and after *Why* a few words, for example: the print has the slur below the staff. "
                 "Correct means that the restoring pair fixes it in work.mei while you watch. "
                 "Look twice at the changes marked ←."]
        for bar in dict.fromkeys(c[0] for c in entries):
            lines += ["", f"## Bar {bar}", ""]
            for _, sign, text, flag in (c for c in entries if c[0] == bar):
                lines += _sheet_entry(sign, text, flag)
        lines += ["", "## Unresolved: to discuss in class", "", "- ", ""]
        sheet.parent.mkdir(exist_ok=True)
        sheet.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote the review sheet, with {len(entries)} entr{'ies' if len(entries) != 1 else 'y'}: {_short(sheet, project)}")
        print("Open it in the editor next to the print and fill it in. Run this cell again when you have finished.")
        return

    listed = _read_sheet(sheet.read_text(encoding="utf-8"))
    current = {f"{sign} {text}": (bar, flag) for bar, sign, text, flag in entries}
    print(f"The review sheet is already there and is kept as it is: {_short(sheet, project)}")

    def word(value):
        return value.split()[0].lower().strip(".,;:!") if value.split() else ""
    decided = [change for change, value in listed.items() if word(value) in REVIEW_DECISIONS]
    unclear = [change for change, value in listed.items() if value and word(value) not in REVIEW_DECISIONS]
    empty = [change for change, value in listed.items() if not value]
    counts = ", ".join(f"{n} {w}" for w in REVIEW_DECISIONS
                       if (n := sum(word(listed[c]) == w for c in decided)))
    done = listed and not unclear and not empty
    print(f"{'✓' if done else '!'} {len(decided)} of {len(listed)} entries have a decision" + (f": {counts}." if counts else "."))
    for change in empty:
        print(f"  no decision yet: {textwrap.shorten(change, 100)}")
    for change in unclear:
        print(f"  write accept, correct or unresolved: {textwrap.shorten(change, 90)}")
    missing = [change for change in current if change not in listed]
    gone = [change for change in listed if change not in current]
    if missing:
        print(f"\nIn work.mei, but not on the sheet ({len(missing)}): a mark added or corrected after the sheet was written. "
              "Copy each entry under its bar on the sheet, and review it:")
        for change in missing:
            bar, flag = current[change]
            print(f"\nBar {bar}", *_sheet_entry(*change.split(" ", 1), flag), sep="\n")
    if gone:
        print(f"\nOn the sheet, but no longer in work.mei ({len(gone)}): corrected or undone since. "
              "Write under Why what was done:")
        for change in gone:
            print(f"  {textwrap.shorten(change, 100)}")
