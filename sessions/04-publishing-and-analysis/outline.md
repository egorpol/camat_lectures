# Session 4 — Publishing the edition, first analysis

Instructor outline, drafted 26 October 2026 from the end of the first session 2
plan. **Two 90-minute blocks.** Block 2 is not prepared yet.
Student page: [docs/sessions/04-publishing-and-analysis/index.md](../../docs/sessions/04-publishing-and-analysis/index.md).

The notebooks stay in [`../02-building-an-edition/notebooks/`](../02-building-an-edition/notebooks/)
with the project `schumann_edition_work`. Previous:
[session 3](../03-linking-and-editing/outline.md).

## Open decision

Repositories per pair: a template repository ("Use this template") or a GitHub
organisation/Classroom. Settle before this session; the Git cycle below assumes
each pair has an empty repository it can push to.

## The result students should leave with

A repository with the edition's MEI, its history (at least two commits), a
release `v0.1.0` whose description says **teaching edition / excerpt** and
names the reviewed passage, and a link to a viewer. Students do the commit and
push themselves; the GitHub Pages deployment is an instructor demonstration.

## Block 1 — Git, release, viewer (90 minutes)

### 0–40 — Git and GitHub in one small cycle

Use the [Git introduction](guides/git-introduction.md),
adapted from the HfM Weimar tutorial, now with time for it. Show a repository, a
meaningful Schumann MEI diff (the three edits from session 3), staging, a local
commit and a push. Distinguish saving, committing, pushing, tagging/releasing
and deploying. Git and the GitHub sign-in were set up in session 2.

### 40–75 — Build and release an edition

Use the [publication guide](guides/publishing.md),
[review/release notebook](../02-building-an-edition/notebooks/02_review_and_release.ipynb)
and [template ZIP](../02-building-an-edition/notebooks/schumann-release-template.zip).
The export preserves the working MEI, copies review evidence and supplies
source retrieval, notices, build scripts and the Pages workflow.

Build and preview `_site` locally; check the selected bar, annotation and
facsimile. Saving MEI refreshes the notebook; publishing needs another build.
Tag `v0.1.0` and write the release description: scope, credits, review, known
issues, how to obtain the facsimile. Instructor demo: the Pages workflow deploys
one repository; open the public URL in a fresh browser and follow a bar link.

Keep the scan a separate third-party source: the template lets readers open
their own PDF locally; the public build contains no scan pixels.

**Checkpoint:** repository URL + release version + one bar link.

### 75–90 — Reflect

What can now be analysed that the scan alone did not support? How would a
missing slur or wrong accidental (the A3 of session 2) affect that analysis?

## Block 2 — From the edition to analysis (90 minutes, to prepare)

Bridge to CAMAT: the edited MEI as a note table and piano roll (session 1's
piano-roll demo prepared this), the difference the A3 → F3 correction makes in
the data, first counts. Material still to be written.

## Before this session

- Revise the Git introduction and publication guide in session 1's voice; move
  "Instructor preflight" and CI/conformance details out of student pages.
- Do one real push and Pages deployment from a student-like account.
