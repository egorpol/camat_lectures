# Schumann teaching edition

This is a worked seminar project, using a notes-and-rhythms teaching derivative
of Maja Hartwig's MEI Sample Collection encoding and IMSLP 51556 as the witness.
The whole piece supplies the technical carrier; the exercise concerns three
editorial tasks in the opening passage. Source approval is recorded only in
`review.json`, never inferred from a working viewer or a green Actions run.

## Before building

Use Python 3.11 and install `requirements.txt`; full validation also needs
`xmllint` (for example `libxml2-utils` on Ubuntu). Choose a unique
`storage_prefix` in `site.json` for your pair. Inspect the edition statement,
credits, reviewed scope and open issues. Preserve `NOTICES.md` and licenses.

```sh
python -m pip install -r requirements.txt
python scripts/check_edition.py
python scripts/build_site.py
python -m http.server --bind 127.0.0.1 --directory _site 8000
```

Open http://127.0.0.1:8000/#landmann/1 (pickup), then #landmann/6 (second
system) and #landmann/21 (last bar). Check an editorial note, the downloaded
MEI and `publication.json`. Open the exact one-page source PDF as described
in `SOURCE.md`. The viewer uses external Verovio/pdf.js libraries; rehearse
internet access. `_site` is generated output and is rebuilt after edits.

Local image files are intentionally ignored by Git. An export from the seminar
notebook includes them for local validation. A fresh clone can still build the
PDF-opening viewer; use `python scripts/check_edition.py --without-local-images`
for the same limited checks as CI. Missing graphic files also appear in CAMAT's
reference pass: only missing local graphics declared by the page manifest are
accepted as CI omissions. Raw full conformance remains **failed/incomplete**;
other broken references still fail CI. Run full
local validation with the original page images before final review/release.

## GitHub Pages and release

The instructor creates the pair repository and configures Git/login before
class. Clone it; commit the MEI, configuration, provenance, source instructions,
review record and helper files. Push to `main`. In the repository, choose
Settings → Pages → Source → **GitHub Actions**. The supplied workflow checks
text/schema/references/rendering, builds, then deploys. The Pages job requires
permission to use the `github-pages` environment. It has not run merely because
the template contains a workflow file.

After the Actions deployment succeeds, inspect the actual Pages URL and one
bar link. `publication.json` records the built Git commit, dirty state, MEI
hash and review record. Compare the hash with the downloadable MEI. A stale
review hash is visible and needs review again. For a classroom tag/release,
target that checked commit as `v0.1.0`; describe the limited scope and remaining
review. Mark the release as a prerelease while it is a teaching draft.

If accounts, permissions or deployment delay the workshop, finish a local
commit and local viewer; record the remote step as pending. The instructor can
demonstrate one deployment later. Do not record a hypothetical URL as tested.

The `RELEASE.md` checklist is a template to fill, not evidence that the release
or source review already happened.
