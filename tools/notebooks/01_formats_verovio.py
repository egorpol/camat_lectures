# %% [markdown]
# # Seven encodings in Verovio, and an LLM writes ABC
#
# Session 1, *Why encode music?*, parts 8 and 10 (Demos B and D). The same demos run on the course page; here you can change the inputs and keep your work.
#
# [Verovio](https://www.verovio.org) reads many text encodings of music and renders them as notation. We give it the first bars of *Alle meine Entchen* in six encodings, plus a chant fragment, and then check a melody written by a language model.
#
# **How to use this notebook:** run the cells from top to bottom with Shift+Enter. Edit the text between the triple quotes `"""` and run the cell again. If something goes wrong, the message appears under the cell; the notebook keeps running.

# %% [markdown]
# ## Setup
#
# The first cell installs what the notebook needs; run it once after each server start. The second cell defines helper functions; it is collapsed because you do not need to read it.

# %% install
%pip install -q verovio==6.3.0 mido matplotlib ipywidgets bokeh

# %% helpers: mei grid checks vrv roll answers

# %% [markdown]
# A rendered score under the next cell is the sign that everything works.

# %%
abc = """X:1
T:Alle meine Entchen
M:4/4
L:1/4
K:C
C D E F | G2 G2 | A A A A | G4 |]
"""
result = render("abc", abc)
print("Verovio", result.get("version", "did not run"))

# %% [markdown]
# ## Part 1: one melody, seven encodings
#
# `render(format, text)` gives the text to Verovio and shows the score with any messages. The format names are Verovio's own (its `inputFrom` option).
#
# ### ABC
#
# Letters for pitches, numbers for lengths relative to the unit `L:`. Lower case is the octave above: `c` is one octave above `C`. A sharp is `^F`, a flat `_B`.

# %%
abc = """X:1
T:Alle meine Entchen
M:4/4
L:1/4
K:C
C D E F | G2 G2 | A A A A | G4 |]
"""
result = render("abc", abc)

# %% [markdown]
# ### Humdrum `**kern`
#
# One line per event, one column ("spine") per voice, separated by tabs. The number before the pitch is the duration: 4 = quarter note, 2 = half note, 1 = whole note. `c` is middle C, `cc` the octave above, `C` the octave below. A sharp is `#`, a flat `-`.

# %%
kern = """!!!OTL: Alle meine Entchen
**kern
*clefG2
*k[]
*M4/4
=1
4c
4d
4e
4f
=2
2g
2g
=3
4a
4a
4a
4a
=4
1g
==
*-
"""
result = render("humdrum", kern)

# %% [markdown]
# ### Plaine & Easie
#
# Made in 1964 for incipits typed on a typewriter; RISM still uses it. A duration (`4`) stays in force until the next one; `'` sets the octave; `/` is a bar line.

# %%
pae = """@clef:G-2
@keysig:
@timesig:4/4
@data:'4CDEF/2GG/4AAAA/1G//
"""
result = render("pae", pae)

# %% [markdown]
# ### EsAC
#
# The Essen folksong format: pitches as scale degrees (1 = the key note), `_` lengthens a note. Verovio needs the collection line (`DEMO01`) before `CUT[...]`, and prints two harmless warnings.

# %%
esac = """DEMO01
CUT[Alle meine Entchen]
REG[Europa, Mitteleuropa, Deutschland]
KEY[X0001 04 C 4/4]
MEL[1234 5_5_ 6666 5__ //]
>>
"""
result = render("esac", esac)

# %% [markdown]
# ### MusicXML
#
# XML for exchange between notation programs. Durations count in `<divisions>` per quarter note.

# %%
musicxml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <work><work-title>Alle meine Entchen</work-title></work>
  <part-list><score-part id="P1"><part-name>Voice</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions><key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <clef><sign>G</sign><line>2</line></clef></attributes>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>D</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>E</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>F</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
    </measure>
    <measure number="2">
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>2</duration><type>half</type></note>
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>2</duration><type>half</type></note>
    </measure>
    <measure number="3">
      <note><pitch><step>A</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>A</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>A</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>A</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
    </measure>
    <measure number="4">
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>4</duration><type>whole</type></note>
      <barline location="right"><bar-style>light-heavy</bar-style></barline>
    </measure>
  </part>
</score-partwise>
"""
result = render("xml", musicxml)

# %% [markdown]
# ### MEI
#
# The format of digital editions. Verovio converts every format it reads into MEI internally, and `result["mei"]` gives that MEI back. Here we take the MEI made from the kern version, print the part with the notes and render it. Every element has an `xml:id`, so other files can point at a single note.

# %%
mei = read_score("humdrum", kern, svg=False)["mei"]
start = mei.index("<section")
print(mei[start:start + 1500], "…")
result = render("mei", mei)

# %% [markdown]
# ### GABC (chant, extra)
#
# Gregorian chant: the syllables of the text, each with its neumes in brackets. Letters are positions on the staff, not pitches.

# %%
gabc = """(c4) Al(f)le(g)lu(h)ia.(hg) (::)
"""
result = render("gabc", gabc)

# %% [markdown]
# ### Sizes and piano rolls
#
# The same four bars take very different amounts of text. And whatever the format, Verovio reads the same notes: the piano roll shows time × pitch, the view from Demo A.

# %%
encodings = {"ABC": abc, "kern": kern, "Plaine & Easie": pae, "EsAC": esac, "MusicXML": musicxml, "MEI": mei}
for name, text in encodings.items():
    print(f"{name:15} {len(text.encode('utf-8')):6,} bytes")

# %%
# Try this: add backend="bokeh" for an interactive roll (drag to move, wheel to zoom, point at a note).
score_roll(read_score("abc", abc, svg=False), title="ABC", height=2.5)
score_roll(read_score("esac", esac, svg=False), title="EsAC", height=2.5)

# %% [markdown]
# ### Try this
#
# 1. Change a note in the ABC and in the kern version above. Add a sharp (`^F` in ABC, `f#` in kern).
# 2. Change the metre to 3/4 (`M:3/4` in ABC, `*M3/4` in kern). What does Verovio do with bars that no longer fit?
# 3. Compare what each format records beyond the notes: the phrase brackets in EsAC, the spines in kern, `<divisions>` in MusicXML, the header and the `xml:id` of every element in MEI.
# 4. Break the syntax on purpose and read the message under the score.
#
# Your own melody (homework 2): encode the first phrase of a melody of your choice here.

# %%
mine = """X:1
T:My melody
M:4/4
L:1/4
K:C
C D E F | G4 |]
"""
result = render("abc", mine)

# %% [markdown]
# ### When the input is broken
#
# Some broken inputs make Verovio 6.3 crash instead of reporting an error. The helper checks for the known cases first, and it runs Verovio in a separate process, so a crash cannot take the notebook down with it. The first three inputs below would crash Verovio. The last one, Plaine & Easie without its `@data:` key, Verovio rejects itself, and its log says why (lines starting with `Verovio:`).

# %%
broken = [
    ("abc", "T:No X line\nK:C\nCDEF|"),
    ("abc", "X:1\nK:C\nCD]EF|"),
    ("humdrum", "**kern\t**kern\n4c\t4e\n4d\n*-\t*-"),
    ("pae", "@clef:G-2\n'4CDEF/2GG//"),
]
for fmt, text in broken:
    print(f"--- {fmt}: {text!r}")
    render(fmt, text)
    print()

# %% [markdown]
# ## Part 2: an LLM writes ABC
#
# We asked a language model for a melody and check the answer. Because the answer is an encoding, we can test it, which a picture of a score would not allow.
#
# The prompt, and the follow-up asking for the same melody in kern:

# %%
PROMPT_ABC = ("Write a short melody in ABC notation: 8 bars in 3/4 time, in D major, using only quarter notes, "
              "half notes, dotted half notes and eighth notes. Keep it between D4 and D5 and end on D. "
              "Reply with the ABC only.")
PROMPT_KERN = "Now write the same melody in Humdrum **kern. Reply with the kern only."
print(PROMPT_ABC)
print(PROMPT_KERN)

# %% [markdown]
# What the prompt asks for. If you change the prompt, change this too. `fifths` is the key signature: the number of sharps, or minus the number of flats (D major: 2).

# %%
SPEC = {"meter": "3/4", "bars": 8, "fifths": 2, "low": "D4", "high": "D5", "final": "D"}

# %% [markdown]
# ### Recorded answers
#
# Claude Opus 5.5 (Anthropic) answered both prompts on 2026-10-14, while the course page was built. The answers are not edited.

# %%
claude_abc = """X:1
T:Morning in D
M:3/4
L:1/8
K:D
D2 F2 A2 | d4 c2 | B2 A2 F2 | A6 |
G2 B2 d2 | c2 A2 F2 | E2 F2 E2 | D6 |]
"""
result = check_answer("abc", claude_abc, SPEC)

# %%
claude_kern = """**kern
*clefG2
*k[f#c#]
*M3/4
=1
4d
4f#
4a
=2
2dd
4cc#
=3
4b
4a
4f#
=4
2.a
=5
4g
4b
4dd
=6
4cc#
4a
4f#
=7
4e
4f#
4e
=8
2.d
==
*-
"""
result = check_answer("humdrum", claude_kern, SPEC)

# %% [markdown]
# This one was written by hand to show what the checks catch. It is not an LLM answer. Note the Markdown code fence around it: LLMs often answer that way, and `check_answer` removes the fence.

# %%
constructed = """```abc
X:1
T:Waltz in D
M:3/4
L:1/8
K:G
D2 F2 A2 | d3 c B2 A | B2 A2 F2 | A6 |
G2 B2 d2 | e2 c2 A2 | F2 E2 | D6 |]
```
"""
result = check_answer("abc", constructed, SPEC)

# %% [markdown]
# ### Your turn
#
# Paste an answer between the triple quotes and run the cell. For a kern answer, write `"humdrum"` instead of `"abc"`.
#
# *Does every bar add up to the metre? Does Verovio warn? Are the key and the range what was asked for? Is the kern valid at all?* The checks rely on how Verovio reads the text: Verovio 6.3, for example, ignores a length written after a chord (`[DFA]2`), and the helper warns when it sees one.

# %%
answer = """
"""
result = check_answer("abc", answer, SPEC)
