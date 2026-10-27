# Get the notes: several entry routes to MEI

For Session 2, minutes **30–45**. Use the [note-entry notebook](../notebooks/02_note_entry.ipynb)
for the editable ABC, Plaine & Easie, MEI and optional Humdrum examples.
The [executed reference](references/02_note_entry_recorded.ipynb) shows their results.
Sources and tool behaviour checked **25 October 2026**.

## One short musical task, a choice of input methods

Enter the **bass melody only**: pickup **C3 eighth**, then **F3 dotted quarter,
A3 eighth, C4 dotted quarter, F3 eighth**. Middle C is C4. This comes from
IMSLP 51556, printed p. 8, first system. The pickup lasts half a quarter-note
unit; the first full bar lasts four. The final F3 follows this print; the
reused sample MEI's inherited A3 was corrected in the teaching derivatives.

This small reduction lets everyone compare the same music. Students who finish
early can add the upper staff using the existing [manual-entry scaffold](../examples/schumann/manual-entry.mei).
The five-note examples omit accompaniment and expression deliberately; they
are not replacements for the whole-piece starter.

## The fifteen-minute sequence

1. **30–32: show the choices.** Demonstrate MuseScore's export and the tiny ABC
   input side by side. Name Plaine & Easie and direct MEI as alternatives.
2. **32–39: choose one route per pair.** Most students can use MuseScore;
   students recalling Session 1 can type ABC or PAE; others edit the MEI scaffold.
   Arrange a neighbouring pair using a different route. Avoid asking everyone
   to install or learn several editors during this block.
3. **39–42: compare the imported music.** Check the five pitches, octaves,
   written durations, key, clef and pickup. Compare different measure labels
   by their content. Generated IDs and layout need not match.
4. **42–45: return to the shared starter.** Locate the same bar in its two-staff
   context, identify two missing expressive features and choose the canonical
   MEI for the subsequent facsimile exercise.

## MuseScore: direct MEI export, with MusicXML as a second route

Create one bass-clef staff, key F major, 4/4, and an eighth-note pickup; enter
the five notes and retain the `.mscz` original. In the New Score dialog,
the Measures settings offer **Create pickup measure**; its actual length is
one eighth while the prevailing metre remains 4/4. See the
[pickup instructions](https://handbook.musescore.org/notation/rhythm-meter-and-measures/pickup-and-non-metered-measures).

Use **File → Export → MEI** if offered by the installed version. MuseScore's
MEI support, available since 4.2, targets **MEI Basic** for notation interchange.
Open the export in mei-friend and check it. Record the version/profile actually
written; do not assume every editor exports the workshop's MEI 5.1 target.
[MEI in MuseScore](https://music-encoding.org/musescore-doc/),
[export instructions](https://handbook.musescore.org/file-management/file-export).

As a comparison or fallback, export uncompressed **MusicXML**, then import into
mei-friend or run:

```sh
camat-convert --source input.musicxml --output-dir imported --mei-version 5.1
```

The notebook's text routes and this GUI route converge on musical MEI. Once
the edition has annotations, facsimile links and stable IDs, edit its MEI
directly. Interchange support does not imply that an editor will preserve
all editorial information through a round trip.

## ABC and Plaine & Easie: reuse Session 1

ABC input for the same melody:

```abc
X:1
T:Schumann Op.68 No.10 — bass entry exercise
M:4/4
L:1/8
K:F clef=bass
C, | F,3 A, C3 F, |]
```

Plaine & Easie input:

```text
@clef:F-4
@keysig:bB
@timesig:4/4
@data:,8C/4.F8A'4.C,8F//
```

The notebook renders each input with Verovio and inspects the resulting MEI.
For a browser route, mei-friend's **File → Import PAE, ABC** imports these
formats; **Save MEI** saves the result. Its menu also imports MusicXML and
Humdrum. [mei-friend](https://mei-friend.mdw.ac.at/).

PAE is suited to this short incipit. Verovio's documented ABC importer lacks
multivoice and tuplet support, so this exercise transcribes one melody rather
than the whole piano texture. These are importer limits, not a claim that ABC
itself cannot represent those features.
[Verovio input formats](https://book.verovio.org/toolkit-reference/input-formats.html).

Verovio 6.3.0's raw `getMEI()` export declares **6.0-dev**. The notebook makes
this visible and shows a CAMAT command for a checked 5.1 target. Do not simply
replace the declaration by hand. Keep the original text input and conversion
report, then inspect the musical result.

## Direct MEI: make the encoded choices visible

Use the miniature one-staff MEI in the notebook, or the two-staff manual-entry
scaffold. Edit `pname`, `oct`, `dur` and `dots` in mei-friend or the notebook;
inspect the rendering after each change. This is the closest preparation for
the later editorial tasks, because students already work in the format that
will hold source links and annotations.

The miniature MEI labels its measures 0 and 1, whereas the whole-piece starter
labels the corresponding music 1 and 2. This is a useful demonstration of why
musical alignment precedes facsimile linking.

## Other options to consider

- **Rhythm first, then re-pitch in MuseScore.** Particularly useful when the
  same rhythm recurs: enter durations or copy the rhythmic pattern, then replace
  pitches. It makes the distinction between pitch data and a notated score
  concrete. [Official input-method guide](https://handbook.musescore.org/basics/alternative-note-input-methods).
- **MIDI keyboard in step time.** An input-device alternative within MuseScore.
  Performed MIDI import adds quantisation and voice-assignment decisions;
  give that its own exercise instead of adding it to these fifteen minutes.
- **Humdrum `**kern`.** The notebook includes the same five notes in this
  format for students interested in analytical data and explicit event syntax.
  It is an optional extension, rather than another compulsory mini-lesson.
- **An LLM drafting ABC or MEI.** Bring back Session 1's generate → render →
  check procedure if students want it. Require explicit pitches, octaves,
  durations and pickup in the prompt, then verify against the witness. The
  source-based editing block later gives this more time.

The common checkpoint is a correct five-note melody and an explanation of
what the chosen route omitted. Continue with the shared starter afterwards.
