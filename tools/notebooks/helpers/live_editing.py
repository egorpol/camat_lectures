"""Small local checks for the Schumann editing session; no model service calls."""

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

MEI_NS = "http://www.music-encoding.org/ns/mei"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
M = "{" + MEI_NS + "}"
ET.register_namespace("", MEI_NS)


def editing_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_editing_changes(before, after):
    """Allow new dynam/tempo/slur/annot measure children; protect the rest.

    This is a structural guard, not a source-fidelity or schema validator.
    Whitespace-only formatting is ignored. Existing editorial/header elements
    remain protected. Every new top-level control needs a unique xml:id.
    """
    baseline = ET.parse(before).getroot()
    current = ET.parse(after).getroot()
    old_ids = {e.get(XML_ID) for e in baseline.iter() if e.get(XML_ID)}
    ids = [e.get(XML_ID) for e in current.iter() if e.get(XML_ID)]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate xml:id in working MEI")
    if not old_ids.issubset(ids):
        raise ValueError("An existing xml:id was removed or renamed")
    allowed = {M + tag for tag in ("dynam", "tempo", "slur", "annot")}
    inserted = []

    def project(element, allow_insertions=False, parent=None):
        if (allow_insertions and parent is not None and parent.tag == M + "measure"
                and element.tag in allowed and element.get(XML_ID) not in old_ids):
            if not element.get(XML_ID):
                raise ValueError("Give each added control/annotation a unique xml:id")
            inserted.append({"id": element.get(XML_ID), "element": element.tag.split("}")[-1],
                             "measure": parent.get("n")})
            return None
        children = [value for child in element
                    if (value := project(child, allow_insertions, element)) is not None]
        return (element.tag, sorted(element.attrib.items()), (element.text or "").strip(),
                (element.tail or "").strip(), children)

    if project(baseline) != project(current, True):
        raise ValueError("Protected content changed: inspect the diff before continuing")
    graphics = current.findall("m:music/m:facsimile/m:surface/m:graphic", {"m": MEI_NS})
    for graphic in graphics:
        target = graphic.get("target", "")
        if not target or "://" in target or not (Path(after).parent / target).is_file():
            raise ValueError(f"Expected local graphic is missing or changed: {target}")
    return {"protected_structure_unchanged": True, "local_graphics_present": len(graphics),
            "new_controls": inserted, "before_sha256": editing_sha(before),
            "after_sha256": editing_sha(after), "human_source_review": "not_assessed"}


def forte_prompt(path):
    root = ET.parse(path).getroot()
    matches = [e for e in root.findall("m:music/m:body//m:measure", {"m": MEI_NS})
               if e.get(XML_ID) == "d1e1231"]
    if len(matches) != 1 or matches[0].get("n") != "6":
        raise ValueError("Expected measure d1e1231 / label 6 is missing")
    measure = matches[0]
    if any(e.get(XML_ID) == "seminar-dynam-second-system" for e in root.iter()):
        raise ValueError("The forte task is already applied; use the unedited checkpoint for a fair comparison")
    return '''Work on MEI 5.1, Schumann Op.68 No.10, edition/mei/work.mei.
Human-verified reading supplied for this exercise: IMSLP 51556, printed p.8,
second system, first full bar (musical bar 5 / MEI label 6), has a printed forte
at the start. Use this description as evidence; you have not inspected the scan.
Target: measure xml:id="d1e1231", n="6". Propose one <dynam> child after its
<staff> children: staff="1", place="below", tstamp="1", text f, unique
xml:id="seminar-dynam-second-system". Use ordinary transcription, not <supplied>.
Identify the insertion point, return only the minimal XML insertion and human
checks. Do not edit files, run commands, re-export or reformat. Preserve all
existing IDs, music, header, facsimile links and image paths. Ask if evidence
or targets are missing. Do not claim validation or personal source inspection.
Actual MEI excerpt (default namespace http://www.music-encoding.org/ns/mei):
''' + ET.tostring(measure, encoding="unicode")
