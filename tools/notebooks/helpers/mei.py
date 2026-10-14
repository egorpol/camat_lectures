# Read pitches, metre and key from the MEI that Verovio writes.
#
# Why not Verovio's own MIDI values? Verovio 6.3 drops gestural accidentals
# when it imports **kern: with *k[f#c#], the token 4f# becomes
# <note pname="f"/> and getMIDIValuesForElement() reports F natural.
# So we apply the key signature ourselves:
#   accid.ges > accid > accidental earlier in the bar > key signature.

import re

STEPS = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
ACCID = {"s": 1, "f": -1, "ss": 2, "x": 2, "ff": -2, "n": 0, "xs": 3, "ts": 3, "tf": -3}
SHARP_ORDER = "fcgdaeb"
FLAT_ORDER = "beadgcf"


def _attrs(text):
    out = {}
    for m in re.finditer(r'([\w.:]+)="([^"]*)"', text, re.ASCII):
        out[m.group(1)] = m.group(2)
    return out


def _key_from_sig(sig):
    # "2s" -> {f: 1, c: 1}; "0" -> {}
    m = re.match(r"^(\d+)([sf]?)$", sig or "")
    key = {}
    if not m:
        return key
    n = int(m.group(1))
    order = FLAT_ORDER if m.group(2) == "f" else SHARP_ORDER
    for i in range(n):
        key[order[i]] = -1 if m.group(2) == "f" else 1
    return key


# Map xml:id -> MIDI pitch for every <note> with pname and oct.
def pitches_from_mei(mei):
    pitches = {}
    key = {}
    carried = {}  # "staff:pname:oct" -> alteration, reset per measure
    staff = "1"
    note = None  # open <note> waiting for a child <accid>

    def finish(n):
        where = f"{staff}:{n['pname']}:{n['oct']}"
        if n.get("ges") is not None:
            alter = n["ges"]
        elif n.get("written") is not None:
            alter = n["written"]
        elif where in carried:
            alter = carried[where]
        else:
            alter = key.get(n["pname"], 0)
        if n.get("written") is not None:
            carried[where] = n["written"]
        pitches[n["id"]] = 12 * (int(n["oct"]) + 1) + STEPS[n["pname"]] + alter

    for m in re.finditer(r"<(/?)([\w]+)\b([^>]*?)(/?)>", mei, re.ASCII):
        closing, tag, body, self_closing = m.group(1), m.group(2), m.group(3), m.group(4)
        if closing:
            if tag == "note" and note:
                finish(note)
                note = None
            continue
        a = _attrs(body)
        if "keysig" in a:
            key = _key_from_sig(a["keysig"])
        if tag == "keySig" and "sig" in a:
            key = _key_from_sig(a["sig"])
        if tag == "measure":
            carried = {}
        if tag == "staff" and a.get("n"):
            staff = a["n"]
        if tag == "note" and a.get("pname") and "oct" in a:
            n = {
                "id": a.get("xml:id"),
                "pname": a["pname"],
                "oct": a["oct"],
                "ges": ACCID.get(a.get("accid.ges")),
                "written": ACCID.get(a.get("accid")),
            }
            if self_closing:
                finish(n)
            else:
                note = n
        if tag == "accid" and note:
            if "accid.ges" in a:
                note["ges"] = ACCID.get(a["accid.ges"])
            if "accid" in a:
                note["written"] = ACCID.get(a["accid"])
    return pitches


# Metre {count, unit}; 4/4 if the MEI has none.
def meter_from_mei(mei):
    tag = re.search(r"<meterSig\b[^>]*>", mei, re.ASCII)
    source = tag.group(0) if tag else mei
    count = re.search(r'\b(?:meter\.)?count="(\d+)"', source, re.ASCII)
    unit = re.search(r'\b(?:meter\.)?unit="(\d+)"', source, re.ASCII)
    if count and unit:
        return {"count": int(count.group(1)), "unit": int(unit.group(1))}
    return {"count": 4, "unit": 4}


# First key signature as fifths: 2 = two sharps, -3 = three flats.
def fifths_from_mei(mei):
    m = re.search(r'\bkeysig="(\d+)([sf]?)"', mei, re.ASCII) or re.search(
        r'<keySig\b[^>]*\bsig="(\d+)([sf]?)"', mei, re.ASCII
    )
    if not m:
        return 0
    n = int(m.group(1))
    return -n if m.group(2) == "f" else n
