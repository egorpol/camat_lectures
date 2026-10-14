"""Load every example encoding with Verovio and print what it understood.

Usage:  python check_examples.py            (needs `pip install verovio`)

For each file: did it load, which pitches and durations came out, file size.
Also writes alle_meine_entchen.mei (Verovio's MEI export of the kern file).
"""
from pathlib import Path
import re

import verovio

HERE = Path(__file__).parent
FORMATS = {
    ".krn": "humdrum",
    ".abc": "abc",
    ".pae": "pae",
    ".esac": "esac",
    ".musicxml": "xml",
    ".mei": "mei",
    ".gabc": "gabc",
}


def summary(mei: str) -> tuple[list[str], list[str]]:
    pitches, durs = [], []
    for tag in re.findall(r"<(?:note|nc) [^>]*>", mei):
        pname = re.search(r'pname="(\w)"', tag)
        octave = re.search(r'oct="(\d)"', tag)
        dur = re.search(r'dur="(\w+)"', tag)
        if pname and octave:
            pitches.append(pname.group(1) + octave.group(1))
        if dur:
            durs.append(dur.group(1))
    return pitches, durs


tk = verovio.toolkit()
print("Verovio", tk.getVersion())

kern = HERE / "alle_meine_entchen.krn"
tk.setOptions({"inputFrom": "humdrum"})
tk.loadData(kern.read_text())
(HERE / "alle_meine_entchen.mei").write_text(tk.getMEI())

for path in sorted(HERE.iterdir()):
    fmt = FORMATS.get(path.suffix)
    if fmt is None:
        continue
    tk = verovio.toolkit()
    tk.setOptions({"inputFrom": fmt})
    ok = tk.loadData(path.read_text())
    pitches, durs = summary(tk.getMEI()) if ok else ([], [])
    print(f"{path.name:28} {path.stat().st_size:5} bytes  load={ok}")
    print(f"{'':28} pitches: {' '.join(pitches)}")
    print(f"{'':28} durations: {' '.join(durs) or '(none: chant)'}")
