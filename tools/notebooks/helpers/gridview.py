# Demo C: draw the grid, change cells from code (on the web page you click
# them), and read the grid back as notes.

import matplotlib.pyplot as plt
import numpy as np

_EMPTY, _SOUND, _START, _CONT = (1, 1, 1), (0.29, 0.56, 0.85), (0.12, 0.37, 0.66), (0.65, 0.78, 0.93)


# One row per pitch (highest at the top), one column per cell, a line at each bar.
# With onsets: dark = a note starts, light = it continues.
def draw_grid(grid, onsets=False, compact=True):
    rows = grid_rows(grid, compact)
    n = grid["nCols"]
    image = np.ones((len(rows), n, 3))
    for r, p in enumerate(rows):
        for i in range(n):
            if grid["occ"][p][i]:
                image[r, i] = (_START if grid["ons"][p][i] else _CONT) if onsets else _SOUND
    fig, ax = plt.subplots(figsize=(min(14, 1.2 + 0.32 * n), 0.6 + 0.32 * len(rows)))
    ax.imshow(image, aspect="auto", interpolation="nearest")
    if n <= 96:
        for r, p in enumerate(rows):
            for i in range(n):
                value = (2 if onsets and grid["ons"][p][i] else 1) if grid["occ"][p][i] else 0
                ax.text(i, r, value, ha="center", va="center", fontsize=8,
                        color="white" if grid["occ"][p][i] else "0.6")
    for x in np.arange(-0.5, n, 1):
        ax.axvline(x, color="0.85", lw=0.5)
    for b in range(0, n + 1, grid["barCells"]):
        ax.axvline(b - 0.5, color="black", lw=1.5)
    ax.set_yticks(range(len(rows)), [pitch_name(p) for p in rows])
    bars = n // grid["barCells"]
    ax.set_xticks([b * grid["barCells"] + (grid["barCells"] - 1) / 2 for b in range(bars)], [f"bar {b + 1}" for b in range(bars)])
    ax.tick_params(length=0)
    fig.tight_layout()
    plt.show()


# Change one cell, as a click on the web page does. Cells count from 1.
# value: 0 (silent), 1 (sounding) or 2 (sounding, and a note starts here; "start" works too).
def set_cell(grid, name, cell, value):
    pitch = parse_pitch(name)
    if pitch is None:
        raise ValueError(f"{name!r} is not a pitch: write for example G4, F#4 or Bb3")
    if not 1 <= cell <= grid["nCols"]:
        raise ValueError(f"The grid has cells 1 to {grid['nCols']}")
    for p in range(min(pitch, grid["low"]), max(pitch, grid["high"]) + 1):
        grid["occ"].setdefault(p, [0] * grid["nCols"])
        grid["ons"].setdefault(p, [0] * grid["nCols"])
    grid["low"] = min(grid["low"], pitch)
    grid["high"] = max(grid["high"], pitch)
    i = cell - 1
    if value == 0:
        grid["occ"][pitch][i] = grid["ons"][pitch][i] = 0
    elif value in (2, "start"):
        grid["occ"][pitch][i] = grid["ons"][pitch][i] = 1
    else:
        grid["occ"][pitch][i] = 1
        grid["ons"][pitch][i] = 0 if i > 0 and grid["occ"][pitch][i - 1] else 1


# Grid -> events -> notes and **kern, compared with the melody we started from.
def round_trip(source, grid, onsets=False):
    events = grid_to_events(grid, onsets=onsets)
    kern = events_to_kern(events, grid)
    back = events_to_notes(events, grid["res"])
    cmp = compare_notes(source["notes"], back)
    n = len(source["notes"])
    print(f"The melody has {n} notes. Read back from the grid: {len(back)} notes, {cmp['kept']} of them unchanged.")
    if grid["lost"]:
        names = ", ".join(pitch_name(x["pitch"]) for x in grid["lost"])
        print(f"{len(grid['lost'])} note(s) start and end inside one cell and disappear: {names}. Try a smaller cell.")
    if cmp["kept"] == n and len(back) == n:
        print("Nothing lost: the round trip gives back the same notes.")
    elif not onsets:
        print("Repeated notes of the same pitch merge into one long note. Use onsets=True to keep them apart.")
    render("humdrum", kern, scale=30, header="none")
    return kern
