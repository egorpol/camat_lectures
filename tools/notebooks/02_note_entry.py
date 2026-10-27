# %% [markdown]
# # Typing the notes
#
# Session 2, *The source and the notes*, part 5.
#
# Besides OMR, the other way to get notes into the computer is to type them. You type the bass (left hand) of the pickup and bar 1 of Schumann's *Fröhlicher Landmann*, as in the first system of page 8:
#
# - pickup: C3, eighth
# - bar 1: F3 dotted quarter, A3 eighth, C4 dotted quarter, F3 eighth
#
# The piece is in F major (one flat), in common time, in the bass clef. Middle C is C4.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. Edit the text between the triple quotes `"""` and run the cell again. Everyone does part 1; part 2 is an extension.

# %% [markdown]
# ## Setup
#
# The first cell makes sure Verovio is installed; after the setup it already is, so the cell finishes quickly. The second cell defines helper functions; it is collapsed because you do not need to read it.

# %% install
%pip install -q verovio==6.3.0

# %% helpers: mei grid checks vrv note_entry

# %% [markdown]
# ## 1. Type bar 1 in ABC
#
# ABC is the format from session 1. The text below has the header and the pickup already. Type bar 1 after the bar line `|`, end with `|]`, and run the cell. Three things you need:
#
# - `L:1/8` makes the eighth note the unit: `G,` is an eighth, `G,2` a quarter, `G,3` a dotted quarter.
# - A comma puts a note one octave lower: `C` is C4 (middle C), `C,` is C3.
# - `|` is a bar line; `|]` ends the piece.
#
# Under the score, *Verovio reads* lists the notes in words. Compare them with the list above, and the score with the print: pitches and octaves, rhythm, pickup, clef and key. The same box is on the course page, part 5.

# %%
abc = """X:1
T:Fröhlicher Landmann, left hand
M:C
L:1/8
K:F clef=bass
% The pickup is given. Type bar 1 after the bar line and end with |]
C, |
"""
abc_result = render("abc", abc)
print_bars(abc_result)

# %% [markdown]
# Then let the computer compare your notes with the print:

# %%
check_bass("ABC", abc_result)

# %% [markdown]
# <details><summary>Solution</summary>
#
# ```
# C, | F,3 A, C3 F, |]
# ```
#
# </details>
#
# Now think about the whole piece: 21 bars on two staves, with chords in the right hand. What does an existing encoding save you, and what does it not?

# %% [markdown]
# ## 2. Extension: the same notes in other formats
#
# The same five notes in three more text formats, and in a notation program. Run each cell and compare: every format should give the same notes. At the end, one cell checks them all.
#
# ### Plaine & Easie
#
# A short format for melodies, used by library catalogues for incipits (the first notes of a piece). `@clef:F-4` is the bass clef, `@keysig:bB` one flat, `@timesig:4/4` common time. In the notes, `,` sets octave 3 and `'` octave 4; `8` is an eighth, `4.` a dotted quarter. `/` is a bar line.

# %%
pae = """@clef:F-4
@keysig:bB
@timesig:4/4
@data:,8C/4.F8A'4.C,8F//
"""
pae_result = render("pae", pae)
print_bars(pae_result)

# %% [markdown]
# ### MEI, written by hand
#
# MEI spells out each note with attributes: `pname` (pitch name), `oct` (octave), `dur` (8 = eighth, 4 = quarter) and `dots`. The pickup bar has `metcon="false"`: it is shorter than the time signature says. Each `xml:id` names one note or bar; these belong to this small exercise only. This is the format of our edition. You can also paste the text into [mei-friend](https://mei-friend.mdw.ac.at/) and edit it there.

# %%
mei = """<?xml version="1.0" encoding="UTF-8"?>
<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.1">
  <meiHead>
    <fileDesc>
      <titleStmt>
        <title>Fröhlicher Landmann, left hand</title>
        <composer>Robert Schumann</composer>
      </titleStmt>
      <pubStmt/>
    </fileDesc>
  </meiHead>
  <music><body><mdiv><score>
    <scoreDef meter.count="4" meter.unit="4" keysig="1f">
      <staffGrp><staffDef n="1" lines="5" clef.shape="F" clef.line="4"/></staffGrp>
    </scoreDef>
    <section>
      <measure n="0" xml:id="entry-pickup" metcon="false">
        <staff n="1"><layer n="1">
          <note xml:id="entry-c3" pname="c" oct="3" dur="8"/>
        </layer></staff>
      </measure>
      <measure n="1" xml:id="entry-bar1">
        <staff n="1"><layer n="1">
          <note xml:id="entry-f3a" pname="f" oct="3" dur="4" dots="1"/>
          <note xml:id="entry-a3" pname="a" oct="3" dur="8"/>
          <note xml:id="entry-c4" pname="c" oct="4" dur="4" dots="1"/>
          <note xml:id="entry-f3b" pname="f" oct="3" dur="8"/>
        </layer></staff>
      </measure>
    </section>
  </score></mdiv></body></music>
</mei>
"""
mei_result = render("mei", mei)
print_bars(mei_result)

# %% [markdown]
# ### Humdrum `**kern`
#
# The format for music analysis from session 1. One line per note: `8C` is C3, an eighth; `4.F` is F3, a dotted quarter; `4.c` is C4. `=1` is the bar line before bar 1.

# %%
kern = """!!!OTL: Fröhlicher Landmann, left hand
**kern
*clefF4
*k[b-]
*M4/4
8C
=1
4.F
8A
4.c
8F
==
*-
"""
kern_result = render("humdrum", kern)
print_bars(kern_result)

# %% [markdown]
# ### Compare them all

# %%
for name, result in {"ABC": abc_result, "Plaine & Easie": pae_result,
                     "MEI": mei_result, "kern": kern_result}.items():
    check_bass(name, result)

# %% [markdown]
# ### MuseScore
#
# If you have [MuseScore](https://musescore.org) 4.2 or newer: create a score for one bass-clef staff in F major, 4/4, with an eighth-note pickup ([how to make a pickup bar](https://handbook.musescore.org/notation/rhythm-meter-and-measures/pickup-and-non-metered-measures)). Enter the five notes. Then choose **File → Export → MEI** ([exporting](https://handbook.musescore.org/file-management/file-export)). Open the exported file in [mei-friend](https://mei-friend.mdw.ac.at/), or paste it into the MEI cell above, and check pitches, rhythm, clef, key and pickup.
#
# A notation program is a good way to enter many notes. Once an edition has links to the scan and editorial notes, though, we edit its MEI directly: a round trip through a notation program can lose them.

# %% [markdown]
# ### Keep your text (optional)
#
# Set `SAVE = True` to save the text of one format, and the MEI Verovio made of it, into a new folder next to this notebook. It never overwrites a file: for a second try, choose another folder name.

# %%
from pathlib import Path

SAVE = False
CHOSEN = "abc"  # "abc", "pae", "mei" or "kern"
FOLDER = Path.cwd() / "schumann_note_entry_work/attempt-01"

if SAVE:
    text, result = {"abc": (abc, abc_result), "pae": (pae, pae_result),
                    "mei": (mei, mei_result), "kern": (kern, kern_result)}[CHOSEN]
    if not result["ok"]:
        raise ValueError("Verovio could not read this text; fix it before saving.")
    FOLDER.mkdir(parents=True, exist_ok=False)
    extension = {"kern": "krn"}.get(CHOSEN, CHOSEN)
    (FOLDER / f"input.{extension}").write_text(text, encoding="utf-8")
    (FOLDER / "verovio.mei").write_text(result["mei"], encoding="utf-8")
    print("Saved in", FOLDER)
else:
    print("Off. Set SAVE = True to keep your text.")

# %% [markdown]
# ### Other ways in
#
# - **mei-friend** imports MusicXML, Humdrum, ABC and Plaine & Easie (menu *File*) and shows the result as MEI.
# - **A MIDI keyboard** can enter notes into a notation program, one at a time.
# - **A language model** can draft ABC or MEI. Check its result as in session 1: the notes, their octaves and lengths, and the pickup.
#
# More about the formats: [Verovio's input formats](https://book.verovio.org/toolkit-reference/input-formats.html), [MEI in MuseScore](https://music-encoding.org/musescore-doc/).
