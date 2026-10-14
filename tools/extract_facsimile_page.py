"""Cut one page out of a facsimile-linked MEI file.

Usage (from the repository root):
    .venv/bin/python tools/extract_facsimile_page.py SOURCE.mei PAGE OUT.mei NOTE

Keeps the header, the page's <surface> and the music between the page's <pb>
and the next one. Control events that point to notes on other pages (ties
into the next page) are dropped. NOTE is written into a comment at the top.
The source must be pretty-printed with one element per line, as the CAMAT
corpus files are; the result is parsed again to check every #reference.
"""

import re
import sys
import xml.etree.ElementTree as ET

XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def index(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if re.search(pattern, lines[i]):
            return i
    raise SystemExit(f"not found: {pattern}")


def main(source, page, out, note):
    lines = open(source, encoding="utf-8").read().splitlines()
    fac = index(lines, r"<facsimile>")
    surf = index(lines, rf'<surface xml:id="([^"]+)" n="{page}"', fac)
    surface_id = re.search(r'xml:id="([^"]+)"', lines[surf]).group(1)
    surf_end = index(lines, r"</surface>", surf)
    fac_end = index(lines, r"</facsimile>", surf_end)
    section = index(lines, r"<section", fac_end)
    pb = index(lines, rf'<pb [^>]*facs="#{surface_id}"', section)
    try:
        next_pb = index(lines, r"<pb ", pb + 1)
    except SystemExit:
        next_pb = max(i for i, line in enumerate(lines) if "</section>" in line)
    closing = max(i for i, line in enumerate(lines) if "</section>" in line)

    head = lines[: fac + 1]
    root = next(i for i, line in enumerate(head) if line.startswith("<mei "))
    # Verovio (6.3) needs <mei> as the first node, so the note goes inside it.
    comment = ["   <!-- " + note.replace("--", "-") + " -->"]
    kept = (
        head[: root + 1] + comment + head[root + 1 :]
        + lines[surf : surf_end + 1]
        + lines[fac_end : section + 1]
        + lines[pb:next_pb]
        + lines[closing:]
    )

    ids = {el.get(XML_ID) for el in ET.fromstring("\n".join(kept[root:])).iter()} - {None}
    dropped = []
    result = []
    for line in kept:
        refs = re.findall(r'(?:startid|endid)="#([^"]+)"', line)
        if refs and any(r not in ids for r in refs):
            if not line.rstrip().endswith("/>"):
                raise SystemExit(f"dangling reference in a multi-line element: {line.strip()}")
            dropped.append(line.strip())
            continue
        result.append(line)
    text = "\n".join(result) + "\n"

    tree = ET.fromstring("\n".join(result[root:]))
    ids = {el.get(XML_ID) for el in tree.iter()} - {None}
    unresolved = sorted(
        {ref for el in tree.iter() for value in el.attrib.values() for ref in re.findall(r"#([\w.\-]+)", value)} - ids
    )
    open(out, "w", encoding="utf-8").write(text)
    measures = len(re.findall(r"<measure ", text))
    zones = len(re.findall(r"<zone ", text))
    print(f"{out}: {len(text.encode()):,} bytes, {measures} measures, {zones} zones")
    print("dropped:", *(dropped or ["none"]), sep="\n  ")
    print("unresolved #refs:", unresolved or "none")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
