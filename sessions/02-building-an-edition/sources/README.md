# Step 1 complete — fixed source pair

Checked on 23 October 2026. Machine-readable provenance, hashes and review limits
are in [sources.json](sources.json). Files under `local/` are ignored by Git;
neither the scan nor its extracted page is published by the course site.

## Printed witness

Robert Schumann, *Album für die Jugend*, Op. 68, No. 10,
“Fröhlicher Landmann, von der Arbeit zurückkehrend.” Clara Schumann edition,
Leipzig: Breitkopf & Härtel, plate R.S. 67; the IMSLP catalogue dates the edition
1887. The inspected title page credits Clara Schumann and the publisher; the
music page carries the plate. The date comes from the catalogue, rather than
a printed date found on those inspected pages.

- [IMSLP work catalogue](https://imslp.org/wiki/Album_f%C3%BCr_die_Jugend,_Op.68_(Schumann,_Robert))
- [File 51556](https://imslp.org/wiki/Special:ImagefromIndex/51556)
- [Downloaded PDF](https://s9.imslp.org/files/imglnks/usimg/0/0a/IMSLP51556-PMLP02707-RS67.pdf)
- Catalogue scan credit: D-Mbs; upload: Ivdruiz, 31 December 2009.
- Catalogue rights statement: Public Domain. This is the recorded provider
  statement, separate from the encoding and new teaching materials.

The original has 50 PDF pages, 9,441,076 bytes. **No. 10 occupies PDF page 8,
printed page 8, in its entirety.** It has five systems. The source carries no
printed bar numbers.

Local originals and derivative:

- `local/imslp-51556-schumann-op68.pdf`: unmodified download.
- `local/schumann-op68-no10-source-page.pdf`: original page 8 extracted as
  a one-page PDF; no crop, resize, rotation or rasterization. Its PDF page 1
  corresponds to original PDF page 8 and printed page 8.

The extracted page was reopened, rendered and visually compared with the
original page. Their 120 dpi page renders were checked for exact pixel equality.

## Base encoding

[Maja Hartwig's MEI sample](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei),
frozen at commit `e4a3c4dece588ae0bdb13e5cf956340dcd99b447`.
The local file's Git blob SHA-1 was verified against the upstream blob:
`192a23f37a2a9f634eabf1bee3efd06ffa5ee637`. SHA-256 is also recorded.

The file declares MEI 5.1 and states that its encoding is public domain; the
collection provides an ECL-2.0 license. Preserve the credit, header and notices
when preparing the derivative. Its source description cites KernScores and does
not identify the selected printed edition as its witness.

**Numbering decision:** preserve the upstream labels. MEI `n="1"` is the pickup;
`n="2"` is the first full bar. The workshop's pickup + first eight full bars
therefore means **MEI labels 1–9**, the first two printed systems.

System map in upstream MEI labels:

1. Pickup 1, then 2–5.
2. 6–9.
3. 10–13.
4. 14–17.
5. 18–21.

Use the **whole one-page piece as the technical carrier**, retaining links and
continuing slurs across the reviewed passage boundary. Declare only labels 1–9
as the passage being edited in the core exercise. This avoids constructing an
excerpt with dangling references or pretending that the whole work was reviewed.

## Initial comparison and preparation issues

The notes/chords and written durations of labels 1–9 were compared manually
with the first two systems. This is an initial source-pair check, not a completed
proofread or a schema-validation result. The pickup has an eighth rest above C3;
the subsequent eight bars have four quarter-note units in each staff's layer.

The existing expressive layer cannot simply be treated as a transcription of
this witness:

- **Missing staff declarations:** body staff definitions `s1` and `s2` omit
  `lines="5"`. The untouched file renders without normal staff lines in Verovio
  6.3.0. Adding just those two attributes in a temporary diagnostic copy restores
  normal staves. The original file remains unchanged.
- **Opening slurs differ:** the first encoded slur runs from pickup C3
  `d1e60` to C4 `d1e619` in label 3. In the selected print, the first slur ends
  on F3 `d1e338` in label 2. A separate slur in label 3 runs from B-flat3
  `d1e561` to A3 `d1e634`.
- **A printed dynamic is absent:** the print's second system starts with
  `f` at musical bar 5 / MEI label 6; no dynamic appears there in the sample.
- **Slur storage needs cleanup:** Verovio reports 20 slurs stored outside the
  measure containing their start. Storage location and correct musical endpoints
  are separate questions; moving an element alone does not reconcile its reading.
- **Phrases are written out:** labels 2–5 and 6–9 are separate written music,
  not an instruction to replace one with a repeat sign.

These findings make the example suitable for source-based enrichment. In step 2,
prepare a separate rendering baseline and teaching reduction, with a change
record distinguishing technical repairs, actual source differences and deliberately
removed markings. Suggested exercises: restore the printed tempo/initial dynamic,
restore the dynamic at label 6, and encode or explain the opening slur division.
Keep both downloaded originals byte-identical.

**24 October update:** the [student starter](../examples/schumann/README.md),
[teacher solutions](../teacher/schumann/answer-key.md) and
[change record](../teacher/schumann/changes.json) are now prepared. The next
step is linking the fixed source page to the working MEI.

**24 October OMR cross-check:** the reused MEI reads A3 at `d1e338` and `d1e1495`; the print reads F3 (labels 2 and 6, final bass eighth). Teaching derivatives correct these readings. The earlier preliminary passage inspection missed them and must not be treated as a complete note-level verification. The technical baseline and upstream original preserve the inherited A3.

**25 October recipe clarification:** the frozen one-page derivative also contains a title, subject and creator metadata field. These are now recorded under `classroom_pdf.pdf_metadata` in `sources.json`; the extraction helper adds them explicitly. The PDF itself and its recorded hash are unchanged. Omitting those fields changes the PDF bytes even though its rendered pixels are identical.
