# Demo D: render an LLM's answer and check it against what the prompt asked for.
# spec: {"meter": "3/4", "bars": 8, "fifths": 2, "low": "D4", "high": "D5", "final": "D"}
# fifths: number of sharps (2 = two sharps), or minus the number of flats.

def check_answer(fmt, text, spec):
    if not text.strip():
        print("Paste an answer between the triple quotes first.")
        return None
    text = clean_answer(text)
    result = read_score(fmt, text, scale=35)
    count, unit = (int(x) for x in spec["meter"].split("/"))
    want = {
        "meter": {"count": count, "unit": unit},
        "bars": spec["bars"],
        "fifths": spec["fifths"],
        "low": parse_pitch(spec["low"]),
        "high": parse_pitch(spec["high"]),
        "final": parse_pitch(spec["final"] + "4"),
    }
    if result["ok"]:
        rows = [{"label": "Verovio reads it", "ok": True,
                 "detail": "with warnings, see below the score" if result["log"] else "no warnings"}]
        found = {"meter": result["meter"], "fifths": result["fifths"],
                 "bars": bar_lengths(result["timemap"], result["notes"]), "notes": result["notes"]}
        rows += melody_checks(found, want)
    else:
        rows = [{"label": "Verovio reads it", "ok": False, "detail": " ".join(result["errors"])}]
    width = max(len(r["label"]) for r in rows)
    for r in rows:
        print(f"{'✓' if r['ok'] else '✗'}  {r['label'].ljust(width)}   {r['detail']}")
    print()
    show(result)
    return result
