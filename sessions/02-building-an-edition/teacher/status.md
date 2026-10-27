# Session 2 preparation status — 26 October 2026

The materials for both 90-minute blocks are assembled for the instructor overview.
The example is Schumann's *Fröhlicher Landmann*, Op.68 No.10. The whole piece
carries the technical workflow; the intended editorial scope is the pickup and
first eight full bars (MEI labels 1–9). Three completed tasks do not establish a
full proofread of every marking in that passage or the piece.

## Prepared

- Source pair/provenance, reduced starter, manual-entry scaffold and teacher key.
- Recorded Schumann OMR examples and several routes for entering five notes.
- PDF preparation, manual-region exercise, 21-zone facsimile linking and checkpoint.
- Live editing/watch workflow, structural guards, validation and teacher candidate.
- Dated free-model research, bounded prompts, SVG/LLM research and packet notebook.
- Beginner SVG browser demos, editable notebook and separate asset ZIP.
- mei-friend guide, peer-review sheet and blank review record bound to a file hash.
- Six-minute Git/GitHub primer adapted with attribution from the HfM Weimar tutorial.
- Review/release notebook, publication template ZIP, pinned Pages workflow,
  exact-source recovery, notices and release checklist.
- An account-free [two-commit Git example](publication/README.md),
  preserved as a small Git bundle with the worked edition and build files.
- [Student workshop page](../../../docs/sessions/02-building-an-edition/index.md),
  downloads and navigation: **eight notebooks and five data ZIPs**.

**Re-planned 26 October 2026:** the material now spans three sessions, because
the laptop setup takes most of session 2's first block. Session 2: setup, OMR,
note entry, PDF preparation ([outline](../outline.md)). Session 3: linking, SVG,
editing, mei-friend, peer review ([outline](../../03-linking-and-editing/outline.md)).
Session 4: Git, release, analysis ([outline](../../04-publishing-and-analysis/outline.md)).
The timings in the notebooks and guides below still follow the first plan.
The [preparation runbook](preparation.md) has the detail.

## What has been verified

Local runs cover PDF/page identity, linking and source/score selection, text
entry conversions, actual recorded OMR attempts, native watch refresh,
protected-content checks, required MEI checks and Verovio rendering. SVG packet
checks preserve IDs and demonstrate unchanged pixels after adding attributes.
Teacher candidates are deterministic examples, not claimed model outputs.
The beginner notebook runs without a CAMAT project. Browser checks over HTTP
cover colour/position, enlargement, direct note selection, pitch switching and
extra SVG attributes. Ordinary-browser offline opening remains to rehearse.

The review/release notebook runs in the fresh PyPI CAMAT 0.2.8 environment. The
exported MEI and download match byte-for-byte; the public build/template omit
scan pixels. A scratch Git rehearsal creates two commits and a tag, records the
correct clean commit in the site, and builds from a fresh clone. Scoped CI
accepts only declared missing local graphics; raw full conformance remains
failed/incomplete, and a broken internal reference still fails. Full local
validation includes images. The source excerpt is reproduced with its frozen
hash; export reruns preserve existing edits. Browser checks cover local PDF
opening, bar links 1/6/21 and annotation anchors. See
[publication evidence](publication/checks.json) and
[executed notebook](references/02_review_and_release_recorded.ipynb).
The strict course-site build and all relative Session 2 links/assets pass.
The publication hook includes only top-level notebook/ZIP downloads, excluding
ignored notebook runtime projects and their downloaded scans.

The mei-friend interface/menu was inspected. Opening the local Schumann file
was blocked when browser upload approval was declined; no alternative upload
was attempted. Its actual save/reopen round trip and local source-image route
remain unverified. The guide offers notebook-source and public-example
fallbacks. Local checker probes are not an actual mei-friend test.

Provider logins, free-account inference and model quality have not been
benchmarked. Technical success does not create source/alignment approval.

## Instructor preflight remaining

1. Approve actual source readings/alignment and scope. Blank records remain
   unreviewed until a named person performs the comparison.
2. Rehearse student VS Code/Jupyter4NFDI, MuseScore input/export and mei-friend
   save/reopen; try one real provider request if models will be used.
3. Configure the class GitHub repositories, login, permissions and Pages;
   perform a real push/deployment and inspect its public URL before class.
4. Run through both blocks with a timer. Load prepared stages when integration
   stalls; preserve review time and move extended model comparisons to homework.

All preparation changes remain local: the assistant has not committed or pushed
this course repository or published a site. Scratch Git commits are rehearsal data.
