"""Rebuild session 2's teaching derivatives from the frozen MEI sample.

Run with CAMAT's validation environment (lxml), from the repository root:
    python tools/prepare_schumann_starter.py

The original lives in sessions/02-building-an-edition/sources/local/;
sources/sources.json gives its pinned URL and hashes. This script does not
download, render, validate against a schema, or modify that original.
Generated files are templates; student work belongs in a separate copy.
"""

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from lxml import etree as E


ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/02-building-an-edition"
NS = {"m": "http://www.music-encoding.org/ns/mei"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
DATE = "2026-10-24"
EXPRESSIVE = {"slur", "dynam", "tempo", "dir", "artic"}


def tag(name):
    return f"{{{NS['m']}}}{name}"


def body(tree):
    return tree.find("m:music/m:body", NS)


def measures(tree):
    return body(tree).findall(".//m:measure", NS)


def measure(tree, number):
    return next(m for m in measures(tree) if m.get("n") == str(number))


def child(parent, name, text=None, **attrs):
    node = E.SubElement(parent, tag(name), **attrs)
    if text is not None:
        node.text = text
    return node


def remove(node):
    node.getparent().remove(node)


def projection(node):
    """Compare musical structure, values and IDs while excluding expression."""
    name = E.QName(node).localname
    if name in EXPRESSIVE or name == "annot":
        return None
    attrs = dict(node.attrib)
    if name == "staffDef":
        attrs.pop("lines", None)  # The two explicit five-line declarations are repairs.
    return (name, tuple(sorted(attrs.items())),
            tuple(p for c in node if (p := projection(c)) is not None))


def check_references(tree):
    ids = [e.get(XML_ID) for e in tree.iter() if isinstance(e.tag, str) and e.get(XML_ID)]
    assert len(ids) == len(set(ids)), "Duplicate xml:id"
    for e in tree.iter():
        for key, value in e.attrib.items():
            if key not in {"facs", "startid", "endid", "target", "plist", "corresp", "sameas",
                           "next", "prev", "copyof", "synch", "decls", "resp", "source"}:
                continue
            for ref in value.split():
                if ref.startswith("#"):
                    assert ref[1:] in ids, (key, ref)


def describe(tree, stage, scope, description, source):
    head = tree.find("m:meiHead", NS)
    # Keep this historical filename without inventing a missing application/link.
    for ref in head.findall('.//m:ref[@target="#transformation.xsl"]', NS):
        paragraph = ref.getparent()
        paragraph.remove(ref)
        paragraph.text = ("Transformation with transformation.xsl transformation Stylesheet. "
                          "The original fragment '#transformation.xsl' did not resolve; "
                          "it is retained here as a historical filename, not a live link.")
    # Avoid a second encoded score and an answer leak in the manual-entry sheet.
    for incipit in head.findall(".//m:incip", NS):
        remove(incipit)
    file_desc = head.find("m:fileDesc", NS)
    edition_stmt = E.Element(tag("editionStmt"))
    child(edition_stmt, "edition", stage + " (AI-assisted teaching draft)", n="0.1.0")
    file_desc.insert(1, edition_stmt)
    source_desc = file_desc.find("m:sourceDesc", NS)
    witness = child(source_desc, "source")
    witness.set(XML_ID, "src.imslp51556")
    bibl = child(witness, "bibl")
    bibl.text = ("Robert Schumann, Album für die Jugend, Op. 68 No. 10; Clara Schumann edition, "
                 "Leipzig: Breitkopf & Härtel, catalogued 1887, plate R.S. 67. "
                 "IMSLP 51556, original PDF page 8 / printed page 8. ")
    child(bibl, "ref", "IMSLP catalogue", target=source["printed_witness"]["file_url"])
    child(bibl, "identifier", source["printed_witness"]["sha256"], type="sha256")
    project = head.find("m:encodingDesc/m:projectDesc", NS)
    application = child(head.find("m:encodingDesc/m:appInfo", NS), "application", version="1")
    application.set(XML_ID, "seminar.prepare-schumann")
    child(application, "name", "prepare_schumann_starter.py (AI-assisted teaching preparation)")
    child(project, "p", f"Teaching derivative prepared {DATE}. {description} {scope}")
    child(project, "p", "Base encoding: Maja Hartwig, MEI Sample Collection, commit "
          + source["base_encoding"]["revision"] + ". Upstream credits, rights statements, "
          "bibliography and revision history are retained. The duplicate header incipit is omitted. "
          "The witness controls new readings; the encoding is a starting document, not that witness. "
          "Instructor review is still required; no whole-piece editorial approval is asserted.")
    if stage != "Technical baseline":
        child(project, "p", "Source-based pitch correction, 24 October 2026: the final bass eighth "
              "in MEI labels 2 and 6 reads F3 in IMSLP 51556, printed p. 8, systems 1 and 2. "
              "The reused encoding reads A3 (d1e338, d1e1495). Teaching notes/solutions use F3; "
              "the upstream original and technical baseline retain A3. Manual-entry placeholders "
              "contain no pitches. Further source review remains necessary.")
    changes = head.find("m:revisionDesc", NS)
    change = child(changes, "change", n=str(len(changes) + 1), resp="#seminar.prepare-schumann")
    change_desc = child(change, "changeDesc")
    child(change_desc, "p", f"{stage}: {description} {scope}")
    child(change, "date", isodate=DATE)


def write(tree, path):
    check_references(tree)
    E.indent(tree, space="  ")
    data = E.tostring(tree, encoding="UTF-8", xml_declaration=True, pretty_print=True).rstrip(b"\n") + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": str(path.relative_to(SESSION)), "sha256": hashlib.sha256(data).hexdigest(),
            "body_measures": len(measures(tree)),
            "body_elements": dict(sorted(Counter(E.QName(e).localname for e in body(tree).iter()).items()))}


def main():
    source = json.loads((SESSION / "sources/sources.json").read_text())
    source_path = SESSION / "sources" / source["base_encoding"]["local_path"]
    original_bytes = source_path.read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == source["base_encoding"]["sha256"]
    original = E.parse(str(source_path), E.XMLParser(resolve_entities=False, no_network=True))
    baseline = copy.deepcopy(original)
    for staff in body(baseline).findall(".//m:staffDef", NS):
        staff.set("lines", "5")
    locations = {e.get(XML_ID): m for m in measures(baseline) for e in m.iter() if e.get(XML_ID)}
    moved = []
    for slur in list(body(baseline).iter(tag("slur"))):
        target = locations[slur.get("startid").lstrip("#")]
        if slur.getparent() is not target:
            moved.append({"from_measure": slur.getparent().get("n"),
                          "to_measure": target.get("n"), "startid": slur.get("startid"),
                          "endid": slur.get("endid")})
            target.append(slur)
    assert projection(body(original)) == projection(body(baseline))

    starter = copy.deepcopy(baseline)
    omitted = []
    for m in measures(starter):
        for element in list(m.iter()):
            if E.QName(element).localname in EXPRESSIVE:
                omitted.append({"measure": m.get("n"), "element": E.QName(element).localname,
                                "xml": E.tostring(element, encoding="unicode", with_tail=False)})
                remove(element)
    assert projection(body(baseline)) == projection(body(starter))

    # The 24 October OMR comparison exposed two missed readings in the reused
    # encoding. Keep the upstream/technical baseline intact; correct only the
    # teaching derivatives against IMSLP 51556, printed p. 8, systems 1 and 2.
    pitch_corrections = []
    for identifier in ("d1e338", "d1e1495"):
        note = next(e for e in body(starter).iter() if e.get(XML_ID) == identifier)
        assert (note.get("pname"), note.get("oct")) == ("a", "3")
        note.set("pname", "f")
        pitch_corrections.append({"xml_id": identifier, "before": "A3", "after": "F3",
                                  "witness": "IMSLP 51556, printed p. 8, systems 1 and 2; final bass eighth of the first full bar in each system."})
    unchanged_check = copy.deepcopy(starter)
    for correction in pitch_corrections:
        next(e for e in body(unchanged_check).iter() if e.get(XML_ID) == correction["xml_id"]).set("pname", "a")
    assert projection(body(baseline)) == projection(body(unchanged_check))

    solution = copy.deepcopy(starter)
    initial = child(measure(solution, 1), "dynam", "f", staff="1", place="below", tstamp="1")
    initial.set(XML_ID, "seminar-dynam-opening")
    tempo = child(measure(solution, 1), "tempo", "Frisch und munter.", staff="1", place="above", tstamp="1")
    tempo.set(XML_ID, "seminar-tempo-opening")
    second = child(measure(solution, 6), "dynam", "f", staff="1", place="below", tstamp="1")
    second.set(XML_ID, "seminar-dynam-second-system")
    for number, start, end, identifier in [
        (1, "d1e60", "d1e338", "seminar-slur-pickup"),
        (3, "d1e561", "d1e634", "seminar-slur-bar2"),
    ]:
        slur = child(measure(solution, number), "slur", staff="2", curvedir="above",
                     startid="#" + start, endid="#" + end)
        slur.set(XML_ID, identifier)
    annotation = child(measure(solution, 1), "annot", type="editorial",
                       label="Opening slur division", plist="#d1e60 #d1e338 #d1e561 #d1e634")
    annotation.set(XML_ID, "seminar-annot-opening-slurs")
    child(annotation, "p", "IMSLP 51556, printed p. 8, first system: the pickup-to-F3 slur "
          "ends in the first full bar; a separate B-flat3-to-A3 slur occupies the second full bar. "
          "The base MEI instead joins the pickup to C4 in the second full bar. "
          "This exercise follows the selected print. Other missing expressive marks remain to be edited.")
    assert projection(body(starter)) == projection(body(solution))

    manual_solution = copy.deepcopy(starter)
    for m in measures(manual_solution)[2:]:
        remove(m)
    manual = copy.deepcopy(manual_solution)
    for m in measures(manual):
        for layer in m.findall(".//m:layer", NS):
            layer.clear(keep_tail=True)
            layer.set("n", "1")
            if m.get("n") == "1":
                child(layer, "space", dur="8", type="exercise-placeholder")
            else:
                child(layer, "mSpace", type="exercise-placeholder")

    passage = ("Whole piece retained; the core exercise concerns MEI labels 1–9 "
               "(pickup plus eight full bars). This file is not a complete edition of that passage.")
    variants = [
        (baseline, "teacher/schumann/baseline.mei", "Technical baseline", passage,
         "Add two five-line staff declarations and store 20 slurs in their starting measures. "
         "Slur endpoints and other readings are inherited, not reconciled with the selected print."),
        (starter, "examples/schumann/starter.mei", "Notes-and-rhythms teaching starter", passage,
         "Remove all body slurs, dynamics, tempo, verbal directions and articulation elements deliberately. "
         "Correct d1e338 and d1e1495 from A3 to F3 against the print. "
         "Keep the other notes, written durations, rests, voices, chords, accidentals, clefs, beams, stems and IDs."),
        (solution, "teacher/schumann/exercise-solution.mei", "Solution to three assigned tasks", passage,
         "Restore opening tempo and forte, add the second-system forte, and encode the two opening "
         "printed slurs with an anchored editorial explanation. Remaining expressive content is incomplete."),
        (manual, "examples/schumann/manual-entry.mei", "Manual-entry scaffold",
         "Pickup and first full bar only (MEI labels 1–2). Replace layer placeholders with the printed music.",
         "Keep staff setup and measure IDs; replace musical layer contents by invisible duration placeholders."),
        (manual_solution, "teacher/schumann/manual-entry-solution.mei", "Manual-entry solution",
         "Pickup and first full bar only (MEI labels 1–2); expressive markings are omitted.",
         "Retain the first two measures of the notes-and-rhythms starter."),
    ]
    artifacts = []
    for tree, relative_path, stage, scope, description in variants:
        describe(tree, stage, scope, description, source)
        artifacts.append(write(tree, SESSION / relative_path))
    record = {"prepared_on": DATE, "source_sha256": source["base_encoding"]["sha256"],
              "source_unchanged": hashlib.sha256(source_path.read_bytes()).hexdigest() == source["base_encoding"]["sha256"],
              "technical_repairs": {"staff_lines": ["s1", "s2"], "slurs_relocated": moved,
                                    "historical_reference": "Record unresolved #transformation.xsl as text; do not invent a URL or target ID."},
              "source_based_pitch_corrections": pitch_corrections,
              "deliberate_omissions": omitted,
              "omission_counts": dict(sorted(Counter(e["element"] for e in omitted).items())),
              "invariants": {"technical_baseline_preserves_upstream_note_rhythm_voice_and_ids": True,
                             "teaching_notes_unchanged_except_documented_pitch_corrections": True,
                             "duplicate_ids": 0, "unresolved_local_pointers": 0},
              "artifacts": artifacts}
    (SESSION / "teacher/schumann/changes.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    for artifact in artifacts:
        print(artifact["path"], artifact["body_measures"], "measures")
    print("Removed expression:", record["omission_counts"])


if __name__ == "__main__":
    main()
