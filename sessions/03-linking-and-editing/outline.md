# Session 3 — Linking and editing

Instructor outline, drafted 26 October 2026 from the second half of the first
session 2 plan. **Two 90-minute blocks.** Not yet rehearsed in this order.
Student page: [docs/sessions/03-linking-and-editing/index.md](../../docs/sessions/03-linking-and-editing/index.md).

The notebooks stay in [`../02-building-an-edition/notebooks/`](../02-building-an-edition/notebooks/):
they continue the project `schumann_edition_work` that session 2's PDF
preparation created next to them. Students open the same folder in VS Code.

Previous: [session 2](../02-building-an-edition/outline.md) (setup, source,
notes, PDF preparation). Next: [session 4](../04-publishing-and-analysis/outline.md)
(Git, publishing, analysis).

## The result students should leave with

Working in pairs, students have an MEI of the pickup and bars 1–8 (MEI `n` 1–9)
in which every bar points to its region on the page image, three source-based
edits with an explanation, and a peer review of those edits. It is not yet
committed or published (session 4).

## Learning goals

Students can:

1. Link measures to page regions using MEI surfaces, zones and identifiers.
2. Add a source marking and an editorial note without changing unrelated music.
3. Review an LLM's proposed edit against the scan, XML and rendered result.
4. Distinguish a valid encoding, a readable rendering and a musically checked text.

## Before class

- Students who did not finish the setup in session 2: check them at the door.
- Students without a finished `02_pdf_preparation.ipynb` run need the project
  folder: rerunning the notebook takes a few minutes (scan download).
- Revise the student-facing notebooks used here (linking, what is SVG, live
  editing, SVG editorial, review/release) and the mei-friend and peer-review
  guides in session 1's voice, then add them to the repository. Students
  download them with `get_notebooks.py`, which never overwrites a notebook they
  already have, so the revised versions must be the first ones they receive.

## Block 1 — From page to linked MEI, first edit (90 minutes)

### 0–25 — Combine MEI and facsimile

Use prepared detector responses or manual boxes to avoid depending on a live
service. If demonstrating the Edirom detector, explain that it finds **bar
regions**, not notes, and sends the page image to an external service.

Use the [Schumann linking notebook](../02-building-an-edition/notebooks/02_facsimile_linking.ipynb),
[manual-region ZIP](../02-building-an-edition/notebooks/schumann-measure-boxes.zip), and
[block guide](guides/facsimile-linking.md). The
[executed reference](../02-building-an-edition/teacher/references/02_facsimile_linking_recorded.ipynb)
preserves the code and text checks. Its exercise deliberately omits the pickup
from manually prepared data; it does not claim an observed detector failure.

Students inspect the labelled overlay, correct one known box problem, then
integrate the facsimile and source breaks. Show one instance of each connection:

1. `surface` describes a page; `graphic` names the image and its dimensions.
2. `zone` gives a rectangular region in that image's pixel coordinates.
3. `measure/@facs` points to its zone; `pb/@facs` points to its surface.

Check first and last bars of a system and the pickup. Matching counts alone do
not establish correct alignment. A split bar may need more than one zone.

**Checkpoint:** selecting a bar identifies the correct source region, and the
linked file opens from the saved edition folder. The working file is
`edition/mei/work.mei`; the notebook also saves
`edition/checkpoints/linked-before-editing.mei` and `linked-stage-checkpoint.json`.

### 25–35 — What is SVG?

Use the [beginner SVG showcase](guides/svg-introduction.md), its
[offline browser demos](../02-building-an-edition/examples/svg-introduction/index.html)
or [introductory notebook](../02-building-an-edition/notebooks/02_what_is_svg.ipynb).
Change a shape's short SVG text, compare PNG/vector enlargement, and connect
Schumann's pickup drawing with its MEI ID. Only element, attribute, group and ID
need explanation. SVG describes the drawing; MEI records the music and its
editorial structure.

### 35–50 — Establish the editing loop

Use the [Schumann live-editing notebook](../02-building-an-edition/notebooks/02_live_editing.ipynb)
and [block guide](guides/live-editing.md). In VS Code, put the
MEI beside the viewer notebook, select the `seminar` kernel, point the viewer at
`edition/mei/work.mei` and enable `auto_watch_mei`. Hover a symbol, copy its
`xml:id`, find it in the text and save a small change. The notebook inspects the
saved file; VS Code or mei-friend performs the edits.

### 50–80 — Edit 1, by hand: restore the opening marks

Assign exact bars/IDs after rehearsing the source ([answer key](../02-building-an-edition/teacher/schumann/answer-key.md)).
Restore the clearly printed opening marks omitted from the starter
(*Frisch und munter*, forte). Save, watch the viewer refresh, compare with the
print.

Do not use `<supplied>` merely because a printed sign was missing from the
starter. Ordinary transcription restores that sign. `<supplied>` is for
editorial additions absent from the witness, `<unclear>` for genuinely
uncertain readings; both are optional extensions.

### 80–90 — Buffer and checkpoint

Pairs that are behind catch up; others start reading the SVG editorial packet.

## Block 2 — Assisted edit, mei-friend, peer review (90 minutes)

### 0–30 — Edit 2, with Copilot: the opening slurs

Use the [SVG-aware editorial workflow](guides/svg-editorial-workflow.md)
and its [packet notebook](../02-building-an-edition/notebooks/02_svg_editorial.ipynb).
The model compares the first-system scan and engraving, infers the two opening
slur divisions (pickup C3 `d1e60` → F3 `d1e338`; B-flat3 `d1e561` → A3 `d1e634`),
identifies the MEI endpoints and proposes a candidate edit. Students review the
diff, validate, re-render and compare with the witness. Keep the model's
proposal and the human corrections distinct.

If Copilot Free cannot take images, use the **text-only fallback**: the printed
forte at `d1e1231` (bar 5, MEI `n` 6), whose prompt supplies a source-verified
reading and exact target ([experiment template](../02-building-an-edition/examples/model-prompts/experiment-template.json)).
A prepared instructor demonstration covers the image route. The
[access handout](teacher/vscode-free-models.md) is instructor
background, not student reading.

Optional representation experiment (same model, fresh chats): A gets scan +
engraving PNG + MEI context; B also gets SVG source text; C gets SVG with MEI
`data-*` attributes. Homework or later session.

Keep notes, rhythms, IDs and facsimile links stable unless the task concerns
one of them. Rendering exports are unsuitable for saving an edition because
they can replace metadata or identifiers.

### 30–40 — Edit 3: an anchored annotation

Add an `<annot>` explaining a decision, source discrepancy or limitation, with
enough detail for someone else to check it. The A3 → F3 correction from
session 2 is a natural subject.

**Checkpoint:** three changes visible in a diff and justified from the source.

### 40–55 — mei-friend as a second editor

Use the [mei-friend guide](guides/mei-friend.md) and optional
cells in the [review/release notebook](../02-building-an-edition/notebooks/02_review_and_release.ipynb).
Open a copy of the MEI in [mei-friend](https://mei-friend.mdw.ac.at/). Select a
note in notation and code, validate, edit the annotation, save as a new file
and reopen it. Check that IDs, annotations and links survive the save.

Rehearse image access first: the hosted application cannot read the local image
paths the notebook uses. Unverified so far: the save/reopen round trip and the
local image route ([status](../02-building-an-edition/teacher/status.md)).

### 55–80 — Peer review

Use the [peer-review sheet](guides/peer-review.md) and the
notebook-generated review record. Partners exchange roles: the reviewer opens
each changed bar against the scan and checks the pickup, accidentals, rhythm and
placement of added marks. Run the prepared validation; a successful render is
not proof of schema validity, and schema validity does not show that a
transcription matches its witness. Record unresolved issues.

**Checkpoint:** every change reviewed, or recorded as unresolved.

### 80–90 — Wrap-up

Each pair shows one consequential change and its evidence. Preview session 4:
the edition goes on GitHub, with a viewer.
