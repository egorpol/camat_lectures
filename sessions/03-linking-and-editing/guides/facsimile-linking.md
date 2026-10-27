# Review the regions and link the Schumann facsimile

Session 2, **65–85 minutes**, plus the **85–90 minute checkpoint**. Use the
[linking notebook](../../02-building-an-edition/notebooks/02_facsimile_linking.ipynb) with
[schumann-measure-boxes.zip](../../02-building-an-edition/notebooks/schumann-measure-boxes.zip) beside it.
The [executed reference](../../02-building-an-edition/teacher/references/02_facsimile_linking_recorded.ipynb) contains
the code and text checks, without embedded scans or the image-bearing viewer.

## Continue the saved project

Complete [PDF preparation](../../02-building-an-edition/teacher/pdf-preparation.md) first. Set `PROJECT` to that
notebook's `schumann_edition_work` folder. This stage verifies its input MEI,
page manifest, fixed source-image hash and dimensions before using the regions.
Keep the whole project together; the linked MEI uses relative image paths.

The supplied regions are tied to the rehearsed PNG hash. If another renderer
produces a different image, keep that as a new derivative and review/redraw its
regions before reuse; do not alter the recorded hash merely to bypass the check.
The student cloud environment still needs this rehearsal.

The supplied rectangles are **AI-assisted manual preparation**, checked against
the source as page/system overlays. They are not a recorded detector response.
`boxes-exercise.json` deliberately omits the pickup; `boxes-checked.json` holds
the prepared 21-region solution. Instructor/student inspection is still required
before claiming their own alignment approval.

## The classroom sequence

1. **65–70: diagnose the error.** The source has 21 MEI measures across five
   systems. The exercise has 20 regions, producing counts `[4,4,4,4,4]` where
   the description expects `[5,4,4,4,4]`. CAMAT rejects this on an isolated
   exercise copy. Find the short pickup before the first full bar.
2. **70–75: add the missing region.** Set `USE_PREPARED_SOLUTION=False` and
   enter a rectangle in `TRY_YOUR_BOXES`. Read full-PNG coordinates from the
   ruler, covering both staves. The first ordinary bar is box index 0 in the
   incomplete file; that index is not an MEI measure label. If time is short,
   the explicitly labelled prepared-solution mode lets the demonstration continue.
3. **Inspect all 21 labelled regions.** Check the pickup, both ends of every
   system, and first/last bars on the page. Confirm that a bar's musical content
   agrees with its label. Slight overlap at a barline is intentional; cross-bar
   slurs and text need the full page as context.
4. **75–80: merge and validate.** Add the facsimile subtree and measure links,
   preserving musical content and existing IDs. Run the schema/reference/resource
   checks and Verovio render. Inspect the printed XML attributes.
5. **80–85: interact with the viewer.** Click a source region, then a rendered
   bar, checking the corresponding highlight and the status line. Check the
   pickup, labels 5/6 at a system transition and the final bar.
6. **85–90: save the unedited stage.** Retain the snapshot and reports. Each
   pair states what the software checked and what they checked visually.

## Record actual review

`CONFIRM_BOXES=False` and an empty `REVIEWER` leave the alignment unreviewed.
A linked draft can still be inspected, and the report states that status.
After checking the overlay, students enter their names, enable confirmation
and rerun the settings/review/merge cells. Approval concerns geometry and
alignment, not a completed musical edition or full-piece proofreading.

Matching region counts is necessary but does not establish correct alignment.
An external detector, if demonstrated later, uploads the image and proposes
regions; it does not create the musical note content. Preserve a genuine detector
response separately from this deliberately modified manual exercise.

## Inspect the connections

- `facsimile/@decls` points to the existing printed-witness source record.
- `surface` represents printed page 8 and its image coordinate space.
- `graphic/@target` is `../pages/page-0001.png` from the MEI folder.
- Each of the 21 `zone` elements gives one rectangular source region.
- Each musical `measure/@facs` points to the corresponding zone.
- The page break points to the surface; four system breaks follow the print.

The sole unnumbered movement is explicitly numbered 1 for CAMAT's alignment.
That controlled change and the facsimile/layout additions are recorded separately
from the unchanged musical structure, values, voices and existing IDs.

## Files for the editing block

- `edition/mei/linked-starter.mei`: generated, unedited baseline.
- `edition/mei/work.mei`: the separate file to edit in Block 2.
- `edition/checkpoints/linked-before-editing.mei`: recoverable snapshot.
- `edition/alignment.json`: regions plus review status and pixel/box hashes.
- `edition/linking-report.json` and `linked-stage-checkpoint.json`: integration,
  preservation and handoff records.
- `edition/validation-linked/`: checks and diagnostics.
- `edition/previews/facsimile-viewer.html`: local interactive preview; contains
  the scan and stays outside the course repository.

Rerunning preserves an existing `work.mei`, including later editorial changes.
A changed generated baseline is refused; use a new attempt folder to regenerate
from different inputs/regions. Keep `pages/`, `mei/` and the supporting records
together. The next block establishes the live editing/watch loop for `work.mei`.

The validator's required conformance checks and Verovio rendering are tested;
the optional CAMAT parse consumer is not requested. The inherited pickup/partial
voice rhythm diagnostics remain visible. The core editorial passage is still
labels 1–9, with the rest serving as an unreviewed musical carrier.

See the [instructor answer key](../../02-building-an-edition/teacher/facsimile/answer-key.md) and
[rehearsal evidence](../../02-building-an-edition/teacher/facsimile/checks.json).
