# The notes per bar in words, as under the course page's ABC box (demos.js,
# barsRead), and a check against the bass of the pickup and bar 1.

LENGTH_NAMES = {0.25: "sixteenth", 0.5: "eighth", 0.75: "dotted eighth", 1: "quarter",
                1.5: "dotted quarter", 2: "half", 3: "dotted half", 4: "whole"}
SHARP_NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
FLAT_NAMES = ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"]

# The print: pickup C3 eighth; bar 1 F3 dotted quarter, A3 eighth, C4 dotted quarter, F3 eighth.
BASS_PRINT = [("Pickup", ["C3 eighth"]),
              ("Bar 1", ["F3 dotted quarter", "A3 eighth", "C4 dotted quarter", "F3 eighth"])]


def _number(q):
    return str(int(q)) if q == int(q) else str(q)


def length_name(q):
    return LENGTH_NAMES.get(q, f"{_number(q)} quarter notes")


def spelled(midi, fifths):
    return (FLAT_NAMES if fifths < 0 else SHARP_NAMES)[midi % 12] + str(midi // 12 - 1)


# A first bar shorter than the metre is the pickup; the next one is bar 1.
def bars_read(result):
    starts = [e["qstamp"] for e in result["timemap"] if e.get("measureOn")]
    lengths = bar_lengths(result["timemap"], result["notes"])
    full = result["meter"]["count"] * 4 / result["meter"]["unit"]
    pickup = bool(lengths) and lengths[0] < full - 1e-6
    events = [(n["on"], f"{spelled(n['pitch'], result['fifths'])} {length_name(n['off'] - n['on'])}")
              for n in result["notes"]]
    rest_ends = {i: e["qstamp"] for e in result["timemap"] for i in e.get("restsOff") or []}
    events += [(e["qstamp"], f"rest {length_name(rest_ends.get(i, e['qstamp']) - e['qstamp'])}")
               for e in result["timemap"] for i in e.get("restsOn") or []]
    events.sort(key=lambda event: event[0])
    bars = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else float("inf")
        is_pickup = pickup and i == 0
        notes = [text for on, text in events if start - 1e-6 <= on < end - 1e-6]
        short = ("" if is_pickup or abs(lengths[i] - full) < 1e-6
                 else f"{_number(lengths[i])} of {_number(full)} quarter notes")
        bars.append((("Pickup" if is_pickup else f"Bar {i if pickup else i + 1}"), notes, short))
    return bars


def print_bars(result):
    if not result["ok"]:
        return
    print("Verovio reads")
    for label, notes, short in bars_read(result):
        print(f"  {label}: {', '.join(notes) or 'nothing'}" + (f" ({short})" if short else ""))


def check_bass(name, result):
    if not result["ok"]:
        print(f"{name}: Verovio could not read it; see the message under the score.")
        return
    found = {label: (notes, short) for label, notes, short in bars_read(result)}
    expected = dict(BASS_PRINT)
    problems = [f"{label} is missing" for label in expected if label not in found]
    if name == "ABC" and "Bar 1" not in found:
        # Verovio leaves out a last bar that no bar line closes.
        problems.append("type it after the bar line and end it with |]")
    for label, (notes, short) in found.items():
        if label not in expected:
            problems.append(f"{label} is extra")
        elif notes != expected[label]:
            problems.append(f"{label} reads {', '.join(notes) or 'nothing'}" + (f" ({short})" if short else ""))
    if result["fifths"] != -1:
        problems.append("the key is not F major (one flat)")
    if problems:
        print(f"{name}: not yet. " + "; ".join(problems))
        return
    print(f"{name}: ✓ the same notes as the print, in F major")
