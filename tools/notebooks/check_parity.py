#!/usr/bin/env python3
"""Parity test: Python helpers vs the site's JS modules on the same inputs."""

import json
import subprocess
import sys
from pathlib import Path

import verovio

ROOT = Path(__file__).resolve().parents[2]
HELPERS = Path(__file__).resolve().parent / "helpers"
PARITY_MJS = Path(__file__).resolve().parent / "parity.mjs"
EXAMPLES = ROOT / "sessions/01-why-encode-music/examples"
ANSWERS_PATH = EXAMPLES / "llm/answers.json"

# Load helpers the same way the notebook does: concatenate and exec.
_ns = {}
_src = "\n".join(
    (HELPERS / name).read_text(encoding="utf-8")
    for name in ("mei.py", "grid.py", "checks.py")
)
exec(_src, _ns)

pitches_from_mei = _ns["pitches_from_mei"]
meter_from_mei = _ns["meter_from_mei"]
fifths_from_mei = _ns["fifths_from_mei"]
notes_from_timemap = _ns["notes_from_timemap"]
to_grid = _ns["to_grid"]
grid_rows = _ns["grid_rows"]
grid_to_text = _ns["grid_to_text"]
grid_to_events = _ns["grid_to_events"]
events_to_notes = _ns["events_to_notes"]
read_grid = _ns["read_grid"]
grid_to_notes = _ns["grid_to_notes"]
notes_to_events = _ns["notes_to_events"]
events_to_kern = _ns["events_to_kern"]
compare_notes = _ns["compare_notes"]
precheck = _ns["precheck"]
clean_answer = _ns["clean_answer"]
bar_lengths = _ns["bar_lengths"]
parse_pitch = _ns["parse_pitch"]
melody_checks = _ns["melody_checks"]


def load_score(fmt, text):
    tk = verovio.toolkit()
    tk.setOptions({"inputFrom": fmt})
    if not tk.loadData(text):
        raise RuntimeError(f"Verovio failed to load as {fmt}: {text[:80]!r}")
    mei = tk.getMEI()
    timemap = tk.renderToTimemap({"includeMeasures": True, "includeRests": True})
    return mei, timemap


def grid_for_json(grid):
    """Plain dict ready for JSON (int keys -> stay ints until dump)."""
    return {
        "res": grid["res"],
        "meter": grid["meter"],
        "rule": grid["rule"],
        "barCells": grid["barCells"],
        "nCols": grid["nCols"],
        "low": grid["low"],
        "high": grid["high"],
        "occ": {k: list(v) for k, v in grid["occ"].items()},
        "ons": {k: list(v) for k, v in grid["ons"].items()},
        "lost": grid["lost"],
        "moved": grid["moved"],
    }


def add_score_cases(cases, labels, mei, timemap, notes=None):
    pitches = pitches_from_mei(mei)
    meter = meter_from_mei(mei)
    notes = notes if notes is not None else notes_from_timemap(timemap, pitches)
    cases.append(("pitches_from_mei", pitches_from_mei, [mei]))
    cases.append(("meter_from_mei", meter_from_mei, [mei]))
    cases.append(("fifths_from_mei", fifths_from_mei, [mei]))
    cases.append(("notes_from_timemap", notes_from_timemap, [timemap, pitches]))
    cases.append(("bar_lengths", bar_lengths, [timemap, notes]))
    for res in (1, 2, 4):
        grid = to_grid(notes, res, meter)
        gjson = grid_for_json(grid)
        cases.append(("to_grid", to_grid, [notes, res, meter]))
        for compact in (True, False):
            cases.append(("grid_rows", grid_rows, [gjson, compact]))
            for onsets in (True, False):
                cases.append(("grid_to_text", grid_to_text, [gjson, compact, onsets]))
        for onsets in (True, False):
            cases.append(("grid_to_events", grid_to_events, [gjson, onsets]))
            events = grid_to_events(grid, onsets)
            cases.append(("events_to_notes", events_to_notes, [events, res]))
            cases.append(("events_to_kern", events_to_kern, [events, gjson]))
            # Round trip: int qstamps vs float cell times — must keep every note.
            round_trip = events_to_notes(events, res)
            cases.append(("compare_notes", compare_notes, [notes, round_trip]))
        add_rule_cases(cases, notes, res, meter)
    labels.append(f"score:{len(notes)}notes")


def add_rule_cases(cases, notes, res, meter):
    for rule in ("demo", "camat"):
        grid = to_grid(notes, res, meter, rule)
        gjson = grid_for_json(grid)
        cases.append(("to_grid", to_grid, [notes, res, meter, rule]))
        cases.append(("grid_to_notes", grid_to_notes, [gjson]))
        for onsets in (True, False):
            cases.append(("read_grid", read_grid, [gjson, onsets]))
            back = read_grid(grid, onsets)
            cases.append(("notes_to_events", notes_to_events, [back["notes"], gjson]))
            cases.append(("events_to_kern", events_to_kern, [back["events"], gjson]))
            cases.append(("compare_notes", compare_notes, [notes, back["notes"]]))


def build_cases():
    cases = []  # (fn, py_fn, args)
    labels = []

    # --- 1. Real Verovio output from shipped examples ---
    formats = [
        ("alle_meine_entchen.abc", "abc"),
        ("alle_meine_entchen.krn", "humdrum"),
        ("alle_meine_entchen.pae", "pae"),
        ("alle_meine_entchen.esac", "esac"),
        ("alle_meine_entchen.musicxml", "xml"),
        ("alle_meine_entchen.mei", "mei"),
    ]
    for name, fmt in formats:
        text = (EXAMPLES / name).read_text(encoding="utf-8")
        mei, timemap = load_score(fmt, text)
        add_score_cases(cases, labels, mei, timemap)

    answers_data = json.loads(ANSWERS_PATH.read_text(encoding="utf-8"))
    spec_raw = answers_data["spec"]
    good_spec = {
        "meter": {"count": spec_raw["meter"][0], "unit": spec_raw["meter"][1]},
        "bars": spec_raw["bars"],
        "fifths": spec_raw["fifths"],
        "low": parse_pitch(spec_raw["low"]),
        "high": parse_pitch(spec_raw["high"]),
        "final": parse_pitch(spec_raw["final"]),
    }
    bad_spec = {
        "meter": {"count": 4, "unit": 4},
        "bars": 2,
        "fifths": -3,
        "low": parse_pitch("C4"),
        "high": parse_pitch("E4"),
        "final": parse_pitch("G4"),
    }

    for ans in answers_data["answers"]:
        text = clean_answer(ans["text"])
        mei, timemap = load_score(ans["format"], text)
        pitches = pitches_from_mei(mei)
        notes = notes_from_timemap(timemap, pitches)
        add_score_cases(cases, labels, mei, timemap, notes)
        found = {
            "meter": meter_from_mei(mei),
            "fifths": fifths_from_mei(mei),
            "bars": bar_lengths(timemap, notes),
            "notes": notes,
        }
        cases.append(("melody_checks", melody_checks, [found, good_spec]))
        cases.append(("melody_checks", melody_checks, [found, bad_spec]))
        labels.append(f"answer:{ans['id']}")

    # Small kern: D major. Verovio writes <note pname="f"/> with no accidental for
    # 4f# under *k[f#c#]; pitches_from_mei must apply the key signature (both F#).
    # (A bare 4f is emitted with accid="n" by Verovio 6.3, so it stays F natural.)
    kern_d = "**kern\n*clefG2\n*k[f#c#]\n*M4/4\n=1\n4f#\n4f#\n4a\n4dd\n==\n*-\n"
    mei, timemap = load_score("humdrum", kern_d)
    add_score_cases(cases, labels, mei, timemap)

    # ABC: eighths, tie across bar, accidental carries (^F F).
    abc_tie = "X:1\nT:t\nM:4/4\nL:1/8\nK:C\nC2 D2 E2 ^F2 | F2 G2 A2 B2 |]\n"
    mei, timemap = load_score("abc", abc_tie)
    add_score_cases(cases, labels, mei, timemap)

    # --- 2. Hand-made note lists for grid functions ---
    m34 = {"count": 3, "unit": 4}
    m68 = {"count": 6, "unit": 8}
    handmade = [
        # empty-ish: one note
        ([{"pitch": 60, "on": 0, "off": 1}], 2, m34),
        # shorter than a cell -> lost
        ([{"pitch": 62, "on": 0.1, "off": 0.2}], 1, m34),
        # chord
        (
            [
                {"pitch": 60, "on": 0, "off": 1},
                {"pitch": 64, "on": 0, "off": 1},
                {"pitch": 67, "on": 0, "off": 1},
            ],
            2,
            m34,
        ),
        # note crossing two bars (3/4: bar = 3 quarters)
        ([{"pitch": 60, "on": 2, "off": 4}], 2, m34),
        # rest gap between notes
        (
            [
                {"pitch": 60, "on": 0, "off": 1},
                {"pitch": 62, "on": 2, "off": 3},
            ],
            2,
            m34,
        ),
        # 6/8 meter
        ([{"pitch": 67, "on": 0, "off": 1.5}], 2, m68),
        # off-beat eighths on a quarter grid: lost (demo) or moved and widened (camat)
        (
            [
                {"pitch": 60, "on": 0, "off": 1.5},
                {"pitch": 62, "on": 1.5, "off": 2},
                {"pitch": 64, "on": 2.5, "off": 3},
            ],
            1,
            m34,
        ),
        # staggered chord: C4 held, E4 enters later, crossing a bar line
        (
            [
                {"pitch": 60, "on": 0, "off": 3},
                {"pitch": 64, "on": 1, "off": 5},
                {"pitch": 60, "on": 3, "off": 4},
            ],
            2,
            m34,
        ),
    ]
    for notes, res, meter in handmade:
        grid = to_grid(notes, res, meter)
        gjson = grid_for_json(grid)
        cases.append(("to_grid", to_grid, [notes, res, meter]))
        cases.append(("grid_rows", grid_rows, [gjson, True]))
        cases.append(("grid_to_text", grid_to_text, [gjson, True, False]))
        cases.append(("grid_to_text", grid_to_text, [gjson, False, True]))
        cases.append(("grid_to_events", grid_to_events, [gjson, False]))
        cases.append(("grid_to_events", grid_to_events, [gjson, True]))
        events = grid_to_events(grid, False)
        cases.append(("events_to_notes", events_to_notes, [events, res]))
        cases.append(("events_to_kern", events_to_kern, [events, gjson]))
        cases.append(("compare_notes", compare_notes, [notes, events_to_notes(events, res)]))
        add_rule_cases(cases, notes, res, meter)
        labels.append("handmade")

    # --- 3. precheck ---
    abc_ex = (EXAMPLES / "alle_meine_entchen.abc").read_text(encoding="utf-8")
    krn_ex = (EXAMPLES / "alle_meine_entchen.krn").read_text(encoding="utf-8")
    precheck_texts = [
        ("abc", abc_ex),
        ("humdrum", krn_ex),
        ("abc", "T:t\nK:C\nCDEF|"),
        ("abc", "X:1\nT:t\nCDEF|"),
        ("abc", "X:1\nK:C\nCD]EF|"),
        ("abc", "X:1\nK:C\nCDEF|]"),
        ("abc", "X:1\nK:C\n[DFA]4 [D2F2A2]|"),
        ("abc", 'X:1\nK:C\n"[x]"C|'),
        ("humdrum", "**kern\t**kern\n4c\t4e\n4d\n*-\t*-"),
        ("humdrum", "**kern  **kern\n4c  4e\n*-  *-"),
        ("humdrum", "**kern\t**kern\n*^\t*\n4c\t4e\t4g\n*v\t*v\n*-\t*-"),
        ("abc", "X:1\r\nK:C\r\nCDEF|]"),
        ("humdrum", "**kern\r\n*M4/4\r\n4c\r\n*-\r\n"),
    ]
    for fmt, text in precheck_texts:
        cases.append(("precheck", precheck, [fmt, text]))
        labels.append("precheck")

    # --- 4. clean_answer ---
    clean_texts = [
        "just plain text\nwith lines\n",
        "before\n```abc\nX:1\nK:C\nC|\n```\nafter\n",
        "```\nnaked fence\n```\n",
        "```abc\nfirst\n```\n```kern\nsecond\n```\n",
    ]
    for text in clean_texts:
        cases.append(("clean_answer", clean_answer, [text]))
        labels.append("clean_answer")

    # --- 5. parse_pitch ---
    for name in ["D4", "d5", "F#3", "Bb-1", "C10", "H4", " E4 ", ""]:
        cases.append(("parse_pitch", parse_pitch, [name]))
        labels.append("parse_pitch")

    # --- 6. pitches_from_mei: accidentals outside the table (JS: undefined, Python: None) ---
    odd = (
        '<mei><music><body><mdiv><score><scoreDef keysig="1s"/><section><measure n="1"><staff n="1"><layer>'
        '<note xml:id="a" pname="f" oct="4" accid="3qs"/><note xml:id="b" pname="f" oct="4"/>'
        '<note xml:id="c" pname="c" oct="5"><accid accid="s" accid.ges="nf"/></note><note xml:id="d" pname="c" oct="5"/>'
        '</layer></staff></measure></section></score></mdiv></body></music></mei>'
    )
    cases.append(("pitches_from_mei", pitches_from_mei, [odd]))
    labels.append("pitches_from_mei")

    return cases


def run_js(cases):
    payload = [{"fn": fn, "args": args} for fn, _py, args in cases]
    proc = subprocess.run(
        ["node", str(PARITY_MJS)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise RuntimeError(f"parity.mjs failed: {proc.returncode}")
    return json.loads(proc.stdout)


def normalize(value):
    """JSON round-trip so keys are strings and numbers compare by value."""
    return json.loads(json.dumps(value, allow_nan=False))


def main():
    cases = build_cases()
    py_results = [normalize(py_fn(*args)) for _fn, py_fn, args in cases]
    js_results = [normalize(r) for r in run_js(cases)]

    counts = {}
    mismatches = 0
    first = None
    for i, ((fn, _py, args), py_r, js_r) in enumerate(zip(cases, py_results, js_results)):
        counts[fn] = counts.get(fn, 0) + 1
        if py_r != js_r:
            mismatches += 1
            if first is None:
                first = (i, fn, args, py_r, js_r)

    print(f"cases: {len(cases)}")
    for fn in sorted(counts):
        print(f"  {fn}: {counts[fn]}")
    if first is not None:
        i, fn, args, py_r, js_r = first
        print(f"\nFIRST MISMATCH case[{i}] {fn}")
        print("args:", json.dumps(args, indent=2)[:4000])
        print("python:", json.dumps(py_r, indent=2)[:4000])
        print("js:    ", json.dumps(js_r, indent=2)[:4000])
        print(f"\n{mismatches} mismatch(es)")
        return 1
    print("all matching")
    return 0


if __name__ == "__main__":
    sys.exit(main())
