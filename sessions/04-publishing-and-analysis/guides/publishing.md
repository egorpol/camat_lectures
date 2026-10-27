# Build and release the Schumann teaching edition

Block 2, **71–85 minutes**, following the [six-minute Git introduction](git-introduction.md).
Use [02_review_and_release.ipynb](../../02-building-an-edition/notebooks/02_review_and_release.ipynb) with
`schumann-release-template.zip` beside it. Account setup and repository permissions
belong before class; fourteen minutes covers a prepared publication route.

## 71–74: export a reviewable project

Run the notebook on the current `schumann_edition_work` project. It exports to
`publication-01`, preserving `edition/mei/work.mei`. A repeated export preserves
the existing folder; after changing the input, choose a new attempt folder.

The project contains the MEI, page manifest, source record/instructions, review,
validation evidence, notices, pinned dependencies and Pages workflow. Local
PDF/PNG files support rehearsal but are ignored by Git and omitted from the
public site. The transfer-only mei-friend file is not the publication MEI.

Set a unique pair `storage_prefix` in `site.json`. Read the title, credits,
edition statement, review scope and open issues. The whole piece is present;
three edited tasks do not establish a fully proofread passage or piece. The
default `review.json` deliberately remains `not_reviewed` until a person fills it.

## 74–78: validate, build and inspect

The notebook runs these commands inside the exported project:

```sh
python scripts/check_edition.py
python scripts/build_site.py
python -m http.server --bind 127.0.0.1 --directory _site 8000
```

Open `http://127.0.0.1:8000/#landmann/1` for the pickup, `#landmann/6` for the
second system and `#landmann/21` for the last bar. Activate the editorial note
and check its anchors. Compare the downloadable MEI hash with `publication.json`.
Saving the MEI refreshes the notebook's live view; rebuilding updates this site.

Open the **one-page excerpt**, not the original 50-page PDF, in the facsimile
panel. `SOURCE.md` explains original PDF page 8 → excerpt page 1 → printed page 8
and gives both hashes. Recover it from the original with
`python scripts/prepare_source.py --original /absolute/path/to/original.pdf`.
An explicit `--download` is another route; verify source access ahead of class.
The source is read locally in the visitor's browser. The viewer still requires
internet access for its Verovio/pdf.js libraries.

Full local validation checks image resources. A fresh Git clone omits them;
`python scripts/check_edition.py --without-local-images` performs the narrower
CI checks. The raw CAMAT report is failed/incomplete because graphic files are
absent; CI accepts only missing local graphics declared in the page manifest,
and rejects other reference errors. A green CI job does not supply the missing
image check or a human source review.

## 78–83: commit, deploy and inspect the actual URL

In the prepared repository, inspect the diff, stage the intended text/configuration
and evidence files, commit, then push to `main`. Keep generated `_site`, local
scans, credentials and runtime reports out of the commit. Frozen
`validation-evidence/` is the earlier review-stage evidence; CI creates its own
coverage record for the committed file.

The instructor configures Settings → Pages → Source → **GitHub Actions**.
The supplied workflow installs pinned tools, checks the MEI, builds `_site`,
uploads the result and deploys it. Wait for its actual result; publishing may
finish after the exercise. Inspect the Pages URL in a fresh tab, the same three
bar links, note and MEI download. `publication.json` must name the intended
commit and show the matching MEI hash. Resolve a stale review hash before calling
the new content reviewed.

## 83–85: identify the version

Once the deployed commit has been checked, tag that commit `v0.1.0`. Create a
GitHub prerelease describing the source, three tasks, actual review, known
limitations and local-PDF instructions. Fill in `RELEASE.md`; it is a checklist,
not evidence until completed. Record real repository, commit/tag, viewer and
bar-link URLs. Tagging another commit later changes what the label identifies.

If remote setup or deployment is pending, finish the local commit and HTTP
preview and record the remote step as pending. The instructor can demonstrate
publication from one prepared repository; account troubleshooting should not
replace the editorial review.

## Instructor preflight

Prepare the initial repository before the six-minute primer so students have
an existing history and a small meaningful diff. Rehearse Git identity/login,
push permission, the `github-pages` environment, Actions availability and the
actual public URL on the teaching network. Action versions were checked against
their official releases on 26 October 2026. The local template/build has been
rehearsed; merely including the workflow does not establish a successful GitHub
deployment. See [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
