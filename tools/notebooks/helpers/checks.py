# Input checks before Verovio sees the text, and melody checks for Demo D.
# Pure functions, no DOM. The notebooks carry the same rules in Python.

import re


# Some broken inputs crash Verovio 6.3 instead of giving an error, and some
# valid ones are misread (tested 2026-10-14). errors: do not load the text;
# warnings: load it, but say what Verovio will get wrong.
def precheck(fmt, text):
    problems = []
    warnings = []
    if fmt == "abc":
        lines = re.split(r"\r?\n", text)
        if not any(re.match(r"^X:", l) for l in lines):
            problems.append("ABC needs an X: line (for example X:1) before the tune.")
        if not any(re.match(r"^K:", l) for l in lines):
            problems.append("ABC needs a K: line (the key, for example K:C) before the notes.")
        depth = 0
        unmatched = False
        chord_length = False
        for line in lines:
            if re.match(r"^[A-Za-z]:", line):
                continue  # header and lyrics lines
            body = re.sub(r"%.*$", "", line)
            body = re.sub(r'"[^"]*"', "", body)
            body = re.sub(r"\|\]|\[\|", "|", body)
            if re.search(r"\][\d/]", body):
                chord_length = True
            for ch in body:
                if ch == "[":
                    depth += 1
                if ch == "]":
                    if depth == 0:
                        unmatched = True
                    else:
                        depth -= 1
        if unmatched:
            problems.append("There is a ] without a matching [ in the notes. Use |] for a final bar line.")
        if chord_length:
            warnings.append(
                "Verovio 6.3 ignores a length written after a chord, as in [CEG]2, and plays it as one unit. "
                "Write the length inside: [C2E2G2]."
            )
    if fmt == "humdrum":
        lines = [l for l in re.split(r"\r?\n", text) if l and not l.startswith("!!")]
        head = next((l for l in lines if l.startswith("**")), None)
        if head and re.search(r" {2,}|\*\*\w+ +\*\*", head, re.ASCII) and "\t" not in head:
            problems.append("Humdrum columns (spines) must be separated by tabs, not spaces.")
        manipulators = any(
            any(re.match(r"^\*[\^v+x]$", t) for t in l.split("\t"))
            for l in lines
        )
        if head and not manipulators:
            width = len(head.split("\t"))
            bad = next((i for i, l in enumerate(lines) if len(l.split("\t")) != width), -1)
            if bad >= 0:
                n_cols = len(lines[bad].split("\t"))
                problems.append(
                    f'Line "{lines[bad]}" has {n_cols} column(s), '
                    f"but the file has {width}. Every line needs one entry per spine."
                )
    return {"errors": problems, "warnings": warnings}


# LLM answers often come inside a Markdown code fence: keep only its content.
def clean_answer(text):
    fence = re.search(r"```[\w-]*\n([\s\S]*?)```", text, re.ASCII)
    return ((fence.group(1) if fence else text).strip() + "\n")


# Bar lengths in quarter notes, from the timemap's measure starts.
def bar_lengths(timemap, notes):
    starts = [e["qstamp"] for e in timemap if e.get("measureOn")]
    end = max(
        [0]
        + [e["qstamp"] for e in timemap]
        + [n["off"] for n in notes]
    )
    return [
        (starts[i + 1] if i + 1 < len(starts) else end) - s
        for i, s in enumerate(starts)
    ]


def parse_pitch(name):
    m = re.match(r"^([A-Ga-g])([#b]?)(-?\d)$", name.strip())
    if not m:
        return None
    step = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}[m.group(1).lower()]
    alter = 1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0
    return 12 * (int(m.group(3)) + 1) + step + alter


def _js_num(n):
    # JS template strings write 2 for 2.0 and 3.5 for 3.5.
    if isinstance(n, float) and n.is_integer():
        return str(int(n))
    return str(n)


# Compare what Verovio understood with what the prompt asked for.
# found: {meter, fifths, bars: [lengths], notes}; spec: {meter, fifths, bars, low, high, final}
def melody_checks(found, spec):
    checks = []

    def add(label, ok, detail):
        checks.append({"label": label, "ok": ok, "detail": detail})

    want = (spec["meter"]["count"] * 4) / spec["meter"]["unit"]
    add(
        f"Metre is {spec['meter']['count']}/{spec['meter']['unit']}",
        found["meter"]["count"] == spec["meter"]["count"] and found["meter"]["unit"] == spec["meter"]["unit"],
        f"found {found['meter']['count']}/{found['meter']['unit']}",
    )
    add(f"{spec['bars']} bars", len(found["bars"]) == spec["bars"], f"found {len(found['bars'])}")
    wrong = [[i + 1, q] for i, q in enumerate(found["bars"]) if abs(q - want) > 1e-6]
    add(
        f"Every bar adds up to {_js_num(want)} quarter notes",
        len(wrong) == 0,
        ", ".join(f"bar {b}: {_js_num(q)}" for b, q in wrong) if wrong else "all bars complete",
    )

    def sig(f):
        if f == 0:
            return "no sharps or flats"
        if f > 0:
            return f"{f} sharp{'s' if f > 1 else ''}"
        return f"{-f} flat{'s' if f < -1 else ''}"

    add(f"Key signature: {sig(spec['fifths'])}", found["fifths"] == spec["fifths"], f"found {sig(found['fifths'])}")
    if found["notes"]:
        pitches = [n["pitch"] for n in found["notes"]]
        low = min(pitches)
        high = max(pitches)
        add(
            f"Range within {pitch_name(spec['low'])}–{pitch_name(spec['high'])}",
            low >= spec["low"] and high <= spec["high"],
            f"found {pitch_name(low)}–{pitch_name(high)}",
        )
        last = found["notes"][-1]["pitch"]
        final_name = re.sub(r"-?\d+$", "", pitch_name(spec["final"]))
        add(
            f"Ends on {final_name}",
            last % 12 == spec["final"] % 12,
            f"last note {pitch_name(last)}",
        )
    else:
        add("Has notes", False, "Verovio found no notes")
    return checks
