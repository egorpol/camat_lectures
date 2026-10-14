# Melody <-> binary pitch x time grid (Demo C). Pure functions, no DOM.
# The Python version in 01_binary_grid.ipynb follows the same rules.
#
# A cell covers [i / res, (i + 1) / res) quarter notes. Two sets of rules:
# "demo": a note fills every cell whose start lies inside the note (what sounds
#   at the start of the cell); notes that cover no cell start are lost. The grid
#   is read back column by column, as a sequence of chords.
# "camat": as CAMAT's create_binary_matrix, onsets are floored and ends ceiled,
#   so a note fills every cell it touches. The grid is read back row by row, as
#   CAMAT's binary_slice_to_df does: each run of 1s is one note. CAMAT has no
#   onset layer (yet), so this read-back ignores onsets.

import math

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def pitch_name(midi):
    return NAMES[midi % 12] + str(math.floor(midi / 12) - 1)


def is_black_key(midi):
    return len(NAMES[midi % 12]) > 1


# Notes from a Verovio timemap: [{pitch, on, off}] in quarter notes.
# pitches: dict xml:id -> MIDI pitch (pitches_from_mei in mei.py); ids not in
# the map (rests) are skipped.
def notes_from_timemap(timemap, pitches):
    offs = {}
    for event in timemap:
        for id_ in event.get("off") or []:
            offs[id_] = event["qstamp"]
    notes = []
    for event in timemap:
        for id_ in event.get("on") or []:
            if id_ not in pitches:
                continue
            notes.append({
                "pitch": pitches[id_],
                "on": event["qstamp"],
                "off": offs.get(id_, event["qstamp"]),
            })
    notes.sort(key=lambda n: (n["on"], n["pitch"]))
    return notes


def bar_quarters(meter):
    return (meter["count"] * 4) / meter["unit"]


# Start of the cell grid: round to avoid 0.9999 artefacts.
EPS = 1e-9


def _js_round(x):
    # Math.round is round-half-up; Python round() is banker's rounding.
    return math.floor(x + 0.5)


# to_grid(notes, res, meter, rule) — positional (JS passes {res, meter, rule}).
def to_grid(notes, res, meter, rule="demo"):
    bar_cells = _js_round(bar_quarters(meter) * res)
    end = max([0] + [n["off"] for n in notes])
    bars = max(1, math.ceil(end / bar_quarters(meter) - EPS))
    n_cols = bars * bar_cells
    pitch_list = [n["pitch"] for n in notes]
    # Math.min(...[]) is Infinity; Math.max(...[]) is -Infinity.
    low = min(pitch_list) if pitch_list else float("inf")
    high = max(pitch_list) if pitch_list else float("-inf")
    occ = {}
    ons = {}
    p = low
    while p <= high:
        occ[p] = [0] * n_cols
        ons[p] = [0] * n_cols
        p += 1
    lost = []
    moved = []  # kept, but starting or ending at a different time
    for n in notes:
        if rule == "camat":
            first = math.floor(n["on"] * res + EPS)
        else:
            first = math.ceil(n["on"] * res - EPS)
        stop = math.ceil(n["off"] * res - EPS)  # first cell not covered
        if first >= stop or n["off"] - n["on"] < EPS:
            lost.append(n)
            continue
        if abs(first - n["on"] * res) > EPS or abs(stop - n["off"] * res) > EPS:
            moved.append(n)
        i = first
        while i < stop and i < n_cols:
            occ[n["pitch"]][i] = 1
            i += 1
        ons[n["pitch"]][first] = 1
    return {
        "res": res,
        "meter": meter,
        "rule": rule,
        "barCells": bar_cells,
        "nCols": n_cols,
        "low": low,
        "high": high,
        "occ": occ,
        "ons": ons,
        "lost": lost,
        "moved": moved,
    }


# Rows to show, highest first. compact: hide black-key rows that stay empty.
def grid_rows(grid, compact=True):
    rows = []
    p = grid["high"]
    while p >= grid["low"]:
        if compact and is_black_key(p) and not any(grid["occ"][p]):
            p -= 1
            continue
        rows.append(p)
        p -= 1
    return rows


# Grid as text, one row per pitch, cells grouped by bar (as on the slides).
def grid_to_text(grid, compact=True, onsets=False):
    rows = grid_rows(grid, compact)
    bars = grid["nCols"] / grid["barCells"]
    width = max(grid["barCells"], 5) + 2

    def label(s):
        return s.ljust(6)

    def block(cells):
        header = label("") + "".join(
            f"bar {b + 1}".ljust(width) for b in range(int(bars))
        ).rstrip()
        lines = [header]
        for p in rows:
            line = label(pitch_name(p))
            for b in range(int(bars)):
                chunk = cells[p][b * grid["barCells"]:(b + 1) * grid["barCells"]]
                line += "".join(str(v) for v in chunk).ljust(width)
            lines.append(line.rstrip())
        return "\n".join(lines)

    if not onsets:
        return block(grid["occ"])
    # Both grids in one: a note can only start where a pitch sounds, so three values are enough.
    three = {p: [(2 if grid["ons"][p][i] else 1) if v else 0 for i, v in enumerate(grid["occ"][p])] for p in rows}
    return (
        f"Sounding (1 = the pitch sounds):\n{block(grid['occ'])}\n\n"
        f"Onsets (1 = a note starts):\n{block(grid['ons'])}\n\n"
        f"Both in one grid (2 = a note starts, 1 = it continues, 0 = silence):\n{block(three)}"
    )


# Read the grid back as events: a new event starts whenever the set of
# sounding pitches changes or (with onsets) a sounding pitch has an onset.
def grid_to_events(grid, onsets=False):
    events = []
    current = None
    for i in range(grid["nCols"]):
        active = []
        attack = False
        p = grid["low"]
        while p <= grid["high"]:
            if grid["occ"][p][i]:
                active.append(p)
                if onsets and grid["ons"][p][i]:
                    attack = True
            p += 1
        key = ",".join(str(x) for x in active)
        if current and current["key"] == key and not attack:
            current["len"] += 1
        else:
            current = {"key": key, "start": i, "len": 1, "pitches": active}
            events.append(current)
    return [{"start": e["start"], "len": e["len"], "pitches": e["pitches"]} for e in events]


# Read the grid back with its rules: {events (for events_to_kern), notes, cut}.
# cut: how often the column-by-column reading cuts a held note because
# another pitch starts or stops while it sounds.
def read_grid(grid, onsets=False):
    if grid.get("rule") == "camat":
        notes = grid_to_notes(grid)
        return {"events": notes_to_events(notes, grid), "notes": notes, "cut": 0}
    events = grid_to_events(grid, onsets)
    cut = 0
    for k in range(1, len(events)):
        i = events[k]["start"]
        for p in events[k]["pitches"]:
            if p in events[k - 1]["pitches"] and not (onsets and grid["ons"][p][i]):
                cut += 1
    return {"events": events, "notes": events_to_notes(events, grid["res"]), "cut": cut}


# Row by row, as CAMAT reads its grids: each run of 1s in one row is one note,
# so repeated notes of the same pitch merge.
def grid_to_notes(grid):
    notes = []
    p = grid["low"]
    while p <= grid["high"]:
        start = -1
        for i in range(grid["nCols"] + 1):
            on = i < grid["nCols"] and grid["occ"][p][i] == 1
            if start >= 0 and not on:
                notes.append({"pitch": p, "on": start / grid["res"], "off": i / grid["res"]})
                start = -1
            if on and start < 0:
                start = i
        p += 1
    notes.sort(key=lambda n: (n["on"], n["pitch"]))
    return notes


# Notes -> events for events_to_kern: cut wherever a note starts or ends.
# tied: pitches that go on sounding from the event before.
def notes_to_events(notes, grid):
    res = grid["res"]
    spans = [(n["pitch"], _js_round(n["on"] * res), _js_round(n["off"] * res)) for n in notes]
    cuts = sorted({0, grid["nCols"], *(s[1] for s in spans), *(s[2] for s in spans)})
    events = []
    for k in range(len(cuts) - 1):
        here = [s for s in spans if s[1] <= cuts[k] < s[2]]
        events.append({
            "start": cuts[k],
            "len": cuts[k + 1] - cuts[k],
            "pitches": sorted(s[0] for s in here),
            "tied": sorted(s[0] for s in here if s[1] < cuts[k]),
        })
    return events


def events_to_notes(events, res):
    notes = []
    for e in events:
        for p in e["pitches"]:
            notes.append({
                "pitch": p,
                "on": e["start"] / res,
                "off": (e["start"] + e["len"]) / res,
            })
    notes.sort(key=lambda n: (n["on"], n["pitch"]))
    return notes


# kern pitch: c = C4, cc = C5, C = C3, CC = C2.
def kern_pitch(midi):
    name = NAMES[midi % 12]
    octave = math.floor(midi / 12) - 1
    letter = name[0]
    accidental = "#" if len(name) > 1 else ""
    repeat = octave - 3 if octave >= 4 else 4 - octave
    base = letter.lower() if octave >= 4 else letter
    return base * repeat + accidental


# Durations kern can write as one token, in quarter notes, largest first.
KERN_DURATIONS = [
    (6, "1."), (4, "1"), (3, "2."), (2, "2"), (1.5, "4."), (1, "4"),
    (0.75, "8."), (0.5, "8"), (0.375, "16."), (0.25, "16"), (0.125, "32"),
]


def _split_duration(quarters):
    parts = []
    left = quarters
    while left > EPS:
        fit = next(((q, recip) for q, recip in KERN_DURATIONS if q <= left + EPS), None)
        if not fit:
            break
        parts.append(fit)
        left -= fit[0]
    return parts


# Events (from grid_to_events or notes_to_events) -> a **kern score Verovio can render.
def events_to_kern(events, grid):
    res, meter, bar_cells = grid["res"], grid["meter"], grid["barCells"]
    sounding = [p for e in events for p in e["pitches"]]
    sorted_p = sorted(sounding)
    median = sorted_p[len(sorted_p) // 2] if sorted_p else 60
    lines = [
        "**kern",
        "*clefF4" if median < 57 else "*clefG2",
        f"*M{meter['count']}/{meter['unit']}",
    ]
    # Cut each event at bar lines, then into writable durations.
    pieces = []
    for k, e in enumerate(events):
        tied_in = e.get("tied", [])
        tied_out = events[k + 1].get("tied", []) if k + 1 < len(events) else []
        start = e["start"]
        end = e["start"] + e["len"]
        chunks = []
        while start < end:
            bar_end = (math.floor(start / bar_cells) + 1) * bar_cells
            stop = min(end, bar_end)
            for q, recip in _split_duration((stop - start) / res):
                chunks.append({"recip": recip, "start": start, "bar": math.floor(start / bar_cells)})
            start = stop
        for j, c in enumerate(chunks):
            pieces.append({**c, "pitches": e["pitches"], "first": j == 0, "last": j == len(chunks) - 1,
                           "tied_in": tied_in, "tied_out": tied_out})
    bar = -1
    for piece in pieces:
        if piece["bar"] != bar:
            bar = piece["bar"]
            lines.append(f"={bar + 1}")
        if not piece["pitches"]:
            lines.append(f"{piece['recip']}r")
            continue
        tokens = []
        for p in piece["pitches"]:
            token = piece["recip"] + kern_pitch(p)
            into = not piece["first"] or p in piece["tied_in"]
            onward = not piece["last"] or p in piece["tied_out"]
            if into and onward:
                tokens.append(token + "_")
            elif onward:
                tokens.append("[" + token)
            elif into:
                tokens.append(token + "]")
            else:
                tokens.append(token)
        lines.append(" ".join(tokens))
    lines.extend(["==", "*-"])
    return "\n".join(lines) + "\n"


# Compare two note lists: same pitches at the same times?
# Key by (pitch, on, off) so 1 and 1.0 match (JS string keys would differ).
def compare_notes(before, after):
    def key(n):
        return (n["pitch"], n["on"], n["off"])

    after_keys = {key(n) for n in after}
    before_keys = {key(n) for n in before}
    return {
        "kept": sum(1 for n in before if key(n) in after_keys),
        "missing": [n for n in before if key(n) not in after_keys],
        "added": [n for n in after if key(n) not in before_keys],
    }
