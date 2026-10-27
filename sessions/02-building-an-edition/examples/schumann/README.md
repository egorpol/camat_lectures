# Schumann — student starter

Teaching files for *Fröhlicher Landmann*, Op. 68 No. 10. The witness is the
Clara Schumann edition, plate R.S. 67, IMSLP file 51556, printed/PDF page 8.
The scan and its provenance are described in [the source record](../../sources/README.md).

Copy the MEI you want to work on into your own edition folder. These are
generated templates: rebuilding the course materials replaces them.

- [starter.mei](starter.mei): the whole short piece as notes and rhythms,
  with 21 measure elements. Dynamics, slurs, verbal directions, tempo and
  articulation elements have deliberately been removed from the musical body.
  Notes, accidentals, durations, rests, voices, chords, clefs, beams, stems and
  existing musical IDs are preserved.
- [manual-entry.mei](manual-entry.mei): a blank scaffold for the pickup and
  first full bar. Its invisible `space` / `mSpace` elements are placeholders,
  not a transcription of silence. Replace each layer's contents with the
  appropriate notes, chords and rests from the print. Keep measure IDs.
- [pickup-bar1.abc](pickup-bar1.abc): the starting text of the ABC box on the
  session page (part 5): header and pickup, bar 1 left to type. Written by
  hand, not generated.

The whole piece is retained so that later facsimile integration can use its
single printed page. **The core exercise concerns the first two printed
systems only: MEI labels 1–9.** Neither file claims a complete edited text.
The header incipit was omitted to avoid a second, competing encoded score.

## Before editing

Open the source page beside your score. The source has no bar numbers. In the
MEI, `n="1"` is the pickup; `n="2"` is the first full bar. Keep these labels
and existing `xml:id` values so that later links continue to work.

After the manual-entry exercise, continue with a copy of `starter.mei`.
The three editorial tasks are:

1. **Opening instruction.** At the pickup, transcribe the printed tempo text
   and dynamic. Use ordinary transcription markup for signs visible in the
   witness; their absence from the starter does not make them editorial additions.
2. **Second-system dynamic.** Compare the start of the second printed system
   with the starter and restore the missing dynamic at MEI label 6.
3. **Opening phrasing.** Encode the first two printed slurs in the lower staff.
   Check their endpoints separately. Add an `<annot>` identifying the source
   and explaining your decision, anchored to the relevant existing note IDs.

For each task: find the source location → inspect the MEI → make a small edit
→ save → render → check against the print. Ask an LLM for a bounded patch only
after identifying the evidence and target. Your comparison with the source is
the review.

An instruction is usually encoded as `<tempo>`, a dynamic as `<dynam>`, and
a slur as `<slur startid="#…" endid="#…">`. Slur endpoints refer to notes;
store the slur in the measure containing its starting note. The annotations
panel in CAMAT will display an anchored `<annot>` even though Verovio does
not engrave its prose as ordinary score text.

The starter has no facsimile records yet. Linking the page and its bar regions
is the next preparation step; keep your edited MEI as the durable working file.

## Credits and notices

Derived from Maja Hartwig's MEI Sample Collection encoding at commit
`e4a3c4dece588ae0bdb13e5cf956340dcd99b447`; upstream copyright is credited to
the Music Encoding Initiative Board. The file's original public-domain
declaration is preserved. The collection's [ECL-2.0 license](LICENSE) is
included. Its publication metadata describes the upstream encoding; the new
`editionStmt`, project description and revision entry identify this teaching
derivative. No license for unrelated course material or scans is implied.

Preparation was assisted by an LLM and recorded on 24 October 2026. The
[teacher's change record](../../teacher/schumann/changes.json) distinguishes
technical repairs, deliberate omissions and the task solutions. Use the
printed witness to check every new reading.

Source-based correction recorded 24 October: the starter changes A3 to F3 at `d1e338` and `d1e1495` (MEI labels 2 and 6, final bass eighth), following IMSLP 51556, printed p. 8. The original and technical baseline retain the inherited A3. This was missed in the preliminary inspection; further source review remains necessary.
