# Piano roll: time from left to right, pitch from bottom to top, one bar per note.
# The same view CAMAT uses later for its note tables.

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle

TRACK_COLORS = ["#1f77b4", "#d62728", "#9467bd", "#ff7f0e", "#2ca02c", "#8c564b"]


# notes: [{"pitch", "start", "end"}], optionally "track" (colour) and "alpha".
# bands: [{"start", "end", "row", "color", "label"}] drawn under the keyboard (pedals).
# bar: draw a line every `bar` time units (for scores: quarter notes per bar).
def draw_roll(notes, start=None, end=None, low=None, high=None, bands=(), bar=None,
              unit="s", title=None, width=12, height=None):
    if start is None:
        start = min((n["start"] for n in notes), default=0)
    if end is None:
        end = max((n["end"] for n in notes), default=start + 1)
    pitches = [n["pitch"] for n in notes]
    if low is None:
        low = min(pitches) - 1 if pitches else 59
    if high is None:
        high = max(pitches) + 1 if pitches else 72
    rows = sorted({b["row"] for b in bands})
    below = 2 * len(rows)
    if height is None:
        height = min(8, max(2.5, 0.12 * (high - low + below) + 1))
    fig, ax = plt.subplots(figsize=(width, height))
    for p in range(low, high + 1):
        if p % 12 in (1, 3, 6, 8, 10):
            ax.axhspan(p - 0.5, p + 0.5, color="0.93", lw=0, zorder=0)
    shortest = (end - start) / 1500
    rects = [Rectangle((n["start"], n["pitch"] - 0.4), max(n["end"] - n["start"], shortest), 0.8) for n in notes]
    colors = [to_rgba(TRACK_COLORS[n.get("track", 0) % len(TRACK_COLORS)], n.get("alpha", 0.9)) for n in notes]
    ax.add_collection(PatchCollection(rects, facecolors=colors, edgecolors="none", zorder=2))
    ticks = [(p, f"C{p // 12 - 1}") for p in range(low, high + 1) if p % 12 == 0]
    for b in bands:
        y = low - 1.5 - 2 * rows.index(b["row"])
        ax.add_patch(Rectangle((b["start"], y - 0.6), b["end"] - b["start"], 1.2, color=b["color"], lw=0))
    for row in rows:
        label = next(b["label"] for b in bands if b["row"] == row)
        ticks.append((low - 1.5 - 2 * rows.index(row), label))
    if bar:
        t = bar * (start // bar)
        while t <= end:
            ax.axvline(t, color="0.6", lw=0.8, zorder=1)
            t += bar
    ax.set_yticks([y for y, _ in ticks], [label for _, label in ticks])
    ax.set_xlim(start, end)
    ax.set_ylim(low - 0.5 - below, high + 0.5)
    ax.set_xlabel({"s": "time (seconds)", "q": "time (quarter notes)"}.get(unit, unit))
    ax.set_ylabel("pitch")
    ax.grid(axis="y", color="0.85", lw=0.6)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    plt.show()


# Piano roll of a score read by read_score(): time in quarter notes, a line per bar.
def score_roll(result, **options):
    notes = [{"pitch": n["pitch"], "start": n["on"], "end": n["off"]} for n in result["notes"]]
    meter = result.get("meter") or {"count": 4, "unit": 4}
    draw_roll(notes, start=0, bar=meter["count"] * 4 / meter["unit"], unit="q", **options)
