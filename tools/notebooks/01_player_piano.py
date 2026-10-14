# %% [markdown]
# # Demo A: Debussy plays *Children's Corner*
#
# Session 1, *Why encode music?*, part 5. The same demo runs on the course page; here you can change the inputs and keep your work.
#
# Debussy recorded *Children's Corner* himself for the Welte-Mignon reproducing piano (roll 2733). Stanford's SUPRA archive scanned the roll (see it in [Stanford's viewer](https://purl.stanford.edu/dc920rk8870)) and turned the scan into two MIDI files:
#
# - **raw:** every hole in the paper becomes an event, in 4 tracks: bass and treble notes, and two tracks of expression holes that control loudness;
# - **expressive:** holes merged into notes, and the expression holes turned into loudness and pedalling.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. Cells marked *Try this* have values you can change; change them and run the cell again.

# %% [markdown]
# ## Setup
#
# The first cell installs what the notebook needs; run it once after each server start. The second cell defines helper functions; it is collapsed because you do not need to read it. The third cell chooses how piano rolls are drawn.

# %% install
%pip install -q verovio==6.3.0 mido matplotlib ipywidgets bokeh

# %% helpers: roll midi ui

# %%
# Try this: "bokeh" draws interactive piano rolls: drag to move, turn the mouse wheel to zoom,
# point at a note to see its pitch, times and loudness. "plt" (matplotlib) draws pictures.
BACKEND = "plt"

# %% [markdown]
# ## 1. Download the two MIDI files
#
# The files come from SUPRA's GitHub repository each time you run this cell (about 330 KB together).

# %%
EXP_URL = "https://raw.githubusercontent.com/pianoroll/SUPRA/master/welte-red/midi-exp/dc920rk8870_exp.mid"
RAW_URL = "https://raw.githubusercontent.com/pianoroll/SUPRA/master/welte-red/midi-raw/dc920rk8870_raw.mid"

rolls = {"raw": load_midi(RAW_URL), "exp": load_midi(EXP_URL)}

for version, midi in rolls.items():
    notes = roll_notes(midi, version)
    kind = "hole events" if version == "raw" else "notes"
    print(f"{version}: {len(notes):,} {kind}, {midi['duration']:.0f} seconds")
    for track in midi["tracks"]:
        if track["index"] in ROLES[version]:
            print(f"   track {track['index']}: {len(track['notes']):6,} {ROLES[version][track['index']][0]}")

# %% [markdown]
# ## 2. The same seconds in both files
#
# A piano roll shows time from left to right and pitch from bottom to top. In the raw file, the expression holes lie outside the piano's range (below the lowest and above the highest note). In the expressive file, the shade of a note is its loudness (the MIDI velocity, decoded from the expression holes): pale notes are soft, solid ones loud. The bands under the roll show the pedals.

# %%
def show_window(version="exp", start=4, length=20, backend=None):
    midi = rolls[version]
    notes = [n for n in roll_notes(midi, version) if n["end"] >= start and n["start"] <= start + length]
    if version == "raw":
        draw_roll(notes, start=start, end=start + length, low=14, high=114, backend=backend,
                  title=f"raw: {len(notes):,} hole events in this window")
    else:
        draw_roll(notes, start=start, end=start + length, low=21, high=108, bands=pedal_bands(midi), backend=backend,
                  title=f"expressive: {len(notes):,} notes in this window (pale = soft, solid = loud)")


# Try this: another start time (in seconds) or a shorter window.
START = 4
LENGTH = 20
show_window("raw", START, LENGTH)
show_window("exp", START, LENGTH)

# %% [markdown]
# ## 3. One note, two files
#
# A long note on the roll is punched as a chain of short holes. The expressive file joins the chain into one note. Here is the C3 (MIDI pitch 48) that starts at about 5.1 seconds:

# %%
C3 = 48
for version in ["raw", "exp"]:
    for n in roll_notes(rolls[version], version):
        if n["pitch"] == C3 and 5.0 <= n["start"] <= 5.4:
            print(f"{version}: C3 from {n['start']:.3f} s to {n['end']:.3f} s, {n['end'] - n['start']:.3f} s long")

# %%
show_window("raw", 4.8, 3.6)
show_window("exp", 4.8, 3.6)

# %% [markdown]
# ## 4. Listen
#
# A very plain synthesiser plays the window: enough to hear rhythm, chords and dynamics, but it is not a piano. The raw version plays only the note holes, all equally loud: the expression holes are not notes. `speed` works as on the course page: 0.5 plays the window at half speed.

# %%
from IPython.display import Audio, display


def listen(version="exp", start=4, length=20, speed=1.0):
    notes = roll_notes(rolls[version], version)
    if version == "raw":
        notes = [n for n in notes if n["track"] < 2]  # bass and treble holes only
    return Audio(synth(notes, start, length, dynamics=version == "exp", speed=speed), rate=22050)


# Try this: 0.5 for half speed, 2 for double speed.
SPEED = 1.0
print("Expressive:")
display(listen("exp", START, LENGTH, SPEED))
print("Raw:")
display(listen("raw", START, LENGTH, SPEED))

# %% [markdown]
# ## 5. Explore with sliders
#
# The same controls as on the course page: version, start, window length and speed. Each change draws the window again and makes a new sound for it (for windows of up to 60 seconds of playing time). If the sliders do not appear, the cell says what to do.
#
# The sliders always draw with matplotlib: a Bokeh plot cannot be drawn inside them. For an interactive plot of a window, write for example `show_window("exp", 30, 40, backend="bokeh")` in a new cell.

# %%
import ipywidgets as widgets


def explore(version="exp", start=4, length=20, speed=1.0):
    show_window(version, start, length, backend="plt")
    if length / speed <= 60:
        display(listen(version, start, length, speed))
    else:
        print(f"No sound for more than 60 s of playing time ({length / speed:.0f} s here): "
              "choose a shorter window or a higher speed.")


controls = widgets.interactive(
    explore,
    version=widgets.Dropdown(options=[("expressive", "exp"), ("raw", "raw")], value="exp"),
    start=widgets.FloatSlider(min=0, max=740, step=0.5, value=4, continuous_update=False),
    length=widgets.Dropdown(options=[5, 10, 20, 40, 80, 160], value=20),
    speed=widgets.SelectionSlider(options=[0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0], value=1.0),
)
show_controls(controls, 'explore("exp", start=4, length=20, speed=1.0)')

# %% [markdown]
# ## 6. A roll as a table
#
# For a computer, the piano roll is a table: one row per note, with pitch, start, end and loudness. This is the form CAMAT works with later in the course, there with bars and beats from a score instead of seconds.

# %%
notes_exp = roll_notes(rolls["exp"], "exp")
print(f"{'pitch':>5}  {'start (s)':>9}  {'end (s)':>8}  {'velocity':>8}  track")
for n in notes_exp[:12]:
    print(f"{n['pitch']:>5}  {n['start']:>9.3f}  {n['end']:>8.3f}  {n['velocity']:>8}  {n['role']}")

# %% [markdown]
# ## Questions
#
# - Is a roll a score, a recording or a program?
# - Where are the bar lines and the quarter notes?
# - What is a "note" when 33,508 holes become 6,031 notes?
#
# ## Source and licence
#
# MIDI files: SUPRA, Stanford University Piano Roll Archive, roll `dc920rk8870`, licensed [CC BY-NC-SA 4.0](https://github.com/pianoroll/SUPRA). Cite: Zhengshan Shi, Craig Stuart Sapp, Kumaran Arul, Jerry McBride and Julius O. Smith III, "SUPRA: Digitizing the Stanford University Piano Roll Archive", *ISMIR 2019*. The notebook downloads the files when you run it; they are not part of the course materials.
