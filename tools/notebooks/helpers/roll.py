# Piano roll: time from left to right, pitch from bottom to top, one bar per note.
# The same view CAMAT uses later for its note tables.
#
# BACKEND chooses how rolls are drawn, as CAMAT's backend="plt" / "bokeh" does:
#   "plt"    a picture, drawn by matplotlib
#   "bokeh"  an interactive plot: drag to move, turn the mouse wheel to zoom,
#            point at a note to see its pitch, times and loudness.

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch, Rectangle

BACKEND = "plt"
TRACK_COLORS = ["#1f77b4", "#d62728", "#9467bd", "#ff7f0e", "#2ca02c", "#8c564b"]
_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_UNITS = {"s": "time (seconds)", "q": "time (quarter notes)"}
_bokeh_loaded = False  # run this cell again after reloading the browser tab


def _pitch_label(p):
    return f"{_NAMES[p % 12]}{p // 12 - 1}"


def _color(n):
    return TRACK_COLORS[n.get("track", 0) % len(TRACK_COLORS)]


# notes: [{"pitch", "start", "end"}], optionally "track" (colour), "role" (legend),
#        "alpha" (opacity) and "velocity" (shown when you point at a note).
# bands: [{"start", "end", "row", "color", "label"}] drawn under the keyboard (pedals).
# bar: draw a line every `bar` time units (for scores: quarter notes per bar).
# backend: "plt" or "bokeh"; None uses BACKEND.
def draw_roll(notes, start=None, end=None, low=None, high=None, bands=(), bar=None,
              unit="s", title=None, width=12, height=None, backend=None):
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
    if height is None:
        height = min(8, max(2.5, 0.12 * (high - low + 2 * len(rows)) + 1))
    backend = (backend or BACKEND).strip().lower()
    if backend == "plt":
        _roll_plt(notes, start, end, low, high, bands, rows, bar, unit, title, width, height)
    elif backend == "bokeh":
        _roll_bokeh(notes, start, end, low, high, bands, rows, bar, unit, title, height)
    else:
        raise ValueError(f"Unknown backend {backend!r}: use 'plt' or 'bokeh'.")


def _roll_plt(notes, start, end, low, high, bands, rows, bar, unit, title, width, height):
    below = 2 * len(rows)
    fig, ax = plt.subplots(figsize=(width, height))
    for p in range(low, high + 1):
        if p % 12 in (1, 3, 6, 8, 10):
            ax.axhspan(p - 0.5, p + 0.5, color="0.93", lw=0, zorder=0)
    shortest = (end - start) / 1500
    rects = [Rectangle((n["start"], n["pitch"] - 0.4), max(n["end"] - n["start"], shortest), 0.8) for n in notes]
    colors = [to_rgba(_color(n), n.get("alpha", 0.9)) for n in notes]
    ax.add_collection(PatchCollection(rects, facecolors=colors, edgecolors="none", zorder=2))
    ticks = [(p, _pitch_label(p)) for p in range(low, high + 1) if p % 12 == 0]
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
    roles = {}
    for n in notes:
        if n.get("role"):
            roles.setdefault(n["role"], _color(n))
    if roles:
        ax.legend(handles=[Patch(color=c, label=r) for r, c in roles.items()], loc="upper left", fontsize=8)
    ax.set_yticks([y for y, _ in ticks], [label for _, label in ticks])
    ax.set_xlim(start, end)
    ax.set_ylim(low - 0.5 - below, high + 0.5)
    ax.set_xlabel(_UNITS.get(unit, unit))
    ax.set_ylabel("pitch")
    ax.grid(axis="y", color="0.85", lw=0.6)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    plt.show()


def _roll_bokeh(notes, start, end, low, high, bands, rows, bar, unit, title, height):
    global _bokeh_loaded
    from bokeh.io import output_notebook, show
    from bokeh.models import ColumnDataSource, FixedTicker, HoverTool, Range1d, Span
    from bokeh.plotting import figure
    from bokeh.resources import INLINE

    if not _bokeh_loaded:
        output_notebook(resources=INLINE, hide_banner=True)  # Bokeh's JavaScript, once per page
        _bokeh_loaded = True
    below = 2 * len(rows)
    fig = figure(
        title=title, height=int(90 * height), sizing_mode="stretch_width",
        x_range=Range1d(start, end, bounds=(start, end)),
        y_range=Range1d(low - 0.5 - below, high + 0.5, bounds=(low - 0.5 - below, high + 0.5)),
        x_axis_label=_UNITS.get(unit, unit), y_axis_label="pitch",
        tools="xpan,xwheel_zoom,box_zoom,reset,save", active_drag="xpan", active_scroll="xwheel_zoom",
    )
    fig.xgrid.grid_line_color = None
    keys = [p for p in range(low, high + 1) if p % 12 in (1, 3, 6, 8, 10)]
    fig.hbar(y=keys, left=start, right=end, height=1, color="black", alpha=0.06)
    if bar:
        t = bar * (start // bar)
        while t <= end:
            fig.add_layout(Span(location=t, dimension="height", line_color="#999999", line_width=1))
            t += bar

    shortest = (end - start) / 1500
    groups = {}
    for n in notes:
        groups.setdefault((n.get("track", 0), n.get("role")), []).append(n)
    for (track, role), group in sorted(groups.items(), key=lambda item: item[0][0]):
        data = {
            "left": [n["start"] for n in group],
            "right": [max(n["end"], n["start"] + shortest) for n in group],
            "bottom": [n["pitch"] - 0.4 for n in group],
            "top": [n["pitch"] + 0.4 for n in group],
            "alpha": [n.get("alpha", 0.9) for n in group],
            "name": [_pitch_label(n["pitch"]) for n in group],
            "start": [n["start"] for n in group],
            "end": [n["end"] for n in group],
        }
        tips = [("pitch", "@name"), ("start", "@start{0.000}"), ("end", "@end{0.000}")]
        if all("velocity" in n for n in group):
            data["velocity"] = [n["velocity"] for n in group]
            tips.append(("velocity", "@velocity"))
        legend = {"legend_label": role} if role else {}
        glyph = fig.quad(source=ColumnDataSource(data), left="left", right="right", bottom="bottom", top="top",
                         fill_color=_color(group[0]), fill_alpha="alpha", line_color=None, **legend)
        fig.add_tools(HoverTool(renderers=[glyph], tooltips=tips))
    if fig.legend:
        fig.legend.location = "top_left"
        fig.legend.click_policy = "hide"  # click a track in the legend to hide it

    ticks = {p: _pitch_label(p) for p in range(low, high + 1) if p % 12 == 0}
    for b in bands:
        y = low - 1.5 - 2 * rows.index(b["row"])
        fig.quad(left=b["start"], right=b["end"], bottom=y - 0.6, top=y + 0.6, color=b["color"], line_color=None)
        ticks[y] = b["label"]
    fig.yaxis.ticker = FixedTicker(ticks=sorted(ticks))
    fig.yaxis.major_label_overrides = ticks
    show(fig)


# Piano roll of a score read by read_score(): time in quarter notes, a line per bar.
def score_roll(result, **options):
    notes = [{"pitch": n["pitch"], "start": n["on"], "end": n["off"]} for n in result["notes"]]
    meter = result.get("meter") or {"count": 4, "unit": 4}
    draw_roll(notes, start=0, bar=meter["count"] * 4 / meter["unit"], unit="q", **options)
