# Instructor preparation — Schumann edition workshop

Companion to [outline.md](../outline.md). This preparation runbook records completed
steps below; the remaining checkboxes are preparation tasks, not completed work.
For a compact overview, see [current status](status.md).
Tool interfaces and sources were checked on 23 October 2026 against CAMAT
0.2.8, the local CAMAT checkout, the source repositories and official documentation.

**Step 1 completed, 23 October:** see the [source-pair check](../sources/README.md)
and [provenance record](../sources/sources.json). IMSLP 51556 contains the whole
piece on PDF/printed page 8. Use that one-page piece as the technical carrier;
the reviewed passage is upstream MEI labels 1–9 (pickup + eight full bars).
The sample needs staff-line declarations and source-based slur/dynamic work
before it becomes a classroom starter. These are recorded separately from
deliberately omitted teaching features.

**Step 2 completed, 24 October:** [student files](../examples/schumann/README.md),
[teacher answer key](schumann/answer-key.md), and
[change record](schumann/changes.json) are prepared. Five MEI derivatives
pass the executed schema/reference checks and render with Verovio. The model
solution answers the three assigned tasks; it is not a complete restoration
of the passage's expressive content. The local PDF/linking preparation is
recorded below; an end-to-end classroom rehearsal remains to be done.

**OMR insert added, 24 October:** [student references and workflow](omr.md)
and [instructor evidence](omr-study-notes.md) connect the earlier CAMAT
HOMR/OeMeR/Clarity comparison to the seminar. Block 1 now includes a ten-minute
insert while retaining its 90-minute total. The follow-up now supplies
[an executed Schumann OMR notebook](references/omr-schumann/02_schumann_omr_recorded.ipynb)
and [portable code notebook](../notebooks/02_schumann_omr.ipynb), with actual HOMR
and OeMeR runs. It also caught two missed A3 → F3 readings in the reused MEI;
the teaching derivatives and answer key now record those corrections. The
earlier passage inspection was preliminary, not a complete note-level proofread.

**Note-entry block prepared, 25 October:** the [entry-methods guide](entry-methods.md)
and [notebook](../notebooks/02_note_entry.ipynb) give the same five-note bass melody
in ABC, Plaine & Easie, direct MEI and optional Humdrum. MuseScore remains the
familiar editor, with direct MEI Basic export as well as the MusicXML route.
Pairs choose one method and compare results before returning to the common
starter. OMR recordings now live in a separate ZIP beside the notebook;
`get_notebooks.py` and the shell downloader copy both files.
The four text examples pass the executed pitch/rhythm/pickup/key/metre checks;
the direct scaffold and three converted outputs pass the MEI 5.1 schema check.
See [rehearsal evidence](note-entry-checks.json). Actual MuseScore GUI
entry/export and the student cloud environment remain to rehearse.

**PDF preparation block completed, 25 October:** the [notebook](../notebooks/02_pdf_preparation.ipynb),
[guide](pdf-preparation.md), [input ZIP](../notebooks/schumann-edition-inputs.zip),
and [executed reference](references/02_pdf_preparation_recorded.ipynb) cover
minutes 45–65. A fresh PyPI installation of CAMAT 0.2.8 reproduced the frozen
excerpt, rendered the fixed page and saved all 21 labels across five systems.
The repeated run preserved PDF/image/manifest/checkpoint hashes. The earlier
extraction recipe now also records the existing PDF metadata fields required
to reproduce its hash. Source PDF bytes and teaching MEI did not change.
See [checks](pdf-preparation/checks.json). The following linking block
uses this checkpoint; live editing and the publication rehearsal remain.

**Linking and checkpoint block prepared, 25 October:** the
[notebook](../notebooks/02_facsimile_linking.ipynb), [guide](../../03-linking-and-editing/guides/facsimile-linking.md),
[manual-region ZIP](../notebooks/schumann-measure-boxes.zip) and
[instructor key](facsimile/answer-key.md) cover minutes 65–90.
Twenty-one prepared regions and a deliberate missing-pickup exercise are saved
as explicit manual data. The merge preserves musical content/IDs and creates
21 zones, one surface, one page break and four system breaks. Required
conformance checks and Verovio rendering pass; browser selection is verified
in both directions. The default alignment remains unreviewed pending actual
instructor/student inspection. See [evidence](facsimile/checks.json)
and the [executed reference](references/02_facsimile_linking_recorded.ipynb).
The later editing and local publication rehearsals are now recorded below.

**Editing block and model research added, 25 October:** the
[live-editing notebook](../notebooks/02_live_editing.ipynb), [guide](../../03-linking-and-editing/guides/live-editing.md),
[free-model research](../../03-linking-and-editing/teacher/vscode-free-models.md), provider configuration examples,
bounded Schumann prompts and experiment log cover Block 2, minutes 0–40.
The research distinguishes Auto-only Copilot Free, named free Gemini/OpenRouter
API routes, local Ollama, and Codex account-dependent IDE access. The public
OpenRouter catalogue is saved separately with refresh code. Provider inference
and student-account setup have not been tested; see the research handout for
the exact documented access/limit conditions. Local watch/edit validation is
recorded in [checks](live-editing/checks.json) and the
[executed reference](references/02_live_editing_recorded.ipynb): direct and
atomic saves trigger native re-renders, protected-content checks reject test
mutations, and the edited scratch file passes required checks plus Verovio.
The original working project is unchanged. VS Code frontend navigation, model
accounts/inference, publication and mei-friend rehearsal remain.

**SVG editorial extension added, 26 October:** the
[research/teaching note](../../03-linking-and-editing/guides/svg-editorial-workflow.md) and
[packet notebook](../notebooks/02_svg_editorial.ipynb) make visual/code comparison
part of Block 2's existing 10–40 minute exercise. The model can inspect a
source system and current engraving, connect SVG IDs to MEI, and edit/re-render
a candidate. A/B holds the model fixed while adding SVG source; optional C
adds explicit encoded attributes. The text-only forte task remains the fallback.
General SVG results, score-reading evidence and this local exercise are
distinguished. The [executed reference](references/02_svg_editorial_recorded.ipynb)
and [checks](svg-editorial/checks.json) confirm five measures/100 mapped
events, unchanged pixels after attribute enrichment, and a validated/rendered
two-slur teacher candidate. Source crops stay local. These are deterministic
preparation checks; provider inference and model quality are not tested.

**Beginner SVG introduction added, 26 October:** the
[eight-minute guide](../../03-linking-and-editing/guides/svg-introduction.md), [browser demos](../examples/svg-introduction/index.html),
[notebook](../notebooks/02_what_is_svg.ipynb) and
[asset ZIP](../notebooks/svg-introduction-assets.zip) introduce drawing instructions,
pixel/vector enlargement and the connection between a note's MEI and SVG ID.
The notebook runs without the Schumann project or a renderer. The teaching
pitch change is explicitly artificial. The revised editing schedule preserves
the 90-minute block; extended A/B work is optional.

**Review, Git and publication prepared, 26 October:** the [mei-friend guide](../../03-linking-and-editing/guides/mei-friend.md),
[peer-review sheet](../../03-linking-and-editing/guides/peer-review.md), [six-minute Git primer](../../04-publishing-and-analysis/guides/git-introduction.md),
[publication guide](../../04-publishing-and-analysis/guides/publishing.md) and [notebook](../notebooks/02_review_and_release.ipynb)
cover minutes 40–90. The separate [template ZIP](../notebooks/schumann-release-template.zip)
contains the pinned build, Pages workflow, notices and exact-source retrieval.
Local notebook, export preservation, full validation, fresh-clone/scoped-CI,
Git/tag/build identity and browser PDF/bar-link checks are recorded in
[publication evidence](publication/checks.json). Source approval remains
blank. The actual mei-friend Schumann round trip was blocked by declined browser
upload approval; it was not retried through another route. GitHub push/deployment,
student-account setup and the timed classroom rehearsal remain external checks.
The complete [student workshop page](../../../docs/sessions/02-building-an-edition/index.md)
and downloads are assembled for the instructor overview.

## 1. Freeze the witness and decide the reviewed scope

- [x] Obtain the selected PDF from the [IMSLP Op. 68 catalogue](https://imslp.org/wiki/Album_f%C3%BCr_die_Jugend,_Op.68_(Schumann,_Robert)).
  Candidate: **51556**, Clara Schumann edition, Breitkopf & Härtel, 1887,
  plate R.S. 67. Confirm the PDF itself, not only the catalogue group.
- [x] Locate No. 10 and record printed page numbers, original PDF page numbers,
  systems and the pickup + first eight full bars.
- [x] Make a source record containing the exact file URL/ID, retrieval date,
  bibliography, scan credit, stated reuse conditions, byte count and SHA-256.
  Keep a copy of the catalogue evidence. Record the scan's conditions separately
  from those of the encoding and from the license on new teaching materials.
- [x] Keep the original unchanged. For classroom efficiency, extract only the
  relevant full pages to a separate PDF; record original → excerpt page mapping,
  extraction tool/command and hash of each file. Work from the excerpt thereafter.
  Do this before drawing boxes. Changing pixels or rendering resolution requires
  new coordinates and review.
- [x] Decide whether the carrier MEI is an excerpt or the whole short piece.
  The guided integration expects the MEI's measure labels to agree with the
  described page content. A full-piece MEI plus only eight described bars does
  not satisfy that condition. If keeping the whole piece, align its pages and
  clearly label only the selected passage as editorially reviewed.

Do not infer that the PDF and base encoding share a printed source. The printed
witness controls the readings in this exercise; the base encoding saves entry.

## 2. Prepare the reusable notation

- [x] Fetch [Schumann_Landmann_Op68_No10.mei](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei)
  at that pinned revision. Record its hash. Credit Maja Hartwig and preserve
  its header and the collection's notices. The encoding declares itself public
  domain; the repository provides an [ECL-2.0 license](https://github.com/music-encoding/sample-encodings/blob/main/LICENSE).
- [x] Inspect the actual score under `music/body`. The header also contains
  an incipit with its own score and measures; avoid counting or editing both.
- [ ] Compare pitches, durations, voices, clefs, accidentals, repeats and pickup
  with the selected witness. Resolve numbering before making any facsimile links.
  Record base-encoding discrepancies rather than transferring its assumptions.
- [x] Derive `starter.mei` with an explicit “teaching reduction” statement and
  a list of deliberately omitted features. Keep a pristine source copy.
  Remove selected dynamics, slurs and articulations; preserve structural ties,
  voices and all information needed to render the correct notes and rhythms.
  Review references after removals; do not leave dangling IDs.
- [x] Prepare a separate small manual-entry scaffold for the pickup and one bar,
  plus the solution. Students who want full manual transcription can continue
  later from it.
- [x] Make a teacher answer key with three actual locations, IDs, source readings,
  before/after MEI and expected rendered result. Choose at least two different
  kinds of expressive marking. If the first system does not supply enough,
  adjust the passage rather than inventing an editorial problem.

An existing MusicXML or Humdrum source is another entry route. The verified
CAMAT CLI syntax is:

```sh
camat-convert --source sources/input.musicxml --output-dir imports --mei-version 5.1
```

Inspect the reported output before promoting it to the working MEI. Import once;
subsequent edition work edits that MEI directly. MIDI transcription and OMR are
optional extensions, because they introduce additional correction work.

For the OMR insert, use the recorded Schumann notebook and the [reference sheet](omr.md).
Keep PDF rendering, note recognition and bar-region detection explicit as three
different operations. For fresh runs or further correction, follow the
[instructor notes](omr-study-notes.md); preserve raw recognition,
converted MEI and corrected MEI as separate stages. The checked Schumann starter
remains the classroom input for linking and enrichment.

## 3. Rehearse the environment and PDF integration

Use **Python 3.11+**. Session 1's Python 3.10 minimum does not cover this CAMAT
workshop. For the rehearsal, pin the shipped version rather than installing a
moving development checkout:

```sh
python -m pip install 'camat[validation,notebooks]==0.2.8' ipykernel
camat-fetch-tutorials
```

The active environment also needs Poppler's `pdfinfo` and `pdftoppm` for rendering,
and `xmllint` for the RELAX NG check. Test these on student machines or on the
chosen Jupyter4NFDI image. Run `check_poppler()` before the workshop. Record
package/tool versions; do not silently switch rendering versions after making
the page hashes and boxes.

The existing CAMAT notebooks provide the sequence:

1. [`mei_pdf_facsimile_guided.ipynb`](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_pdf_facsimile_guided.ipynb):
   page images → page description → boxes → review → linked MEI.
2. [`mei_facsimile_viewer.ipynb`](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_facsimile_viewer.ipynb):
   compare the saved MEI with the facsimile during editing.
3. [`mei_web_edition.ipynb`](https://github.com/egorpol/camat_v2/blob/v0.2.8/notebooks/mei_web_edition.ipynb):
   build and preview the publication viewer.

Their defaults demonstrate Buxtehude. The Schumann settings and page description
are now supplied in [02_pdf_preparation.ipynb](../notebooks/02_pdf_preparation.ipynb).
The following [linking notebook](../notebooks/02_facsimile_linking.ipynb) supplies
prepared manual boxes and a missing-pickup exercise; do not ask students to
invent the settings from the Buxtehude example during class. The guided route handles one movement. Use
the more detailed integration notebook for multiple movements.

The Schumann exercise now uses prepared manual boxes with one deliberate
omission. Demonstrating the external detector remains optional; preserve its
actual response if used. Remove any unrelated regions from a shared page and
record that edit. Verify labels visually, even if all counts match.

Keep the complete generated result folder together. It contains `pages/`,
`overlays/` and `mei/`. Use that folder as the edition project root. Promote a
copy of the generated linked MEI to `mei/work.mei` **within the same directory**,
so its `../pages/...` image paths still resolve. Edit this canonical copy.
Do not rerun the guided merge on the editorial working file: that operation
regenerates its output and can replace later work. Checkpoints preserve progress.

## 4. Prove the editing loop

Use [02_live_editing.ipynb](../notebooks/02_live_editing.ipynb) for the Schumann
paths, generated prompt, protected-content guard and validator. Its project
layout uses `edition/mei/work.mei`; the generic snippet below assumes a notebook
already running **inside `edition/`**. It must resolve to the same file.

Open the edition project in VS Code, use a local Python kernel with CAMAT
installed, and run this from a notebook whose working directory is that root:

```python
from pathlib import Path
from camat import launch_interactive_facsimile_viewer

work = Path('mei/work.mei').resolve()
assert work.is_file(), work
viewer = launch_interactive_facsimile_viewer(
    str(work),
    auto_watch_mei=True,
    verovio_breaks='encoded',
    show_annotations=True,
    allow_missing_facsimile=False,
)
```

Make and save one edit in the XML tab. Confirm that the viewer reloads and
retains its navigation. A local file can be watched; a downloaded HTTP source
requires reload and will not follow edits to a different local copy. If watching
fails, use **Reload score** for a local file (**Reload source** for HTTP).
Install/select the Python and Jupyter support in
VS Code before class. A JupyterLab text editor plus the viewer is the cloud route.

The viewer is read-only. An LLM edits the XML through the editor; it does not
turn the notebook into an autonomous musical editor. Students can complete all
tasks without an LLM account; an instructor demonstration is sufficient.

Rehearse one route from the [25 October access research](../../03-linking-and-editing/teacher/vscode-free-models.md)
before class. Use Chat/proposal mode and the supplied verified text so vision
is optional. A free extension does not imply a free API, and a free web chat
account does not imply IDE access. Keep keys in personal extension secrets or
the documented local configuration, outside notebooks and the course repo.
An untested account/login or model availability remains a rehearsal task.

Use this bounded prompt with a real, checked source description and actual IDs:

> Edit only the passage and XML IDs specified below in mei/work.mei. The attached
> source crop, or the explicitly verified reading I provide, is the evidence.
> First describe the proposed change and its target. Propose a minimal patch for
> the specified printed marking. Preserve existing IDs, notes, rhythms, voices,
> metadata and facsimile links. If the evidence or target is unclear, explain
> what is missing instead of guessing. Add an editorial annotation only if
> requested, with links to the relevant existing IDs. List what a human must
> verify. Do not re-export or reformat the whole document.

Afterward: inspect diff → save → validate → compare rendering and scan → record
review → commit. A model's statement that something is checked is not the review.

For mei-friend, rehearse opening and saving the same MEI. Its
[facsimile documentation](https://mei-friend.github.io/docs/advanced/facsimile/)
describes web-accessible images and CORS requirements. Local notebook image paths
need a separate access solution in the hosted application. Demonstrate with
prepared accessible images or its documented example. Preserve the canonical
file and reconcile the saved copy before continuing in VS Code.

## 5. Prepare review and the publication build

The following background recipe is implemented by the
[publication template](../examples/edition-template/README.md). Use its scripts
for the classroom route: they add commit/hash/review identity and preserve notices.

From the edition root, rehearse:

```sh
camat-validate-mei mei/work.mei --output-dir validation/v0.1.0 --verovio
```

Read `run.json` and findings: XML/references, RELAX NG, Schematron, resources,
input hashes and Verovio are different checks. Required unavailable checks mean
incomplete validation. Review consumer results too; do not infer that every
optional check passed from the CLI exit code. Add `--camat-parse` only when the
analysis bridge is part of this rehearsal. Compare the reviewed music with the
scan separately. Preserve the complete release report, not only an empty CSV.

With the generated `pages/` and `mei/work.mei` layout above, this `site.json`
uses the PDF that a visitor opens in their own browser:

```json
{
  "title": "Schumann, Op. 68 No. 10 — teaching edition",
  "subtitle": "Teaching draft: three tasks in the opening passage; further source review remains",
  "storage_prefix": "schumann-op68-10-seminar",
  "works": [
    {"id": "landmann", "title": "Fröhlicher Landmann", "mei": "mei/work.mei"}
  ],
  "facsimile": {
    "type": "pdf",
    "pages": "pages/pages.json",
    "pdf": true
  }
}
```

Adjust the declared scope to the final carrier. Give each pair's publication a
distinct `storage_prefix`. Add source, credits, licensing and edition links
before releasing. If hosting page images, record the applicable conditions and
use `images.copy` or hosted-image configuration deliberately. The PDF option
above keeps scans out of the published site; the README must tell readers which
exact original or extracted PDF matches the manifest and how to obtain it.

```sh
camat-build-site site.json _site
python -m http.server --directory _site 8000
```

Open `http://localhost:8000/` and a bar link using the **actual MEI measure label**.
Do not assume that `#landmann/1` means the first full bar until numbering has been
settled. `_site` is regenerated; edit the MEI/configuration, then rebuild. Opening
`index.html` directly from disk does not provide the required HTTP module loading.
The publication viewer uses external rendering libraries, so rehearse network
access or prepare a separate offline presentation fallback.

## 6. Make publication routine before class

The workflow/build files are prepared and checked locally. These checkboxes
concern actual class repositories and public deployment, which have not run.

- [ ] Prepare one repository per pair, or one instructor repository with clear
  pair contributions. Put GitHub login and permissions ahead of the lesson.
- [ ] Commit the MEI, `site.json`, manifests, selected provenance, credits,
  notices, editorial policy, reviewed scope and validation evidence. Keep local
  PDFs/images and generated `_site` out of Git unless deliberately publishing
  those assets under documented conditions.
- [ ] Configure GitHub Pages to use **GitHub Actions**. Prepare a workflow that
  checks out the source, installs the pinned CAMAT version, builds
  `camat-build-site site.json _site`, uploads that folder and deploys it.
  It needs `contents: read`, `pages: write`, `id-token: write` and a
  `github-pages` environment. See [GitHub's workflow instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
  and [Webern's existing workflow](https://github.com/egorpol/webern_op27/blob/main/.github/workflows/pages.yml).
  Webern uses its own build script: replace that build step for the reusable
  CAMAT template rather than copying the script invocation unchanged.
- [ ] Rehearse a complete edit → commit → push → deployment. Check the live
  site in a fresh browser, its downloadable MEI and one note/bar link.
- [ ] Tag the reviewed, deployed commit `v0.1.0`; create a GitHub release with
  scope, source, credits, known issues and facsimile instructions. Explain that
  a Git commit, a tag, a release and a deployed site are separate objects.
- [ ] If the template carries the full piece, preserve the warning that only
  the declared passage was edited. A working viewer does not broaden review.

## 7. Package the recoverable stages

Stages 1–5 below now have prepared assets and recorded local checks. Stage 5
still needs final human source review and an actual remote deployment:

1. Source record, immutable PDF or retrieval instructions, page mapping and hashes.
2. Original MEI, teaching reduction, manual-entry scaffold and exact edit answer key.
3. Page manifest, detector/manual boxes and reviewed overlays.
4. Linked MEI checkpoint that students can load if integration stalls.
5. Edited teacher candidate, validation record, working `site.json`, Git/Pages
   template and local viewer; public deployment remains a live preflight task.

Use one short workshop notebook or a clearly numbered set of sections linking
the existing CAMAT notebooks. In this seminar repo, new notebook sources belong
in `tools/notebooks/02_*.py` and are built with `tools/build_notebooks.py`; do not
hand-edit generated `.ipynb` files. The current `get_notebooks` downloaders copy
notebooks **and their data ZIPs**. These supply the starter/settings, regions,
OMR recordings, beginner SVG assets and release configuration separately from notebook source. Keep
third-party scans out of this repository, consistent with the existing materials.

The student-facing page, downloads and navigation are assembled. See
[status.md](status.md) for the remaining instructor/account/timed rehearsal,
rather than interpreting prepared files as completed human review or deployment.
