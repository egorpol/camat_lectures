# Session 2 — The source and the notes

Instructor outline, re-planned 26 October 2026. **Two 90-minute blocks**, with a
break between them. Materials in English. Student page:
[docs/sessions/02-building-an-edition/index.md](../../docs/sessions/02-building-an-edition/index.md).

## Sessions 2–4 at a glance

Students build one small edition of **Schumann, “Fröhlicher Landmann, von der
Arbeit zurückkehrend,” Op. 68 No. 10** over three sessions. From this session
on they work on their own laptops; the setup is done together in class and
takes most of block 1. Topics that do not fit move to the next session rather
than being squeezed.

| Session | Block 1 | Block 2 |
|---|---|---|
| 2 (this outline) | laptop setup; source/scan/encoding/edition and the A3→F3 story during the long download | setup buffer; OMR next to the scan; five notes in ABC; PDF preparation and bar table; find the note in the MEI |
| 3 ([outline](../03-linking-and-editing/outline.md)) | facsimile linking; what is SVG; live-editing loop; edit 1 by hand | edit 2 with Copilot; edit 3 (annotation); mei-friend; peer review |
| 4 ([outline](../04-publishing-and-analysis/outline.md)) | Git cycle (diff, commit, push); release; Pages deploy as instructor demo | from the edition to a CAMAT note table and piano roll |

All Schumann notebooks stay in **this** folder, also those used in sessions 3
and 4: PDF preparation, linking, live editing, SVG editorial and review/release
share the project `schumann_edition_work`, which each notebook finds next to
itself (`Path.cwd()`). Session 3 and 4 pages link here.

## Files this session uses

- **Student pages:** the [session 2 page](../../docs/sessions/02-building-an-edition/index.md),
  [Setup on your laptop](../../docs/setup-laptop.md) and the
  [cloud route](../../docs/setup.md#from-session-2-the-cloud-route).
- **Notebooks** in [`notebooks/`](notebooks/), in class order:
  `02_schumann_omr` with `schumann-omr-recordings.zip`, `02_note_entry`,
  `02_pdf_preparation` with `schumann-edition-inputs.zip`. The other five
  notebooks and three ZIPs there are drafts for sessions 3 and 4; they stay
  out of git (listed in `.git/info/exclude`) until they are revised.
- **Example:** [`examples/schumann/`](examples/schumann/README.md): `starter.mei`,
  and `pickup-bar1.abc` for the page's ABC box.
- **Sources:** [`sources/`](sources/README.md): the source-pair check and
  provenance record (scans in the ignored `sources/local/`).
- **For the instructor,** in [`teacher/`](teacher/): the
  [answer key](teacher/schumann/answer-key.md); background guides for
  [OMR](teacher/omr.md), [note entry](teacher/entry-methods.md) and
  [PDF preparation](teacher/pdf-preparation.md); executed notebooks in
  `teacher/references/`; the [preparation runbook](teacher/preparation.md)
  and [status](teacher/status.md).

## The example and its roles

- **Printed witness:** the Clara Schumann edition, Leipzig: Breitkopf & Härtel,
  plate R.S. 67, dated 1887 by the IMSLP catalogue, listed on
  [IMSLP's Op. 68 page](https://imslp.org/wiki/Album_f%C3%BCr_die_Jugend,_Op.68_(Schumann,_Robert)).
  File **51556** is frozen for this workshop; No. 10 occupies PDF/printed page 8,
  five systems, no printed bar numbers. See the [source-pair check](sources/README.md).
- **Starting encoding:** Maja Hartwig's [MEI 5.1 sample](https://github.com/music-encoding/sample-encodings/blob/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei).
  Its header declares the encoding public domain; the collection has an
  [ECL-2.0 repository license](https://github.com/music-encoding/sample-encodings/blob/main/LICENSE).
  Its source description cites KernScores, not this print.
- **Teaching starter:** a notes-and-rhythms derivative with slurs, dynamics,
  tempo, verbal directions and articulation removed on purpose (recorded in its
  header), and the two A3 → F3 corrections. See the
  [starter README](examples/schumann/README.md) and the
  [teacher's task solutions](teacher/schumann/answer-key.md).
- **Scope:** the whole piece is the technical carrier; the edited passage is the
  pickup and bars 1–8 (MEI `n` 1–9, systems 1–2).
- **Worked comparison:** [the Webern edition](https://egorpol.github.io/webern_op27/)
  and its [editorial policy](https://github.com/egorpol/webern_op27/blob/main/docs/editorial-policy.md).

## Bar numbering: one vocabulary

The student page uses **musicians' bars**: "pickup", then bar 1 = first full
bar. Say "MEI `n`" only when pointing into the file. Avoid the other schemes in
class (zero-based `measure_index` in the OMR inspector, scaffold labels 0/1,
viewer `1/2`); the notebooks still need that clean-up (see open items).

| Bar | MEI `n` | System | Measure `xml:id` |
|---|---|---|---|
| pickup | 1 | 1 | `d1e9` |
| 1–4 | 2–5 | 1 | `d1e74` … `d1e968` |
| 5–8 | 6–9 | 2 | `d1e1231` … `d1e2125` |
| 9–12 | 10–13 | 3 | |
| 13–16 | 14–17 | 4 | |
| 17–20 | 18–21 | 5 | |

## Learning goals

Students can:

1. Open and run the seminar notebooks in VS Code on their own laptop.
2. Distinguish a printed witness, a downloaded scan, a base encoding and an edition.
3. Explain what OMR produces and why its result is compared with the scan.
4. Enter a short passage in a text notation and check it against the print,
   and explain what a reused encoding saves.
5. Locate a bar on the page image and in the MEI, by its number and its ID.

## Before class

- Ask students by e-mail to download the installers for steps 2, 3 and 5 of
  [setup-laptop.md](../../docs/setup-laptop.md) at home (the page has the tip).
  The `seminar` environment downloads about 770 MB per laptop; on shared
  Wi-Fi this is the bottleneck.
- Have the following open on the projector: IMSLP 51556 page 8, the upstream MEI
  on GitHub at the line of `d1e338`, the starter at the same line.
- Fallback for a laptop that cannot be set up today, and the route for
  tablet-only students: the cloud route in
  [setup.md](../../docs/setup.md#from-session-2-the-cloud-route) (Jupyter4NFDI
  workshop, image built by Repo2Docker from `binder/environment.yml`, same pins
  as the laptop). Pair work on a neighbour's laptop stays the default for a
  short failure. Preflight, at least a day before class:
    - Create the workshop in the Workshop Manager: Repo2Docker from
      `gh/egorpol/camat_lectures`, persistent storage mounted at
      `/home/jovyan/work` (the direct-link equivalent is
      `https://hub.nfdi-jupyter.de/v2/gh/egorpol/camat_lectures/<ref>?localstoragepath=%2Fhome%2Fjovyan%2Fwork`).
      Prefer a tag or commit as `<ref>`: with `main`, every push builds a new
      image at the next start. Put the link on the setup page (step 2 says
      "You get it in class").
    - Start it once yourself, so the image is built before class. Check that
      `work` exists, that a file in `work` survives a stop and restart, and run
      `02_pdf_preparation` up to `CAMAT: 0.2.8`.
    - Try the setup page's mei-friend link and part 7 on an iPad.
    - Verified only locally (2026-10-26): repo2docker's two conda steps
      (base lock for Python 3.12, then `env update` with `binder/environment.yml`)
      give Python 3.12.12, Poppler 25.07, CAMAT 0.2.8, and all three session 2
      notebooks run without warnings from a `work/` folder; JupyterLab 4.4.9
      opens `starter.mei` as text, and *Find* + *Next Match* jumps to the note.
      The terminal fallback (`conda` in the default Jupyter4NFDI image) is
      not tested there.
- Bring the scan on a USB stick or a shared folder, in case IMSLP refuses 20
  downloads at once: students copy it as
  `schumann_edition_work/sources/imslp-51556-schumann-op68.pdf` next to the
  notebooks. `02_schumann_omr` (part 4) and `02_pdf_preparation` (part 6) then
  use that copy after checking its SHA-256.

## Block 1 — Setup, with the source told during the download (90 minutes)

### 0–10 — Why our own laptops, and what we are building

Show a finished facsimile-linked edition (the Webern edition): source image,
rendered MEI, a bar link. Name the three sessions' arc: notes (today), linking
and editing (session 3), publishing and first analysis (session 4). Explain why
local tools now: VS Code edits the MEI next to the live viewer, Git keeps the
history, GitHub publishes.

### 10–40 — Setup steps 1–3

GitHub account, VS Code with the Python/Jupyter extensions, Miniforge. Walk
through each step on the projector for Windows and macOS; wait at each
**✓ Check**. Common delays: e-mail verification for GitHub, macOS security
prompts, Windows "Add to PATH" questions.

### 40–45 — Start step 4

Everyone starts `conda create …` and the `pip install` line. This is the long
download; laptops can be left alone while it runs.

### 45–60 — Source, scan, encoding, edition; the A3 → F3 story

On the projector, while the downloads run:

1. **Four objects** (student page part 2): the print as witness, the BSB scan on
   IMSLP, Hartwig's encoding (made from another source), the edition we make.
2. **The wrong note** (part 3): bass, bar 1 (MEI `n` 2), last eighth. Show it on
   the scan: the same staff position as the bar's first note, F3. Then the
   upstream MEI: `d1e338` has A3; the same in bar 5 (`n` 6, `d1e1495`). HOMR
   read F3 in both places, which is how the discrepancy surfaced on 24 October.
   The student page's comparison (part 3) shows the pickup and bar 1, and bar 5,
   from both files with the note in blue; it loads the upstream file from GitHub
   and adds the `lines="5"` that the file lacks (Verovio 6.3 draws no staff lines
   without it).
   Point: reuse saves typing, never the comparison with the source.

Interrupt for anyone whose step 4 fails.

### 60–90 — Setup steps 4 (check) to 7

Git with `git config`, VS Code GitHub sign-in and Copilot Free, `get_notebooks.py`
into `~/seminar-work`, then `02_pdf_preparation.ipynb` up to `CAMAT: 0.2.8`.

**Checkpoint:** each pair has at least one laptop that prints `CAMAT: 0.2.8`.
Note who is still stuck and at which step.

## Block 2 — From scan to notes (90 minutes)

### 0–10 — Finish the setup

Help the stuck laptops first; others open the OMR notebook and read its first
part. Do not wait for everyone: pairs share a laptop.

### 10–25 — OMR next to the scan

[`02_schumann_omr.ipynb`](notebooks/02_schumann_omr.ipynb) with the recorded
results ([guide](teacher/omr.md), [executed reference](teacher/references/omr-schumann/02_schumann_omr_recorded.ipynb),
[instructor evidence](teacher/omr-study-notes.md)). Students compare HOMR's crop
result for the first two systems with the scan, and find bar 1 and bar 5's last
bass note. Talking points:

- OMR proposes notes; it is a draft, not a transcription. HOMR's full page fails
  to import; its two-system crop imports and gets the bass of bar 1 right.
- HOMR's crop result has every pitch and length of the pickup and bars 1–8
  right, but drops *Frisch und munter*, both fortes and all beams. Its slurs sit
  on the right bass notes except for the missing start of the bars 3–4 slur; the
  slurs drawn from the treble (bars 2, 6, 7) and the lost bar 4–5 slur come from
  Verovio, not HOMR. Errors can enter at every step, not only in OMR.
  The full-page run puts bar 2's bass F4 into the treble chord (extension part
  4). The notebook's collapsed "What we found" has the answers.
- Page part 4 now says what HOMR and OeMeR are (with Audiveris as the
  window-based, correctable alternative) and points to the HOMR demo site
  `homr.site` (JPG/PNG in, MusicXML out; operator and privacy not stated; not
  tried by us). Its MusicXML opens in the part 5 *Any format* box.
- OeMeR (optional, part 4): right hand in the bass clef until its label 16, no
  key signature until its second label 12, 19 instead of 21 bars, a rest
  instead of the pickup's bass C3.
- Page images feed both OMR and measure detection (session 3): one yields notes,
  the other yields bar regions without notes.

**Optional instructor demo, only if the setup buffer (0–10) was not needed;
otherwise it opens session 3's Copilot part.** In Copilot chat, attach HOMR's
two-system MusicXML ([`raw.musicxml`](teacher/references/omr-schumann/homr-two-systems/raw.musicxml),
46 KB, pickup and bars 1–8, numbered 1–9) and `starter.mei`, and ask: "List
every difference in pitch or length between these two encodings, bar by bar.
Name each MEI note by its `xml:id`." Check each claim with `read_bar` in the OMR
notebook and on the scan. Expected (checked 2026-10-27 on the MusicXML text):
all 138 notes have the same onset, length, pitch and staff as in the starter; HOMR has
no beams, dynamics or tempo words, and has slurs that the starter leaves out.
Give Copilot the MusicXML, not Verovio's MEI conversion of it: Verovio 6.3's
import stretches HOMR's bars (6–8 `<backup>`s each) to 4.5–7.5 quarters in its
timemap, although each staff sums to 4. Any pitch difference the model reports is
invented, which is the point: the model reads both files, but the scan decides.
The MusicXML has no note ids; the MEI does, so the model can name `d1e338` and
we can find it in the drawing and in the file (part 7). Not tried yet: what
Copilot actually answers on these two files, and whether Copilot Free's monthly
chat limit matters for one demo.

### 25–45 — Five notes in ABC

The ABC box on the student page (part 5), or
[`02_note_entry.ipynb`](notebooks/02_note_entry.ipynb), part 1 (ABC), as in
session 1 ([guide](teacher/entry-methods.md), [executed reference](teacher/references/02_note_entry_recorded.ipynb)).
The page box gives the header and the pickup; students type bar 1, and under the
score *Verovio reads* lists pitches and lengths per bar and flags an incomplete
bar. It runs in any browser, so pairs whose setup is not finished can do it.
The solution is collapsed under the box. Everyone enters the same bass: pickup C3 eighth; bar 1 F3 dotted quarter, A3
eighth, C4 dotted quarter, F3 eighth (F major, common time, bass clef). Check
pitches/octaves, rhythm, pickup, clef and key against the print.

Extensions for fast pairs: the page's *Two more ways in* tabs, MuseScore (only
if installed; not part of the setup; export MEI or uncompressed MusicXML) and a
language model (Copilot chat, or any browser chat for cloud students), both
feeding the *Any format* box, which detects ABC, MEI, MusicXML, kern and PAE,
strips a code fence and has *Show as MEI*. Notebook part 2: Plaine & Easie, MEI
by hand, kern. Compare with a neighbour's format. Not tested here: a real
MuseScore MEI export in the box (no MuseScore on the build machine; MusicXML
and MEI files are covered by `tools/check_site_s2.py`).

Close with the question on the student page: what does an existing encoding of
all 21 bars save, and what not? "Notes only" here means durations, rests,
voices and notation context too; a pitch list cannot recreate the print.

### 45–75 — Prepare the PDF; the bar table

Continue [`02_pdf_preparation.ipynb`](notebooks/02_pdf_preparation.ipynb) from
the setup's check ([guide](teacher/pdf-preparation.md), [executed reference](teacher/references/02_pdf_preparation_recorded.ipynb)).
It keeps the original volume unchanged, extracts page 8 as a one-page PDF
(excerpt page 1 = printed page 8), renders it at 300 dpi, writes CAMAT's
`pages.json`, and checks the 21 bars across five systems against the MEI,
including two deliberately wrong layouts.

Go through the bar table on the student page: the pickup is MEI `n` 1, so bar 1
is `n` 2. Do not renumber after links exist (session 3).

**Checkpoint:** both partners agree on the system of each bar of the scope.
The notebook saves `page-preparation-checkpoint.json` and
`edition/measure-page-map.json`; session 3's linking notebook needs them.

### 75–85 — Find the note in the MEI

Start with the click demo on the student page (part 7, about 3 minutes): the
pickup and bar 1 of `starter.mei`, F3 `d1e338` selected. Clicking a note or rest
shows its pitch and length, its `<note>` tag in the MEI and Verovio's SVG group
with the same id (`<g id="d1e338" class="note">`, inside it notehead, stem,
flag). The point: the drawing knows *which* note it draws, the MEI knows *what*
the note is. The collapsed "What is SVG?" box links the offline
[SVG introduction](examples/svg-introduction/index.html); the full SVG part stays
in session 3. Then students search for the id they just clicked:

In VS Code (cloud: JupyterLab, *Edit → Find…*, then the *Next Match* arrow),
open `schumann_edition_work/inputs/<code>/starter.mei` and search for
`"d1e338"` with the quotes: F3 eighth in `<measure n="2">`. Without the quotes
there are five hits, and the first is in the header's change note. Introduce `xml:id` as the address the
viewer, the facsimile links and the edits use. No editing yet; session 3 edits
`edition/mei/work.mei`, which the linking notebook creates.

### 85–90 — Wrap-up

Source vs. everything checked against it; OMR and reuse save typing, not the
comparison. Preview session 3. Homework: finish the setup; compare bars 2–4 of
the bass with HOMR's reading.

## Open items before this session

1. Open the three notebooks once in VS Code: the collapsed "What we found" and
   "Solution" boxes (HTML `<details>`) are checked in JupyterLab 4.4.9 only.
2. Dry-run `setup-laptop.md` on one Windows and one Mac laptop; click through
   Copilot setup.
3. Commit, push and `mkdocs gh-deploy` early enough for students to read the
   setup page; `get_notebooks.py` cannot fetch session 2 before the push.

Detailed preparation notes and checks from the first plan:
[preparation.md](teacher/preparation.md), [status.md](teacher/status.md).
