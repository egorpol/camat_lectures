# %% [markdown]
# # Demo C: a melody as a binary grid
#
# Session 1, *Why encode music?*, part 9. The same demo runs on the course page; here you can change the inputs and keep your work.
#
# A perforation is binary: there is a hole at a position, or there is not. The raw piano roll in Demo A is exactly that. The same idea turns a melody into a grid with one row per pitch and one column per time step: 1 = the pitch sounds, 0 = it does not. We go from the melody to the grid and back, and see what survives.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. Change the values in the cells marked *Try this* and run them again.

# %% [markdown]
# ## Setup
#
# The first cell installs what the notebook needs; run it once after each server start. The second cell defines helper functions; it is collapsed because you do not need to read it.

# %% install
%pip install -q verovio==6.3.0 mido matplotlib ipywidgets

# %% helpers: mei grid checks vrv roll gridview ui

# %% [markdown]
# ## 1. The melody
#
# *Alle meine Entchen* in ABC. Verovio reads it; `source["notes"]` is the list of notes it found, with start (`on`) and end (`off`) in quarter notes.

# %%
melody = """X:1
T:Alle meine Entchen
M:4/4
L:1/4
K:C
C D E F | G2 G2 | A A A A | G4 |]
"""
source = render("abc", melody, scale=30, header="none")
for n in source["notes"]:
    print(f"{pitch_name(n['pitch']):4} from {n['on']:>4} to {n['off']:>4}")

# %% [markdown]
# ## 2. The grid
#
# `RES` is the number of cells per quarter note: 1 = one cell per quarter note, 2 = per eighth note, 4 = per sixteenth note. A note fills every cell whose start lies inside the note.

# %%
RES = 1  # Try this: 2 or 4
grid = to_grid(source["notes"], RES, source["meter"])
draw_grid(grid)
print(grid_to_text(grid))

# %% [markdown]
# *Which bars can you no longer tell apart?*
#
# ## 3. Back from the grid to notes
#
# Reading the grid back, a new note starts wherever the set of sounding pitches changes. So a run of 1s in one row is read as one held note, the way a roll is read (a long note on a roll is a chain of short holes): `1111` comes back as a whole note. The helper writes the result as `**kern`, renders it, and compares it with the melody.

# %%
kern = round_trip(source, grid)
print(kern)

# %% [markdown]
# Bars 2 (two half notes), 3 (four quarter notes) and 4 (one whole note) all become a run of four cells. Pure occupancy loses where one note ends and the next begins.
#
# Why not read every 1 as a new note? That would give four quarter notes: right for bar 3, wrong for bars 2 and 4, and with `RES = 4` every note would come back as sixteenths. Without onsets, no rule gets all three bars right.
#
# ## 4. A second grid for onsets
#
# One fix: keep a second grid that marks where notes start. In the picture, dark cells are note starts and light cells are continuations.
#
# The two grids together are one grid with three values: **0** = silence, **1** = a note continues, **2** = a note starts. Two yes/no grids would allow four combinations, but "a note starts where nothing sounds" cannot happen, so three are left: the grid is no longer binary but *ternary*. Every cell that is not 0 still means "sounding", so a tool written for the 0/1 grid can read it too. The last block printed below is this ternary grid.

# %%
draw_grid(grid, onsets=True)
print(grid_to_text(grid, onsets=True))
kern = round_trip(source, grid, onsets=True)

# %% [markdown]
# ## 5. Resolution is a choice
#
# A melody with eighth notes. With one cell per quarter note, a note that starts and ends inside one cell covers no cell start, and it disappears. Finer grids keep more, but cost size: CAMAT's default cell is a sixteenth note.

# %%
melody2 = """X:1
T:With eighth notes
M:4/4
L:1/8
K:C
C D E F G2 G2 | A A A A G4 |]
"""
source2 = render("abc", melody2, scale=30, header="none")

for res in [1, 2]:  # Try this: add 4
    print(f"--- {res} cell(s) per quarter note")
    grid2 = to_grid(source2["notes"], res, source2["meter"])
    draw_grid(grid2, onsets=True)
    round_trip(source2, grid2, onsets=True)

# %% [markdown]
# ## 6. Change the grid
#
# On the course page you click cells; here you call `set_cell(grid, pitch, cell, value)`. Cells count from 1; with one cell per quarter note, bar 2 is cells 5 to 8. The value is `0` (silent), `1` (sounding) or `2` (sounding, and a note starts here): the three values of the ternary grid.

# %%
grid = to_grid(source["notes"], 1, source["meter"])
set_cell(grid, "G4", 8, 0)      # shorten the second G in bar 2
set_cell(grid, "B4", 13, 1)     # add a B4 at the start of bar 4
set_cell(grid, "G4", 13, 0)
draw_grid(grid)
kern = round_trip(source, grid)

# %% [markdown]
# **Try this:** turn bar 3 (cells 9 to 12) into two half notes on A4. A `1` in a cell right after a sounding cell continues the note instead of starting a new one.

# %%
grid = to_grid(source["notes"], 1, source["meter"])
# your set_cell(...) lines here
draw_grid(grid, onsets=True)
kern = round_trip(source, grid, onsets=True)

# %% [markdown]
# ## 7. Explore with controls
#
# Change the melody in part 1, then choose the cell size and whether to keep onsets. If the controls do not appear, the cell says what to do.

# %%
import ipywidgets as widgets

def explore(res=1, onsets=False):
    g = to_grid(source["notes"], res, source["meter"])
    draw_grid(g, onsets=onsets)
    round_trip(source, g, onsets=onsets)

controls = widgets.interactive(
    explore,
    res=widgets.Dropdown(options=[("quarter note", 1), ("eighth note", 2), ("sixteenth note", 4)], value=1, description="cell"),
    onsets=widgets.Checkbox(value=False, description="keep an onset grid"),
)
show_controls(controls, "explore(res=2, onsets=True)")

# %% [markdown]
# ## Questions
#
# - What does the grid record, and what does it leave out?
# - What would you need to keep, next to the grid, to get the melody back exactly? CAMAT keeps a note table next to its grids, with identifiers that point back into the score.
